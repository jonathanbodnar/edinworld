from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class EpochResponse(BaseModel):
    id: uuid.UUID
    title: str
    time_start: int | None = None
    time_end: int | None = None
    summary: str | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterResponse(BaseModel):
    id: uuid.UUID
    epoch_id: uuid.UUID
    title: str
    time_start: int | None = None
    time_end: int | None = None
    chapter_summary: str | None = None
    chapter_order: int
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterDetailResponse(ChapterResponse):
    actors: list[ActorResponse] = []
    events: list[EventResponse] = []
    places: list[PlaceResponse] = []


class ActorResponse(BaseModel):
    id: uuid.UUID
    canonical_name: str
    actor_type: str
    summary: str | None = None
    time_start: int | None = None
    time_end: int | None = None
    merge_confidence: float | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    id: uuid.UUID
    canonical_name: str
    event_type: str
    summary: str | None = None
    time_start: int | None = None
    time_end: int | None = None
    merge_confidence: float | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlaceResponse(BaseModel):
    id: uuid.UUID
    canonical_name: str
    place_type: str
    summary: str | None = None
    geo_hint_json: dict | None = None
    time_start: int | None = None
    time_end: int | None = None
    merge_confidence: float | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TimelineEntry(BaseModel):
    id: uuid.UUID
    canonical_type: str
    name: str
    time_start: int | None = None
    time_end: int | None = None
    summary: str | None = None


class TimelineResponse(BaseModel):
    entries: list[TimelineEntry]
    total: int


class SupportLinkResponse(BaseModel):
    id: uuid.UUID
    canonical_type: str
    canonical_id: uuid.UUID
    archive_object_type: str
    archive_object_id: uuid.UUID
    support_type: str
    weight: float

    model_config = {"from_attributes": True}


class SynthesisRequest(BaseModel):
    run_extraction: bool = True
    run_synthesis: bool = True
    run_chapters: bool = True


class SynthesisResponse(BaseModel):
    extraction: dict | None = None
    synthesis: dict | None = None
    chapters: dict | None = None
    status: str = "completed"


ChapterDetailResponse.model_rebuild()
