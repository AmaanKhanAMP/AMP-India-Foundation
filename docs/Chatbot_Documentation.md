# Chatbot documentation

Production chat path is **FastAPI** in `chatbot/`. The public widget calls `POST /api/chat` (and `/api/chat/stream`).

## Answer order (zero API first)

1. Sanitize, normalize, typo-correct
2. Language + session
3. Intent / greeting / security canned replies
4. Answer cache
5. Built-in verified facts
6. Pinecone retrieve (Top15 → Top5)
7. Gemini only for DYNAMIC or UNKNOWN
8. Local knowledge files / emergency contacts
9. Compose + clean

Streaming is currently full-answer-then-chunk, not true token SSE.

## Knowledge

- `chatbot/knowledge/*.md` — RAG corpus (not project docs)
- Flask CMS sync exports `cms_*` sources
- `backend/knowledge/*.json` synced as `backend_*`

`/projects/*` React page copy is not fully ingested; that remains a known gap.

## Security

Public: sanitize, injection detection, SlowAPI rate limit, CORS allowlist.  
Admin ingest: `X-Admin-Token` (empty/`change-me` fails closed).

Full pipeline, cost, tests, and open quality items: [`../AIF_CHATBOT_DOCUMENTATION.md`](../AIF_CHATBOT_DOCUMENTATION.md).
