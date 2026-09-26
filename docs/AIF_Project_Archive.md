# AIF project archive

Merged historical notes from `docs/archive/` (August 2026 chatbot and production reports). Prefer the current guides in this folder and [`AIF_CHATBOT_DOCUMENTATION.md`](../AIF_CHATBOT_DOCUMENTATION.md) when information conflicts.

## Table of contents

1. [Project Timeline](#project-timeline)
2. [Development Notes](#development-notes)
3. [CMS Development](#cms-development)
4. [Backend & Railway](#backend--railway)
5. [Render Deployment](#render-deployment)
6. [Vercel Deployment](#vercel-deployment)
7. [Chatbot Development](#chatbot-development)
8. [SEO Implementation](#seo-implementation)
9. [Performance Fixes](#performance-fixes)
10. [Home & Events Bug History](#home--events-bug-history)
11. [Future Improvements](#future-improvements)

## Project Timeline

| Date | Notes |
|------|--------|
| Through 2026-07 | Vite frontend migrated to Next.js; Flask CMS API; CMS app added |
| 2026-07–08 | CMS setup guide, seed scripts, package READMEs archived |
| 2026-08-03 | Chatbot architecture audit and production improvement plan (docs only) |
| 2026-08-03 | Upgrade phases A–D: SourcePlan, emergency knowledge, Top15→5, 77 tests |
| 2026-08-03 | UX: builtin answers, response composer, static-first, bank-on-ask |
| 2026-08-04 | Cost/prod: query normalize, answer cache, analytics, Gemini hard-gate |
| 2026-08-04 | Polish: special FAQs, event max-5, ~242 tests |
| 2026-08-04 | Analysis-only audits (quality P0–P5 deferred) |
| 2026-08-04 | Docs consolidation into `AIF_CHATBOT_DOCUMENTATION.md`; reports moved to `docs/archive/` |
| 2026-09 | Public site: ISR, image optimization, on-demand revalidation, SEO, Privacy/Refund pages |

## Development Notes

Design doctrine from 2026-08: feel like ChatGPT for users; stay a closed, verified NGO knowledge system; prefer local intelligence over paid APIs.

Compatibility rule repeated across every production report: do not change FastAPI/Flask public contracts, frontend widget, CMS schema, Pinecone index, or MySQL schema during chatbot polish.

## CMS Development

Early CMS setup (July 2026):

- Next.js admin → Flask `:5000` → MySQL → public site reads published APIs.
- Seed: `python scripts/seed_website_content.py` (idempotent).
- Default admin: `admin@ampindiafoundation.org` / `Admin@12345`.
- Port notes conflicted (`3001` vs `3002`). Current package default is **3001**.

Later CMS work (not in those August reports): footer/navbar modules, section visibility, publish-triggered site revalidation. See [CMS_Documentation.md](./CMS_Documentation.md).

## Backend & Railway

August reports treated Flask as the CMS API + chatbot sync trigger. Railway was used at times for MySQL/backend experiments; production Flask later settled on Render. Do not assume Railway is the live origin without checking current env.

Sync is fire-and-forget with a short debounce. Failed sync must not block CMS save.

## Render Deployment

Production Flask/uploads origin is Render (`NEXT_PUBLIC_API_URL`). Uploads need long cache headers; large images are resized on upload/serve. First-load slowness on Vercel was often Render origin fetch of full originals before image optimization.

## Vercel Deployment

Public frontend (and CMS) deploy on Vercel. ISR `revalidate` 60 plus on-demand `revalidateTag`/`revalidatePath`. Stale public content after CMS save was Vercel Full Route Cache / Data Cache, not Railway. Requires matching `REVALIDATION_SECRET` on frontend and CMS, and CMS `FRONTEND_ORIGIN` = public site URL.

## Chatbot Development

Answer layers (priority): builtin → cache → markdown knowledge → backend JSON → CMS export → Pinecone → Gemini (dynamic/unknown only).

**Static (no Gemini):** greetings, about, programs overview, volunteer, donate, bank, contact, timings.

**Dynamic:** event lists, gallery, testimonials, latest CMS listings.

Known 2026-08 quality issues (analysis; implementation deferred in those reports):

- `/projects/*` JSX copy not ingested.
- About-overfit: bare “AIF/AMP” routed to About.
- “How do families benefit?” refused as general knowledge.
- Short token “education” classified UNKNOWN.
- Program builtins sounded template-similar.
- Fake SSE; process-local cache (no Redis).

Cost target: 82–88% zero-token paths; Gemini only 4–6% of traffic.

## SEO Implementation

Not covered in the August archive reports. Current implementation (2026-09): static `pageMeta`, canonical aliases, `sitemap.js`, `robots.js`, JSON-LD. See [SEO_Documentation.md](./SEO_Documentation.md).

## Performance Fixes

Chatbot (2026-08): skip network for static intents; 1h answer cache; RapidFuzz normalize; Top15→5; retrieval cache 180s. Expected 60–80% average latency drop vs Pinecone-first.

Website (2026-09): Next Image `deviceSizes` capped at 1920; lazy non-LCP images; Pillow resize on Render; immutable upload Cache-Control.

## Home & Events Bug History

Not in the August chatbot archive. Later production issues:

- Empty live lists overwriting good ISR/session data — hold last renderable list.
- Publish notify after list reload could skip revalidation — notify immediately after DB success.
- CMS `/api/*` login redirect looked like 200 — unauthenticated API now returns 401 JSON.
- Concurrent `next dev` + `next build` caused webpack/HMR issues.

## Future Improvements

From 2026-08 P0–P5 plan (then unimplemented):

| Phase | Focus |
|-------|--------|
| P0 | Intent surgery (About regex, education, testimonials, beneficiaries) |
| P1 | Ingest project-page mirrors as knowledge markdown |
| P2 | Lightweight knowledge planner |
| P3 | Wire page soft prior to real `/projects/*` routes |
| P4 | Prompt/composer polish |
| P5 | Regression tests for failing question classes |

Longer-term: Redis shared cache, true SSE, sync retry queue.

## Documents merged into this file

`API_COST_ANALYSIS.md`, `API_COST_REPORT.md`, `CHATBOT_ARCHITECTURE.md`, `CHATBOT_FULL_AUDIT.md`, `CMS_SETUP.md`, `FINAL_ARCHITECTURE.md`, `FINAL_IMPLEMENTATION_REPORT.md`, `FINAL_PIPELINE_ANALYSIS.md`, `FINAL_PRODUCTION_AUDIT.md`, `FINAL_PRODUCTION_PLAN.md`, `FINAL_PRODUCTION_POLISH.md`, `FINAL_PRODUCTION_REPORT.md`, `PERFORMANCE_REPORT.md`, `PRODUCTION_IMPROVEMENT_PLAN.md`, `PRODUCTION_UPGRADE_DELIVERY.md`, `PRODUCTION_UX_DELIVERY.md`, `WEBSITE_KNOWLEDGE_AUDIT.md`.
