from flask import Blueprint, request

from controllers import contact_controller

contact_bp = Blueprint("contact", __name__)


@contact_bp.post("")
def create_contact():
    """POST /api/contact — submit a contact form message."""
    data = request.get_json(silent=True) or {}
    return contact_controller.submit_contact(data)


@contact_bp.get("/messages")
def list_messages():
    """GET /api/contact/messages — list stored contact messages."""
    return contact_controller.get_messages()
