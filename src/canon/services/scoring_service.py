"""Scoring-service: calculates confidence scores for canonical entities.

Formula: final_score = (age * 0.3) + (corroboration * 0.3) + (independence * 0.2) - (ambiguity * 0.2)

Thresholds:
  high (>0.7)   -> core canon
  medium (0.4-0.7) -> canon with caution
  low (<0.4)    -> branch
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.models.canonical_actor import CanonicalActor
from src.canon.models.canonical_event import CanonicalEvent
from src.canon.models.canonical_place import CanonicalPlace
from src.canon.models.canon_score import CanonScore
from src.canon.models.canon_support_link import CanonSupportLink
from src.canon.models.enums import CanonicalType, SupportType
from src.canon.models.system_a import SATrustedSource, SARawObject, SASourceRecord

logger = logging.getLogger(__name__)

AGE_WEIGHT = 0.3
CORROBORATION_WEIGHT = 0.3
INDEPENDENCE_WEIGHT = 0.2
AMBIGUITY_WEIGHT = 0.2


class ScoringService:

    async def _count_support_links(
        self, session: AsyncSession, canonical_type: CanonicalType, canonical_id: uuid.UUID
    ) -> dict:
        """Count support links by type for a canonical entity."""
        q = select(
            CanonSupportLink.support_type,
            func.count(CanonSupportLink.id),
            func.sum(CanonSupportLink.weight),
        ).where(
            CanonSupportLink.canonical_type == canonical_type,
            CanonSupportLink.canonical_id == canonical_id,
        ).group_by(CanonSupportLink.support_type)

        result = await session.execute(q)
        counts = {}
        for row in result.all():
            counts[row[0]] = {"count": row[1], "total_weight": float(row[2] or 0)}
        return counts

    async def _count_distinct_sources(
        self, session: AsyncSession, canonical_type: CanonicalType, canonical_id: uuid.UUID
    ) -> int:
        """Count how many distinct trusted sources back this entity (for independence)."""
        q = (
            select(func.count(func.distinct(SARawObject.trusted_source_id)))
            .select_from(CanonSupportLink)
            .join(SASourceRecord, SASourceRecord.id == CanonSupportLink.archive_object_id)
            .join(SARawObject, SARawObject.id == SASourceRecord.raw_object_id)
            .where(
                CanonSupportLink.canonical_type == canonical_type,
                CanonSupportLink.canonical_id == canonical_id,
            )
        )
        try:
            result = await session.execute(q)
            return result.scalar() or 0
        except Exception:
            return 0

    def _compute_age_score(self, time_start: int | None, time_end: int | None) -> float:
        """Older sources get higher age scores (antiquity is evidence of persistence)."""
        if time_start is None and time_end is None:
            return 0.3
        ref = time_start if time_start is not None else time_end
        age = abs(ref)
        if age > 4000:
            return 1.0
        if age > 3000:
            return 0.85
        if age > 2000:
            return 0.7
        if age > 1000:
            return 0.5
        return 0.3

    def _compute_corroboration_score(self, link_counts: dict) -> float:
        """More support links (especially primary + corroborating) = higher score."""
        primary = link_counts.get(SupportType.PRIMARY_EVIDENCE, {}).get("count", 0)
        corroborating = link_counts.get(SupportType.CORROBORATING, {}).get("count", 0)
        secondary = link_counts.get(SupportType.SECONDARY_CONTEXT, {}).get("count", 0)
        contradicting = link_counts.get(SupportType.CONTRADICTING, {}).get("count", 0)

        total_positive = primary + corroborating + (secondary * 0.5)
        if total_positive == 0:
            return 0.1

        score = min(total_positive / 5.0, 1.0)
        if contradicting > 0:
            penalty = min(contradicting * 0.1, 0.3)
            score = max(score - penalty, 0.0)
        return score

    def _compute_independence_score(self, distinct_sources: int) -> float:
        """More independent sources = higher independence score."""
        if distinct_sources <= 0:
            return 0.1
        if distinct_sources == 1:
            return 0.3
        if distinct_sources == 2:
            return 0.6
        if distinct_sources >= 3:
            return min(0.5 + (distinct_sources * 0.1), 1.0)
        return 0.3

    def _compute_ambiguity_score(self, link_counts: dict, merge_confidence: float | None) -> float:
        """Higher ambiguity = penalty. Contradictions and low merge confidence increase ambiguity."""
        contradicting = link_counts.get(SupportType.CONTRADICTING, {}).get("count", 0)
        ambiguity = 0.0

        if contradicting > 0:
            ambiguity += min(contradicting * 0.15, 0.5)

        if merge_confidence is not None and merge_confidence < 0.5:
            ambiguity += (0.5 - merge_confidence)

        return min(ambiguity, 1.0)

    async def score_entity(
        self,
        session: AsyncSession,
        canonical_type: CanonicalType,
        canonical_id: uuid.UUID,
        time_start: int | None,
        time_end: int | None,
        merge_confidence: float | None,
    ) -> CanonScore:
        """Compute and store the score for a single canonical entity."""
        link_counts = await self._count_support_links(session, canonical_type, canonical_id)
        distinct_sources = await self._count_distinct_sources(session, canonical_type, canonical_id)

        age = self._compute_age_score(time_start, time_end)
        corroboration = self._compute_corroboration_score(link_counts)
        independence = self._compute_independence_score(distinct_sources)
        ambiguity = self._compute_ambiguity_score(link_counts, merge_confidence)

        final = (
            (age * AGE_WEIGHT)
            + (corroboration * CORROBORATION_WEIGHT)
            + (independence * INDEPENDENCE_WEIGHT)
            - (ambiguity * AMBIGUITY_WEIGHT)
        )
        final = max(0.0, min(1.0, final))

        existing_q = select(CanonScore).where(
            CanonScore.canonical_type == canonical_type,
            CanonScore.canonical_id == canonical_id,
        )
        existing = (await session.execute(existing_q)).scalar_one_or_none()

        if existing:
            existing.age_score = age
            existing.corroboration_score = corroboration
            existing.independence_score = independence
            existing.ambiguity_score = ambiguity
            existing.final_score = final
            return existing

        score = CanonScore(
            id=uuid.uuid4(),
            canonical_type=canonical_type,
            canonical_id=canonical_id,
            age_score=age,
            corroboration_score=corroboration,
            independence_score=independence,
            ambiguity_score=ambiguity,
            final_score=final,
        )
        session.add(score)
        return score

    async def run_full_scoring(self, session: AsyncSession) -> dict:
        """Score all current canonical entities."""
        scored = 0

        actors_q = select(CanonicalActor).where(CanonicalActor.is_current.is_(True))
        for a in (await session.execute(actors_q)).scalars().all():
            await self.score_entity(
                session, CanonicalType.ACTOR, a.id, a.time_start, a.time_end, a.merge_confidence
            )
            scored += 1

        events_q = select(CanonicalEvent).where(CanonicalEvent.is_current.is_(True))
        for e in (await session.execute(events_q)).scalars().all():
            await self.score_entity(
                session, CanonicalType.EVENT, e.id, e.time_start, e.time_end, e.merge_confidence
            )
            scored += 1

        places_q = select(CanonicalPlace).where(CanonicalPlace.is_current.is_(True))
        for p in (await session.execute(places_q)).scalars().all():
            await self.score_entity(
                session, CanonicalType.PLACE, p.id, p.time_start, p.time_end, p.merge_confidence
            )
            scored += 1

        await session.flush()
        logger.info("Scored %d canonical entities", scored)
        return {"entities_scored": scored}
