# Next.js Migration Notes

## Status — COMPLETE (non-destructive)

The site runs on **Next.js 15 App Router**. The original Vite/`src` tree was **not deleted**.

### Verified
- `npm run build` succeeds
- `npm run dev` serves on http://localhost:3000
- Key routes return HTTP 200: `/`, `/about`, `/events`, `/volunteer`, `/support-us`, `/contact`, `/projects`, `/projects/education`

## Canonical Next.js code (use this)

| Path | Role |
|------|------|
| `app/` | App Router pages + `layout.jsx` + `globals.css` |
| `components/` | Migrated UI (layout, home, events, pages) |
| `styles/Events.css` | Events page styles |
| `public/assets/` | Static images (logo, contact, volunteer, etc.) |
| `next.config.mjs` | Next config (Unsplash remote images) |
| `jsconfig.json` | `@/` path alias |

## Preserved original sources (do not delete yet)

| Path | Role |
|------|------|
| `src/` | Original Vite React tree (kept intact) |
| `_vite_archive/` | Restored copies of Vite entry files for reference |

Archived Vite entry files:
- `_vite_archive/index.html`
- `_vite_archive/vite.config.js`
- `_vite_archive/main.jsx`
- `_vite_archive/App.jsx`

## Active commands

```bash
cd frontend
npm run dev      # Next.js → http://localhost:3000
npm run build
npm run start
```

## App Router routes

| URL | File |
|-----|------|
| `/` | `app/page.jsx` |
| `/home` | `app/home/page.jsx` |
| `/about` | `app/about/page.jsx` |
| `/what-we-do` | `app/what-we-do/page.jsx` |
| `/events` | `app/events/page.jsx` |
| `/volunteer` | `app/volunteer/page.jsx` |
| `/support` | `app/support/page.jsx` |
| `/support-us` | `app/support-us/page.jsx` |
| `/contact` | `app/contact/page.jsx` |
| `/projects` | `app/projects/page.jsx` |
| `/projects/education` … | `app/projects/*/page.jsx` |

## Important note about `src/pages`

Because `src/pages` still exists, Next.js **also** registers a legacy Pages Router tree (e.g. `/About`, `/Events`).  
**Use the App Router URLs above** (lowercase paths from `app/`).

When you are ready for **final cleanup** (only after you confirm everything looks correct), you may manually:

1. Rename or remove `src/pages` (stops Pages Router duplicates)
2. Remove leftover Vite-only files if any remain outside `_vite_archive`
3. Optionally remove `_vite_archive/` and unused `src/` once Flask backend work begins

**Do not delete `src/` until you explicitly choose to.**

## Ready for Flask backend

Yes — the frontend is on Next.js App Router and can proceed with Flask API integration (API routes / `NEXT_PUBLIC_API_URL`, fetch from client components, etc.).
