# AIF CMS

Independent Next.js 15 content management studio for AMP India Foundation. Runs separately from the public website (`frontend/`) and talks to the Flask API.

## Stack

- Next.js 15 (App Router) + React 19
- Tailwind CSS 4
- Axios, Framer Motion, Lucide React
- Port **3001**

## Setup

```bash
cd cms
npm install
```

Ensure `.env.local` exists:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

On Vercel (Production), set:

```env
NEXT_PUBLIC_API_URL=https://aif-backend-6jwe.onrender.com
```

CMS is Next.js — use `NEXT_PUBLIC_API_URL` (not `VITE_API_URL`). Restart `npm run dev` after changing env vars.

## Run

1. Ensure the Flask backend is reachable (local `:5000` or Render).
2. Seed an admin user if needed:

```bash
cd ../backend
python scripts/seed_admin.py
```

Default credentials (from backend `.env` / seed script):

- Email: `admin@ampindiafoundation.org`
- Password: `Admin@12345`

3. Start the CMS:

```bash
cd cms
npm run dev
```

Open [http://localhost:3001](http://localhost:3001).

## Scripts

| Script | Command |
|--------|---------|
| Dev | `npm run dev` → `next dev -p 3001` |
| Build | `npm run build` |
| Start | `npm run start` → `next start -p 3001` |

## Features

- JWT login with middleware route protection
- Dashboard stats
- CRUD + reorder/duplicate for hero banners, projects, home events, testimonials, featured/upcoming events, gallery
- Contact message inbox (search, pagination, mark read, bulk delete)
- Profile + change password
- Image upload via `/api/admin/upload`

## Notes

- Relative image URLs from the API (`/uploads/...`) are prefixed with `NEXT_PUBLIC_API_URL` when displayed.
- Auth token is stored in `localStorage` (`cms_token`); a `cms_auth` cookie is set for Next.js middleware.
