"""Drop unused home_projects fields not rendered on the frontend.

Latest Projects carousel only uses image_url + title.
Removes description, button_text, button_link.

Revision ID: 011_home_projects_trim_fields
Revises: 010_navbar_footer
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa


revision = "011_home_projects_trim_fields"
down_revision = "010_navbar_footer"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("home_projects") as batch:
        batch.drop_column("description")
        batch.drop_column("button_text")
        batch.drop_column("button_link")


def downgrade():
    with op.batch_alter_table("home_projects") as batch:
        batch.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch.add_column(sa.Column("button_text", sa.String(length=100), nullable=True))
        batch.add_column(sa.Column("button_link", sa.String(length=500), nullable=True))
