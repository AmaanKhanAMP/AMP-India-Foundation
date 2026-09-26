"""Chatbot REST endpoints.

GET  /api/chat/quick-actions
POST /api/chat/message
"""

from flask import Blueprint, request

from controllers import chat_controller

chat_bp = Blueprint("chat", __name__)


@chat_bp.get("/quick-actions")
def quick_actions():
    return chat_controller.get_quick_actions()


@chat_bp.post("/message")
def message():
    data = request.get_json(silent=True) or {}
    return chat_controller.post_message(data)
