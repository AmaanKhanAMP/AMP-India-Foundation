"""AMP India Foundation chat orchestrator — mandatory Pinecone RAG for domain queries."""

from __future__ import annotations

import asyncio
import re
import time
from contextvars import ContextVar
from typing import AsyncIterator, Dict, List, Optional

from google.genai import types

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.conversation_service import reply_for
from app.services.gemini_client import get_gemini_client
from app.services.intent_router import Intent, RAG_INTENTS, route_intent
from app.services.language_service import Language, detect_language, resolve_session_language
from app.services.memory_service import memory_service
from app.services.prompt_service import (
    CLARIFY_RESPONSE,
    DOMAIN_ONLY_RESPONSE,
    FORM_CLARIFY_RESPONSE,
    GIBBERISH_RESPONSE,
    IDENTITY_RESPONSE,
    INJECTION_RESPONSE,
    LINK_CLARIFY_RESPONSE,
    MODEL_IDENTITY_RESPONSE,
    UNAVAILABLE_RESPONSE,
    build_rag_messages,
    t,
)
from app.services.query_rewrite import RewrittenQuery, rewrite_query
from app.services.local_fallback import lookup_local
from app.services.emergency_knowledge import final_apology, lookup_emergency
from app.services.builtin_answers import (
    DYNAMIC_INTENTS,
    answer_builtin,
    should_use_builtin_first,
)
from app.services.response_composer import compose_final, compose_from_documents
from app.services.rag_service import rag_service
from app.services.response_formatter import format_user_response, looks_like_prompt_leak
from app.services.fallback_generator import generate_from_documents, generate_from_local
from app.services.security_service import sanitize_message
from app.services.source_planner import plan_sources
from app.services.query_normalize import NormalizedQuery, looks_gibberish, normalize_query
from app.services.focus_entity import extract_focus
from app.services.answer_cache import get_cached_answer, set_cached_answer, cache_stats
from app.services.analytics_service import (
    confidence_for_source,
    record_chat,
    record_exception,
    record_retrieval,
    snapshot as analytics_snapshot,
)

logger = get_logger(__name__)

_CHAT_AUDIT: ContextVar[dict] = ContextVar("chat_audit", default={})

_CONVERSATIONAL_INTENTS = {
    Intent.GREETING,
    Intent.SMALL_TALK,
    Intent.GOODBYE,
    Intent.CASUAL_CHAT,
    Intent.ASSISTANT_IDENTITY,
}

_DOMAIN_RAG_INTENTS = set(RAG_INTENTS)


def _is_quota_error(exc: BaseException) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    if any(
        s in text
        for s in (
            "429",
            "resource_exhausted",
            "quota",
            "rate_limit",
            "rate limit",
            "ratelimit",
        )
    ):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code == 429


def _is_transient_llm_error(exc: BaseException) -> bool:
    """429/503/timeouts/connection — recover with Pinecone-grounded fallback."""
    if _is_quota_error(exc):
        return True
    text = f"{type(exc).__name__} {exc}".lower()
    if any(
        s in text
        for s in (
            "503",
            "500",
            "502",
            "504",
            "unavailable",
            "high demand",
            "404",
            "not_found",
            "no longer available",
            "not found",
            "timeout",
            "timed out",
            "deadline_exceeded",
            "deadline exceeded",
            "connection",
            "connecterror",
            "retryerror",
            "ratelimit",
            "temporarily",
        )
    ):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code in {500, 502, 503, 504, 404, 408}


def _to_gemini_contents(messages: List[dict]) -> tuple[str, list]:
    system_parts: List[str] = []
    contents: list = []
    for msg in messages:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if role == "system":
            system_parts.append(content)
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content)],
            )
        )
    if contents and contents[-1].role != "user":
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text="Please continue.")])
        )
    return "\n\n".join(system_parts).strip(), contents


def _reply_language(detected: Language, message: str) -> Language:
    lower = (message or "").lower()
    if detected != Language.ENGLISH:
        return detected
    if re.search(
        r"\b(hi|hello|hey|how are you|thank|thanks|good\s*(morning|night|evening|afternoon)|bye|goodbye)\b",
        lower,
    ):
        return Language.ENGLISH
    return detected


def _resolve_canned(token: str, language: Language) -> str:
    if token.startswith("__CONV__:"):
        key = token.split(":", 1)[-1]
        return reply_for(key, language)
    if token == "__IDENTITY__":
        return t(IDENTITY_RESPONSE, language)
    if token == "__MODEL__":
        return t(MODEL_IDENTITY_RESPONSE, language)
    if token.startswith("__SMALL__:"):
        key = token.split(":", 1)[-1]
        if key == "help":
            return reply_for("hello", language)
        return reply_for("aur_batao", language)
    if token in {"__GREETING__", "__THANKS__", "__GOODBYE__"}:
        mapping = {
            "__GREETING__": "hello",
            "__THANKS__": "thanks",
            "__GOODBYE__": "goodbye",
        }
        return reply_for(mapping[token], language)
    return token if not token.startswith("__") else reply_for("hello", language)


def _docs_confidence(docs) -> float:
    best = 0.0
    for doc in docs or []:
        meta = doc.metadata or {}
        for key in ("final_score", "rerank_score", "score"):
            try:
                best = max(best, float(meta.get(key) or 0.0))
            except (TypeError, ValueError):
                continue
    return best


def _confidence_style(answer: str, score: float, language: Language) -> tuple[str, str]:
    """High: answer. Medium: clarify. Low: ask a follow-up instead of guessing."""
    text = (answer or "").strip()
    if score >= 0.28:
        return text, "high"
    if score >= 0.18:
        if language == Language.HINDI:
            prefix = "अगर मैंने सही समझा, तो "
        elif language == Language.HINGLISH:
            prefix = "Agar maine sahi samjha, to "
        else:
            prefix = "If I understood you correctly, "
        return prefix + text[:1].lower() + text[1:] if text else text, "medium"
    follow = t(CLARIFY_RESPONSE, language)
    if language == Language.HINDI:
        follow = (
            "मुझे पूरा भरोसा नहीं कि मैं सही विषय पर हूँ। "
            "क्या आप इवेंट, परियोजना, स्वयंसेवा, दान या संपर्क जानकारी पूछ रहे हैं?"
        )
    elif language == Language.HINGLISH:
        follow = (
            "Mujhe poora confidence nahi ki main sahi topic par hoon. "
            "Kya aap events, projects, volunteering, donations ya contact pooch rahe hain?"
        )
    else:
        follow = (
            "I want to make sure I point you to the right AMP India Foundation information. "
            "Are you asking about an event, a project, volunteering, donations, or contact details?"
        )
    return follow, "low"


def _looks_unclear(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return True
    if len(re.sub(r"\W+", "", text, flags=re.UNICODE)) <= 1:
        return True
    return False


class AiService:
    """
    Production pipeline:

    Language → Intent → (canned conversational/security)
      → Query rewrite → Embed → Pinecone → Relevance check
      → LLM grounded on retrieved context → Answer

    FAQ is ONLY a post-RAG quota fallback — never a Pinecone bypass.
    General knowledge is NEVER answered.
    """

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        page: Optional[str] = None,
    ) -> Dict:
        logger.info("chat_request_received", question=(message or "")[:200], page=page or "")
        try:
            return await self._chat_pipeline(message, session_id, page)
        except Exception as exc:
            logger.error(
                "chat_pipeline_crash",
                error=type(exc).__name__,
                detail=str(exc)[:240],
                question=(message or "")[:200],
            )
            record_exception("pipeline")
            return self._recover_from_failure(message, session_id, page, exc)

    async def _chat_pipeline(
        self,
        message: str,
        session_id: Optional[str] = None,
        page: Optional[str] = None,
    ) -> Dict:
        t_total = time.perf_counter()
        timings: Dict[str, float] = {
            "classify_ms": 0.0,
            "rewrite_ms": 0.0,
            "retrieve_ms": 0.0,
            "embed_ms": 0.0,
            "pinecone_ms": 0.0,
            "gemini_ms": 0.0,
            "total_ms": 0.0,
        }
        settings = get_settings()
        clean = sanitize_message(message)
        try:
            nq = normalize_query(clean)
        except Exception as exc:
            record_exception("normalize")
            logger.error("normalize_failed", error=type(exc).__name__)
            nq = NormalizedQuery(
                original=clean, normalized=clean, routing_text=clean, fixes_applied=[], fuzzy_used=False
            )
        routing_message = nq.routing_text or nq.normalized or clean
        sid = memory_service.ensure_session(session_id)
        session_topic = memory_service.get_topic(sid)
        session_entity = memory_service.get_entity(sid)
        session_lang = memory_service.get_language(sid)
        _CHAT_AUDIT.set(
            {
                "user_query": (clean or "")[:240],
                "active_context": session_topic or "",
            }
        )

        try:
            detected = detect_language(clean, session_language=session_lang)
            language = resolve_session_language(detected, clean, session_lang)
            memory_service.set_language(sid, language.value)
        except Exception as exc:
            record_exception("language")
            logger.error("language_failed", error=type(exc).__name__)
            language = Language.ENGLISH

        try:
            route = route_intent(
                routing_message,
                has_session_topic=bool(session_topic),
                session_topic=session_topic,
            )
            if looks_gibberish(clean) or looks_gibberish(nq.original):
                from app.services.intent_router import RouteResult

                route = RouteResult(
                    Intent.GIBBERISH,
                    0.99,
                    "gibberish",
                    canned_response=t(GIBBERISH_RESPONSE, language),
                )
            elif route.intent in {Intent.UNKNOWN, Intent.CLARIFICATION_NEEDED} and routing_message != clean:
                alt = route_intent(
                    clean,
                    has_session_topic=bool(session_topic),
                    session_topic=session_topic,
                )
                if alt.intent not in {Intent.UNKNOWN, Intent.CLARIFICATION_NEEDED}:
                    route = alt
        except Exception as exc:
            record_exception("intent")
            logger.error("intent_failed", error=type(exc).__name__)
            from app.services.intent_router import RouteResult

            route = RouteResult(Intent.AMP_KNOWLEDGE, 0.4, "intent_error_fallback")
        timings["classify_ms"] = getattr(route, "classify_ms", 0.0)

        rag_used = False
        gemini_used = False
        http_status = 200
        cache_hit = False

        # 0) Answer cache for static domain (skip for conversational/security)
        if route.intent in _DOMAIN_RAG_INTENTS and should_use_builtin_first(route.intent, routing_message):
            cached = get_cached_answer(
                language=language.value,
                normalized_question=nq.normalized,
                intent=route.intent.value,
            )
            if cached and (cached.get("response") or "").strip():
                cache_hit = True
                text = cached["response"]
                conf = float(cached.get("confidence") or 1.0)
                timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                memory_service.add_turn(sid, clean, text)
                memory_service.set_topic(sid, route.intent.value)
                record_chat(
                    intent=route.intent.value,
                    response_source="CACHE",
                    fallback_level="cache",
                    question=clean,
                    latency_ms=timings["total_ms"],
                    cache_hit=True,
                    builtin_used=True,
                )
                self._log(route.intent.value, conf, language.value, False, False, False, timings, 200)
                return self._ok(
                    text,
                    sid,
                    route.intent.value,
                    conf,
                    "answer_cache",
                    language=language.value,
                    meta={
                        "timings": timings,
                        "page": page,
                        "pipeline": "cache",
                        "rag_used": False,
                        "gemini_used": False,
                        "cache_hit": True,
                        "confidence": conf,
                        "response_source": "CACHE",
                        "answer_source": "CACHE",
                        "query_fixes": nq.fixes_applied[:8],
                    },
                )

        if (route.reason or "") == "gibberish" or route.intent == Intent.GIBBERISH:
            text = route.canned_response or t(GIBBERISH_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                "gibberish",
                0.2,
                "gibberish",
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "gibberish",
                    "rag_used": False,
                    "why_intent_selected": "gibberish",
                    "fallback_reason": "none",
                    "response_source": "GIBBERISH",
                },
            )

        # 1) Conversational
        if route.intent in _CONVERSATIONAL_INTENTS:
            turn_detected = detect_language(clean, session_language=None)
            reply_lang = _reply_language(turn_detected, clean)
            if "salam" in (route.reason or "") or re.search(r"ass?ala+m|salaam", clean, re.I):
                reply_lang = Language.HINGLISH
            text = (
                _resolve_canned(route.canned_response, reply_lang)
                if route.canned_response
                else reply_for("hello", reply_lang)
            )
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            self._log(route.intent.value, route.confidence, reply_lang.value, False, False, False, timings, 200)
            return self._ok(
                text,
                sid,
                route.intent.value,
                route.confidence,
                route.reason,
                language=reply_lang.value,
                meta={
                    "timings": timings,
                    "page": page,
                    "fast_path": True,
                    "rag_used": False,
                    "gemini_used": False,
                    "language": reply_lang.value,
                    "conversational": True,
                    "pipeline": "conversational",
                    "response_source": "CANNED",
                },
            )

        # 2) Injection
        if route.intent == Intent.INJECTION:
            text = route.canned_response or t(INJECTION_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            self._log("injection", route.confidence, language.value, False, False, False, timings, 200)
            return self._ok(
                text,
                sid,
                "injection",
                route.confidence,
                "security_request",
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "security",
                    "rag_used": False,
                    "response_source": "SECURITY",
                },
            )

        # 3) Unsafe / explicit out of scope
        if route.intent == Intent.OUT_OF_SCOPE:
            text = route.canned_response or t(DOMAIN_ONLY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            self._log("out_of_scope", route.confidence, language.value, False, False, False, timings, 200)
            return self._ok(
                text,
                sid,
                "out_of_scope",
                route.confidence,
                route.reason,
                language=language.value,
                meta={"timings": timings, "pipeline": "domain_refuse", "rag_used": False},
            )

        # 4) Strict domain — NEVER answer general knowledge with Gemini
        if route.intent == Intent.GENERAL_KNOWLEDGE:
            text = t(DOMAIN_ONLY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            self._log(
                "general_knowledge",
                route.confidence,
                language.value,
                False,
                False,
                False,
                timings,
                200,
            )
            return self._ok(
                text,
                sid,
                "out_of_scope",
                route.confidence,
                "domain_refuse_general",
                language=language.value,
                meta={
                    "timings": timings,
                    "page": page,
                    "pipeline": "domain_refuse",
                    "rag_used": False,
                    "gemini_used": False,
                    "language": language.value,
                },
            )

        if route.intent == Intent.FORM_CLARIFY:
            text = route.canned_response or t(FORM_CLARIFY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                "form_clarify",
                route.confidence,
                "form_clarify",
                language=language.value,
                meta={"timings": timings, "pipeline": "form_clarify", "rag_used": False},
            )

        if route.intent == Intent.LINK_CLARIFY:
            text = route.canned_response or t(LINK_CLARIFY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                "link_clarify",
                route.confidence,
                "link_clarify",
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "link_clarify",
                    "rag_used": False,
                    "why_intent_selected": route.reason,
                    "response_source": "LINK_CLARIFY",
                },
            )

        if route.intent == Intent.LOCATION_STATEMENT:
            text = route.canned_response or t(CLARIFY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                "location_statement",
                route.confidence,
                route.reason,
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "location_statement",
                    "rag_used": False,
                    "why_intent_selected": route.reason,
                    "response_source": "LOCATION_STATEMENT",
                },
            )

        if route.canned_response:
            token = route.canned_response
            text = (
                _resolve_canned(token, language)
                if str(token).startswith("__")
                else token
            )
            memory_service.add_turn(sid, clean, text)
            if route.intent in _DOMAIN_RAG_INTENTS:
                memory_service.set_topic(sid, route.intent.value)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                route.intent.value,
                route.confidence,
                route.reason or "canned",
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "canned",
                    "rag_used": False,
                    "why_intent_selected": route.reason,
                    "response_source": "CANNED",
                },
            )

        # 5) Unclear
        if _looks_unclear(clean):
            text = t(CLARIFY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                "clarify",
                0.5,
                "unclear",
                language=language.value,
                meta={"timings": timings, "pipeline": "clarify", "rag_used": False},
            )

        # 6) Domain RAG — never treat UNKNOWN as a Contact/Pinecone dump
        use_rag = bool(route.uses_rag)
        if not use_rag:
            text = t(DOMAIN_ONLY_RESPONSE, language)
            memory_service.add_turn(sid, clean, text)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                route.intent.value,
                route.confidence,
                "non_rag_refuse",
                language=language.value,
                meta={"timings": timings, "pipeline": "domain_refuse", "rag_used": False},
            )

        # 6b) Built-in verified answers for static topics — skip Pinecone
        if (
            route.intent in _DOMAIN_RAG_INTENTS
            and should_use_builtin_first(route.intent, clean)
        ):
            builtin = answer_builtin(clean, intent=route.intent, language=language)
            if builtin:
                text = compose_final(
                    question=clean,
                    draft=builtin,
                    intent=route.intent,
                    language=language,
                )
                conf = confidence_for_source("BUILTIN_KNOWLEDGE")
                set_cached_answer(
                    language=language.value,
                    normalized_question=nq.normalized,
                    intent=route.intent.value,
                    response=text,
                    confidence=conf,
                    response_source="BUILTIN_KNOWLEDGE",
                )
                memory_service.add_turn(sid, clean, text)
                memory_service.set_topic(sid, route.intent.value)
                focus = extract_focus(clean, session_entity)
                if focus:
                    memory_service.set_entity(sid, focus)
                timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                record_chat(
                    intent=route.intent.value,
                    response_source="BUILTIN_KNOWLEDGE",
                    fallback_level="builtin",
                    question=clean,
                    latency_ms=timings["total_ms"],
                    builtin_used=True,
                )
                self._log(
                    route.intent.value,
                    route.confidence,
                    language.value,
                    False,
                    False,
                    False,
                    timings,
                    200,
                )
                return self._ok(
                    text,
                    sid,
                    route.intent.value,
                    max(route.confidence, conf),
                    "builtin_static",
                    language=language.value,
                    meta={
                        "timings": timings,
                        "page": page,
                        "pipeline": "builtin_knowledge",
                        "rag_used": False,
                        "gemini_used": False,
                        "fallback_level": "builtin",
                        "response_source": "BUILTIN_KNOWLEDGE",
                        "answer_source": "BUILTIN_KNOWLEDGE",
                        "confidence": conf,
                        "query_fixes": nq.fixes_applied[:8],
                        "cache_hit": False,
                    },
                )

        if not settings.rag_ready:
            # Emergency knowledge when Pinecone/Gemini not configured
            emergency = lookup_emergency(
                clean,
                intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                language=language,
            )
            text = emergency or final_apology(language)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            return self._ok(
                text,
                sid,
                route.intent.value if route.intent in _DOMAIN_RAG_INTENTS else "config",
                0.7 if emergency else 0.0,
                "emergency_rag_not_ready" if emergency else "rag_not_ready",
                language=language.value,
                meta={
                    "timings": timings,
                    "pipeline": "emergency",
                    "rag_used": False,
                    "fallback_level": "emergency" if emergency else "apology",
                    "response_source": "EMERGENCY_KNOWLEDGE" if emergency else "FINAL_APOLOGY",
                },
            )

        try:
            rag_used = True
            t_rw = time.perf_counter()
            try:
                rewritten = rewrite_query(
                    clean,
                    language=language,
                    intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else Intent.AMP_KNOWLEDGE,
                    session_topic=session_topic,
                    last_entity=session_entity or extract_focus(clean),
                )
            except Exception as exc:
                record_exception("rewrite")
                logger.error("rewrite_failed", error=type(exc).__name__)
                rewritten = RewrittenQuery(clean, clean, language.value, route.intent.value, clean, [])
            timings["rewrite_ms"] = (time.perf_counter() - t_rw) * 1000
            focus = extract_focus(clean, session_entity)
            if focus:
                memory_service.set_entity(sid, focus)

            source_filter = None if route.intent == Intent.UNKNOWN else route.source_filter
            section_filter = getattr(route, "section_filter", None)
            if route.intent in _DOMAIN_RAG_INTENTS and not source_filter:
                plan = plan_sources(route.intent)
                source_filter = plan.sources
                section_filter = section_filter or plan.section

            try:
                docs, context, retrieve_timings, relevant = await rag_service.retrieve_validated(
                    rewritten.search_query,
                    top_k=5,
                    source_filter=source_filter,
                    original_query=clean,
                    section_filter=section_filter,
                    intent=route.intent.value if route.intent != Intent.UNKNOWN else None,
                )
            except Exception as exc:
                record_exception("pinecone")
                logger.error("retrieve_failed", error=type(exc).__name__)
                docs, context, relevant = [], "", False
                retrieve_timings = {"retrieve_ms": 0.0, "embed_ms": 0.0, "pinecone_ms": 0.0}
            record_retrieval(
                hit=bool(relevant and docs),
                pinecone_ms=float(retrieve_timings.get("pinecone_ms") or 0.0),
            )
            timings["retrieve_ms"] = retrieve_timings.get("retrieve_ms", 0.0)
            timings["embed_ms"] = retrieve_timings.get("embed_ms", 0.0)
            timings["pinecone_ms"] = retrieve_timings.get("pinecone_ms", 0.0)

            self._pipeline_debug(
                {
                    "original_query": clean[:200],
                    "detected_language": language.value,
                    "detected_intent": route.intent.value,
                    "section_filter": section_filter,
                    "rewritten_query": rewritten.search_query[:240],
                    "embedding_model": settings.gemini_embedding_model,
                    "namespace": settings.pinecone_namespace,
                    "top_k": settings.rag_top_k,
                    "filters": source_filter,
                    "relevant": relevant,
                    "chunk_count": len(docs),
                    "chunks": [
                        {
                            "source": (d.metadata or {}).get("source"),
                            "section": (d.metadata or {}).get("section"),
                            "score": (d.metadata or {}).get("score"),
                            "rerank": (d.metadata or {}).get("rerank_score"),
                            "final_score": (d.metadata or {}).get("final_score"),
                            "preview": (d.page_content or "")[:160],
                        }
                        for d in docs[:10]
                    ],
                    "embed_ms": round(timings["embed_ms"], 1),
                    "pinecone_ms": round(timings["pinecone_ms"], 1),
                }
            )

            # Pinecone miss → CMS/builtin facts → cache/local → emergency → apology
            if not relevant or not context.strip() or not docs:
                builtin_fb = answer_builtin(
                    clean,
                    intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                    language=language,
                )
                if builtin_fb:
                    text = compose_final(
                        question=clean,
                        draft=builtin_fb,
                        intent=route.intent,
                        language=language,
                    )
                    timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                    memory_service.add_turn(sid, clean, text)
                    return self._ok(
                        text,
                        sid,
                        route.intent.value,
                        0.85,
                        "cms_facts_after_pinecone_miss",
                        language=language.value,
                        meta={
                            "timings": timings,
                            "pipeline": "cms_after_pinecone_miss",
                            "rag_used": True,
                            "fallback_level": "cms_facts",
                            "response_source": "CMS_CONTACT_FACTS"
                            if route.intent == Intent.CONTACT
                            else "BUILTIN_KNOWLEDGE",
                        },
                    )
                local = lookup_local(
                    clean,
                    intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                    language=language,
                )
                if local:
                    fb = generate_from_local(local.text, language=language)
                    text = fb.text or local.text
                    memory_service.add_turn(sid, clean, text)
                    topic = route.intent.value if route.intent in _DOMAIN_RAG_INTENTS else "amp_knowledge"
                    memory_service.set_topic(sid, topic)
                    timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                    self._request_audit(
                        question=clean,
                        language=language.value,
                        intent=route.intent.value,
                        rewritten=rewritten.search_query,
                        pinecone_ok=True,
                        docs=docs,
                        gemini_called=False,
                        gemini_ok=False,
                        gemini_ms=0.0,
                        fallback_used=True,
                        fallback_type="local_knowledge",
                        response_source="LOCAL_KNOWLEDGE",
                        total_ms=timings["total_ms"],
                    )
                    self._log(topic, route.confidence, language.value, False, True, False, timings, 200)
                    return self._ok(
                        text,
                        sid,
                        topic,
                        0.75,
                        "local_after_pinecone_miss",
                        language=language.value,
                        meta={
                            "timings": timings,
                            "page": page,
                            "rag_used": True,
                            "gemini_used": False,
                            "fallback": local.source,
                            "fallback_level": "markdown_local",
                            "pipeline": "local_after_pinecone_miss",
                            "search_query": rewritten.search_query,
                            "language": language.value,
                            "answer_source": "LOCAL_KNOWLEDGE",
                            "response_source": "LOCAL_KNOWLEDGE",
                        },
                    )

                emergency = lookup_emergency(
                    clean,
                    intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                    language=language,
                )
                if emergency:
                    memory_service.add_turn(sid, clean, emergency)
                    topic = route.intent.value if route.intent in _DOMAIN_RAG_INTENTS else "amp_knowledge"
                    memory_service.set_topic(sid, topic)
                    timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                    self._log(topic, 0.7, language.value, False, True, False, timings, 200)
                    return self._ok(
                        emergency,
                        sid,
                        topic,
                        0.7,
                        "emergency_after_pinecone_miss",
                        language=language.value,
                        meta={
                            "timings": timings,
                            "page": page,
                            "rag_used": True,
                            "gemini_used": False,
                            "fallback_level": "emergency",
                            "pipeline": "emergency_after_pinecone_miss",
                            "answer_source": "EMERGENCY_KNOWLEDGE",
                            "response_source": "EMERGENCY_KNOWLEDGE",
                        },
                    )

                if route.intent == Intent.UNKNOWN:
                    text = t(DOMAIN_ONLY_RESPONSE, language)
                    reason = "unknown_no_amp_context"
                    out_intent = "out_of_scope"
                else:
                    text = final_apology(language)
                    reason = "no_relevant_context"
                    out_intent = route.intent.value
                memory_service.add_turn(sid, clean, text)
                timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                self._log(out_intent, route.confidence, language.value, False, True, False, timings, 200)
                return self._ok(
                    text,
                    sid,
                    out_intent,
                    0.4,
                    reason,
                    language=language.value,
                    meta={
                        "timings": timings,
                        "page": page,
                        "rag_used": True,
                        "gemini_used": False,
                        "language": language.value,
                        "pipeline": "rag_no_hit",
                        "fallback_level": "apology",
                        "search_query": rewritten.search_query,
                        "chunks": 0,
                        "answer_source": "NO_RESULT",
                        "response_source": "FINAL_APOLOGY" if route.intent != Intent.UNKNOWN else "DOMAIN_ONLY",
                    },
                )

            t0 = time.perf_counter()
            # Gemini ONLY for dynamic CMS/events or ambiguous unknown — save API cost
            allow_gemini = route.intent in DYNAMIC_INTENTS or route.intent == Intent.UNKNOWN
            try:
                if not allow_gemini:
                    raise RuntimeError("skip_gemini_static_intent")
                answer, prompt_preview = await self._generate_rag_answer(
                    clean, context, sid, language, return_prompt=True
                )
                gemini_used = True
                self._pipeline_debug(
                    {
                        "llm_used": True,
                        "llm_status": "ok",
                        "prompt_length": len(prompt_preview or ""),
                        "raw_preview": (answer or "")[:300],
                    }
                )
            except Exception as exc:
                if str(exc) == "skip_gemini_static_intent" or _is_transient_llm_error(exc) or not allow_gemini:
                    http_status = 200 if str(exc) == "skip_gemini_static_intent" else (
                        429 if _is_quota_error(exc) else 503
                    )
                    fb = generate_from_documents(
                        docs, question=clean, language=language, intent=route.intent
                    )
                    text = (fb.text or "").strip()
                    if text:
                        text = compose_final(
                            question=clean,
                            draft=text,
                            intent=route.intent,
                            language=language,
                            docs=docs,
                        )
                        response_source = "PINECONE_ONLY"
                        fallback_type = (
                            "composer_no_gemini"
                            if str(exc) == "skip_gemini_static_intent"
                            else "pinecone_after_gemini_error"
                        )
                        fallback_level = "cms_pinecone"
                    else:
                        local = lookup_local(
                            clean,
                            intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                            language=language,
                        )
                        if local:
                            text = generate_from_local(local.text, language=language).text or local.text
                            response_source = "LOCAL_KNOWLEDGE"
                            fallback_type = "local_after_empty_pinecone_format"
                            fallback_level = "markdown_local"
                        else:
                            emergency = lookup_emergency(
                                clean,
                                intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                                language=language,
                            )
                            if emergency:
                                text = emergency
                                response_source = "EMERGENCY_KNOWLEDGE"
                                fallback_type = "emergency_after_gemini_error"
                                fallback_level = "emergency"
                            else:
                                text = final_apology(language)
                                response_source = "FINAL_APOLOGY"
                                fallback_type = "apology"
                                fallback_level = "apology"

                    memory_service.add_turn(sid, clean, text)
                    timings["gemini_ms"] = (time.perf_counter() - t0) * 1000
                    timings["total_ms"] = (time.perf_counter() - t_total) * 1000
                    self._request_audit(
                        question=clean,
                        language=language.value,
                        intent=route.intent.value,
                        rewritten=rewritten.search_query,
                        pinecone_ok=True,
                        docs=docs,
                        gemini_called=allow_gemini and str(exc) != "skip_gemini_static_intent",
                        gemini_ok=False,
                        gemini_ms=timings["gemini_ms"],
                        fallback_used=True,
                        fallback_type=fallback_type,
                        response_source=response_source,
                        total_ms=timings["total_ms"],
                        gemini_error="" if str(exc) == "skip_gemini_static_intent" else str(type(exc).__name__),
                    )
                    self._log(
                        route.intent.value,
                        route.confidence,
                        language.value,
                        False,
                        True,
                        False,
                        timings,
                        http_status,
                    )
                    return self._ok(
                        text,
                        sid,
                        route.intent.value,
                        route.confidence,
                        "pinecone_grounded_after_llm_error",
                        language=language.value,
                        meta={
                            "timings": timings,
                            "rag_used": True,
                            "gemini_used": False,
                            "pipeline": "pinecone_grounded_llm_error",
                            "http_status": http_status,
                            "search_query": rewritten.search_query,
                            "chunks": len(docs),
                            "answer_source": response_source,
                            "response_source": response_source,
                            "fallback_type": fallback_type,
                            "fallback_level": fallback_level,
                        },
                    )
                raise

            timings["gemini_ms"] = (time.perf_counter() - t0) * 1000
            answer = self._validate_output(answer, language, fallback=None)
            response_source = "PINECONE+GEMINI"
            fallback_type = "none"
            if not (answer or "").strip():
                fb = generate_from_documents(
                    docs, question=clean, language=language, intent=route.intent
                )
                if fb.text:
                    answer = fb.text
                    response_source = "PINECONE_ONLY"
                    fallback_type = "pinecone_after_empty_gemini"
                else:
                    emergency = lookup_emergency(
                        clean,
                        intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                        language=language,
                    )
                    answer = emergency or final_apology(language)
                    response_source = "EMERGENCY_KNOWLEDGE" if emergency else "FINAL_APOLOGY"
                    fallback_type = "emergency_after_empty_gemini"

            answer = compose_final(
                question=clean,
                draft=answer,
                intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                language=language,
                docs=docs,
            )
            ret_conf = _docs_confidence(docs)
            answer, conf_band = _confidence_style(answer, ret_conf, language)
            memory_service.add_turn(sid, clean, answer)
            topic = route.intent.value if route.intent in _DOMAIN_RAG_INTENTS else "amp_knowledge"
            memory_service.set_topic(sid, topic)
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            chunk_meta = [
                {
                    "source": (d.metadata or {}).get("source"),
                    "score": (d.metadata or {}).get("score"),
                    "rerank": (d.metadata or {}).get("rerank_score"),
                }
                for d in docs
            ]
            self._request_audit(
                question=clean,
                language=language.value,
                intent=topic,
                rewritten=rewritten.search_query,
                pinecone_ok=True,
                docs=docs,
                gemini_called=True,
                gemini_ok=response_source == "PINECONE+GEMINI",
                gemini_ms=timings["gemini_ms"],
                fallback_used=fallback_type != "none",
                fallback_type=fallback_type,
                response_source=response_source,
                total_ms=timings["total_ms"],
            )
            self._log(
                topic,
                route.confidence,
                language.value,
                False,
                True,
                response_source == "PINECONE+GEMINI",
                timings,
                200,
            )
            return self._ok(
                answer,
                sid,
                topic,
                route.confidence,
                route.reason or "rag",
                language=language.value,
                meta={
                    "chunks": len(docs),
                    "page": page,
                    "source_filter": source_filter,
                    "search_query": rewritten.search_query,
                    "normalized_query": rewritten.normalized,
                    "synonyms": rewritten.synonyms,
                    "chunk_scores": chunk_meta,
                    "retrieved_sources": [c.get("source") for c in chunk_meta],
                    "pinecone_scores": chunk_meta,
                    "timings": timings,
                    "rag_used": True,
                    "gemini_used": response_source == "PINECONE+GEMINI",
                    "language": language.value,
                    "pipeline": "rag",
                    "relevance_ok": True,
                    "answer_source": response_source,
                    "response_source": response_source,
                    "confidence_band": conf_band,
                    "retrieval_confidence": round(ret_conf, 4),
                },
            )
        except Exception as exc:
            logger.error(
                "chat_failed",
                error=str(type(exc).__name__),
                detail=str(exc)[:240],
                quota=_is_quota_error(exc),
            )
            record_exception("rag")
            http_status = 429 if _is_quota_error(exc) else (503 if _is_transient_llm_error(exc) else 500)
            # Prefer verified local / emergency knowledge over a quota-busy banner
            local = lookup_local(
                clean,
                intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                language=language,
            )
            if local:
                text = generate_from_local(local.text, language=language).text or local.text
                response_source = "LOCAL_KNOWLEDGE"
            else:
                emergency = lookup_emergency(
                    clean,
                    intent=route.intent if route.intent in _DOMAIN_RAG_INTENTS else None,
                    language=language,
                )
                if emergency:
                    text = emergency
                    response_source = "EMERGENCY_KNOWLEDGE"
                else:
                    text = t(UNAVAILABLE_RESPONSE, language)
                    response_source = "FINAL_APOLOGY"
            timings["total_ms"] = (time.perf_counter() - t_total) * 1000
            self._log(
                route.intent.value,
                route.confidence,
                language.value,
                False,
                rag_used,
                gemini_used,
                timings,
                http_status,
            )
            return self._ok(
                text,
                sid,
                route.intent.value,
                route.confidence,
                "handled_error",
                language=language.value,
                meta={
                    "timings": timings,
                    "rag_used": rag_used,
                    "gemini_used": gemini_used,
                    "language": language.value,
                    "http_status": http_status,
                    "pipeline": "error",
                    "response_source": response_source,
                },
            )

    async def stream_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        page: Optional[str] = None,
    ) -> AsyncIterator[str]:
        result = await self.chat(message, session_id, page)
        text = result.get("response") or t(UNAVAILABLE_RESPONSE, Language.ENGLISH)
        step = 80
        for i in range(0, len(text), step):
            yield text[i : i + step]
            await asyncio.sleep(0)

    async def _generate_rag_answer(
        self,
        question: str,
        context: str,
        session_id: str,
        language: Language,
        return_prompt: bool = False,
    ):
        settings = get_settings()
        history = memory_service.history_as_chat(session_id, limit=6)
        messages = build_rag_messages(
            context,
            question,
            history,
            language=language.value,
        )
        system_instruction, contents = _to_gemini_contents(messages)
        client = get_gemini_client()
        response = client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction or None,
                temperature=settings.gemini_rag_temperature,
                max_output_tokens=settings.gemini_rag_max_output_tokens,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if return_prompt:
            preview = (
                f"SYSTEM:\n{(system_instruction or '')[:400]}\n\n"
                f"USER:\n{messages[-1]['content'][:800]}"
            )
            return text, preview
        return text

    def _pipeline_debug(self, payload: Dict) -> None:
        """Detailed RAG traces in development / debug mode only."""
        settings = get_settings()
        if not (settings.debug or (settings.app_env or "").lower() in {"development", "dev", "local"}):
            return
        logger.info("rag_pipeline_debug", **{k: v for k, v in payload.items() if v is not None})

    def _request_audit(
        self,
        *,
        question: str,
        language: str,
        intent: str,
        rewritten: str,
        pinecone_ok: bool,
        docs: list,
        gemini_called: bool,
        gemini_ok: bool,
        gemini_ms: float,
        fallback_used: bool,
        fallback_type: str,
        response_source: str,
        total_ms: float,
        gemini_error: str = "",
    ) -> None:
        """Always-on structured audit of answer provenance (no secrets)."""
        logger.info(
            "chat_answer_audit",
            question=(question or "")[:200],
            detected_language=language,
            intent=intent,
            rewritten_query=(rewritten or "")[:240],
            embedding_generated="Yes",
            pinecone_search_success="Yes" if pinecone_ok else "No",
            retrieved_documents=len(docs or []),
            similarity_scores=[
                {
                    "source": (d.metadata or {}).get("source"),
                    "score": (d.metadata or {}).get("score"),
                    "rerank": (d.metadata or {}).get("rerank_score"),
                }
                for d in (docs or [])[:8]
            ],
            gemini_called="Yes" if gemini_called else "No",
            gemini_success="Yes" if gemini_ok else "No",
            gemini_latency_ms=round(gemini_ms or 0.0, 1),
            gemini_error=gemini_error or None,
            fallback_used="Yes" if fallback_used else "No",
            fallback_type=fallback_type,
            final_response_source=response_source,
            response_time_ms=round(total_ms or 0.0, 1),
        )

    def _validate_output(
        self,
        text: str,
        language: Language,
        fallback: Optional[str] = None,
    ) -> str:
        if not (text or "").strip():
            return ""
        if looks_like_prompt_leak(text or ""):
            # Strip leaks; if nothing usable remains, signal empty to caller
            cleaned = format_user_response(text, language=language, fallback="<<<EMPTY>>>")
            return "" if cleaned == "<<<EMPTY>>>" or looks_like_prompt_leak(cleaned) else cleaned
        cleaned = format_user_response(text, language=language, fallback="<<<EMPTY>>>")
        if cleaned == "<<<EMPTY>>>" or len(cleaned) < 8:
            return ""
        if cleaned.rstrip().endswith(("Man", "Halima", "Room", "Floor,")):
            return ""
        return cleaned

    def _log(
        self,
        intent: str,
        confidence: float,
        language: str,
        cache_hit: bool,
        rag_used: bool,
        gemini_used: bool,
        timings: Dict[str, float],
        http_status: int,
    ) -> None:
        logger.info(
            "chat_request",
            intent=intent,
            confidence=round(confidence, 3),
            language=language,
            cache_hit="Yes" if cache_hit else "No",
            rag_used="Yes" if rag_used else "No",
            gemini_used="Yes" if gemini_used else "No",
            pinecone_ms=round(timings.get("pinecone_ms", 0), 1),
            gemini_ms=round(timings.get("gemini_ms", 0), 1),
            total_ms=round(timings.get("total_ms", 0), 1),
            http_status=http_status,
            quota_error="Yes" if http_status == 429 else "No",
        )

    def _recover_from_failure(
        self,
        message: str,
        session_id: Optional[str],
        page: Optional[str],
        exc: Exception,
    ) -> Dict:
        """Pinecone/CMS/API crash: builtin → local cache → emergency → last-resort message."""
        from app.services.builtin_answers import answer_builtin
        from app.services.contact_facts import answer_contact
        from app.services.emergency_knowledge import lookup_emergency
        from app.services.local_fallback import lookup_local

        sid = memory_service.ensure_session(session_id)
        clean = sanitize_message(message or "")
        try:
            language = detect_language(clean)
        except Exception:
            language = Language.ENGLISH
        try:
            route = route_intent(clean)
        except Exception:
            from app.services.intent_router import RouteResult

            route = RouteResult(Intent.AMP_KNOWLEDGE, 0.3, "recovery_intent")
        text = ""
        source = "ALL_SOURCES_FAILED"
        if route.intent in _DOMAIN_RAG_INTENTS or route.intent == Intent.CONTACT:
            builtin = answer_builtin(clean, intent=route.intent, language=language)
            if builtin:
                text, source = builtin, "BUILTIN_KNOWLEDGE"
        if not text and route.intent == Intent.CONTACT:
            text, source = answer_contact(clean), "CMS_CONTACT_FACTS"
        if not text:
            local = lookup_local(clean, intent=route.intent, language=language)
            if local:
                text, source = local.text, "LOCAL_KNOWLEDGE"
        if not text:
            emergency = lookup_emergency(clean, intent=route.intent, language=language)
            if emergency:
                text, source = emergency, "EMERGENCY_KNOWLEDGE"
        if not text:
            text = t(UNAVAILABLE_RESPONSE, language)
            source = "ALL_SOURCES_FAILED"
        logger.info(
            "chat_recovery",
            intent=route.intent.value,
            error=type(exc).__name__,
            recovered_source=source,
            question=clean[:200],
        )
        return self._ok(
            text,
            sid,
            route.intent.value,
            0.7 if source != "ALL_SOURCES_FAILED" else 0.0,
            f"recovered_after_{type(exc).__name__}",
            language=language.value,
            meta={
                "page": page,
                "pipeline": "recovery",
                "response_source": source,
                "error_reason": type(exc).__name__,
            },
        )

    def _ok(
        self,
        response: str,
        session_id: str,
        intent: str,
        confidence: float,
        reason: str,
        language: str = "en",
        meta: Optional[Dict] = None,
    ) -> Dict:
        safe = format_user_response(response, language=language)
        audit = dict(_CHAT_AUDIT.get() or {})
        meta_out = {"reason": reason, "language": language, **audit, **(meta or {})}
        src = str(meta_out.get("response_source") or meta_out.get("answer_source") or "")
        chunk_scores = meta_out.get("chunk_scores") or meta_out.get("pinecone_scores") or []
        retrieved = meta_out.get("retrieved_sources")
        if retrieved is None and isinstance(chunk_scores, list):
            retrieved = [c.get("source") for c in chunk_scores if isinstance(c, dict)]
        logger.info(
            "chat_final",
            user_query=str(meta_out.get("user_query") or "")[:240],
            detected_intent=intent,
            intent=intent,
            confidence_score=round(float(confidence or 0.0), 3),
            confidence=round(float(confidence or 0.0), 3),
            why_intent_selected=reason,
            active_context=str(meta_out.get("active_context") or ""),
            retrieved_sources=retrieved,
            pinecone_scores=chunk_scores,
            fallback_reason=str(meta_out.get("fallback_reason") or meta_out.get("fallback_level") or "none"),
            response_source=src or "unknown",
            response_time=round(float((meta_out.get("timings") or {}).get("total_ms") or 0.0), 1),
            answer_chars=len(safe or ""),
            used_unavailable="unable to retrieve the latest information" in (safe or "").lower(),
        )
        if "confidence" not in meta_out:
            meta_out["confidence"] = confidence_for_source(src) if src else float(confidence or 0.0)
        # Prefer higher of router confidence vs source confidence for static
        conf_out = max(float(confidence or 0.0), float(meta_out.get("confidence") or 0.0))
        if src in {"BUILTIN_KNOWLEDGE", "CACHE"}:
            conf_out = max(conf_out, 0.95)
        meta_out["confidence"] = round(conf_out, 3)
        if "cache_stats" not in meta_out:
            meta_out["cache_stats"] = cache_stats()
        record_chat(
            intent=intent,
            response_source=src or "unknown",
            fallback_level=str(meta_out.get("fallback_level") or ""),
            question=str(meta_out.get("user_query") or ""),
            latency_ms=float((meta_out.get("timings") or {}).get("total_ms") or 0.0),
            gemini_used=bool(meta_out.get("gemini_used")),
            pinecone_used=bool(meta_out.get("rag_used")),
            builtin_used=src in {"BUILTIN_KNOWLEDGE", "CACHE", "CMS_CONTACT_FACTS"},
            cache_hit=src == "CACHE",
            unanswered=src in {"FINAL_APOLOGY", "ALL_SOURCES_FAILED", "NO_RESULT"}
            or "unable to retrieve the latest information" in (safe or "").lower(),
        )
        return {
            "success": True,
            "response": safe,
            "reply": safe,
            "session_id": session_id,
            "intent": intent,
            "category": intent,
            "confidence": conf_out,
            "meta": meta_out,
        }


ai_service = AiService()
