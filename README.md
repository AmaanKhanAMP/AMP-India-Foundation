# AMP India Foundation (AIF)

Public website, admin CMS, Flask API, and FastAPI chatbot for AMP India Foundation.

## Documentation

**Primary documentation (single source of truth):**

➡️ **[AIF_CHATBOT_DOCUMENTATION.md](./AIF_CHATBOT_DOCUMENTATION.md)**

Historical reports are preserved in [`docs/archive/`](./docs/archive/) (not deleted).

## Quick start (local)

| Service | Directory | Typical command | Port |
|---------|-----------|-----------------|------|
| MySQL | — | database `aif_cms` | `3306` |
| Backend | `backend/` | `python app.py` | `5000` |
| Chatbot | `chatbot/` | `python run.py` | `8000` |
| Frontend | `frontend/` | `npm run dev` | `3000` |
| CMS | `cms/` | `npm run dev` | `3001` |

See the master document for architecture, env vars, CMS sync, RAG pipeline, and production readiness.
