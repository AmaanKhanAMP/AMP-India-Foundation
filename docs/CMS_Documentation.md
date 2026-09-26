# CMS documentation

Independent Next.js admin for AMP India Foundation. It talks only to the Flask API.

```
CMS → Flask /api/admin/* → MySQL → public site reads /api/content/*
```

## Setup

```powershell
cd cms
npm install
# .env.local: NEXT_PUBLIC_API_URL=http://localhost:5000
npm run dev
```

Default local port: **3001**. Include that origin in backend `CORS_ORIGINS`.

## Content modules

Generic list/form pages (`ContentListPage` / `ContentFormPage`) driven by `cms/utils/resourceConfigs.js`.

Useful Links (`footer-links`) include Home, About, Projects, Events, Volunteer, Support, Contact, Terms & Conditions, Privacy Policy, Refund Policy.

After a successful publish, the CMS notifies the public site via same-origin `/api/revalidate-site` (server proxy). That must not fail the CMS save.

## Seed

```powershell
cd backend
flask db upgrade
python scripts/seed_website_content.py
```

The public site keeps hardcoded fallbacks and overlays published CMS data when the API is reachable.

Historical package README: [`archive/cms_README.md`](./archive/cms_README.md).
