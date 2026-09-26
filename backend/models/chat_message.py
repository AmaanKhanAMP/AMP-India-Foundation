"""Persisted chatbot conversation turns."""

from datetime import datetime, timezone

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class ChatMessage(db.Model):
    """One user→bot exchange within a browser session."""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(128), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(64), nullable=True, index=True)
    page = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "intent": self.intent,
            "page": self.page,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ChatMessage {self.id} session={self.session_id!r} intent={self.intent!r}>"
