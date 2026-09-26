"""Known website sections that support Hide/Show visibility.

Add new entries here to enable the same toggle for other homepage/page sections
without schema changes (rows are created on first read/update).
"""

SECTION_REGISTRY = {
    "upcoming_events": {
        "label": "Upcoming Events",
        "default_visible": True,
    },
    "home_events": {
        "label": "Home Upcoming Events",
        "default_visible": True,
    },
}


def is_known_section(section_name: str) -> bool:
    return section_name in SECTION_REGISTRY


def section_label(section_name: str) -> str:
    meta = SECTION_REGISTRY.get(section_name) or {}
    return meta.get("label") or section_name.replace("_", " ").title()


def default_visible(section_name: str) -> bool:
    meta = SECTION_REGISTRY.get(section_name) or {}
    return bool(meta.get("default_visible", True))
