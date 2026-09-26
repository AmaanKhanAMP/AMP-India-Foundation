"""Add page settings and remaining public-site CMS tables.

Revision ID: 014_site_content_sync
Revises: 013_home_gallery_title_desc
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "014_site_content_sync"
down_revision = "013_home_gallery_title_desc"
branch_labels = None
depends_on = None


def _soft_cols():
    return [
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
    ]


def upgrade():
    op.alter_column(
        "home_gallery_items",
        "description",
        existing_type=sa.String(length=120),
        type_=sa.String(length=280),
        existing_nullable=False,
        existing_server_default="",
    )

    def create_list_table(name, extra_cols):
        cols = [sa.Column("id", sa.Integer(), primary_key=True)]
        cols.extend(extra_cols)
        cols.extend(_soft_cols())
        op.create_table(name, *cols)
        op.create_index(f"ix_{name}_status", name, ["status"])
        op.create_index(f"ix_{name}_display_order", name, ["display_order"])
        op.create_index(f"ix_{name}_is_deleted", name, ["is_deleted"])

    create_list_table(
        "home_preview_cards",
        [
            sa.Column("image_url", sa.String(length=500), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("subtitle", sa.String(length=160), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("href", sa.String(length=500), nullable=False, server_default="/projects"),
        ],
    )
    create_list_table(
        "impact_stats",
        [
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("target_value", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("suffix", sa.String(length=8), nullable=False, server_default="+"),
            sa.Column("icon_key", sa.String(length=40), nullable=True),
        ],
    )
    create_list_table(
        "project_cards",
        [
            sa.Column("slug", sa.String(length=80), nullable=False),
            sa.Column("image_url", sa.String(length=500), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("subtitle", sa.String(length=160), nullable=True),
            sa.Column("href", sa.String(length=500), nullable=False, server_default="/projects"),
            sa.Column("initiatives", sa.Text(), nullable=True),
        ],
    )
    op.create_index("ix_project_cards_slug", "project_cards", ["slug"])

    create_list_table(
        "project_pages",
        [
            sa.Column("slug", sa.String(length=80), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("subtitle", sa.String(length=160), nullable=True),
            sa.Column("quote", sa.Text(), nullable=True),
            sa.Column("badge", sa.String(length=80), nullable=True),
            sa.Column("image_url", sa.String(length=500), nullable=False),
            sa.Column("paragraph_1", sa.Text(), nullable=True),
            sa.Column("paragraph_2", sa.Text(), nullable=True),
            sa.Column("paragraph_3", sa.Text(), nullable=True),
        ],
    )
    op.create_index("ix_project_pages_slug", "project_pages", ["slug"], unique=True)

    create_list_table(
        "about_focus_items",
        [
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
        ],
    )
    create_list_table(
        "about_values",
        [
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("icon_key", sa.String(length=40), nullable=True),
        ],
    )
    create_list_table(
        "about_objectives",
        [
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("number_label", sa.String(length=8), nullable=True),
            sa.Column("highlighted", sa.String(length=8), nullable=False, server_default="no"),
        ],
    )
    create_list_table(
        "about_faqs",
        [
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
        ],
    )
    create_list_table(
        "events_timeline_items",
        [
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("period", sa.String(length=80), nullable=True),
        ],
    )
    create_list_table(
        "events_categories",
        [
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("icon_key", sa.String(length=40), nullable=True),
        ],
    )

    op.create_table(
        "page_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_key", sa.String(length=40), nullable=False),
        sa.Column("hero_image_url", sa.String(length=500), nullable=True),
        sa.Column("secondary_image_url", sa.String(length=500), nullable=True),
        sa.Column("tertiary_image_url", sa.String(length=500), nullable=True),
        sa.Column("badge", sa.String(length=80), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("title_accent", sa.String(length=120), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("cta_text", sa.String(length=80), nullable=True),
        sa.Column("cta_link", sa.String(length=500), nullable=True),
        sa.Column("extra_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_page_settings_page_key", "page_settings", ["page_key"], unique=True)


def downgrade():
    op.drop_index("ix_page_settings_page_key", table_name="page_settings")
    op.drop_table("page_settings")
    for name in [
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
    ]:
        op.drop_table(name)
    op.alter_column(
        "home_gallery_items",
        "description",
        existing_type=sa.String(length=280),
        type_=sa.String(length=120),
        existing_nullable=False,
        existing_server_default="",
    )
