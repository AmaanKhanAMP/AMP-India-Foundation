"""Pinecone vector store + retrieval for AMP knowledge (official SDK)."""

from __future__ import annotations

import hashlib
import re
import time
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from pinecone import Pinecone, ServerlessSpec

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.embedding_service import get_embeddings
from app.services.types import Document

logger = get_logger(__name__)

# Short-lived retrieval cache (avoids re-embedding identical queries)
_RETRIEVAL_CACHE: Dict[str, Tuple[float, Tuple[List[Document], str, Dict[str, float]]]] = {}
_RETRIEVAL_CACHE_TTL_SECONDS = 180
_RETRIEVAL_CACHE_MAX = 128

_INDEX_READY = False
_INDEX_HANDLE = None


@lru_cache
def get_pinecone_client() -> Pinecone:
    settings = get_settings()
    if not settings.pinecone_configured:
        raise RuntimeError("Pinecone is not configured.")
    return Pinecone(api_key=settings.pinecone_api_key)


def _index_dimension(pc: Pinecone, name: str) -> Optional[int]:
    try:
        desc = pc.describe_index(name)
        return getattr(desc, "dimension", None)
    except Exception:
        return None


def _wait_until_index_gone(pc: Pinecone, name: str, timeout: float = 90.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        names = {idx["name"] for idx in pc.list_indexes()}
        if name not in names:
            return
        time.sleep(2)


def _wait_until_index_ready(pc: Pinecone, name: str, timeout: float = 120.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            desc = pc.describe_index(name)
            status = getattr(desc, "status", None)
            ready = getattr(status, "ready", None) if status is not None else None
            if ready is True:
                return
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception:
            pass
        time.sleep(2)


def _ensure_index() -> None:
    """Create Pinecone index, or recreate if embedding dimension changed."""
    global _INDEX_READY
    settings = get_settings()
    pc = get_pinecone_client()
    names = {idx["name"] for idx in pc.list_indexes()}
    dimension = settings.gemini_embedding_dimension
    name = settings.pinecone_index_name

    if name in names:
        current_dim = _index_dimension(pc, name)
        if current_dim == dimension:
            _INDEX_READY = True
            return
        logger.warning(
            "pinecone_dimension_mismatch",
            index=name,
            current=current_dim,
            expected=dimension,
        )
        logger.info("recreating_pinecone_index", name=name, dimension=dimension)
        pc.delete_index(name)
        _wait_until_index_gone(pc, name)

    logger.info("creating_pinecone_index", name=name, dimension=dimension)
    pc.create_index(
        name=name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=settings.pinecone_cloud,
            region=settings.pinecone_region,
        ),
    )
    _wait_until_index_ready(pc, name)
    _INDEX_READY = True


def get_index():
    """Return a cached Index handle (avoids list/describe on every query)."""
    global _INDEX_HANDLE, _INDEX_READY
    settings = get_settings()
    if _INDEX_HANDLE is not None and _INDEX_READY:
        return _INDEX_HANDLE
    _ensure_index()
    _INDEX_HANDLE = get_pinecone_client().Index(settings.pinecone_index_name)
    return _INDEX_HANDLE


def _normalize_source_filter(source_filter: Optional[Any]) -> Optional[List[str]]:
    if not source_filter:
        return None
    if isinstance(source_filter, str):
        return [source_filter]
    if isinstance(source_filter, (list, tuple, set)):
        values = [str(v) for v in source_filter if v]
        return values or None
    return [str(source_filter)]


def _pinecone_metadata_filter(
    sources: Optional[List[str]] = None,
    section: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Build Pinecone metadata filter for source and/or section."""
    clauses: List[Dict[str, Any]] = []
    if sources:
        if len(sources) == 1:
            clauses.append({"source": {"$eq": sources[0]}})
        else:
            clauses.append({"source": {"$in": list(sources)}})
    if section:
        clauses.append({"section": {"$eq": section}})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _pinecone_source_filter(sources: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    return _pinecone_metadata_filter(sources=sources)


def _cache_key(
    query: str,
    top_k: int,
    source_filter: Optional[Any],
    section_filter: Optional[str] = None,
) -> str:
    settings = get_settings()
    sources = _normalize_source_filter(source_filter) or []
    filt = ",".join(sorted(sources))
    sec = (section_filter or "").strip()
    raw = f"{settings.pinecone_namespace}|{top_k}|{filt}|{sec}|{query.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _is_relevant(docs: List[Document], settings) -> bool:
    """Reject weak / off-topic retrieval so LLM never sees garbage context."""
    if not docs:
        return False
    best_score = max(float((d.metadata or {}).get("score") or 0.0) for d in docs)
    best_rerank = max(float((d.metadata or {}).get("rerank_score") or 0.0) for d in docs)
    # Require at least one solid vector match OR a strong rerank signal
    if best_score >= settings.rag_score_threshold:
        return True
    if best_rerank >= max(0.22, settings.rag_score_threshold * 0.85):
        return True
    return False


def _get_cached(key: str):
    item = _RETRIEVAL_CACHE.get(key)
    if not item:
        return None
    expires_at, payload = item
    if time.time() > expires_at:
        _RETRIEVAL_CACHE.pop(key, None)
        return None
    return payload


def _set_cached(key: str, payload) -> None:
    if len(_RETRIEVAL_CACHE) >= _RETRIEVAL_CACHE_MAX:
        for old_key in list(_RETRIEVAL_CACHE.keys())[:32]:
            _RETRIEVAL_CACHE.pop(old_key, None)
    _RETRIEVAL_CACHE[key] = (time.time() + _RETRIEVAL_CACHE_TTL_SECONDS, payload)


def clear_retrieval_cache() -> None:
    """Drop in-memory Pinecone retrieval cache (useful after ingest / bugfixes)."""
    _RETRIEVAL_CACHE.clear()


def _normalize_chunk(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _dedupe_docs(docs: List[Document]) -> List[Document]:
    seen = set()
    unique: List[Document] = []
    for doc in docs:
        key = _normalize_chunk(doc.page_content)[:240]
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(doc)
    return unique


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", (text or "").lower()))


def _query_topic_flags(query: str) -> Dict[str, bool]:
    q = (query or "").lower()
    return {
        "events": bool(
            re.search(
                r"\b(event|events|upcoming|past events|job\s*fair|career\s*fair|"
                r"employment\s*drive|medical\s*camp|workshop|naukri\s*mela|featured)\b",
                q,
            )
        ),
        "upcoming": bool(
            re.search(
                r"\b(upcoming|future|next|coming|happening|this month|this year|scheduled)\b",
                q,
            )
        ),
        "past": bool(
            re.search(
                r"\b(past|previous|old|last|happened|completed|earlier|20\d{2})\b",
                q,
            )
        ),
        "featured": bool(re.search(r"\b(featured|spotlight|highlighted)\b", q)),
        "employment": bool(
            re.search(
                r"\b(job|jobs|employment|placement|hiring|recruitment|naukri|rozgar|"
                r"resume|interview)\b",
                q,
            )
        ),
        "volunteer": bool(re.search(r"\b(volunteer|volunteering|स्वयंसेवक)\b", q)),
        "scholarship": bool(re.search(r"\b(scholarship|scholarships|student funding)\b", q)),
        "donation": bool(re.search(r"\b(donat(?:e|ion)|contribute|support us|ifsc|bank)\b", q)),
        "healthcare": bool(re.search(r"\b(medical|healthcare|health\s*camp|hospital)\b", q)),
        "education": bool(
            re.search(r"\b(education|padhai|vocational training|bpl youth)\b", q)
            and not re.search(r"\b(job\s*fair|event|events)\b", q)
        ),
        "empowerment": bool(re.search(r"\b(economic\s+empowerment|livelihood|empowerment)\b", q)),
        "contact": bool(
            re.search(
                r"\b(contact|phone|email|mail|address|location|office|"
                r"timing|timings|hours|helpline|telephone|mobile)\b",
                q,
            )
        ),
    }


def _rerank(
    query: str,
    docs: List[Document],
    top_k: int,
    *,
    section_filter: Optional[str] = None,
    preferred_sources: Optional[List[str]] = None,
    intent: Optional[str] = None,
) -> List[Document]:
    """Lightweight lexical + vector-score + keyword/source/section boosting."""
    q_tokens = _token_set(query)
    flags = _query_topic_flags(query)
    intent_l = (intent or "").lower()
    preferred = [str(s).lower() for s in (preferred_sources or [])]
    has_cms_pref = any(s.startswith("cms_") for s in preferred)
    contact_intent = intent_l == "contact" or (
        flags["contact"]
        and not (
            flags["events"]
            or flags["volunteer"]
            or flags["scholarship"]
            or flags["donation"]
            or flags["healthcare"]
            or flags["employment"]
        )
    )
    donation_intent = intent_l == "donations" or flags["donation"]
    medical_intent = intent_l == "medical" or (
        flags["healthcare"] and not flags["events"] and "camp" not in (query or "").lower()
    )
    education_intent = intent_l == "education" or flags.get("education")
    empowerment_intent = intent_l == "economic_empowerment" or flags.get("empowerment")
    employment_intent = intent_l == "employment" or (
        flags.get("employment") and not flags.get("events")
    )
    event_intent = intent_l in {
        "events",
        "upcoming_events",
        "past_events",
        "featured_event",
    } or (
        flags["events"]
        and not education_intent
        and not empowerment_intent
        and intent_l != "employment"
    ) or (
        flags["employment"] and bool(re.search(r"\b(fair|drive|camp|upcoming)\b", query.lower()))
        and not education_intent
        and not empowerment_intent
        and intent_l != "employment"
    )
    want_upcoming = section_filter == "upcoming_events" or (
        flags["upcoming"] and not flags["past"] and not flags["featured"]
    )
    want_past = section_filter == "past_events" or (flags["past"] and not flags["upcoming"])
    want_featured = section_filter == "featured_event" or flags["featured"]

    event_sources = {
        "events",
        "cms_events",
        "backend_events",
        "cms_gallery",
        "employment",
    }
    volunteer_sources = {"volunteer", "backend_volunteer", "faq"}
    scholarship_sources = {"scholarships", "backend_scholarships", "faq", "programs"}
    contact_sources = {"contact", "backend_contact", "faq", "cms_footer"}
    donation_sources = {"donations", "backend_donations"}

    scored: List[Tuple[float, Document]] = []
    for doc in docs:
        vector_score = float((doc.metadata or {}).get("score") or 0.0)
        d_tokens = _token_set(doc.page_content)
        overlap = len(q_tokens & d_tokens) / max(len(q_tokens), 1)
        source = str((doc.metadata or {}).get("source", "")).lower()
        section = str((doc.metadata or {}).get("section", "")).lower()
        text_l = (doc.page_content or "").lower()
        source_boost = 0.05 if any(t in source for t in q_tokens) else 0.0

        # Prefer earlier sources in the SourcePlan order
        if preferred and source in preferred:
            rank = preferred.index(source)
            source_boost += max(0.0, 0.20 - (rank * 0.015))

        # CMS should beat FAQ for domain questions
        if has_cms_pref and source.startswith("cms_"):
            source_boost += 0.16
        if has_cms_pref and source == "faq":
            source_boost -= 0.22
        if preferred and source == "faq" and any(
            s in preferred for s in donation_sources | event_sources | {"programs", "projects", "employment"}
        ):
            source_boost -= 0.12

        # Section-aware event ranking (production requirement)
        if want_upcoming:
            if section == "upcoming_events" or "upcoming event" in text_l or "home event" in text_l:
                source_boost += 0.30
            if section == "past_events" or "past event" in text_l:
                source_boost -= 0.20
            if section == "featured_event":
                source_boost -= 0.05
        elif want_past:
            if section == "past_events" or "past event" in text_l:
                source_boost += 0.30
            if section == "upcoming_events" or "upcoming event" in text_l:
                source_boost -= 0.20
            if section == "featured_event":
                source_boost -= 0.10
        elif want_featured:
            if section == "featured_event" or "featured event" in text_l:
                source_boost += 0.30
            if section in {"past_events", "upcoming_events"}:
                source_boost -= 0.20

        if event_intent:
            if source in event_sources or "event" in source:
                source_boost += 0.18
            if any(
                k in text_l
                for k in (
                    "upcoming event",
                    "featured event",
                    "job fair",
                    "medical camp",
                    "workshop",
                    "career guidance",
                    "employment drive",
                )
            ):
                source_boost += 0.10
            if source in contact_sources or any(
                k in text_l for k in ("working hours", "9:00 am", "office timing", "kitne baje")
            ):
                source_boost -= 0.32

        if flags["volunteer"] and source in volunteer_sources:
            source_boost += 0.18
        if flags["scholarship"] and source in scholarship_sources:
            source_boost += 0.16

        if donation_intent:
            if source in donation_sources:
                source_boost += 0.22
            if source in contact_sources and "support us" not in text_l and "donat" not in text_l:
                source_boost -= 0.35
            if any(k in text_l for k in ("8291101312", "office timing", "kitne baje")) and "donat" not in text_l:
                source_boost -= 0.25

        if medical_intent:
            if source in {"programs", "projects", "scholarships", "website_projects", "cms_projects"} or "medical" in text_l or "health" in text_l:
                source_boost += 0.18
            if "crowdfund" in text_l or ("donat" in text_l and "medical camp" not in text_l):
                source_boost -= 0.30
            if source in contact_sources and "medical" not in text_l:
                source_boost -= 0.20
            if source in event_sources or "job fair" in text_l:
                source_boost -= 0.28

        if education_intent:
            if "/projects/education" in text_l or "education —" in text_l or "education project" in text_l:
                source_boost += 0.32
            if any(k in text_l for k in ("vocational", "bpl", "scholarships for deserving", "centres of excellence")):
                source_boost += 0.16
            if source in {"website_projects", "cms_projects", "website_about"}:
                source_boost += 0.18
            if source in event_sources or any(
                k in text_l for k in ("job fair", "mega job", "upcoming event", "past event")
            ):
                source_boost -= 0.45

        if empowerment_intent:
            if "economic empowerment" in text_l or "/projects/empowerment" in text_l or "livelihood" in text_l:
                source_boost += 0.32
            if source in {"website_projects", "cms_projects", "website_about"}:
                source_boost += 0.18
            if source in event_sources or "job fair" in text_l:
                source_boost -= 0.45

        if employment_intent:
            if any(
                k in text_l
                for k in (
                    "employment assistance",
                    "career guidance",
                    "placement",
                    "resume",
                    "/projects/employment",
                    "employability training",
                )
            ) or source in {"website_projects", "cms_projects", "website_home"}:
                source_boost += 0.28
            wants_fair = bool(re.search(r"\b(job\s*fair|naukri\s*mela|fair)\b", query.lower()))
            if source in event_sources and not wants_fair:
                source_boost -= 0.38
            if wants_fair and ("job fair" in text_l or source in event_sources):
                source_boost += 0.16
            if source in contact_sources and "employment" not in text_l:
                source_boost -= 0.22

        if flags["healthcare"] and any(k in text_l for k in ("medical", "health", "camp")):
            source_boost += 0.12

        if contact_intent and source in contact_sources:
            source_boost += 0.18 if source in {"contact", "backend_contact", "cms_footer"} else 0.06
            if any(
                t in text_l
                for t in ("8291101312", "contact@ampindiafoundation.org", "nagpada", "halima")
            ):
                source_boost += 0.12

        # Non-contact intents: penalize pure contact blobs
        if not contact_intent and source in contact_sources:
            if not any(
                k in text_l
                for k in ("donat", "volunteer", "scholarship", "event", "medical", "employment")
            ):
                source_boost -= 0.20

        length_penalty = min(len(doc.page_content) / 4000.0, 0.15)
        final = (vector_score * 0.68) + (overlap * 0.22) + source_boost - length_penalty
        scored.append((final, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    reranked: List[Document] = []
    for final, doc in scored[:top_k]:
        meta = dict(doc.metadata or {})
        meta["rerank_score"] = round(final, 4)
        meta["final_score"] = round(final, 4)
        reranked.append(Document(page_content=doc.page_content, metadata=meta))
    return reranked


def _filter_docs_by_section(docs: List[Document], section: Optional[str]) -> List[Document]:
    """Hard post-filter so upcoming never mixes with past/featured."""
    if not section:
        return docs
    matched = [
        d
        for d in docs
        if str((d.metadata or {}).get("section") or "").lower() == section.lower()
    ]
    if matched:
        return matched
    # Soft fallback: heading text when older vectors lack section metadata
    heading_map = {
        "upcoming_events": ("upcoming event", "home event"),
        "featured_event": ("featured event",),
        "past_events": ("past event",),
    }
    needles = heading_map.get(section.lower(), ())
    soft = [
        d
        for d in docs
        if any(n in (d.page_content or "").lower() for n in needles)
    ]
    return soft if soft else []


class RagService:
    """Retrieve top-k AMP knowledge chunks from Pinecone."""

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        source_filter: Optional[Any] = None,
        original_query: Optional[str] = None,
        section_filter: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Tuple[List[Document], str, Dict[str, float]]:
        """
        Retrieve, dedupe, and rerank chunks.

        Pipeline: fetch Top 15 → dedupe → rerank → keep best Top 5.

        `query` should be the rewritten English search query used for embeddings.
        `original_query` (optional) improves lexical rerank with user tokens.
        `section_filter` (optional) restricts to metadata.section (upcoming/past/featured).
        `intent` (optional) improves topic-aware reranking.

        Returns (docs, context_block, timings_ms).
        """
        settings = get_settings()
        keep_n = max(3, min(int(top_k or 5), 5))
        k = keep_n
        timings: Dict[str, float] = {
            "embed_ms": 0.0,
            "pinecone_ms": 0.0,
            "rerank_ms": 0.0,
            "retrieve_ms": 0.0,
            "cache_hit": 0.0,
        }
        t_all = time.perf_counter()

        if not settings.rag_ready:
            logger.warning("rag_not_ready")
            return [], "", timings

        sources = _normalize_source_filter(source_filter)
        section = (section_filter or "").strip() or None
        key = _cache_key(query, k, sources, section)
        cached = _get_cached(key)
        if cached is not None:
            docs, context, cached_timings = cached
            timings = {**cached_timings, "cache_hit": 1.0}
            timings["retrieve_ms"] = (time.perf_counter() - t_all) * 1000
            return docs, context, timings

        fetch_k = 15
        rerank_query = f"{query} {original_query or ''}".strip()
        try:
            embeddings = get_embeddings()
            t0 = time.perf_counter()
            vector = await embeddings.aembed_query(query)
            timings["embed_ms"] = (time.perf_counter() - t0) * 1000
            timings["embedding_dim"] = float(len(vector) if vector else 0)

            index = get_index()
            query_kwargs: Dict[str, Any] = {
                "vector": vector,
                "top_k": fetch_k,
                "include_metadata": True,
                "namespace": settings.pinecone_namespace,
            }
            pine_filter = _pinecone_metadata_filter(sources=sources, section=section)
            if pine_filter:
                query_kwargs["filter"] = pine_filter

            t1 = time.perf_counter()
            result = index.query(**query_kwargs)
            timings["pinecone_ms"] = (time.perf_counter() - t1) * 1000

            matches = getattr(result, "matches", None) or result.get("matches", [])

            # If section+source filter returns nothing (pre-v2 vectors), retry source-only
            # then hard-filter by section/heading client-side.
            if section and not matches and sources:
                t1 = time.perf_counter()
                result = index.query(
                    vector=vector,
                    top_k=fetch_k,
                    include_metadata=True,
                    namespace=settings.pinecone_namespace,
                    filter=_pinecone_metadata_filter(sources=sources),
                )
                timings["pinecone_ms"] += (time.perf_counter() - t1) * 1000
                matches = getattr(result, "matches", None) or result.get("matches", [])

            # Contact intent only — avoid duplicate Pinecone calls for other topics
            contact_primary = (intent or "").lower() == "contact" or (
                bool(sources)
                and sources[0] in {"contact", "cms_footer", "backend_contact"}
                and "contact" in sources
            )
            if contact_primary and sources and "contact" in sources:
                t1 = time.perf_counter()
                contact_only = index.query(
                    vector=vector,
                    top_k=8,
                    include_metadata=True,
                    namespace=settings.pinecone_namespace,
                    filter={"source": {"$eq": "contact"}},
                )
                timings["pinecone_ms"] += (time.perf_counter() - t1) * 1000
                extra = getattr(contact_only, "matches", None) or contact_only.get("matches", [])
                seen_ids = set()
                merged = []
                for m in list(extra) + list(matches):
                    mid = getattr(m, "id", None) or (m.get("id") if isinstance(m, dict) else None)
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)
                    merged.append(m)
                matches = merged
            elif sources and not matches:
                expanded = list(dict.fromkeys([*sources, "about_aif", "programs"]))
                t1 = time.perf_counter()
                result = index.query(
                    vector=vector,
                    top_k=fetch_k,
                    include_metadata=True,
                    namespace=settings.pinecone_namespace,
                    filter=_pinecone_metadata_filter(sources=expanded),
                )
                timings["pinecone_ms"] += (time.perf_counter() - t1) * 1000
                matches = getattr(result, "matches", None) or result.get("matches", [])
        except Exception as exc:
            logger.error(
                "pinecone_retrieve_failed",
                error=str(type(exc).__name__),
                detail=str(exc)[:200],
            )
            timings["retrieve_ms"] = (time.perf_counter() - t_all) * 1000
            return [], "", timings

        docs: List[Document] = []
        for match in matches:
            score = getattr(match, "score", None)
            if score is None and isinstance(match, dict):
                score = match.get("score", 0)
            metadata = getattr(match, "metadata", None) or {}
            if isinstance(match, dict):
                metadata = match.get("metadata") or {}

            content = (metadata.get("text") or metadata.get("page_content") or "").strip()
            if not content:
                continue
            if isinstance(score, (int, float)) and score < settings.rag_score_threshold:
                continue

            meta = {
                mk: mv
                for mk, mv in metadata.items()
                if mk not in {"text", "page_content"}
            }
            meta["score"] = float(score or 0.0)
            meta["id"] = getattr(match, "id", None) or (match.get("id") if isinstance(match, dict) else None)
            docs.append(Document(page_content=content, metadata=meta))

        t2 = time.perf_counter()
        docs = _dedupe_docs(docs)
        ranked = _rerank(
            rerank_query,
            docs,
            top_k=15,
            section_filter=section,
            preferred_sources=sources,
            intent=intent,
        )
        # Hard section gate — never mix upcoming/past/featured
        if section:
            ranked = _filter_docs_by_section(ranked, section)
            docs_pre = _filter_docs_by_section(docs, section)
            if docs_pre:
                ranked = _rerank(
                    rerank_query,
                    docs_pre,
                    top_k=15,
                    section_filter=section,
                    preferred_sources=sources,
                    intent=intent,
                )
                ranked = _filter_docs_by_section(ranked, section)

        min_rerank = max(0.18, settings.rag_score_threshold * 0.55)
        strong = [
            d
            for d in ranked
            if float((d.metadata or {}).get("rerank_score") or 0.0) >= min_rerank
            or float((d.metadata or {}).get("score") or 0.0) >= settings.rag_score_threshold
        ]
        docs = (strong or ranked)[:keep_n]
        timings["rerank_ms"] = (time.perf_counter() - t2) * 1000
        logger.info(
            "rag_top_candidates",
            query=(query or "")[:200],
            section_filter=section,
            intent=intent,
            intent_section=section,
            candidates=[
                {
                    "source": (d.metadata or {}).get("source"),
                    "section": (d.metadata or {}).get("section"),
                    "score": (d.metadata or {}).get("score"),
                    "rerank": (d.metadata or {}).get("rerank_score"),
                    "final_score": (d.metadata or {}).get("final_score"),
                    "chunk": (d.metadata or {}).get("chunk"),
                    "preview": (d.page_content or "")[:250],
                }
                for d in ranked[:15]
            ],
            selected=[
                {
                    "source": (d.metadata or {}).get("source"),
                    "section": (d.metadata or {}).get("section"),
                    "score": (d.metadata or {}).get("score"),
                    "rerank": (d.metadata or {}).get("rerank_score"),
                    "final_score": (d.metadata or {}).get("final_score"),
                    "preview": (d.page_content or "")[:120],
                }
                for d in docs
            ],
            discarded=[
                {
                    "source": (d.metadata or {}).get("source"),
                    "section": (d.metadata or {}).get("section"),
                    "score": (d.metadata or {}).get("score"),
                    "rerank": (d.metadata or {}).get("rerank_score"),
                }
                for d in ranked[keep_n:15]
            ],
            selected_count=len(docs),
        )

        blocks = [
            f"[source: {(d.metadata or {}).get('source', 'knowledge')} | "
            f"section: {(d.metadata or {}).get('section', '-')} | "
            f"score: {(d.metadata or {}).get('score', 0):.3f}]\n{d.page_content}"
            for d in docs
        ]
        context = "\n\n---\n\n".join(blocks)
        timings["retrieve_ms"] = (time.perf_counter() - t_all) * 1000
        _set_cached(key, (docs, context, timings))
        return docs, context, timings

    async def retrieve_validated(
        self,
        query: str,
        top_k: Optional[int] = None,
        source_filter: Optional[Any] = None,
        original_query: Optional[str] = None,
        section_filter: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Tuple[List[Document], str, Dict[str, float], bool]:
        """Retrieve and return relevance flag — False means do not call the LLM with context."""
        settings = get_settings()
        docs, context, timings = await self.retrieve(
            query,
            top_k=top_k,
            source_filter=source_filter,
            original_query=original_query,
            section_filter=section_filter,
            intent=intent,
        )
        relevant = _is_relevant(docs, settings)
        if not relevant:
            return [], "", timings, False
        return docs, context, timings, True

    def upsert_documents(self, documents: List[Document], ids: Optional[List[str]] = None) -> int:
        if not documents:
            return 0

        settings = get_settings()
        embeddings = get_embeddings()
        texts = [d.page_content for d in documents]
        vectors = embeddings.embed_documents(texts)
        index = get_index()

        payload = []
        for i, doc in enumerate(documents):
            vid = ids[i] if ids and i < len(ids) else str(uuid4())
            meta = {
                **(doc.metadata or {}),
                "text": doc.page_content,
            }
            clean_meta = {
                str(k): (v if isinstance(v, (str, int, float, bool)) else str(v))
                for k, v in meta.items()
                if v is not None
            }
            payload.append({"id": vid, "values": vectors[i], "metadata": clean_meta})

        batch = 50
        for start in range(0, len(payload), batch):
            index.upsert(
                vectors=payload[start : start + batch],
                namespace=settings.pinecone_namespace,
            )
        return len(documents)

    def delete_by_source(self, source: str) -> int:
        settings = get_settings()
        if not settings.pinecone_configured:
            return 0
        try:
            index = get_index()
            index.delete(
                filter={"source": {"$eq": source}},
                namespace=settings.pinecone_namespace,
            )
            return 1
        except Exception as exc:
            logger.warning("delete_by_source_failed", source=source, error=str(type(exc).__name__))
            return 0

    def index_stats(self) -> Dict[str, Any]:
        settings = get_settings()
        if not settings.pinecone_configured:
            return {"configured": False}
        try:
            index = get_index()
            stats = index.describe_index_stats()
            return {
                "configured": True,
                "index": settings.pinecone_index_name,
                "namespace": settings.pinecone_namespace,
                "dimension": settings.gemini_embedding_dimension,
                "stats": stats,
            }
        except Exception as exc:
            return {"configured": True, "error": "unavailable", "detail": str(type(exc).__name__)}


rag_service = RagService()
