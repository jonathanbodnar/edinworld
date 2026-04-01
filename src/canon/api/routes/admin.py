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
from src.canon.models.extracted_hint import ExtractedHint
from src.canon.schemas.canonical import SynthesisRequest, SynthesisResponse
from src.canon.services.canon_synth import CanonSynthService
from src.canon.services.chapter_builder import ChapterBuilderService
from src.canon.services.knowledge_prep import KnowledgePrepService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run-synthesis", response_model=SynthesisResponse)
async def run_synthesis(
    request: SynthesisRequest = SynthesisRequest(),
    session: AsyncSession = Depends(get_session),
):
    """Trigger the full canon synthesis pipeline."""
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

    return result


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)):
    """Get system B stats."""
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

    return {
        "extracted_hints": hints_count,
        "epochs": epochs_count,
        "chapters": chapters_count,
        "actors": actors_count,
        "events": events_count,
        "places": places_count,
    }
