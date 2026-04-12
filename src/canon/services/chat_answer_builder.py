"""ChatAnswerBuilder: receives a user query, retrieves relevant evidence using
text search across System A data and chapter bundles, calls an LLM (DeepSeek,
Ollama, or Anthropic) for a grounded answer, creates answer_packets with linked
sources/context."""

from __future__ import annotations

import json
import logging
import re
import uuid

import httpx
from sqlalchemy import Integer, func, or_, select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from src.canon.config import settings
from src.canon.models.answer_packet import AnswerPacket, AnswerPacketContext, AnswerPacketSource
from src.canon.models.chapter_context_set import ChapterContextSet
from src.canon.models.chapter_source_set import ChapterSourceSet
from src.canon.models.chat_session import ChatMessage, ChatSession
from src.canon.models.enums import AnswerMode, ChatRole
from src.canon.models.system_a import SAContextualStatement, SASegment, SASourceRecord, SASourceVersion

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are a scholarly research assistant for an ancient history and mythology research platform called Edinworld.
The platform contains source records, text segments, and contextual analysis from museums, text corpora, and historical archives.

You answer questions using the provided source evidence: source records (with titles, culture, category) and text segments (actual content from these sources).

Rules:
- Use the evidence provided to construct the best answer you can.
- When referencing a source, mention it by title and culture.
- Quote relevant text segments when they directly support a point.
- If multiple sources disagree, present both perspectives.
- If the evidence is only partially relevant, answer what you can and note what's missing.
- If NO evidence is relevant, explain what kinds of sources would be needed and suggest the user try different search terms.
- Be conversational, concise, and scholarly.
- Keep answers to 2-4 paragraphs maximum."""

CHAT_SYSTEM_PROMPT_JSON = CHAT_SYSTEM_PROMPT + """

You MUST respond with valid JSON in this exact format (no markdown, no extra text):
{"answer": "your answer text", "confidence": 0.8, "answer_mode": "source", "referenced_source_indices": [0, 1], "referenced_context_indices": [0]}

answer_mode must be one of: source, context, synthesis, unsupported
- source = directly backed by primary sources
- context = based on scholarly interpretation
- synthesis = combines multiple sources
- unsupported = insufficient evidence
confidence is 0.0 to 1.0
referenced_source_indices and referenced_context_indices are arrays of integers indexing into the provided sources/texts lists."""

ANSWER_TOOL = {
    "name": "provide_answer",
    "description": "Provide an answer to the user's question based on the evidence.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "The answer text"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "answer_mode": {
                "type": "string",
                "enum": ["source", "context", "synthesis", "unsupported"],
                "description": "source=directly backed by primary sources, context=based on scholarly interpretation, synthesis=combines multiple sources, unsupported=insufficient evidence",
            },
            "referenced_source_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Indices into the sources list that support this answer",
            },
            "referenced_context_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Indices into the contexts list that support this answer",
            },
        },
        "required": ["answer", "confidence", "answer_mode"],
    },
}

STOP_WORDS = {
    "the", "a", "an", "is", "was", "were", "are", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "of", "in", "to", "for",
    "with", "on", "at", "from", "by", "about", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "and", "but",
    "or", "not", "no", "so", "if", "then", "than", "too", "very", "just",
    "that", "this", "these", "those", "it", "its", "what", "which", "who",
    "whom", "how", "when", "where", "why", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "any", "only", "own",
    "same", "tell", "me", "i", "my", "you", "your", "we", "our", "they",
    "their", "there", "here", "up", "out", "many", "much",
}


def _extract_keywords(query: str) -> list[str]:
    """Extract meaningful search keywords from a natural language query,
    with basic stemming to improve ILIKE matching."""
    words = re.findall(r"[a-zA-ZÀ-ÿ'ʼ]{2,}", query.lower())
    keywords = [w for w in words if w not in STOP_WORDS]

    stemmed: list[str] = []
    for w in keywords:
        stem = w
        if stem.endswith("ies") and len(stem) > 4:
            stem = stem[:-3] + "y"
        elif stem.endswith("es") and len(stem) > 4:
            stem = stem[:-2]
        elif stem.endswith("s") and not stem.endswith("ss") and len(stem) > 3:
            stem = stem[:-1]
        if stem.endswith("ing") and len(stem) > 5:
            stem = stem[:-3]
        if stem not in stemmed:
            stemmed.append(stem)
        if w != stem and w not in stemmed:
            stemmed.append(w)

    return stemmed[:12]


class ChatAnswerBuilder:
    def __init__(self):
        self._anthropic_client = None

    @property
    def anthropic_client(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    @property
    def _use_deepseek(self) -> bool:
        return bool(settings.deepseek_api_key)

    @property
    def _use_ollama(self) -> bool:
        return bool(settings.ollama_base_url)

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

        sources, contexts = await self._retrieve_evidence(session, query, chapter_id)

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
        self, session: AsyncSession, query: str, chapter_id: uuid.UUID | None
    ) -> tuple[list[dict], list[dict]]:
        """Query-aware evidence retrieval: searches source records by title/culture
        and segments by text content, using keywords from the user's question."""
        keywords = _extract_keywords(query)
        if not keywords:
            keywords = query.lower().split()[:5]

        sources = await self._search_source_records(session, keywords, chapter_id)
        contexts = await self._search_segments(session, keywords, chapter_id)

        return sources, contexts

    async def _search_source_records(
        self, session: AsyncSession, keywords: list[str], chapter_id: uuid.UUID | None
    ) -> list[dict]:
        """Search source_records by matching keywords against title, culture, and category."""
        if chapter_id:
            src_q = (
                select(ChapterSourceSet)
                .where(ChapterSourceSet.chapter_id == chapter_id)
                .order_by(ChapterSourceSet.relevance_weight.desc())
                .limit(15)
            )
            rows = (await session.execute(src_q)).scalars().all()
            sources = []
            for row in rows:
                record = await session.get(SASourceRecord, row.source_record_id)
                sources.append({
                    "source_record_id": row.source_record_id,
                    "title": row.title or (record.canonical_title if record else "Unknown"),
                    "culture": record.culture if record else None,
                    "excerpt": row.excerpt or "",
                    "source_type": row.source_type,
                    "weight": row.relevance_weight,
                })
            return sources

        if not keywords:
            return []

        match_cases = []
        for kw in keywords:
            pattern = f"%{kw}%"
            match_cases.append(
                func.coalesce(func.cast(SASourceRecord.canonical_title.ilike(pattern), Integer), 0)
                + func.coalesce(func.cast(SASourceRecord.culture.ilike(pattern), Integer), 0)
            )
        relevance = sum(match_cases).label("relevance")

        any_conditions = []
        for kw in keywords:
            pattern = f"%{kw}%"
            any_conditions.append(SASourceRecord.canonical_title.ilike(pattern))
            any_conditions.append(SASourceRecord.culture.ilike(pattern))

        q = (
            select(SASourceRecord, relevance)
            .where(or_(*any_conditions))
            .order_by(relevance.desc())
            .limit(15)
        )
        rows = (await session.execute(q)).all()

        sources = []
        seen: set[uuid.UUID] = set()
        for rec, score in rows:
            if rec.id in seen:
                continue
            seen.add(rec.id)

            excerpt = ""
            ver_q = (
                select(SASourceVersion)
                .where(SASourceVersion.source_record_id == rec.id)
                .where(SASourceVersion.text_extracted.isnot(None))
                .limit(1)
            )
            ver = (await session.execute(ver_q)).scalar_one_or_none()
            if ver and ver.text_extracted:
                excerpt = ver.text_extracted[:500]

            sources.append({
                "source_record_id": rec.id,
                "title": rec.canonical_title,
                "culture": rec.culture,
                "excerpt": excerpt,
                "source_type": rec.source_category,
                "weight": float(score or 1),
            })

        return sources

    async def _search_segments(
        self, session: AsyncSession, keywords: list[str], chapter_id: uuid.UUID | None
    ) -> list[dict]:
        """Search segments by matching keywords against normalized_text, and
        return them as context entries with actual text excerpts."""
        if chapter_id:
            ctx_q = (
                select(ChapterContextSet)
                .where(ChapterContextSet.chapter_id == chapter_id)
                .order_by(ChapterContextSet.relevance_weight.desc())
                .limit(10)
            )
            rows = (await session.execute(ctx_q)).scalars().all()
            contexts = []
            for row in rows:
                stmt = await session.get(SAContextualStatement, row.contextual_statement_id)
                contexts.append({
                    "contextual_statement_id": row.contextual_statement_id,
                    "summary": row.summary or (stmt.statement_text[:500] if stmt and stmt.statement_text else ""),
                    "weight": row.relevance_weight,
                })
            return contexts

        if not keywords:
            return []

        match_cases = []
        for kw in keywords:
            pattern = f"%{kw}%"
            match_cases.append(
                func.coalesce(func.cast(SASegment.normalized_text.ilike(pattern), Integer), 0)
            )
        relevance = sum(match_cases).label("relevance")

        any_conditions = []
        for kw in keywords:
            pattern = f"%{kw}%"
            any_conditions.append(SASegment.normalized_text.ilike(pattern))

        q = (
            select(SASegment, relevance)
            .where(or_(*any_conditions))
            .where(SASegment.normalized_text.isnot(None))
            .where(SASegment.normalized_text != "")
            .order_by(relevance.desc())
            .limit(15)
        )
        rows = (await session.execute(q)).all()

        contexts = []
        for seg, score in rows:
            text = seg.normalized_text or seg.original_text or ""
            excerpt = text[:600]
            contexts.append({
                "contextual_statement_id": seg.id,
                "summary": excerpt,
                "weight": float(score or 1),
            })

        return contexts

    def _build_evidence_prompt(self, query: str, sources: list[dict], contexts: list[dict]) -> str:
        parts = [f"User question: {query}\n"]

        if sources:
            parts.append("== Source Records ==")
            for i, s in enumerate(sources):
                culture = f" ({s['culture']})" if s.get("culture") else ""
                parts.append(f"[Source {i}] {s['title']}{culture}")
                if s.get("excerpt"):
                    parts.append(f"  Content: {s['excerpt'][:600]}")
                parts.append(f"  Category: {s.get('source_type', 'unknown')}")
                parts.append(f"  Relevance weight: {s.get('weight', 0)}")
                parts.append("")

        if contexts:
            parts.append("== Text Segments / Evidence ==")
            for i, c in enumerate(contexts):
                parts.append(f"[Text {i}] {c['summary']}")
                parts.append("")

        if not sources and not contexts:
            parts.append("(No relevant evidence found in the database for this query.)")

        return "\n".join(parts)

    async def _call_deepseek(self, prompt: str) -> dict:
        """Call DeepSeek API (OpenAI-compatible) for structured chat answers."""
        url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": settings.deepseek_model,
            "messages": [
                {"role": "system", "content": CHAT_SYSTEM_PROMPT_JSON},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        }
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        raw = data["choices"][0]["message"]["content"]
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"No JSON found in DeepSeek response: {raw[:300]}")

    async def _call_anthropic(self, prompt: str) -> dict:
        """Call Anthropic Claude with tool_use for structured answers (fallback)."""
        try:
            response = await self.anthropic_client.messages.create(
                model=settings.anthropic_model,
                max_tokens=4096,
                system=CHAT_SYSTEM_PROMPT,
                tools=[ANSWER_TOOL],
                tool_choice={"type": "tool", "name": "provide_answer"},
                messages=[{"role": "user", "content": prompt}],
            )
            for block in response.content:
                if block.type == "tool_use" and block.name == "provide_answer":
                    return block.input
        except Exception:
            logger.exception("Anthropic chat answer failed")
        return {
            "answer": "I encountered an error processing your question. Please try again.",
            "confidence": 0.0,
            "answer_mode": "unsupported",
        }

    async def _call_llm_and_create_packet(
        self,
        session: AsyncSession,
        query: str,
        chapter_id: uuid.UUID | None,
        sources: list[dict],
        contexts: list[dict],
    ) -> AnswerPacket:
        prompt = self._build_evidence_prompt(query, sources, contexts)

        answer_data = None

        # Priority: DeepSeek > Anthropic > error
        if self._use_deepseek:
            try:
                answer_data = await self._call_deepseek(prompt)
                logger.info("DeepSeek answered query: %s", query[:80])
            except Exception:
                logger.exception("DeepSeek chat failed, trying fallback")
                answer_data = None

        if answer_data is None and settings.anthropic_api_key:
            try:
                answer_data = await self._call_anthropic(prompt)
                logger.info("Anthropic fallback answered query: %s", query[:80])
            except Exception:
                logger.exception("Anthropic fallback also failed")
                answer_data = None

        if answer_data is None:
            answer_data = {
                "answer": "I encountered an error processing your question. Please try again.",
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
            answer_summary="No relevant evidence was found for this query. Try rephrasing with specific names, places, cultures, or time periods.",
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
