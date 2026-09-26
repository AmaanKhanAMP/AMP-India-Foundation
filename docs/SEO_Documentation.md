# SEO documentation

Frontend SEO is static App Router metadata. It does not fetch CMS.

## Global

`frontend/app/layout.jsx` sets `metadataBase` from `NEXT_PUBLIC_SITE_URL`, title template `%s | AMP India Foundation`, default description, robots, Open Graph, and Twitter.

## Page helpers

`frontend/lib/pageMetadata.js` → `pageMeta({ title, description, canonical })`.

- Canonical paths are relative; Next resolves them with `metadataBase`.
- Aliases: `/home` → `/`, `/what-we-do` → `/about`, `/support` → `/support-us`, `/projects/healthcare` → `/projects/medical`.

## Files

| File | Role |
|------|------|
| `frontend/app/sitemap.js` | Canonical public routes only |
| `frontend/app/robots.js` | Allow `/`, point at sitemap |
| `frontend/lib/jsonLd.js` | Organization, WebSite, WebPage, breadcrumbs |
| `frontend/components/seo/JsonLd.jsx` | Safe JSON-LD script |

Sitemap includes `/privacy-policy` and `/refund-policy`.

Production `sitemap.xml` / `robots.txt` only exist after the frontend SEO branch is deployed to Vercel.
