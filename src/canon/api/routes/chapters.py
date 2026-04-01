from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.database import get_session
from src.canon.models.canonical_chapter import CanonicalChapter
from src.canon.models.canonical_actor import CanonicalActor
from src.canon.models.canonical_event import CanonicalEvent
from src.canon.models.canonical_place import CanonicalPlace
from src.canon.models.canon_dependency import CanonDependency
from src.canon.models.enums import CanonicalType
from src.canon.schemas.canonical import (
    ActorResponse,
    ChapterDetailResponse,
    ChapterResponse,
    EventResponse,
    PlaceResponse,
)

router = APIRouter()


@router.get("/", response_model=list[ChapterResponse])
async def list_chapters(
    epoch_id: uuid.UUID | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(CanonicalChapter)
        .where(CanonicalChapter.is_current.is_(True))
        .order_by(CanonicalChapter.chapter_order)
        .limit(limit)
        .offset(offset)
    )
    if epoch_id:
        q = q.where(CanonicalChapter.epoch_id == epoch_id)
    result = await session.execute(q)
    return [ChapterResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/{chapter_id}", response_model=ChapterDetailResponse)
async def get_chapter(
    chapter_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    chapter = await session.get(CanonicalChapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    deps_q = select(CanonDependency).where(
        CanonDependency.parent_type == CanonicalType.CHAPTER,
        CanonDependency.parent_id == chapter_id,
    )
    deps = (await session.execute(deps_q)).scalars().all()

    actor_ids = [d.child_id for d in deps if d.child_type == CanonicalType.ACTOR]
    event_ids = [d.child_id for d in deps if d.child_type == CanonicalType.EVENT]
    place_ids = [d.child_id for d in deps if d.child_type == CanonicalType.PLACE]

    actors = []
    if actor_ids:
        aq = select(CanonicalActor).where(CanonicalActor.id.in_(actor_ids))
        actors = [ActorResponse.model_validate(a) for a in (await session.execute(aq)).scalars().all()]

    events = []
    if event_ids:
        eq = select(CanonicalEvent).where(CanonicalEvent.id.in_(event_ids))
        events = [EventResponse.model_validate(e) for e in (await session.execute(eq)).scalars().all()]

    places = []
    if place_ids:
        pq = select(CanonicalPlace).where(CanonicalPlace.id.in_(place_ids))
        places = [PlaceResponse.model_validate(p) for p in (await session.execute(pq)).scalars().all()]

    return ChapterDetailResponse(
        **ChapterResponse.model_validate(chapter).model_dump(),
        actors=actors,
        events=events,
        places=places,
    )
