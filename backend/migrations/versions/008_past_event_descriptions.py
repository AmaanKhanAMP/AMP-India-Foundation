"""Backfill empty Past Event descriptions without overwriting existing text.

Revision ID: 008_past_event_descriptions
Revises: 007_past_events_fields
Create Date: 2026-07-31
"""

from alembic import op
from sqlalchemy import text


revision = "008_past_event_descriptions"
down_revision = "007_past_events_fields"
branch_labels = None
depends_on = None


# Known titles → descriptions (same copy previously shown on the Events page).
# Only applied when description is NULL or blank.
KNOWN_DESCRIPTIONS = {
    "National Job Fair 2025": (
        "A large-scale placement drive connecting skilled youth with corporate "
        "employers across manufacturing, IT, and services."
    ),
    "Medical Relief Camp": (
        "Free health check-ups, screenings, and medical relief support delivered "
        "to underserved neighbourhoods."
    ),
    "Scholarship Distribution Ceremony": (
        "Recognising meritorious students and awarding scholarships to support "
        "higher education pathways."
    ),
    "Scholarship Distribution": (
        "Recognising meritorious students and awarding scholarships to support "
        "higher education pathways."
    ),
    "Skill Training Graduation": (
        "Celebrating graduates of vocational programs in digital skills, "
        "tailoring, and entrepreneurship."
    ),
    "Mentorship Summit": (
        "Industry mentors guided students through academic choices, resume "
        "building, and career planning."
    ),
    "Community Upliftment Drive": (
        "Grassroots outreach with essential supplies, financial literacy "
        "workshops, and self-help group support."
    ),
}


def upgrade():
    conn = op.get_bind()

    for title, description in KNOWN_DESCRIPTIONS.items():
        conn.execute(
            text(
                """
                UPDATE gallery_items
                SET description = :description
                WHERE title = :title
                  AND (description IS NULL OR TRIM(description) = '')
                """
            ),
            {"title": title, "description": description},
        )

    # Generic fill for any remaining blank rows — does not overwrite stored text
    conn.execute(
        text(
            """
            UPDATE gallery_items
            SET description = CONCAT(
              'Highlights from ',
              title,
              ', celebrating AMP India Foundation''s community impact.'
            )
            WHERE description IS NULL OR TRIM(description) = ''
            """
        )
    )


def downgrade():
    # Non-destructive: leave descriptions in place
    pass
