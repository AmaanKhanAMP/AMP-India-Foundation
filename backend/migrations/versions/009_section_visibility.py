"""Create section_visibility table for Hide/Show Section controls.

Revision ID: 009_section_visibility
Revises: 008_past_event_descriptions
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa


revision = "009_section_visibility"
down_revision = "008_past_event_descriptions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "section_visibility",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section_name", sa.String(length=100), nullable=False),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("section_name", name="uq_section_visibility_section_name"),
    )
    op.create_index(
        "ix_section_visibility_section_name",
        "section_visibility",
        ["section_name"],
        unique=False,
    )

    # Seed Upcoming Events as visible by default (events page section only).
    op.execute(
        """
        INSERT INTO section_visibility (section_name, is_visible, created_at, updated_at)
        VALUES ('upcoming_events', 1, UTC_TIMESTAMP(), UTC_TIMESTAMP())
        """
    )


def downgrade():
    op.drop_index("ix_section_visibility_section_name", table_name="section_visibility")
    op.drop_table("section_visibility")
