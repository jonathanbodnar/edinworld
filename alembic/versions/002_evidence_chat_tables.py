"""Add evidence bundle tables and chat/answer tables.

Revision ID: world_002
Revises: world_001
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "world_002"
down_revision = "world_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    chat_role = postgresql.ENUM("user", "assistant", "system", name="chat_role", create_type=False)
    answer_mode = postgresql.ENUM("source", "context", "synthesis", "unsupported", name="answer_mode", create_type=False)

    chat_role.create(op.get_bind(), checkfirst=True)
    answer_mode.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "chapter_source_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("source_record_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(2048), nullable=True),
        sa.Column("excerpt", sa.Text, nullable=True),
        sa.Column("relevance_weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("image_ref", sa.String(4096), nullable=True),
        sa.Column("source_type", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chapter_context_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("contextual_statement_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("artifact_description", sa.Text, nullable=True),
        sa.Column("relevance_weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chapter_artifact_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("raw_object_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(2048), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("image_url", sa.String(4096), nullable=True),
        sa.Column("location", sa.String(1024), nullable=True),
        sa.Column("date_label", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chapter_image_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("object_image_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("image_url", sa.String(4096), nullable=True),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("image_type", sa.String(128), nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chapter_focus_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("object_type", sa.String(128), nullable=False),
        sa.Column("object_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("focus_reason", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("role", chat_role, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("answer_packet_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "answer_packets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("answer_mode", answer_mode, nullable=False),
        sa.Column("answer_summary", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "answer_packet_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("answer_packet_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("source_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("excerpt", sa.Text, nullable=True),
        sa.Column("support_type", sa.Text, nullable=True),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
    )

    op.create_table(
        "answer_packet_context",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("answer_packet_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("contextual_statement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
    )


def downgrade() -> None:
    op.drop_table("answer_packet_context")
    op.drop_table("answer_packet_sources")
    op.drop_table("answer_packets")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("chapter_focus_objects")
    op.drop_table("chapter_image_sets")
    op.drop_table("chapter_artifact_sets")
    op.drop_table("chapter_context_sets")
    op.drop_table("chapter_source_sets")

    for name in ["answer_mode", "chat_role"]:
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
