"""Align gallery_items with Past Events EventCard fields.

Adds event_date, event_time, venue, registration_link and backfills
from legacy year/location columns. Existing rows are preserved.

Revision ID: 007_past_events_fields
Revises: 006_chat_messages
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa


revision = "007_past_events_fields"
down_revision = "006_chat_messages"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "gallery_items",
        sa.Column("event_date", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "gallery_items",
        sa.Column("event_time", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "gallery_items",
        sa.Column("venue", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "gallery_items",
        sa.Column("registration_link", sa.String(length=500), nullable=True),
    )

    # Preserve legacy gallery data into the new Past Events fields
    op.execute(
        """
        UPDATE gallery_items
        SET event_date = year
        WHERE (event_date IS NULL OR event_date = '')
          AND year IS NOT NULL
          AND year <> ''
        """
    )
    op.execute(
        """
        UPDATE gallery_items
        SET venue = location
        WHERE (venue IS NULL OR venue = '')
          AND location IS NOT NULL
          AND location <> ''
        """
    )


def downgrade():
    op.drop_column("gallery_items", "registration_link")
    op.drop_column("gallery_items", "venue")
    op.drop_column("gallery_items", "event_time")
    op.drop_column("gallery_items", "event_date")
