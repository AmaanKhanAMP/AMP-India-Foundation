from flask import jsonify

from services import contact_service
from utils.validators import validate_contact_payload


def submit_contact(data):
    cleaned, errors = validate_contact_payload(data)
    if errors:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": errors,
                }
            ),
            400,
        )

    try:
        contact_service.create_contact_message(cleaned)
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unable to save your message. Please try again later.",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Your message has been submitted successfully.",
            }
        ),
        201,
    )


def get_messages():
    try:
        records = contact_service.list_contact_messages()
        return (
            jsonify(
                {
                    "success": True,
                    "count": len(records),
                    "data": [item.to_dict() for item in records],
                }
            ),
            200,
        )
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unable to fetch contact messages.",
                }
            ),
            500,
        )
