"""AMP contact facts. Prefer CMS-synced live_facts.json, else verified defaults."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

_DEFAULTS = {
    "phone": "+91 8291101312",
    "email": "contact@ampindiafoundation.org",
    "office_timings": "Monday to Saturday, 9:00 AM to 6:00 PM",
    "address": (
        "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
        "A Clare Road, Nagpada, Mumbai - 400008"
    ),
}


def _facts_path() -> Path:
    from app.core.config import get_settings

    root = Path(get_settings().documents_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root / "live_facts.json"


def load_live_facts() -> Dict[str, str]:
    path = _facts_path()
    data: Dict[str, Any] = dict(_DEFAULTS)
    if path.is_file():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                for key in _DEFAULTS:
                    value = parsed.get(key)
                    if value and str(value).strip():
                        data[key] = str(value).strip()
        except (OSError, ValueError, TypeError):
            pass
    return data


def write_live_facts(payload: Dict[str, Any]) -> None:
    data = load_live_facts()
    for key in _DEFAULTS:
        value = payload.get(key)
        if value and str(value).strip():
            data[key] = str(value).strip()
    path = _facts_path()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_phone() -> str:
    return load_live_facts()["phone"]


def get_email() -> str:
    return load_live_facts()["email"]


def get_address() -> str:
    return load_live_facts()["address"]


def get_office_timings() -> str:
    return load_live_facts()["office_timings"]


# Module aliases for older imports / tests (defaults until CMS sync writes live_facts)
PHONE = _DEFAULTS["phone"]
EMAIL = _DEFAULTS["email"]
OFFICE_TIMINGS = _DEFAULTS["office_timings"]
ADDRESS = _DEFAULTS["address"]


def answer_contact(question: str) -> str:
    """
    Build a natural contact answer from CMS-synced facts (or defaults).
    """
    facts = load_live_facts()
    phone = facts["phone"]
    email = facts["email"]
    timings = facts["office_timings"]
    address = facts["address"]
    full = (
        f"You can contact AMP India Foundation at {phone}. "
        f"Email: {email}. "
        f"Office timings: {timings}. "
        f"Office address: {address}."
    )

    q = (question or "").lower().strip()

    wants_email = bool(re.search(r"\b(email|e-?mail|mail)\b", q))
    wants_hours = bool(re.search(r"\b(timing|timings|hours|open|kitne)\b", q))
    wants_address = bool(
        re.search(r"\b(address|location|where|located|reach|kaha|kahan)\b", q)
    )
    wants_phone = bool(
        re.search(r"\b(phone|call|number|helpline|mobile|telephone)\b", q)
    )

    broad = bool(
        re.search(
            r"\b(contact|details?|info|information|reach)\b",
            q,
        )
    ) or not (wants_email or wants_hours or wants_address or wants_phone)

    if broad or (wants_phone and wants_email) or q in {
        "contact",
        "number",
        "phone",
        "mail",
        "email",
    }:
        return full

    lead: list[str] = []
    if wants_phone:
        lead.append(f"You can call AMP India Foundation at {phone}.")
    if wants_email:
        lead.append(f"Email: {email}. We typically reply within 24 hours.")
    if wants_hours:
        lead.append(f"Office timings: {timings}.")
    if wants_address:
        lead.append(f"Office address: {address}.")

    if not lead:
        return full

    extras: list[str] = []
    joined = " ".join(lead)
    if phone not in joined:
        extras.append(f"Phone: {phone}.")
    if email not in joined:
        extras.append(f"Email: {email}.")
    if timings not in joined:
        extras.append(f"Office timings: {timings}.")
    if address not in joined and "Nagpada" not in joined:
        extras.append(f"Office address: {address}.")
    return " ".join(lead + extras)


def try_contact_fast_path(question: str) -> str:
    """Always available for CONTACT intent."""
    return answer_contact(question)
