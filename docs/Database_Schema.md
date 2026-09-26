# Database schema

MySQL database: **`aif_cms`**. Migrations live in `backend/migrations/`.

| Table | Purpose |
|-------|---------|
| `admin_users` | CMS admins (JWT) |
| `password_reset_tokens` | Admin password reset |
| `hero_banners` | Home hero carousel |
| `home_projects` | Home project cards |
| `home_gallery_items` | Home gallery |
| `home_events` | Home events teaser |
| `testimonials` | Home testimonials |
| `featured_events` | Events featured |
| `upcoming_events` | Events upcoming |
| `gallery_items` | Past events / gallery |
| `section_visibility` | Show/hide Home Events and Upcoming Events |
| `navbar_settings` | Logo and navbar settings |
| `navbar_items` | Navbar links |
| `footer_settings` | Footer copy and social URLs |
| `footer_links` | Footer Useful Links |
| `footer_focus_items` | Footer Recent Focus |

Most content tables share publish status, `display_order`, and soft-delete fields.

Do not recreate or rename these tables as part of routine deploys. Add columns only through Alembic migrations.
