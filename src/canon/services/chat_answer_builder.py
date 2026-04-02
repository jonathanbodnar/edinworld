"""ChatAnswerBuilder: receives a user query, retrieves evidence from chapter bundles,
calls Anthropic for a grounded answer, creates answer_packets with linked sources/context."""

from __future__ import annotations

import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.config import settings
from src.canon.models.answer_packet import AnswerPacket, AnswerPacketContext, AnswerPacketSource
from src.canon.models.chapter_context_set import ChapterContextSet
from src.canon.models.chapter_source_set import ChapterSourceSet
from src.canon.models.chat_session import ChatMessage, ChatSession
from src.canon.models.enums import AnswerMode, ChatRole
from src.canon.models.system_a import SAContextualStatement, SASourceRecord

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are a scholarly research assistant specializing in ancient history and mythology.
You answer questions based ONLY on the provided source evidence and contextual statements.
If the evidence is insufficient, say so honestly.

Rules:
- Ground every claim in a specific source or statement from the evidence provided.
- When referencing a source, mention it by title.
- If multiple sources disagree, present both perspectives.
- Never fabricate information not present in the evidence.
- Be concise but thorough.

Respond with a JSON object:
{
  "answer": "your answer text",
  "confidence": 0.0-1.0,
  "answer_mode": "source|context|synthesis|unsupported",
  "referenced_source_indices": [0, 1],
  "referenced_context_indices": [0, 2]
}

answer_mode values:
- "source": answer is directly supported by primary sources
- "context": answer relies on scholarly context/interpretation
- "synthesis": answer synthesizes multiple sources
- "unsupported": evidence is insufficient to answer"""

ANSWER_TOOL = {
    "name": "provide_answer",
    "description": "Provide a grounded answer to the user's question based on the evidence.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "The answer text"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "answer_mode": {"type": "string", "enum": ["source", "context", "synthesis", "unsupported"]},
            "referenced_source_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Indices into the sources list that support this answer",
            },
            "referenced_context_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Indices into the context list that support this answer",
            },
        },
        "required": ["answer", "confidence", "answer_mode"],
    },
}


class ChatAnswerBuilder:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def answer_query(
        self,
        session: AsyncSession,
        query: str,
        chapter_id: uuid.UUID | None = None,
        session_id: uuid.UUID | None = None,
    ) -> dict:
        """Process a user query: retrieve evidence, call LLM, create answer packet."""
        if session_id:
            chat_session = await session.get(ChatSession, session_id)
        else:
            chat_session = ChatSession(id=uuid.uuid4(), chapter_id=chapter_id)
            session.add(chat_session)
            await session.flush()

        user_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=chat_session.id,
            role=ChatRole.USER.value,
            content=query,
        )
        session.add(user_msg)

        sources, contexts = await self._retrieve_evidence(session, chapter_id)

        if not sources and not contexts:
            answer_packet = await self._create_unsupported_packet(session, query, chapter_id)
        else:
            answer_packet = await self._call_llm_and_create_packet(
                session, query, chapter_id, sources, contexts
            )

        assistant_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=chat_session.id,
            role=ChatRole.ASSISTANT.value,
            content=answer_packet.answer_summary,
            answer_packet_id=answer_packet.id,
        )
        session.add(assistant_msg)
        await session.flush()

        return {
            "session_id": str(chat_session.id),
            "answer_packet_id": str(answer_packet.id),
            "answer": answer_packet.answer_summary,
            "answer_mode": answer_packet.answer_mode,
            "confidence": answer_packet.confidence,
            "sources": [
                {
                    "id": str(s.id),
                    "source_record_id": str(s.source_record_id),
                    "excerpt": s.excerpt,
                    "support_type": s.support_type,
                    "weight": s.weight,
                }
                for s in (await self._get_packet_sources(session, answer_packet.id))
            ],
            "contexts": [
                {
                    "id": str(c.id),
                    "contextual_statement_id": str(c.contextual_statement_id),
                    "summary": c.summary,
                    "weight": c.weight,
                }
                for c in (await self._get_packet_contexts(session, answer_packet.id))
            ],
        }

    async def _retrieve_evidence(
        self, session: AsyncSession, chapter_id: uuid.UUID | None
    ) -> tuple[list[dict], list[dict]]:
        """Retrieve source and context evidence for a chapter."""
        sources = []
        contexts = []

        if not chapter_id:
            return sources, contexts

        src_q = (
            select(ChapterSourceSet)
            .where(ChapterSourceSet.chapter_id == chapter_id)
            .order_by(ChapterSourceSet.relevance_weight.desc())
            .limit(20)
        )
        src_rows = (await session.execute(src_q)).scalars().all()

        for row in src_rows:
            record = await session.get(SASourceRecord, row.source_record_id)
            sources.append({
                "source_record_id": row.source_record_id,
                "title": row.title or (record.canonical_title if record else "Unknown"),
                "excerpt": row.excerpt or "",
                "source_type": row.source_type,
                "weight": row.relevance_weight,
            })

        ctx_q = (
            select(ChapterContextSet)
            .where(ChapterContextSet.chapter_id == chapter_id)
            .order_by(ChapterContextSet.relevance_weight.desc())
            .limit(20)
        )
        ctx_rows = (await session.execute(ctx_q)).scalars().all()

        for row in ctx_rows:
            stmt = await session.get(SAContextualStatement, row.contextual_statement_id)
            contexts.append({
                "contextual_statement_id": row.contextual_statement_id,
                "summary": row.summary or (stmt.statement_text[:500] if stmt and stmt.statement_text else ""),
                "weight": row.relevance_weight,
            })

        return sources, contexts

    def _build_evidence_prompt(self, query: str, sources: list[dict], contexts: list[dict]) -> str:
        parts = [f"Question: {query}\n"]

        if sources:
            parts.append("== Primary Sources ==")
            for i, s in enumerate(sources):
                parts.append(f"[Source {i}] {s['title']}")
                if s.get("excerpt"):
                    parts.append(f"  Excerpt: {s['excerpt']}")
                parts.append(f"  Type: {s.get('source_type', 'unknown')}")
                parts.append("")

        if contexts:
            parts.append("== Contextual Statements ==")
            for i, c in enumerate(contexts):
                parts.append(f"[Context {i}] {c['summary']}")
                parts.append("")

        return "\n".join(parts)

    async def _call_llm_and_create_packet(
        self,
        session: AsyncSession,
        query: str,
        chapter_id: uuid.UUID | None,
        sources: list[dict],
        contexts: list[dict],
    ) -> AnswerPacket:
        prompt = self._build_evidence_prompt(query, sources, contexts)

        answer_data = {"answer": "", "confidence": 0.0, "answer_mode": "unsupported"}

        if settings.anthropic_api_key:
            try:
                response = self.client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=4096,
                    system=CHAT_SYSTEM_PROMPT,
                    tools=[ANSWER_TOOL],
                    tool_choice={"type": "tool", "name": "provide_answer"},
                    messages=[{"role": "user", "content": prompt}],
                )
                for block in response.content:
                    if block.type == "tool_use" and block.name == "provide_answer":
                        answer_data = block.input
                        break
            except Exception:
                logger.exception("Anthropic chat answer failed")
                answer_data = {
                    "answer": "I encountered an error processing your question. Please try again.",
                    "confidence": 0.0,
                    "answer_mode": "unsupported",
                }
        else:
            answer_data = {
                "answer": "AI answering is not configured. Evidence has been retrieved for manual review.",
                "confidence": 0.0,
                "answer_mode": "unsupported",
            }

        packet = AnswerPacket(
            id=uuid.uuid4(),
            query=query,
            chapter_id=chapter_id,
            answer_mode=answer_data.get("answer_mode", "unsupported"),
            answer_summary=answer_data.get("answer", ""),
            confidence=answer_data.get("confidence", 0.0),
        )
        session.add(packet)
        await session.flush()

        ref_src = answer_data.get("referenced_source_indices", list(range(min(5, len(sources)))))
        for idx in ref_src:
            if 0 <= idx < len(sources):
                s = sources[idx]
                ps = AnswerPacketSource(
                    id=uuid.uuid4(),
                    answer_packet_id=packet.id,
                    source_record_id=s["source_record_id"],
                    excerpt=s.get("excerpt"),
                    support_type=s.get("source_type"),
                    weight=s.get("weight", 1.0),
                )
                session.add(ps)

        ref_ctx = answer_data.get("referenced_context_indices", list(range(min(5, len(contexts)))))
        for idx in ref_ctx:
            if 0 <= idx < len(contexts):
                c = contexts[idx]
                pc = AnswerPacketContext(
                    id=uuid.uuid4(),
                    answer_packet_id=packet.id,
                    contextual_statement_id=c["contextual_statement_id"],
                    summary=c.get("summary"),
                    weight=c.get("weight", 1.0),
                )
                session.add(pc)

        return packet

    async def _create_unsupported_packet(
        self, session: AsyncSession, query: str, chapter_id: uuid.UUID | None
    ) -> AnswerPacket:
        packet = AnswerPacket(
            id=uuid.uuid4(),
            query=query,
            chapter_id=chapter_id,
            answer_mode=AnswerMode.UNSUPPORTED.value,
            answer_summary="No evidence is available to answer this question. Try selecting a chapter first, or rephrase your question.",
            confidence=0.0,
        )
        session.add(packet)
        await session.flush()
        return packet

    async def _get_packet_sources(self, session: AsyncSession, packet_id: uuid.UUID) -> list[AnswerPacketSource]:
        q = select(AnswerPacketSource).where(AnswerPacketSource.answer_packet_id == packet_id)
        return list((await session.execute(q)).scalars().all())

    async def _get_packet_contexts(self, session: AsyncSession, packet_id: uuid.UUID) -> list[AnswerPacketContext]:
        q = select(AnswerPacketContext).where(AnswerPacketContext.answer_packet_id == packet_id)
        return list((await session.execute(q)).scalars().all())
