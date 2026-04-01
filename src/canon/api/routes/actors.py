from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.database import get_session
from src.canon.models.canonical_actor import CanonicalActor
from src.canon.models.canon_support_link import CanonSupportLink
from src.canon.models.enums import CanonicalType
from src.canon.schemas.canonical import ActorResponse, SupportLinkResponse

router = APIRouter()


@router.get("/", response_model=list[ActorResponse])
async def list_actors(
    actor_type: str | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(CanonicalActor)
        .where(CanonicalActor.is_current.is_(True))
        .order_by(CanonicalActor.canonical_name)
        .limit(limit)
        .offset(offset)
    )
    if actor_type:
        q = q.where(CanonicalActor.actor_type == actor_type)
    if search:
        q = q.where(CanonicalActor.canonical_name.ilike(f"%{search}%"))
    result = await session.execute(q)
    return [ActorResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor(actor_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    actor = await session.get(CanonicalActor, actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return ActorResponse.model_validate(actor)


@router.get("/{actor_id}/support-links", response_model=list[SupportLinkResponse])
async def get_actor_support_links(
    actor_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    q = select(CanonSupportLink).where(
        CanonSupportLink.canonical_type == CanonicalType.ACTOR,
        CanonSupportLink.canonical_id == actor_id,
    )
    result = await session.execute(q)
    return [SupportLinkResponse.model_validate(sl) for sl in result.scalars().all()]
