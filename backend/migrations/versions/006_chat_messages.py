"""create chat_messages table for chatbot history

Revision ID: 006_chat_messages
Revises: 005_soft_delete
Create Date: 2026-07-25
"""

from alembic import op
import sqlalchemy as sa


revision = "006_chat_messages"
down_revision = "005_soft_delete"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=128), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("bot_response", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=64), nullable=True),
        sa.Column("page", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_messages_session_id"),
        "chat_messages",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_messages_intent"),
        "chat_messages",
        ["intent"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_chat_messages_intent"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_session_id"), table_name="chat_messages")
    op.drop_table("chat_messages")
