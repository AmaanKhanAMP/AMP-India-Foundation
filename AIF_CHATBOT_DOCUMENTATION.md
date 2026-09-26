# AIF Chatbot Documentation

**Single source of truth** for the AMP India Foundation (AIF) monorepo documentation.  
**Last consolidated:** 2026-08-04  

> Older reports live in [`docs/archive/`](docs/archive/). Prefer this file when information conflicts.

---

## Table of contents

1. [Project Overview](#1-project-overview)
2. [Complete Architecture](#2-complete-architecture)
3. [Folder Structure](#3-folder-structure)
4. [Tech Stack](#4-tech-stack)
5. [Frontend](#5-frontend)
6. [Backend](#6-backend)
7. [AI Pipeline](#7-ai-pipeline)
8. [RAG Workflow](#8-rag-workflow)
9. [Pinecone](#9-pinecone)
10. [CMS Sync](#10-cms-sync)
11. [Knowledge Sources](#11-knowledge-sources)
12. [Built-in Knowledge](#12-built-in-knowledge)
13. [LLM Flow](#13-llm-flow)
14. [Response Pipeline](#14-response-pipeline)
15. [Cache](#15-cache)
16. [Typo Handling](#16-typo-handling)
17. [Prompt Engineering](#17-prompt-engineering)
18. [API Cost Optimization](#18-api-cost-optimization)
19. [Performance](#19-performance)
20. [Security](#20-security)
21. [Testing](#21-testing)
22. [Deployment](#22-deployment)
23. [Environment Variables](#23-environment-variables)
24. [Production Readiness](#24-production-readiness)
25. [Known Limitations](#25-known-limitations)
26. [Future Improvements](#26-future-improvements)
27. [Changelog](#27-changelog)

---

## 1. Project Overview

AMP India Foundation’s digital platform is a **monorepo** with four runtime pieces:

| Piece | Role | Typical port |
|-------|------|--------------|
| **Frontend** | Public website + chat widget | `3000` |
| **CMS** | Admin UI for content | `3001` |
| **Backend (Flask)** | MySQL CMS API + chatbot sync trigger | `5000` |
| **Chatbot (FastAPI)** | Domain RAG assistant (production chat path) | `8000` |

**Product doctrine**

- Feel as smooth as ChatGPT/Claude for conversation quality.
- Remain a **closed-domain NGO assistant** — verified AMP facts only.
- Prefer **local intelligence** (builtin, cache, knowledge files) over paid APIs.
- Use Gemini/OpenAI as a **response writer**, never as an unchecked fact generator.
- Keep **public APIs, frontend widget contract, CMS schema, Pinecone index, and MySQL schema** stable across upgrades.

**Database:** MySQL schema `aif_cms`.  
**Default CMS admin (change after first login):** `admin@ampindiafoundation.org` / `Admin@12345`.

---

## 2. Complete Architecture

### 2.1 System context

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  CMS Next   │────▶│ Flask :5000  │────▶│ MySQL aif_cms   │
│  (:3001)    │     │ CMS API      │     └─────────────────┘
└─────────────┘     └──────┬───────┘
                           │ schedule_chatbot_sync (1.5s debounce)
                           ▼ POST /api/admin/ingest/cms-sync
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Frontend   │────▶│ FastAPI :8000│────▶│ Pinecone +      │
│  ChatWidget │     │ Chatbot      │     │ Gemini embed/LLM│
└─────────────┘     └──────────────┘     └─────────────────┘
                           ▲
                           │ knowledge/* + backend/knowledge/*.json
```

### 2.2 Production request lifecycle (authoritative)

```
User message
  → sanitize
  → query normalize + typo correction          [0 API]
  → language detection (en | hi | hinglish)
  → session memory (topic + language)
  → intent detection
  → greeting / thanks / bye / security canned
  → answer CACHE?                              [0 API]
  → built-in knowledge?                        [0 API]
  → rewrite + source plan
  → Pinecone Top15 → rerank → Top5
       → Gemini ONLY if DYNAMIC | UNKNOWN
       → else Response Composer (no LLM)
  → local knowledge files
  → emergency knowledge
  → apology + phone/email
  → compose + clean
  → ChatResponse (+ analytics meta)
```

**Streaming:** `POST /api/chat/stream` runs full `chat()` then fake-chunks the finished answer (not true token streaming).

### 2.3 Compatibility constraints

Do **not** break: FastAPI chat/ingest contracts, Flask CMS APIs, frontend widget, Pinecone index layout, MySQL schema, authentication tokens, environment variable names.

---

## 3. Folder Structure

```
AIF/
├── AIF_CHATBOT_DOCUMENTATION.md   ← this file (primary docs)
├── README.md
├── docs/archive/                  ← historical .md reports
├── frontend/                      ← public Next.js site + chatbot widget
│   └── chatbot/                   ← ChatWidget, useChat, chatApi
├── cms/                           ← admin Next.js CMS
├── backend/                       ← Flask API, MySQL models, chatbot_sync
│   ├── knowledge/*.json           ← Phase-2 JSON (synced as backend_*)
│   └── services/chatbot_sync.py
└── chatbot/                       ← FastAPI assistant (production chat)
    ├── app/
    │   ├── main.py
    │   ├── core/                  ← config, logging
    │   ├── routers/               ← chat, health, ingest
    │   └── services/              ← AI orchestration, RAG, builtin, …
    ├── knowledge/                 ← static RAG corpus (NOT project docs)
    ├── documents/                 ← uploads + .source_hashes.json
    ├── scripts/
    └── tests/
```

**Note:** Files under `chatbot/knowledge/*.md` are **RAG content**, not project documentation. They stay in place.

---

## 4. Tech Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | Next.js 15 App Router, React (migrated from Vite) |
| CMS | Next.js 15, React 19, Tailwind 4, Axios, Framer Motion |
| Backend | Flask, MySQL, PyJWT, Flask-Migrate |
| Chatbot | FastAPI, Uvicorn, SlowAPI, structlog, LangChain text splitters, RapidFuzz ≥3.9 |
| LLM / embed | Google Gemini chat + `gemini-embedding-001` (768-d); OpenAI optional as writer |
| Vector DB | Pinecone index `aif-chatbot`, namespace `amp-foundation` |

---

## 5. Frontend

### 5.1 Public routes

`/`, `/home`, `/about`, `/what-we-do`, `/events`, `/volunteer`, `/support`, `/support-us`, `/contact`, `/projects`, `/projects/education`, `/projects/medical`, `/projects/healthcare`, `/projects/employment`, `/projects/empowerment`, `/projects/mentorship`, `/projects/training`, `/projects/featured`, `/terms-and-conditions`.

### 5.2 Chat widget

- Mounted from site layout (`ChatWidget`).
- Base URL: `NEXT_PUBLIC_CHAT_API_URL` → else `NEXT_PUBLIC_API_URL` → else `http://localhost:8000`.
- Prefers `POST /api/chat/stream`, falls back to `POST /api/chat`.
- Session id in `localStorage` (`aif_chat_session_id`).
- Optional `page` field sent with messages (soft prior planned; not fully wired for retrieval).

### 5.3 Migration note

Frontend was migrated from Vite to Next.js 15. Legacy `src/` and `_vite_archive/` may remain. Prefer App Router paths under `frontend/app/`.

---

## 6. Backend

### 6.1 Local setup (summary)

1. Create venv → `pip install -r requirements.txt`
2. Create MySQL database `aif_cms`
3. Configure `.env` (DB + CORS + chatbot sync tokens)
4. `flask db upgrade`
5. Seed admin / website content scripts
6. `python app.py` (port 5000)

### 6.2 Core MySQL entities

`admin_users`, `hero_banners`, `home_projects`, `home_events`, `testimonials`, `featured_events`, `upcoming_events`, `gallery_items`, `contact_messages`, plus layout settings (navbar/footer) used by sync.

### 6.3 Important APIs

| Area | Examples |
|------|----------|
| Auth | `POST /api/auth/login`, `GET /api/auth/me`, profile/password |
| Admin content | CRUD/reorder/publish for banners, projects, events, gallery, testimonials |
| Public content | `GET /api/content/{resource}` (published only) |
| Upload | `POST /api/admin/upload` → `/uploads/...` |
| Contact | Public `POST /api/contact`; admin list/read |
| Chatbot sync | `POST /api/admin/chatbot/sync`, `GET /api/admin/chatbot/status` |
| Legacy chat | `POST /api/chat/message` — **unused by widget** |
| Health | `GET /api/health` |

**Example production API host:** `https://aif-backend-6jwe.onrender.com`

### 6.4 FastAPI chatbot surface (unchanged contract)

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/health` | Liveness |
| GET | `/api/status` | Gemini/Pinecone readiness |
| POST | `/api/chat` | JSON chat (30/min) |
| POST | `/api/chat/stream` | Fake SSE (30/min) |
| POST | `/api/admin/ingest/*` | knowledge, documents, source, cms-sync, upload |

**Chat body:** `{ message, session_id?, page? }`  
**Chat response:** `{ success, response, reply, session_id, intent, category, confidence, meta }`

Admin ingest requires header `X-Admin-Token` matching `ADMIN_INGEST_TOKEN`.

---

## 7. AI Pipeline

### 7.1 Intent classes (current)

Greeting, small_talk, goodbye, general_knowledge, contact, donations, scholarships, events, upcoming_events, past_events, featured_event, projects, volunteering, employment, medical, mentorship, training, amp_knowledge, unknown, injection, out_of_scope.

### 7.2 Static vs dynamic

| Static (prefer builtin / cache — **0 Gemini**) | Dynamic (Pinecone ± Gemini) |
|------------------------------------------------|-----------------------------|
| Greetings, about, mission, vision, contact, timings, donate, bank, volunteer, healthcare overview, employment overview, scholarships, fees, genuine/trust, inclusive FAQs | Upcoming / past / featured events, gallery, testimonials, live CMS listings, UNKNOWN synthesis |

### 7.3 Orchestration modules

| Concern | Primary file |
|---------|----------------|
| Orchestrator | `chatbot/app/services/ai_service.py` |
| Intent | `intent_router.py` |
| Normalize | `query_normalize.py`, `text_normalize.py` |
| Language | `language_service.py` |
| Memory | `memory_service.py` |
| Conversation | `conversation_service.py` |
| Builtin | `builtin_answers.py` |
| Cache | `answer_cache.py` |
| Source plan | `source_planner.py` |
| Rewrite | `query_rewrite.py` |
| RAG | `rag_service.py` |
| Composer | `response_composer.py` |
| Fallback | `fallback_generator.py`, `local_fallback.py` |
| Emergency | `emergency_knowledge.py` |
| Analytics | `analytics_service.py` |
| Website map | `website_knowledge.py` (**defined; not used on live path**) |
| FAQ cache | `faq_cache.py` (**warmed; not used on live chat path**) |

---

## 8. RAG Workflow

1. Build search query (`query_rewrite`) + preferred sources (`source_planner`).
2. Embed query (Gemini embedding).
3. Query Pinecone with metadata filter (`source` ± `section`).
4. Drop scores below threshold (~**0.28**).
5. Dedupe → lexical/vector **rerank** → keep best ~**5** (from Top **15** fetch).
6. Event section hard-gate: upcoming ≠ past ≠ featured.
7. Build context block for LLM **or** pass docs to composer / fallback (no LLM).

**Chunking:** ~550 tokens / 100 overlap; CMS/backend events → **one vector per event** with `metadata.section`.

**Conflict policy:** CMS wins live dates/venues; static files win evergreen policy (contact, bank, mission).

---

## 9. Pinecone

| Setting | Value |
|---------|--------|
| Index | `aif-chatbot` |
| Namespace | `amp-foundation` |
| Embedding model | `gemini-embedding-001` |
| Dimension | 768 |
| Live retrieve | Top 15 → keep ~5 |
| Score floor | ~0.28 |
| Event sections | `upcoming_events`, `past_events`, `featured_event` |

**Risk:** Recreating the index on embedding-dimension mismatch is destructive — avoid during routine deploys.

---

## 10. CMS Sync

```
CMS content save
  → Flask commit
  → schedule_chatbot_sync (≈1.5s debounce, background thread)
  → export cms_* (+ backend/knowledge JSON as backend_*)
  → POST {CHATBOT_URL}/api/admin/ingest/cms-sync
     Header: X-Admin-Token
  → content-hash skip / delete_by_source / chunk / embed / upsert
  → delete_missing_cms for stale cms_* sources
```

### Exported CMS sources

`cms_home`, `cms_projects` (**titles only**), `cms_home_gallery`, `cms_events`, `cms_gallery`, `cms_testimonials`, `cms_footer`, `cms_navbar`, `cms_footer_links`.

### Not exported today

- Draft / soft-deleted rows
- Image binaries/URLs as knowledge
- Full `/projects/*` React page copy (hardcoded in JSX)
- Terms page
- `FooterFocusItem` depth

**Tokens must match:** backend `CHATBOT_INGEST_TOKEN` / `ADMIN_INGEST_TOKEN` ≡ chatbot `ADMIN_INGEST_TOKEN`.

---

## 11. Knowledge Sources

| Priority (conceptual) | Source | Role |
|----------------------|--------|------|
| 1 | Answer cache | Instant repeat static answers |
| 2 | Built-in verified answers | Contact, bank, program overviews, trust FAQs |
| 3 | `chatbot/knowledge/*` | Evergreen markdown/txt corpus |
| 4 | `backend/knowledge/*.json` → `backend_*` | Synced JSON mirror |
| 5 | CMS vectors `cms_*` | Live events, gallery, testimonials, home |
| 6 | Pinecone | Vector access layer for 3–5 |
| 7 | Emergency knowledge | Hardcoded last resort |
| 8 | Apology | Phone + email when nothing verified |

### Static knowledge files

`about_aif.txt`, `contact.txt`, `donations.md`, `employment.txt`, `events.txt`, `faq.txt`, `programs.txt`, `projects.md`, `scholarships.md`, `volunteer.md`.

### Website coverage gap (important)

Rich copy on `/projects/education`, `/projects/medical`, etc. lives in React components and is **not ingested**. The bot therefore cannot mirror full website page depth unless builtins / `programs.txt` paraphrase it. See archived `WEBSITE_KNOWLEDGE_AUDIT.md` for the page matrix.

---

## 12. Built-in Knowledge

`builtin_answers.py` answers STATIC intents **before** Pinecone when `should_use_builtin_first` is true.

**Includes:** contact / phone / email / address / timings, donate overview, **bank details only when asked**, volunteer registration link, healthcare / employment / scholarship / economic overviews, about / mission / vision, fees (job fair), genuine/trust, inclusive (women/anyone apply), get-help router.

**Design rule:** Do not invent unpublished event dates in builtin. Point users to upcoming-events for schedules.

---

## 13. LLM Flow

```
allow_gemini = intent in {UPCOMING_EVENTS, PAST_EVENTS, FEATURED_EVENT, EVENTS}
               OR intent == UNKNOWN
```

| Call Gemini? | When |
|--------------|------|
| **No** | Cache hit, builtin hit, greetings, static overviews, Pinecone-only composer path |
| **Yes** | Dynamic event synthesis or ambiguous UNKNOWN with retrieved docs |

On Gemini 429/empty/error → rewrite from Pinecone docs → local → emergency → apology. **Never invent** fees, phones, bank numbers, or event dates.

LLM temperature for RAG is low (~0.15). Sync embed/LLM calls inside async handlers remain a known blocking-debt item.

---

## 14. Response Pipeline

1. Obtain draft (builtin | Gemini | fallback | emergency | apology)
2. `compose_final` / `compose_from_documents` — natural prose; events sorted, **max 5**
3. `clean_response` — strip markdown headings, `Q:`/`A:`, source names, duplicate phones
4. Leak/secret scrub (`format_user_response`)
5. Soft word budgets (~80–150 by topic)
6. Cache static answers; update session memory; record analytics

**Style target:** Short, friendly, professional — not FAQ dumps or retrieval dumps.

---

## 15. Cache

| Cache | Scope | TTL / size |
|-------|--------|------------|
| Answer cache | Static Q → answer | ~1 hour, ~512 entries; cleared on ingest |
| Retrieval cache | Query + filters → docs | ~180s, ~128 keys |
| Sessions | Topic + turns | `SESSION_TTL_MINUTES` (default 60); process-local |
| FAQ cache | Legacy | Warmed; **not** on live chat path |

**Limitation:** In-process only — multi-worker deployments do not share cache/sessions (Redis recommended later).

---

## 16. Typo Handling

**Zero API cost.** Applied **before** intent and retrieval via `text_normalize` + `query_normalize` (optional RapidFuzz ≥ **85%**).

Examples: `scholership` / `scholarhsip` → scholarship; `volunter` / `volenteer` → volunteer; `helthcare` → healthcare; `emploment` → employment; `donat` / `donte` → donate; `adress` / `contat` → address/contact; `asalamualaikum` / `asslam` → assalamualaikum; `aidf` → aif; `upcomming` → upcoming.

Islamic conversational forms (Ameen, Mashallah, Inshallah, Alhamdulillah, Jazakallah, Khuda Hafiz, …) are handled in conversation routing.

---

## 17. Prompt Engineering

- Domain-only system prompt: answer from verified context; refuse world trivia.
- Language lock: reply in user’s English / Hindi / Hinglish.
- Context is **facts only** — never dump chunk IDs, markdown FAQ, or “According to retrieved context”.
- Canned strings for injection refuse, out-of-scope, clarify, unavailable, apology (with phone/email).
- Multilingual templates via `t(...)` helpers.

---

## 18. API Cost Optimization

**Goal:** ≥80% fewer Gemini/embedding calls vs “RAG everything”.

| Path | Optimized share (est.) |
|------|-------------------------|
| Zero-token (conversation + builtin + cache) | **82–88%** |
| Pinecone only (no LLM) | 8–12% |
| Pinecone + LLM | 4–6% |
| Apology / refuse | ~2% |

**Never call LLM for:** greetings, contact, address, timings, donate, bank, volunteer how-to, healthcare/education/employment overviews, about/mission/vision, fees, genuine/trust, FAQs with verified facts.

**Quality ≠ more Gemini.** Remaining quality work is intent precision + indexing real project-page knowledge, not raising LLM spend.

Analytics: `analytics_service` counters for gemini / pinecone / builtin / cache / latency / intents.

---

## 19. Performance

| Path | Expected latency |
|------|------------------|
| Greeting / canned | &lt; 20–50 ms |
| Cache hit | &lt; 15–50 ms |
| Builtin static | typically tens of ms (local) |
| Pinecone, no Gemini | ~1–3 s (network-bound) |
| Pinecone + Gemini | ~2–6 s |

**Shipped optimizations:** skip network for static; answer cache; local RapidFuzz; Top15→5; retrieval cache; section filters; event list max 5.

**Open:** offload blocking embed/LLM from event loop; true SSE; Redis shared cache; event-list short TTL cache.

---

## 20. Security

- Public chat: sanitize, injection detection, domain refuse, SlowAPI **30/min** per IP, CORS allowlist, secret scrub, prompt-leak strip.
- Admin ingest: `X-Admin-Token`; empty/`change-me` → fail closed (503); wrong token → 401.
- Flask CMS/sync: JWT admin auth.
- Never reveal API keys, system prompts, Pinecone internals, tokens, or DB credentials.
- Bank account details only when the user explicitly asks.

---

## 21. Testing

| Milestone | Result |
|-----------|--------|
| Production upgrade (phases A–D) | 77 tests OK |
| UX / cost / polish era | **242** automated tests OK (latest reported suite) |

Representative suites: conversation, query_pipeline, security, event_sections, contact_pipeline, cms_sync, production_ready, production_suite, ux_response_composer, production_cost_cache, final_production_polish, production_polish_gate.

**Gaps:** multi-worker memory, true streaming, full offline failure matrix, and P0–P5 quality regressions (About-overfit, families-benefit, short “education”, testimonials) still tracked as open analysis items.

---

## 22. Deployment

**Local (typical):** MySQL + Flask `:5000` + chatbot `:8000` + frontend `:3000` + CMS `:3001`.

**Checklist**

1. Align sync tokens across Flask and chatbot.
2. Set frontend `NEXT_PUBLIC_CHAT_API_URL` to chatbot origin.
3. `pip install -r chatbot/requirements.txt` (includes RapidFuzz).
4. Restart chatbot workers after code/env changes (in-memory cache/modules).
5. Trigger CMS sync or knowledge ingest after content changes.
6. Verify `GET /api/status` shows RAG ready when keys configured.

---

## 23. Environment Variables

### Chatbot

`APP_NAME`, `APP_ENV`, `APP_HOST`, `APP_PORT`, `DEBUG`, `LOG_LEVEL`, `CORS_ORIGINS`,  
`GEMINI_API_KEY`, `GEMINI_CHAT_MODEL`, `GEMINI_GENERAL_MODEL`, `GEMINI_EMBEDDING_MODEL`, `GEMINI_EMBEDDING_DIMENSION`, Gemini timeout/retry/temperature/token settings,  
`PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, `PINECONE_CLOUD`, `PINECONE_REGION`,  
`RAG_TOP_K`, `RAG_SCORE_THRESHOLD`, `CHUNK_SIZE`, `CHUNK_OVERLAP`,  
`RATE_LIMIT`, `MAX_MESSAGE_LENGTH`, `MAX_UPLOAD_MB`, `SESSION_TTL_MINUTES`, `ADMIN_INGEST_TOKEN`,  
`KNOWLEDGE_DIR`, `DOCUMENTS_DIR`

`rag_ready` ≈ Gemini configured **and** Pinecone configured.

### Backend sync / DB

`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `CORS_ORIGINS`,  
`CHATBOT_URL`, `CHATBOT_INGEST_TOKEN` or `ADMIN_INGEST_TOKEN`, `CHATBOT_SYNC_ENABLED`

### Frontend / CMS

`NEXT_PUBLIC_CHAT_API_URL`, `NEXT_PUBLIC_API_URL` (CMS → Flask, e.g. `http://localhost:5000`)

---

## 24. Production Readiness

| Dimension | Status (2026-08-04) |
|-----------|---------------------|
| Chat APIs stable | Yes |
| Frontend widget contract | Yes |
| CMS sync contract | Yes |
| Zero-token static FAQs | Yes |
| Answer cache + typo normalize | Yes |
| Gemini gated to dynamic/unknown | Yes |
| Composer + cleaner | Yes |
| Event section filters | Yes |
| Automated tests (~242) | Yes |
| Shared Redis cache/sessions | No |
| True streaming | No |
| Full website project-page index | No |
| About-overfit / benefit-question fixes (P0–P5) | **Plan ready; not implemented** |

**Readiness interpretation:** Pipeline, cost, and UX polish are production-usable for contact/donate/events/volunteer. **Program-page depth and several intent edge cases remain open** (see §25–26). Earlier “92/100” polish score measures pipeline/cost/compat; it does not mean all quality RCA items are closed.

---

## 25. Known Limitations

1. Fake SSE (full answer then chunked).
2. Process-local sessions and answer cache (multi-worker blind spot).
3. Triple corpus (`cms_*` + `backend_*` + knowledge stems) can drift if sync tokens fail silently.
4. `/projects/*` JSX copy not ingested; `cms_projects` exports titles only.
5. `website_knowledge.layers_for_page` unused; widget `page` mostly meta-only.
6. About-overfit: bare “AIF/AMP” can route to About (e.g. “How does AIF help women?”).
7. “How do families benefit?” may classify as general knowledge / refuse.
8. Short token “education” may be `UNKNOWN`.
9. Testimonials / success stories weakly routed.
10. `cms_navbar` / `cms_footer_links` synced but rarely in source filters.
11. Program builtins can sound template-similar.
12. Sync is fire-and-forget (no durable retry queue).
13. Blocking embed/LLM inside async event loop.
14. `faq_cache` still warmed though unused on live path.
15. CMS admin port documented variously as 3001 vs 3002 in older notes — prefer **3001** from cms package docs.

---

## 26. Future Improvements

### Priority plan (from analysis — pending implementation)

| Phase | Focus |
|-------|--------|
| **P0** | Intent surgery: narrow About regex; education/empowerment/testimonials/beneficiary; short tokens; inclusive (disabled/women); fix session follow-up |
| **P1** | Ingest project-page mirrors as knowledge markdown; distinct program builtins |
| **P2** | Lightweight knowledge planner (builtin vs +CMS vs Pinecone) |
| **P3** | Wire `page` soft prior; fix website path map to real `/projects/*` routes |
| **P4** | Prompt/composer polish (writer, not chunk narrator) |
| **P5** | Regression tests for failing question classes |

### Longer-term

- Redis for shared answer cache + sessions
- True SSE streaming
- Sync retry / dead-letter queue
- Wire `RATE_LIMIT` from settings into routes
- Deprecate unused Flask Phase-2 chat path when safe
- Optional CMS modules: richer About/Projects/Volunteer/Blog admin

**Non-goals:** vendor lock-in swaps, general world knowledge, CMS UI rewrite, Pinecone recreate, DB migration, public API field renames.

---

## 27. Changelog

| Date | Change |
|------|--------|
| Pre-2026-08 | FastAPI RAG chatbot + Flask CMS sync; Pinecone-first domain answers |
| 2026-08-03 | Architecture audit + improvement plan (docs) |
| 2026-08-03 | Upgrade A–D: SourcePlan, emergency knowledge, Top15→5, FAQ deprecate, Islamic phrases, 77 tests |
| 2026-08-03 | UX: builtin answers, response composer/cleaner, static-first, bank-on-ask |
| 2026-08-04 | Cost/prod: query normalize, answer cache, analytics, Gemini hard-gate, RapidFuzz |
| 2026-08-04 | Polish: special FAQs, typo extras, event sort/max-5, ~242 tests |
| 2026-08-04 | Analysis-only: full audit, website knowledge audit, cost analysis, production plan (P0–P5 deferred) |
| 2026-08-04 | **Docs consolidation:** all project Markdown merged into this master file; prior reports moved to `docs/archive/` |

---

## Appendix A — Emergency contact facts (verified)

- **Phone:** +91 8291101312  
- **Email:** contact@ampindiafoundation.org  
- **Office hours:** Monday–Saturday, 9:00 AM–6:00 PM (Sunday closed)  
- **Volunteer form:** https://tinyurl.com/AIFVolunteerRegn  

## Appendix B — Archive index

All superseded documentation files are preserved under [`docs/archive/`](docs/archive/) without deletion. This master document replaces them as the **single source of truth**.

---

*End of AIF Chatbot Documentation*
