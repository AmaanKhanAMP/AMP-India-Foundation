from extensions import db
from models.contact_message import ContactMessage


def create_contact_message(payload):
    """Persist a validated contact message."""
    record = ContactMessage(
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload["email"],
        phone=payload["phone"],
        message=payload["message"],
        status="New",
    )
    db.session.add(record)
    db.session.commit()
    return record


def list_contact_messages():
    """Return all contact messages, newest first."""
    return (
        ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    )
