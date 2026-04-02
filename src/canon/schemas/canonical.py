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


class MotifResponse(BaseModel):
    id: uuid.UUID
    label: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MotifAssignmentResponse(BaseModel):
    id: uuid.UUID
    motif_id: uuid.UUID
    motif_label: str | None = None
    target_type: str
    target_id: uuid.UUID
    confidence: float

    model_config = {"from_attributes": True}


class ScoreResponse(BaseModel):
    id: uuid.UUID
    canonical_type: str
    canonical_id: uuid.UUID
    age_score: float
    corroboration_score: float
    independence_score: float
    ambiguity_score: float
    final_score: float
    tier: str = ""

    model_config = {"from_attributes": True}


class NarrationPacketResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    intro_summary: str | None = None
    core_summary: str | None = None
    branch_summary: str | None = None
    key_actor_ids_json: list | None = None
    key_event_ids_json: list | None = None
    key_place_ids_json: list | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorldPacketResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    canon_version: int
    packet_version: int
    time_start: int | None = None
    time_end: int | None = None
    world_summary: str | None = None
    environment_profile_json: dict | None = None
    material_culture_json: dict | None = None
    symbol_system_json: dict | None = None
    motifs_json: dict | list | None = None
    key_actors_json: dict | list | None = None
    key_places_json: dict | list | None = None
    key_events_json: dict | list | None = None
    hard_constraints_json: dict | None = None
    soft_constraints_json: dict | None = None
    consistency_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryThreadResponse(BaseModel):
    id: uuid.UUID
    title: str
    thread_type: str
    summary: str | None = None
    time_start: int | None = None
    time_end: int | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BranchResponse(BaseModel):
    id: uuid.UUID
    parent_type: str
    parent_id: uuid.UUID
    branch_title: str
    branch_reason: str | None = None
    alternate_summary: str | None = None
    confidence_profile_json: dict | None = None
    version: int
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChangeEventResponse(BaseModel):
    id: uuid.UUID
    change_type: str
    source_object_type: str
    source_object_id: uuid.UUID
    affected_time_start: int | None = None
    affected_time_end: int | None = None
    impact_score: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterSourceSetResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    source_record_id: uuid.UUID
    title: str | None = None
    excerpt: str | None = None
    relevance_weight: float
    image_ref: str | None = None
    source_type: str | None = None

    model_config = {"from_attributes": True}


class ChapterContextSetResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    contextual_statement_id: uuid.UUID
    summary: str | None = None
    artifact_description: str | None = None
    relevance_weight: float

    model_config = {"from_attributes": True}


class ChapterArtifactSetResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    raw_object_id: uuid.UUID
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    location: str | None = None
    date_label: str | None = None

    model_config = {"from_attributes": True}


class ChapterImageSetResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    object_image_id: uuid.UUID | None = None
    image_url: str | None = None
    caption: str | None = None
    image_type: str | None = None
    display_order: int

    model_config = {"from_attributes": True}


class ChapterFocusObjectResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    object_type: str
    object_id: uuid.UUID
    focus_reason: str | None = None
    display_order: int

    model_config = {"from_attributes": True}


class EpochWithCountResponse(EpochResponse):
    chapter_count: int = 0


class ChatQueryRequest(BaseModel):
    query: str
    chapter_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None


class ChatQueryResponse(BaseModel):
    session_id: str
    answer_packet_id: str
    answer: str
    answer_mode: str
    confidence: float
    sources: list[dict] = []
    contexts: list[dict] = []


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    answer_packet_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetailResponse(ChatSessionResponse):
    messages: list[ChatMessageResponse] = []


class AnswerPacketResponse(BaseModel):
    id: uuid.UUID
    query: str
    chapter_id: uuid.UUID | None = None
    answer_mode: str
    answer_summary: str
    confidence: float
    created_at: datetime
    sources: list[dict] = []
    contexts: list[dict] = []

    model_config = {"from_attributes": True}


class SynthesisRequest(BaseModel):
    run_extraction: bool = True
    run_synthesis: bool = True
    run_chapters: bool = True
    run_motifs: bool = False
    run_scoring: bool = False
    run_narration: bool = False
    run_world_packets: bool = False
    run_change_detection: bool = False
    run_impact_resolution: bool = False
    run_canon_updates: bool = False
    run_evidence_bundles: bool = False


class SynthesisResponse(BaseModel):
    extraction: dict | None = None
    synthesis: dict | None = None
    chapters: dict | None = None
    motifs: dict | None = None
    scoring: dict | None = None
    narration: dict | None = None
    world_packets: dict | None = None
    change_detection: dict | None = None
    impact_resolution: dict | None = None
    canon_updates: dict | None = None
    evidence_bundles: dict | None = None
    status: str = "completed"


ChapterDetailResponse.model_rebuild()
