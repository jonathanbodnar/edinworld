"""System B initial schema - all canonical tables.

Revision ID: world_001
Revises:
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "world_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ENUM types ---
    hint_type = postgresql.ENUM("actor", "event", "place", name="hint_type", create_type=False)
    actor_type = postgresql.ENUM(
        "deity", "ruler", "mythic_figure", "historical_person", "collective", "unknown",
        name="actor_type", create_type=False,
    )
    event_type = postgresql.ENUM(
        "creation", "flood", "war", "migration", "founding", "ritual",
        "astronomical", "death", "succession", "trade", "construction", "unknown",
        name="event_type", create_type=False,
    )
    place_type = postgresql.ENUM(
        "city", "temple", "river", "mountain", "region", "underworld",
        "celestial", "sacred_site", "unknown",
        name="place_type", create_type=False,
    )
    thread_type = postgresql.ENUM(
        "kingship", "divine_conflict", "creation_cycle", "hero_journey",
        "descent", "flood_cycle", "cultural_transmission", "unknown",
        name="thread_type", create_type=False,
    )
    canonical_type = postgresql.ENUM(
        "epoch", "chapter", "actor", "event", "place", "story_thread", "branch",
        name="canonical_type", create_type=False,
    )
    support_type = postgresql.ENUM(
        "primary_evidence", "secondary_context", "corroborating", "contradicting",
        name="support_type", create_type=False,
    )
    archive_object_type = postgresql.ENUM(
        "source_record", "source_version", "segment", "contextual_statement",
        name="archive_object_type", create_type=False,
    )
    world_job_type = postgresql.ENUM(
        "extract_hints", "synth_canon", "build_chapters", "build_narration",
        "build_world_packets", "update_canon",
        name="world_job_type", create_type=False,
    )
    world_job_status = postgresql.ENUM(
        "queued", "running", "succeeded", "failed", "paused", "canceled",
        name="world_job_status", create_type=False,
    )
    change_type = postgresql.ENUM(
        "new_segment", "updated_segment", "new_statement", "updated_statement", "new_source",
        name="change_type", create_type=False,
    )
    update_target_status = postgresql.ENUM(
        "pending", "processing", "completed", "failed",
        name="update_target_status", create_type=False,
    )

    hint_type.create(op.get_bind(), checkfirst=True)
    actor_type.create(op.get_bind(), checkfirst=True)
    event_type.create(op.get_bind(), checkfirst=True)
    place_type.create(op.get_bind(), checkfirst=True)
    thread_type.create(op.get_bind(), checkfirst=True)
    canonical_type.create(op.get_bind(), checkfirst=True)
    support_type.create(op.get_bind(), checkfirst=True)
    archive_object_type.create(op.get_bind(), checkfirst=True)
    world_job_type.create(op.get_bind(), checkfirst=True)
    world_job_status.create(op.get_bind(), checkfirst=True)
    change_type.create(op.get_bind(), checkfirst=True)
    update_target_status.create(op.get_bind(), checkfirst=True)

    # --- extracted_hints ---
    op.create_table(
        "extracted_hints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hint_type", hint_type, nullable=False, index=True),
        sa.Column("name", sa.String(1024), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("source_segment_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("source_statement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("extraction_model", sa.String(256), nullable=True),
        sa.Column("metadata_jsonb", postgresql.JSONB, nullable=True),
        sa.Column("merged_into_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_epochs ---
    op.create_table(
        "canonical_epochs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_chapters ---
    op.create_table(
        "canonical_chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("epoch_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("chapter_summary", sa.Text, nullable=True),
        sa.Column("chapter_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_actors ---
    op.create_table(
        "canonical_actors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_name", sa.String(1024), nullable=False, index=True),
        sa.Column("actor_type", actor_type, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("merge_confidence", sa.Float, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_events ---
    op.create_table(
        "canonical_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_name", sa.String(1024), nullable=False, index=True),
        sa.Column("event_type", event_type, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("merge_confidence", sa.Float, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_places ---
    op.create_table(
        "canonical_places",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_name", sa.String(1024), nullable=False, index=True),
        sa.Column("place_type", place_type, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("geo_hint_json", postgresql.JSONB, nullable=True),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("merge_confidence", sa.Float, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canonical_story_threads ---
    op.create_table(
        "canonical_story_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(1024), nullable=False, index=True),
        sa.Column("thread_type", thread_type, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canon_branches ---
    op.create_table(
        "canon_branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("parent_type", canonical_type, nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("branch_title", sa.String(1024), nullable=False),
        sa.Column("branch_reason", sa.Text, nullable=True),
        sa.Column("alternate_summary", sa.Text, nullable=True),
        sa.Column("confidence_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canon_support_links ---
    op.create_table(
        "canon_support_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_type", canonical_type, nullable=False),
        sa.Column("canonical_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("archive_object_type", archive_object_type, nullable=False),
        sa.Column("archive_object_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("support_type", support_type, nullable=False),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canon_scores ---
    op.create_table(
        "canon_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_type", canonical_type, nullable=False),
        sa.Column("canonical_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("age_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("corroboration_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("independence_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("ambiguity_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("final_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canon_dependencies ---
    op.create_table(
        "canon_dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("parent_type", canonical_type, nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("child_type", canonical_type, nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- motifs ---
    op.create_table(
        "motifs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("label", sa.String(512), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- motif_assignments ---
    op.create_table(
        "motif_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("motif_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("target_type", canonical_type, nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- narration_packets ---
    op.create_table(
        "narration_packets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("intro_summary", sa.Text, nullable=True),
        sa.Column("core_summary", sa.Text, nullable=True),
        sa.Column("branch_summary", sa.Text, nullable=True),
        sa.Column("key_actor_ids_json", postgresql.JSONB, nullable=True),
        sa.Column("key_event_ids_json", postgresql.JSONB, nullable=True),
        sa.Column("key_place_ids_json", postgresql.JSONB, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- world_packets ---
    op.create_table(
        "world_packets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("canon_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("packet_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("time_start", sa.Integer, nullable=True),
        sa.Column("time_end", sa.Integer, nullable=True),
        sa.Column("world_summary", sa.Text, nullable=True),
        sa.Column("environment_profile_json", postgresql.JSONB, nullable=True),
        sa.Column("material_culture_json", postgresql.JSONB, nullable=True),
        sa.Column("symbol_system_json", postgresql.JSONB, nullable=True),
        sa.Column("motifs_json", postgresql.JSONB, nullable=True),
        sa.Column("key_actors_json", postgresql.JSONB, nullable=True),
        sa.Column("key_places_json", postgresql.JSONB, nullable=True),
        sa.Column("key_events_json", postgresql.JSONB, nullable=True),
        sa.Column("hard_constraints_json", postgresql.JSONB, nullable=True),
        sa.Column("soft_constraints_json", postgresql.JSONB, nullable=True),
        sa.Column("reference_image_ids_json", postgresql.JSONB, nullable=True),
        sa.Column("source_panel_ids_json", postgresql.JSONB, nullable=True),
        sa.Column("consistency_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- change_events ---
    op.create_table(
        "change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("change_type", change_type, nullable=False),
        sa.Column("source_object_type", archive_object_type, nullable=False),
        sa.Column("source_object_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("affected_time_start", sa.Integer, nullable=True),
        sa.Column("affected_time_end", sa.Integer, nullable=True),
        sa.Column("impact_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- canon_update_targets ---
    op.create_table(
        "canon_update_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("change_event_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("target_type", canonical_type, nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", update_target_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- world_queued_jobs ---
    op.create_table(
        "world_queued_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_type", world_job_type, nullable=False, index=True),
        sa.Column("status", world_job_status, nullable=False, server_default="queued", index=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("payload_json", postgresql.JSONB, nullable=True),
        sa.Column("result_json", postgresql.JSONB, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer, nullable=False, server_default="3"),
        sa.Column("worker_id", sa.String(256), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- world_job_checkpoints ---
    op.create_table(
        "world_job_checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("checkpoint_data", postgresql.JSONB, nullable=False),
        sa.Column("items_processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("world_job_checkpoints")
    op.drop_table("world_queued_jobs")
    op.drop_table("canon_update_targets")
    op.drop_table("change_events")
    op.drop_table("world_packets")
    op.drop_table("narration_packets")
    op.drop_table("motif_assignments")
    op.drop_table("motifs")
    op.drop_table("canon_dependencies")
    op.drop_table("canon_scores")
    op.drop_table("canon_support_links")
    op.drop_table("canon_branches")
    op.drop_table("canonical_story_threads")
    op.drop_table("canonical_places")
    op.drop_table("canonical_events")
    op.drop_table("canonical_actors")
    op.drop_table("canonical_chapters")
    op.drop_table("canonical_epochs")
    op.drop_table("extracted_hints")

    for name in [
        "update_target_status", "change_type", "world_job_status", "world_job_type",
        "archive_object_type", "support_type", "canonical_type", "thread_type",
        "place_type", "event_type", "actor_type", "hint_type",
    ]:
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
