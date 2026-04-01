from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.database import get_session
from src.canon.models.canonical_event import CanonicalEvent
from src.canon.models.canon_support_link import CanonSupportLink
from src.canon.models.enums import CanonicalType
from src.canon.schemas.canonical import EventResponse, SupportLinkResponse

router = APIRouter()


@router.get("/", response_model=list[EventResponse])
async def list_events(
    event_type: str | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(CanonicalEvent)
        .where(CanonicalEvent.is_current.is_(True))
        .order_by(CanonicalEvent.canonical_name)
        .limit(limit)
        .offset(offset)
    )
    if event_type:
        q = q.where(CanonicalEvent.event_type == event_type)
    if search:
        q = q.where(CanonicalEvent.canonical_name.ilike(f"%{search}%"))
    result = await session.execute(q)
    return [EventResponse.model_validate(e) for e in result.scalars().all()]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    event = await session.get(CanonicalEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)


@router.get("/{event_id}/support-links", response_model=list[SupportLinkResponse])
async def get_event_support_links(
    event_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    q = select(CanonSupportLink).where(
        CanonSupportLink.canonical_type == CanonicalType.EVENT,
        CanonSupportLink.canonical_id == event_id,
    )
    result = await session.execute(q)
    return [SupportLinkResponse.model_validate(sl) for sl in result.scalars().all()]
