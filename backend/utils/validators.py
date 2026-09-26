import re

from email_validator import EmailNotValidError, validate_email


PHONE_PATTERN = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def validate_contact_payload(data):
    """
    Validate contact form payload.

    Returns:
        tuple: (cleaned_data: dict | None, errors: dict)
    """
    errors = {}

    if not isinstance(data, dict):
        return None, {"_form": "Request body must be a JSON object."}

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    message = (data.get("message") or "").strip()

    if not first_name:
        errors["first_name"] = "First name is required."
    elif len(first_name) > 100:
        errors["first_name"] = "First name must be at most 100 characters."

    if not last_name:
        errors["last_name"] = "Last name is required."
    elif len(last_name) > 100:
        errors["last_name"] = "Last name must be at most 100 characters."

    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validated = validate_email(email, check_deliverability=False)
            email = validated.normalized
        except EmailNotValidError:
            errors["email"] = "Please provide a valid email address."

    if not phone:
        errors["phone"] = "Phone number is required."
    elif not PHONE_PATTERN.match(phone):
        errors["phone"] = "Please provide a valid phone number."

    if not message:
        errors["message"] = "Message is required."
    elif len(message) < 10:
        errors["message"] = "Message must be at least 10 characters."
    elif len(message) > 5000:
        errors["message"] = "Message must be at most 5000 characters."

    if errors:
        return None, errors

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "message": message,
    }, {}
