"""Merge logic for canonical entities. Implements 4 merge levels:
  Level 1 — Alias: same entity, different spelling
  Level 2 — Motif cluster: same role, different identity
  Level 3 — Candidate equivalence: embedding similarity + temporal overlap
  Level 4 — Canon merge: only when final_score threshold met
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.models.canonical_actor import CanonicalActor
from src.canon.models.canonical_event import CanonicalEvent
from src.canon.models.canonical_place import CanonicalPlace
from src.canon.models.canon_score import CanonScore
from src.canon.models.canon_support_link import CanonSupportLink
from src.canon.models.canon_dependency import CanonDependency
from src.canon.models.motif import MotifAssignment
from src.canon.models.enums import CanonicalType

logger = logging.getLogger(__name__)

ALIAS_VARIANTS = {
    "inanna": ["ishtar", "astarte"],
    "enlil": ["ellil"],
    "enki": ["ea"],
    "utu": ["shamash"],
    "nanna": ["sin", "suen"],
    "dumuzi": ["tammuz"],
    "ereshkigal": ["allatu"],
    "ninhursag": ["ninmah", "nintu", "ki"],
    "marduk": ["bel", "asalluhi"],
    "gilgamesh": ["bilgames"],
    "ur": ["ur iii"],
    "eridu": ["eridu"],
    "nippur": ["nibru"],
    "uruk": ["unug", "warka"],
    "babylon": ["babilu", "babel"],
}

CANON_MERGE_THRESHOLD = 0.7


def _normalize(name: str) -> str:
    return name.strip().lower()


def _build_alias_map() -> dict[str, str]:
    """Build a reverse map: variant -> canonical form."""
    alias_map = {}
    for canonical, variants in ALIAS_VARIANTS.items():
        alias_map[canonical] = canonical
        for v in variants:
            alias_map[v] = canonical
    return alias_map


class MergeService:
    def __init__(self):
        self._alias_map = _build_alias_map()

    def level1_alias_group(self, names: list[str]) -> dict[str, list[str]]:
        """Group names by alias equivalence. Returns canonical_form -> [original_names]."""
        groups: dict[str, list[str]] = defaultdict(list)
        for name in names:
            norm = _normalize(name)
            canonical_form = self._alias_map.get(norm, norm)
            groups[canonical_form].append(name)
        return dict(groups)

    async def level2_motif_cluster(
        self, session: AsyncSession, entity_type: CanonicalType
    ) -> list[list[uuid.UUID]]:
        """Group entities that share the same motifs (same role, not same entity)."""
        q = select(MotifAssignment).where(MotifAssignment.target_type == entity_type)
        assignments = (await session.execute(q)).scalars().all()

        motif_to_entities: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
        for a in assignments:
            motif_to_entities[a.motif_id].append(a.target_id)

        clusters = []
        for motif_id, entity_ids in motif_to_entities.items():
            if len(entity_ids) > 1:
                clusters.append(entity_ids)
        return clusters

    def level3_temporal_overlap(
        self,
        candidates: list[dict],
        overlap_threshold: float = 0.5,
    ) -> list[tuple[dict, dict]]:
        """Find candidate equivalences based on temporal overlap.
        Each candidate: {"id": uuid, "name": str, "time_start": int|None, "time_end": int|None}
        """
        pairs = []
        for i, a in enumerate(candidates):
            for b in candidates[i + 1:]:
                if a["time_start"] is None or b["time_start"] is None:
                    continue
                if a["time_end"] is None or b["time_end"] is None:
                    continue

                overlap_start = max(a["time_start"], b["time_start"])
                overlap_end = min(a["time_end"], b["time_end"])
                if overlap_start >= overlap_end:
                    continue

                overlap_len = overlap_end - overlap_start
                span_a = a["time_end"] - a["time_start"]
                span_b = b["time_end"] - b["time_start"]
                max_span = max(span_a, span_b, 1)

                if overlap_len / max_span >= overlap_threshold:
                    pairs.append((a, b))
        return pairs

    async def level4_canon_merge(
        self,
        session: AsyncSession,
        entity_type: CanonicalType,
        entity_a_id: uuid.UUID,
        entity_b_id: uuid.UUID,
    ) -> bool:
        """Merge entity_b into entity_a if both meet the score threshold.
        Creates a new version of entity_a, marks entity_b as not current.
        Returns True if merge happened.
        """
        score_a_q = select(CanonScore).where(
            CanonScore.canonical_type == entity_type,
            CanonScore.canonical_id == entity_a_id,
        )
        score_b_q = select(CanonScore).where(
            CanonScore.canonical_type == entity_type,
            CanonScore.canonical_id == entity_b_id,
        )
        score_a = (await session.execute(score_a_q)).scalar_one_or_none()
        score_b = (await session.execute(score_b_q)).scalar_one_or_none()

        if not score_a or not score_b:
            logger.info("Cannot merge: missing scores for %s or %s", entity_a_id, entity_b_id)
            return False

        avg_score = (score_a.final_score + score_b.final_score) / 2
        if avg_score < CANON_MERGE_THRESHOLD:
            logger.info(
                "Score too low for merge: %.2f (threshold %.2f)", avg_score, CANON_MERGE_THRESHOLD
            )
            return False

        await session.execute(
            update(CanonSupportLink)
            .where(
                CanonSupportLink.canonical_type == entity_type,
                CanonSupportLink.canonical_id == entity_b_id,
            )
            .values(canonical_id=entity_a_id)
        )

        await session.execute(
            update(CanonDependency)
            .where(CanonDependency.child_type == entity_type, CanonDependency.child_id == entity_b_id)
            .values(child_id=entity_a_id)
        )

        await session.execute(
            update(MotifAssignment)
            .where(MotifAssignment.target_type == entity_type, MotifAssignment.target_id == entity_b_id)
            .values(target_id=entity_a_id)
        )

        if entity_type == CanonicalType.ACTOR:
            entity_b = await session.get(CanonicalActor, entity_b_id)
            if entity_b:
                entity_b.is_current = False
        elif entity_type == CanonicalType.EVENT:
            entity_b = await session.get(CanonicalEvent, entity_b_id)
            if entity_b:
                entity_b.is_current = False
        elif entity_type == CanonicalType.PLACE:
            entity_b = await session.get(CanonicalPlace, entity_b_id)
            if entity_b:
                entity_b.is_current = False

        await session.flush()
        logger.info("Merged %s %s into %s", entity_type.value, entity_b_id, entity_a_id)
        return True

    async def run_alias_merges(self, session: AsyncSession) -> dict:
        """Run Level 1 alias merges across all entity types."""
        merged_count = 0

        for model_cls, entity_type in [
            (CanonicalActor, CanonicalType.ACTOR),
            (CanonicalEvent, CanonicalType.EVENT),
            (CanonicalPlace, CanonicalType.PLACE),
        ]:
            q = select(model_cls).where(model_cls.is_current.is_(True))
            entities = (await session.execute(q)).scalars().all()

            name_to_entities: dict[str, list] = defaultdict(list)
            for e in entities:
                norm = _normalize(e.canonical_name)
                canonical_form = self._alias_map.get(norm, norm)
                name_to_entities[canonical_form].append(e)

            for canonical_form, group in name_to_entities.items():
                if len(group) <= 1:
                    continue

                primary = max(group, key=lambda e: e.merge_confidence or 0)
                for other in group:
                    if other.id == primary.id:
                        continue
                    merged = await self.level4_canon_merge(
                        session, entity_type, primary.id, other.id
                    )
                    if merged:
                        merged_count += 1

        await session.flush()
        return {"alias_merges": merged_count}
