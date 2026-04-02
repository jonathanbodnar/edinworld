from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.database import get_session
from src.canon.models.canonical_actor import CanonicalActor
from src.canon.models.canonical_chapter import CanonicalChapter
from src.canon.models.canonical_epoch import CanonicalEpoch
from src.canon.models.canonical_event import CanonicalEvent
from src.canon.models.canonical_place import CanonicalPlace
from src.canon.models.canon_score import CanonScore
from src.canon.models.change_event import ChangeEvent, CanonUpdateTarget
from src.canon.models.extracted_hint import ExtractedHint
from src.canon.models.motif import Motif, MotifAssignment
from src.canon.models.narration_packet import NarrationPacket
from src.canon.models.world_packet import WorldPacket
from src.canon.schemas.canonical import SynthesisRequest, SynthesisResponse
from src.canon.services.canon_synth import CanonSynthService
from src.canon.services.canon_update import CanonUpdateService
from src.canon.services.change_detect import ChangeDetectService
from src.canon.services.chapter_builder import ChapterBuilderService
from src.canon.services.impact_resolver import ImpactResolver
from src.canon.services.knowledge_prep import KnowledgePrepService
from src.canon.services.merge_service import MergeService
from src.canon.services.motif_service import MotifService
from src.canon.services.narration_builder import NarrationBuilderService
from src.canon.services.scoring_service import ScoringService
from src.canon.services.evidence_bundle_builder import EvidenceBundleBuilder
from src.canon.services.world_packet_builder import WorldPacketBuilderService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run-synthesis", response_model=SynthesisResponse)
async def run_synthesis(
    request: SynthesisRequest = SynthesisRequest(),
    session: AsyncSession = Depends(get_session),
):
    """Trigger the full canon synthesis pipeline (all phases)."""
    result = SynthesisResponse()

    if request.run_extraction:
        svc = KnowledgePrepService()
        result.extraction = await svc.run_full_extraction(session)
        await session.commit()

    if request.run_synthesis:
        svc = CanonSynthService()
        result.synthesis = await svc.run_full_synthesis(session)
        await session.commit()

    if request.run_chapters:
        svc = ChapterBuilderService()
        result.chapters = await svc.run_full_build(session)
        await session.commit()

    if request.run_motifs:
        svc = MotifService()
        result.motifs = await svc.run_full_motif_assignment(session)
        await session.commit()

    if request.run_scoring:
        svc = ScoringService()
        result.scoring = await svc.run_full_scoring(session)
        await session.commit()

    if request.run_narration:
        svc = NarrationBuilderService()
        result.narration = await svc.run_full_build(session)
        await session.commit()

    if request.run_world_packets:
        svc = WorldPacketBuilderService()
        result.world_packets = await svc.run_full_build(session)
        await session.commit()

    if request.run_change_detection:
        svc = ChangeDetectService()
        result.change_detection = await svc.run_full_detection(session)
        await session.commit()

    if request.run_impact_resolution:
        svc = ImpactResolver()
        result.impact_resolution = await svc.resolve_all_pending(session)
        await session.commit()

    if request.run_canon_updates:
        svc = CanonUpdateService()
        result.canon_updates = await svc.process_all_pending(session)
        await session.commit()

    if request.run_evidence_bundles:
        svc = EvidenceBundleBuilder()
        result.evidence_bundles = await svc.build_all(session)
        await session.commit()

    return result


@router.post("/run-full-pipeline", response_model=SynthesisResponse)
async def run_full_pipeline(session: AsyncSession = Depends(get_session)):
    """Run every phase of the pipeline in sequence."""
    return await run_synthesis(
        SynthesisRequest(
            run_extraction=True,
            run_synthesis=True,
            run_chapters=True,
            run_motifs=True,
            run_scoring=True,
            run_narration=True,
            run_world_packets=True,
            run_change_detection=True,
            run_impact_resolution=True,
            run_canon_updates=True,
        ),
        session,
    )


@router.post("/run-alias-merges")
async def run_alias_merges(session: AsyncSession = Depends(get_session)):
    """Run Level 1 alias merges across all entity types."""
    svc = MergeService()
    result = await svc.run_alias_merges(session)
    await session.commit()
    return result


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)):
    """Get comprehensive system B stats."""
    hints_count = (await session.execute(select(func.count(ExtractedHint.id)))).scalar() or 0
    epochs_count = (await session.execute(
        select(func.count(CanonicalEpoch.id)).where(CanonicalEpoch.is_current.is_(True))
    )).scalar() or 0
    chapters_count = (await session.execute(
        select(func.count(CanonicalChapter.id)).where(CanonicalChapter.is_current.is_(True))
    )).scalar() or 0
    actors_count = (await session.execute(
        select(func.count(CanonicalActor.id)).where(CanonicalActor.is_current.is_(True))
    )).scalar() or 0
    events_count = (await session.execute(
        select(func.count(CanonicalEvent.id)).where(CanonicalEvent.is_current.is_(True))
    )).scalar() or 0
    places_count = (await session.execute(
        select(func.count(CanonicalPlace.id)).where(CanonicalPlace.is_current.is_(True))
    )).scalar() or 0
    motifs_count = (await session.execute(select(func.count(Motif.id)))).scalar() or 0
    motif_assignments_count = (await session.execute(select(func.count(MotifAssignment.id)))).scalar() or 0
    scores_count = (await session.execute(select(func.count(CanonScore.id)))).scalar() or 0
    narration_count = (await session.execute(select(func.count(NarrationPacket.id)))).scalar() or 0
    world_packets_count = (await session.execute(select(func.count(WorldPacket.id)))).scalar() or 0
    change_events_count = (await session.execute(select(func.count(ChangeEvent.id)))).scalar() or 0
    update_targets_count = (await session.execute(select(func.count(CanonUpdateTarget.id)))).scalar() or 0

    return {
        "extracted_hints": hints_count,
        "epochs": epochs_count,
        "chapters": chapters_count,
        "actors": actors_count,
        "events": events_count,
        "places": places_count,
        "motifs": motifs_count,
        "motif_assignments": motif_assignments_count,
        "scores": scores_count,
        "narration_packets": narration_count,
        "world_packets": world_packets_count,
        "change_events": change_events_count,
        "update_targets": update_targets_count,
    }
