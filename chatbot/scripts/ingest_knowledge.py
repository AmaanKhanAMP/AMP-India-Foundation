"""Index AMP knowledge (md/txt/pdf/json) into Pinecone via Gemini embeddings.

Usage (from chatbot/):
  python -m scripts.ingest_knowledge
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.services.document_service import ingest_documents_dir, ingest_knowledge_dir
from app.services.rag_service import rag_service


def main() -> None:
    setup_logging()
    logger = get_logger("ingest")
    settings = get_settings()

    print("=== AMP India Foundation — Knowledge Ingest ===")
    print(f"Embedding model : {settings.gemini_embedding_model}")
    print(f"Embedding dim   : {settings.gemini_embedding_dimension}")
    print(f"Pinecone index  : {settings.pinecone_index_name}")
    print(f"Namespace       : {settings.pinecone_namespace}")
    print(f"Knowledge dir   : {settings.knowledge_dir}")
    print()

    if not settings.rag_ready:
        logger.error(
            "missing_credentials",
            hint="Set GEMINI_API_KEY and PINECONE_API_KEY in chatbot/.env",
        )
        sys.exit(1)

    knowledge = ingest_knowledge_dir()
    logger.info(
        "knowledge_done",
        indexed=knowledge.get("indexed"),
        files=knowledge.get("files"),
        failures=len(knowledge.get("failures") or []),
    )

    documents = ingest_documents_dir()
    logger.info("documents_done", indexed=documents.get("indexed"))

    print()
    print(knowledge["message"])
    if knowledge.get("failures"):
        print("Failures:")
        for item in knowledge["failures"]:
            print(f"  - {item}")
    print(documents["message"])

    stats = rag_service.index_stats()
    print()
    print("Pinecone stats:", stats)
    indexed = int(knowledge.get("indexed") or 0) + int(documents.get("indexed") or 0)
    if indexed <= 0 and not (knowledge.get("skipped") or 0):
        print("ERROR: No vectors were indexed. Check embedding model / API key / Pinecone.")
        sys.exit(2)

    print("Ingest completed successfully.")


if __name__ == "__main__":
    main()
