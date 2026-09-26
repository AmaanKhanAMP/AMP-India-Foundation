# Deployment guide

## Local

| Service | Directory | Command | Port |
|---------|-----------|---------|------|
| MySQL | — | database `aif_cms` | `3306` |
| Backend | `backend/` | `python app.py` | `5000` |
| Chatbot | `chatbot/` | `python run.py` | `8000` |
| Frontend | `frontend/` | `npm run dev` | `3000` |
| CMS | `cms/` | `npm run dev` | `3001` |

Backend first-time setup:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/create_database.py
flask db upgrade
python scripts/seed_admin.py
python scripts/seed_website_content.py
python app.py
```

Default CMS admin (change after first login): `admin@ampindiafoundation.org` / `Admin@12345`.

## Environment (summary)

**Backend / DB:** `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `CORS_ORIGINS`, `CHATBOT_URL`, `CHATBOT_INGEST_TOKEN` or `ADMIN_INGEST_TOKEN`, `CHATBOT_SYNC_ENABLED`.

**Frontend / CMS:** `NEXT_PUBLIC_API_URL` (Flask origin), `NEXT_PUBLIC_SITE_URL` (public site origin), `NEXT_PUBLIC_CHAT_API_URL` (chatbot origin). CMS on-demand revalidation uses server-only `REVALIDATION_SECRET` and `FRONTEND_ORIGIN` (not `NEXT_PUBLIC_*`).

**Chatbot:** Gemini and Pinecone keys, `ADMIN_INGEST_TOKEN`, CORS, RAG settings. See the master document §23.

## Production hosts (current)

- Public frontend: Vercel (`amp-aif.vercel.app` when configured).
- Flask API / uploads: Render.
- CMS: Vercel (separate app).
- Chatbot: deploy with aligned ingest tokens.

## After deploy

1. Align sync tokens between Flask and chatbot.
2. Set frontend `NEXT_PUBLIC_API_URL` to the production Flask origin.
3. Restart chatbot workers after env/code changes.
4. Trigger CMS sync or knowledge ingest after content changes.
5. Confirm `GET /api/status` when chatbot keys are configured.

Full checklist: [`AIF_CHATBOT_DOCUMENTATION.md`](../AIF_CHATBOT_DOCUMENTATION.md) §22–24.
