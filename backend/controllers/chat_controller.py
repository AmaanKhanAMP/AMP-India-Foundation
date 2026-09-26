"""HTTP adapters for the chatbot API."""

from flask import jsonify

from services import chat_service


def get_quick_actions():
    try:
        data = chat_service.get_quick_actions()
        return (
            jsonify(
                {
                    "success": True,
                    "data": data,
                }
            ),
            200,
        )
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "message": chat_service.CONNECTION_ERROR_RESPONSE,
                }
            ),
            500,
        )


def post_message(data):
    """Handle POST /api/chat/message."""
    payload = data if isinstance(data, dict) else {}
    message = payload.get("message")
    if message is None:
        message = ""
    if not isinstance(message, str):
        message = str(message)

    session_id = payload.get("session_id") or payload.get("sessionId")
    page = payload.get("page")

    try:
        result = chat_service.process_message(
            message=message,
            session_id=session_id,
            page=page if isinstance(page, str) else None,
        )
        return jsonify(result), 200
    except Exception:
        # Never return a blank body — keep frontend contract intact
        return (
            jsonify(
                {
                    "success": False,
                    "intent": "error",
                    "confidence": 0.0,
                    "response": chat_service.CONNECTION_ERROR_RESPONSE,
                    "session_id": chat_service.ensure_session_id(
                        session_id if isinstance(session_id, str) else None
                    ),
                }
            ),
            500,
        )
