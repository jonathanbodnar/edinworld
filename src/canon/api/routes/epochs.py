from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.database import get_session
from src.canon.models.canonical_chapter import CanonicalChapter
from src.canon.models.canonical_epoch import CanonicalEpoch
from src.canon.schemas.canonical import EpochResponse, EpochWithCountResponse

router = APIRouter()


@router.get("/", response_model=list[EpochWithCountResponse])
async def list_epochs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(CanonicalEpoch)
        .where(CanonicalEpoch.is_current.is_(True))
        .order_by(CanonicalEpoch.time_start.asc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    epochs = (await session.execute(q)).scalars().all()

    results = []
    for epoch in epochs:
        count_q = select(func.count(CanonicalChapter.id)).where(
            CanonicalChapter.epoch_id == epoch.id,
            CanonicalChapter.is_current.is_(True),
        )
        chapter_count = (await session.execute(count_q)).scalar() or 0
        resp = EpochWithCountResponse(
            **EpochResponse.model_validate(epoch).model_dump(),
            chapter_count=chapter_count,
        )
        results.append(resp)

    return results


@router.get("/{epoch_id}", response_model=EpochWithCountResponse)
async def get_epoch(
    epoch_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    epoch = await session.get(CanonicalEpoch, epoch_id)
    if not epoch:
        raise HTTPException(status_code=404, detail="Epoch not found")

    count_q = select(func.count(CanonicalChapter.id)).where(
        CanonicalChapter.epoch_id == epoch.id,
        CanonicalChapter.is_current.is_(True),
    )
    chapter_count = (await session.execute(count_q)).scalar() or 0
    return EpochWithCountResponse(
        **EpochResponse.model_validate(epoch).model_dump(),
        chapter_count=chapter_count,
    )
