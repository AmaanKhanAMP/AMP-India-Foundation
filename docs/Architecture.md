# Architecture

AMP India Foundation is a monorepo with four runtimes.

| Piece | Role | Typical port |
|-------|------|--------------|
| Frontend | Public Next.js website | `3000` |
| CMS | Admin Next.js UI | `3001` (package default; older notes also mention `3002`) |
| Backend | Flask CMS API + MySQL + chatbot sync | `5000` |
| Chatbot | FastAPI domain RAG assistant | `8000` |

## System context

```
CMS (:3001) ──▶ Flask (:5000) ──▶ MySQL aif_cms
                     │
                     └── schedule_chatbot_sync ──▶ FastAPI ingest
Frontend ──▶ published Flask content APIs
Frontend ChatWidget ──▶ FastAPI /api/chat
```

## Compatibility

Do not break public Flask content APIs, CMS admin contracts, frontend widget chat contract, Pinecone index layout, MySQL schema, or environment variable names.

## Product doctrine

- Closed-domain NGO assistant: verified AMP facts only.
- Prefer local answers (builtin, cache, knowledge files) over paid APIs.
- Use Gemini as a response writer, not an unchecked fact generator.

See [`AIF_CHATBOT_DOCUMENTATION.md`](../AIF_CHATBOT_DOCUMENTATION.md) sections 1–4 for the full architecture write-up.
