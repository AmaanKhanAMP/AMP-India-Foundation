"""Drop CMS tables added only to make previously static pages CMS-driven.

Keeps 014's home_gallery_items.description widening (existing CMS gallery).

Revision ID: 015_drop_extra_cms_tables
Revises: 014_site_content_sync
Create Date: 2026-08-14
"""

from alembic import op


revision = "015_drop_extra_cms_tables"
down_revision = "014_site_content_sync"
branch_labels = None
depends_on = None

TABLES = [
    "page_settings",
    "events_categories",
    "events_timeline_items",
    "about_faqs",
    "about_objectives",
    "about_values",
    "about_focus_items",
    "project_pages",
    "project_cards",
    "impact_stats",
    "home_preview_cards",
]


def upgrade():
    list_tables = [name for name in TABLES if name != "page_settings"]
    for name in list_tables:
        op.drop_index(f"ix_{name}_status", table_name=name)
        op.drop_index(f"ix_{name}_display_order", table_name=name)
        op.drop_index(f"ix_{name}_is_deleted", table_name=name)
    op.drop_index("ix_project_cards_slug", table_name="project_cards")
    op.drop_index("ix_project_pages_slug", table_name="project_pages")
    op.drop_index("ix_page_settings_page_key", table_name="page_settings")
    for name in TABLES:
        op.drop_table(name)


def downgrade():
    pass
