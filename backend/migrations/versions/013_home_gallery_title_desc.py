"""Add title and description to home_gallery_items.

Revision ID: 013_home_gallery_title_desc
Revises: 012_home_gallery
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa


revision = "013_home_gallery_title_desc"
down_revision = "012_home_gallery"
branch_labels = None
depends_on = None

# Backfill short titles/descriptions for the 6 seeded gallery images.
BACKFILL = [
    (
        "Indian schoolchildren seated together in a classroom learning session",
        "Classroom Learning",
        "Students engaged together in a supported classroom learning session.",
    ),
    (
        "Two young Indian girls studying at a school desk with notebooks",
        "Focused Study Time",
        "Young learners building strong foundations through guided study.",
    ),
    (
        "Indian boys reading and studying together during an education support session",
        "Reading Together",
        "Peer learning and reading support during an education session.",
    ),
    (
        "Indian teacher volunteering at a chalkboard to guide students in class",
        "Volunteer Teaching",
        "Dedicated volunteers guiding students through classroom lessons.",
    ),
    (
        "Rural Indian women engaged in a livelihood weaving and skill development program",
        "Livelihood Skills",
        "Women building sustainable livelihoods through skill development.",
    ),
    (
        "Indian children learning outdoors during a community education outreach program",
        "Community Outreach",
        "Outdoor learning moments from our community education programs.",
    ),
]


def upgrade():
    op.add_column(
        "home_gallery_items",
        sa.Column("title", sa.String(length=60), nullable=False, server_default=""),
    )
    op.add_column(
        "home_gallery_items",
        sa.Column("description", sa.String(length=120), nullable=False, server_default=""),
    )

    for alt, title, description in BACKFILL:
        safe_alt = alt.replace("'", "''")
        safe_title = title.replace("'", "''")
        safe_desc = description.replace("'", "''")
        op.execute(
            f"""
            UPDATE home_gallery_items
            SET title = '{safe_title}', description = '{safe_desc}'
            WHERE alt_text = '{safe_alt}'
              AND (title = '' OR title IS NULL)
            """
        )

    # Any remaining empty rows: derive a short title from alt_text
    op.execute(
        """
        UPDATE home_gallery_items
        SET title = LEFT(alt_text, 60)
        WHERE title = '' OR title IS NULL
        """
    )
    op.execute(
        """
        UPDATE home_gallery_items
        SET description = LEFT(alt_text, 120)
        WHERE description = '' OR description IS NULL
        """
    )


def downgrade():
    op.drop_column("home_gallery_items", "description")
    op.drop_column("home_gallery_items", "title")
