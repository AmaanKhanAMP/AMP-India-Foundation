"""Document ingestion: PDF / DOCX / TXT / MD / JSON → chunks → Pinecone."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.rag_service import clear_retrieval_cache, rag_service
from app.services.answer_cache import clear_answer_cache
from app.services.types import Document

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown", ".json"}

# Do not re-index these knowledge files — they contained dated dummy events / old contact.
SKIP_KNOWLEDGE_STEMS = {
    "events",
    "faq",
    "contact",
    "employment",
    "about_aif",
    "programs",
    "projects",
    "scholarships",
    "donations",
    "volunteer",
}

# Content hash cache to skip unchanged sources during re-ingest (also persisted on disk)
_SOURCE_HASHES: Dict[str, str] = {}
_HASHES_LOADED = False


def _hash_store_path() -> Path:
    settings = get_settings()
    root = Path(settings.documents_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root / ".source_hashes.json"


def _load_hashes() -> None:
    global _HASHES_LOADED
    if _HASHES_LOADED:
        return
    path = _hash_store_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _SOURCE_HASHES.update({str(k): str(v) for k, v in data.items()})
        except Exception:
            pass
    _HASHES_LOADED = True


def _save_hashes() -> None:
    path = _hash_store_path()
    try:
        path.write_text(json.dumps(_SOURCE_HASHES, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("hash_store_write_failed", error=str(type(exc).__name__))


def _splitter() -> RecursiveCharacterTextSplitter:
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        import docx

        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs if p.text)
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return json_to_text(data, source=path.stem)
    raise ValueError(f"Unsupported file type: {suffix}")


def json_to_text(data: Any, source: str = "knowledge") -> str:
    lines: List[str] = [f"Source module: {source}"]

    def walk(node: Any, prefix: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"keywords", "id", "page", "image_url", "banner_image"}:
                    continue
                if isinstance(value, (dict, list)):
                    walk(value, prefix=prefix)
                else:
                    walk(value, prefix=f"{prefix}{key}: ")
        elif isinstance(node, list):
            for item in node:
                walk(item, prefix=prefix)
        elif node is not None and str(node).strip():
            lines.append(f"{prefix}{node}".strip())

    walk(data)
    return "\n".join(lines)


def _chunk_faq_pairs(text: str, source: str, category: str) -> List[Document]:
    """Keep Q/A pairs together for better retrieval precision."""
    import re

    parts = re.split(r"(?=\nQ:\s)", text.strip())
    docs: List[Document] = []
    preamble = []
    idx = 0
    for part in parts:
        block = part.strip()
        if not block:
            continue
        if not block.startswith("Q:"):
            preamble.append(block)
            continue
        # Bundle 2–3 Q&A pairs per chunk for denser embeddings
        docs.append(
            Document(
                page_content=block,
                metadata={
                    "source": source,
                    "category": category,
                    "chunk": idx,
                    "doc_type": "faq",
                },
            )
        )
        idx += 1
    if preamble:
        docs.insert(
            0,
            Document(
                page_content="\n\n".join(preamble),
                metadata={"source": source, "category": category, "chunk": 0, "doc_type": "faq_intro"},
            ),
        )
        # Re-number
        for i, doc in enumerate(docs):
            doc.metadata["chunk"] = i
    # Merge tiny adjacent FAQ chunks (under ~350 chars) in pairs
    merged: List[Document] = []
    i = 0
    while i < len(docs):
        cur = docs[i]
        if (
            i + 1 < len(docs)
            and len(cur.page_content) < 350
            and (cur.metadata or {}).get("doc_type") == "faq"
            and (docs[i + 1].metadata or {}).get("doc_type") == "faq"
        ):
            nxt = docs[i + 1]
            merged.append(
                Document(
                    page_content=f"{cur.page_content}\n\n{nxt.page_content}",
                    metadata={
                        "source": source,
                        "category": category,
                        "chunk": len(merged),
                        "doc_type": "faq",
                    },
                )
            )
            i += 2
        else:
            meta = dict(cur.metadata or {})
            meta["chunk"] = len(merged)
            merged.append(Document(page_content=cur.page_content, metadata=meta))
            i += 1
    return merged


def chunk_text(text: str, source: str, category: str = "document") -> List[Document]:
    # CMS / backend event docs: one vector per event with metadata.section
    if _is_event_source(source) or _looks_like_sectioned_events(text):
        event_docs = _chunk_event_blocks(text, source=source, category=category)
        if event_docs:
            return event_docs

    # FAQ files: prefer Q/A-aware chunking
    if source.lower().startswith("faq") or "\nQ:" in text:
        faq_docs = _chunk_faq_pairs(text, source=source, category=category)
        if faq_docs:
            return faq_docs

    splitter = _splitter()
    chunks = splitter.split_text(text)
    docs: List[Document] = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        docs.append(
            Document(
                page_content=chunk.strip(),
                metadata={
                    "source": source,
                    "category": category,
                    "chunk": i,
                    "doc_type": "section",
                },
            )
        )
    return docs


def _is_event_source(source: str) -> bool:
    s = (source or "").lower()
    return s in {
        "cms_events",
        "cms_gallery",
        "backend_events",
        "events",
    } or "event" in s


def _looks_like_sectioned_events(text: str) -> bool:
    return bool(
        re.search(
            r"(?im)^##\s*(Upcoming event|Featured event|Home event|Past event)\s*:",
            text or "",
        )
    )


def _infer_event_section(heading: str, body: str) -> str:
    blob = f"{heading}\n{body}".lower()
    explicit = re.search(r"(?im)^section:\s*(\w[\w-]*)", body or "")
    if explicit:
        return explicit.group(1).strip().lower()
    if "featured event" in heading.lower() or "featured_event" in blob:
        return "featured_event"
    if "past event" in heading.lower() or "past_events" in blob:
        return "past_events"
    if "upcoming event" in heading.lower() or "home event" in heading.lower():
        return "upcoming_events"
    if "section: upcoming" in blob:
        return "upcoming_events"
    if "section: featured" in blob:
        return "featured_event"
    if "section: past" in blob:
        return "past_events"
    return "upcoming_events"


def _chunk_event_blocks(text: str, source: str, category: str) -> List[Document]:
    """
    Split CMS/backend event documents into ONE vector per event.
    Each chunk carries metadata.section = upcoming_events | featured_event | past_events.
    """
    import re as _re

    raw = (text or "").strip()
    if not raw:
        return []

    # Split on ## event headings while keeping the delimiter
    parts = _re.split(
        r"(?im)(?=^##\s*(?:Upcoming event|Featured event|Home event|Past event)\s*:)",
        raw,
    )
    docs: List[Document] = []
    idx = 0
    for part in parts:
        block = part.strip()
        if not block:
            continue
        heading_m = _re.match(
            r"(?im)^(##\s*(?:Upcoming event|Featured event|Home event|Past event)\s*:[^\n]*)",
            block,
        )
        if not heading_m:
            # Intro/preamble — skip for event-specific retrieval (avoid polluting past/upcoming)
            continue
        heading = heading_m.group(1).strip()
        body = block[len(heading_m.group(0)) :].strip()
        section = _infer_event_section(heading, body)
        # Drop the machine Section: line from visible text (kept in metadata)
        body_clean = _re.sub(r"(?im)^section:\s*\w[\w-]*\s*$", "", body).strip()
        content = f"{heading}\n{body_clean}".strip() if body_clean else heading
        if len(content) < 12:
            continue
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": source,
                    "category": category,
                    "chunk": idx,
                    "doc_type": "event",
                    "section": section,
                    "event_title": _re.sub(
                        r"(?i)^##\s*(?:Upcoming event|Featured event|Home event|Past event)\s*:\s*",
                        "",
                        heading,
                    ).strip()[:120],
                },
            )
        )
        idx += 1
    return docs


def _stable_ids(documents: List[Document], source: str) -> List[str]:
    ids = []
    for doc in documents:
        raw = f"{source}:{doc.metadata.get('chunk')}:{doc.page_content[:80]}"
        ids.append(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32])
    return ids


def _source_name_for_path(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "live" in parts:
        return f"website_live_{path.stem}"
    return path.stem


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def discover_knowledge_files(root: Path) -> List[Path]:
    """Find all supported knowledge files under a directory (non-recursive top + one level)."""
    files: List[Path] = []
    if not root.is_dir():
        return files
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.stem in SKIP_KNOWLEDGE_STEMS and "live" not in {p.lower() for p in path.parts}:
            continue
        files.append(path)
    return files


def ingest_text(
    source: str,
    text: str,
    category: Optional[str] = None,
    *,
    skip_unchanged: bool = True,
) -> Tuple[int, str, str]:
    """
    Incremental ingest of a named source from raw text (CMS / API sync).

    Deletes prior vectors for `source`, then upserts new chunks with stable IDs.
    Returns (chunk_count, source, status) where status is:
      indexed | skipped_duplicate | empty | failed
    """
    _load_hashes()
    source = (source or "").strip()
    if not source:
        return 0, "", "empty"
    body = (text or "").strip()
    if not body:
        # Empty payload means remove this source from the index
        rag_service.delete_by_source(source)
        _SOURCE_HASHES.pop(source, None)
        _save_hashes()
        clear_retrieval_cache()
        clear_answer_cache()
        return 0, source, "empty"

    digest = _content_hash(body)
    if skip_unchanged and _SOURCE_HASHES.get(source) == digest:
        return 0, source, "skipped_duplicate"

    cat = category or source
    rag_service.delete_by_source(source)
    docs = chunk_text(body, source=source, category=cat)
    if not docs:
        return 0, source, "empty"

    ids = _stable_ids(docs, source)
    count = rag_service.upsert_documents(docs, ids=ids)
    _SOURCE_HASHES[source] = digest
    _save_hashes()
    clear_retrieval_cache()
    clear_answer_cache()
    logger.info("indexed_source", source=source, chunks=count)
    return count, source, "indexed"


def ingest_sources_batch(
    sources: List[Dict[str, str]],
    *,
    skip_unchanged: bool = True,
    delete_missing_prefix: Optional[str] = None,
    delete_sources: Optional[List[str]] = None,
    extra_delete_prefixes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Upsert multiple named sources. Optionally delete CMS sources that vanished
    (prefix match against previously hashed sources).
    """
    _load_hashes()
    total = 0
    skipped = 0
    deleted = 0
    seen: List[str] = []
    failures: List[str] = []

    for item in sources:
        source = str(item.get("source") or "").strip()
        text = str(item.get("text") or "")
        category = str(item.get("category") or source)
        if not source:
            continue
        try:
            count, src, status = ingest_text(
                source, text, category=category, skip_unchanged=skip_unchanged
            )
            seen.append(src)
            if status == "indexed":
                total += count
            elif status == "skipped_duplicate":
                skipped += 1
        except Exception as exc:
            failures.append(f"{source}:{type(exc).__name__}")
            logger.error("source_ingest_failed", source=source, error=str(type(exc).__name__))

    extra_delete = [s for s in (delete_sources or []) if s and s not in seen]
    for old_source in extra_delete:
        rag_service.delete_by_source(old_source)
        _SOURCE_HASHES.pop(old_source, None)
        deleted += 1
        logger.info("deleted_legacy_source", source=old_source)

    prefixes = []
    if delete_missing_prefix:
        prefixes.append(delete_missing_prefix)
    for extra_prefix in extra_delete_prefixes or []:
        if extra_prefix:
            prefixes.append(extra_prefix)
    for prefix in prefixes:
        for old_source in list(_SOURCE_HASHES.keys()):
            if old_source.startswith(prefix) and old_source not in seen:
                rag_service.delete_by_source(old_source)
                _SOURCE_HASHES.pop(old_source, None)
                deleted += 1
                logger.info("deleted_stale_source", source=old_source)
    if deleted:
        _save_hashes()
        clear_retrieval_cache()
        clear_answer_cache()

    return {
        "indexed": total,
        "skipped": skipped,
        "deleted": deleted,
        "sources": seen,
        "failures": failures,
        "message": (
            f"Indexed {total} chunks across {len(seen)} sources "
            f"({skipped} unchanged, {deleted} stale deleted, {len(failures)} failures)."
        ),
    }


def ingest_file(
    path: Path,
    category: Optional[str] = None,
    *,
    skip_unchanged: bool = True,
) -> Tuple[int, str, str]:
    """
    Ingest one file.

    Returns (chunk_count, source, status) where status is:
      indexed | skipped_duplicate | empty | failed
    """
    _load_hashes()
    text = extract_text_from_file(path)
    if not text.strip():
        return 0, path.stem, "empty"

    source = _source_name_for_path(path)
    digest = _content_hash(text)
    if skip_unchanged and _SOURCE_HASHES.get(source) == digest:
        return 0, source, "skipped_duplicate"

    cat = category or source
    rag_service.delete_by_source(source)
    docs = chunk_text(text, source=source, category=cat)
    if not docs:
        return 0, source, "empty"

    ids = _stable_ids(docs, source)
    count = rag_service.upsert_documents(docs, ids=ids)
    _SOURCE_HASHES[source] = digest
    _save_hashes()
    clear_retrieval_cache()
    clear_answer_cache()
    return count, source, "indexed"


def ingest_knowledge_dir(knowledge_dir: Optional[Path] = None) -> Dict[str, Any]:
    settings = get_settings()
    root = Path(knowledge_dir or settings.knowledge_dir)
    if not root.is_dir():
        return {
            "indexed": 0,
            "files": 0,
            "sources": [],
            "failures": [],
            "skipped": 0,
            "message": f"Knowledge dir not found: {root}",
        }

    files = discover_knowledge_files(root)
    total = 0
    skipped = 0
    sources: List[str] = []
    failures: List[str] = []

    print(f"Reading {len(files)} files from {root}...")
    logger.info("ingest_start", directory=str(root), files=len(files))

    all_docs_preview = 0
    for path in files:
        try:
            text = extract_text_from_file(path)
            docs = chunk_text(text, source=path.stem, category=path.stem) if text.strip() else []
            all_docs_preview += len(docs)
        except Exception:
            pass
    print(f"Created {all_docs_preview} chunks...")
    print("Generating embeddings...")
    print("Uploading to Pinecone...")

    for path in files:
        try:
            count, source, status = ingest_file(path, category=path.stem)
            if status == "indexed":
                total += count
                sources.append(source)
                logger.info("indexed_knowledge", source=source, chunks=count, file=path.name)
            elif status == "skipped_duplicate":
                skipped += 1
                sources.append(source)
                logger.info("skipped_duplicate", source=source, file=path.name)
            elif status == "empty":
                failures.append(f"{path.name}: empty")
                logger.warning("empty_file", file=path.name)
            time.sleep(0.8)
        except Exception as exc:
            failures.append(f"{path.name}: {type(exc).__name__}")
            logger.error(
                "index_failed",
                file=path.name,
                error=str(type(exc).__name__),
                detail=str(exc)[:240],
            )
            time.sleep(1.0)

    message = (
        f"Indexed {total} vectors successfully "
        f"({len(files)} files, {skipped} skipped duplicates, {len(failures)} failures)."
    )
    print(message)
    return {
        "indexed": total,
        "files": len(files),
        "sources": sources,
        "failures": failures,
        "skipped": skipped,
        "message": message,
    }


def ingest_documents_dir(documents_dir: Optional[Path] = None) -> Dict[str, Any]:
    settings = get_settings()
    root = Path(documents_dir or settings.documents_dir)
    root.mkdir(parents=True, exist_ok=True)
    files = discover_knowledge_files(root)
    total = 0
    skipped = 0
    sources: List[str] = []
    failures: List[str] = []

    for path in files:
        try:
            count, source, status = ingest_file(path)
            if status == "indexed":
                total += count
                sources.append(source)
            elif status == "skipped_duplicate":
                skipped += 1
                sources.append(source)
            elif status == "empty":
                failures.append(f"{path.name}: empty")
        except Exception as exc:
            failures.append(f"{path.name}: {type(exc).__name__}")
            logger.error("doc_index_failed", file=path.name, error=str(type(exc).__name__))

    return {
        "indexed": total,
        "files": len(files),
        "sources": sources,
        "failures": failures,
        "skipped": skipped,
        "message": (
            f"Indexed {total} document chunks from {len(sources)} files "
            f"({skipped} skipped, {len(failures)} failures)."
        ),
    }
