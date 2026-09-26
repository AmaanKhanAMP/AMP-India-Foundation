"""Admin + public routes for section Hide/Show visibility."""

from flask import Blueprint

from controllers import section_visibility_controller as svc
from utils.auth import admin_required

admin_sections_bp = Blueprint("admin_sections", __name__)
public_sections_bp = Blueprint("public_sections", __name__)


@public_sections_bp.get("/<section_name>/visibility")
def public_get_visibility(section_name):
    return svc.get_visibility(section_name)


@admin_sections_bp.get("/<section_name>/visibility")
@admin_required
def admin_get_visibility(section_name):
    return svc.get_visibility(section_name)


@admin_sections_bp.put("/<section_name>/visibility")
@admin_required
def admin_update_visibility(section_name):
    return svc.update_visibility(section_name)
