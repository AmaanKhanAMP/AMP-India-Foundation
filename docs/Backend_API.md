# Backend API

Flask app in `backend/`. Serves CMS admin APIs, public content APIs, uploads, and contact.

## Auth (`/api/auth`)

- `POST /login` — `{ email, password, remember }`
- `GET /me` — current admin (Bearer)
- `PUT /profile`
- `PUT /change-password`
- `POST /logout`

## Admin content (`/api/admin/content/{resource}`)

Resources include `hero-banners`, `home-projects`, `home-events`, `home-gallery`, `testimonials`, `featured-events`, `upcoming-events`, `past-events` / `gallery-items`, `navbar-items`, `footer-links`, `footer-focus`.

- `GET /` list
- `GET /:id` detail
- `POST /` create
- `PUT /:id` update
- `DELETE /:id` soft delete
- `POST /:id/duplicate`
- `POST /reorder`
- `POST /:id/publish` / `unpublish`
- `POST /bulk`

Also: dashboard stats, contact message admin, `POST /api/admin/upload`.

## Public content

`GET /api/content/{resource}` — published rows only.  
`GET /api/layout/navbar` and `GET /api/layout/footer`.  
`GET /api/sections/{name}/visibility`.

## Contact

Public: `POST /api/contact`.

## Uploads

Files stored under `backend/uploads` and served with long-lived cache headers. New images are resized in place (max edge 1920) when needed.

## Chatbot sync

After CMS mutations, Flask can `POST` the chatbot ingest endpoint (debounced). Sync failure must not block CMS save.
