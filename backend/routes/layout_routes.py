"""Admin + public routes for Navbar/Footer singleton settings."""

from flask import Blueprint

from controllers import layout_settings_controller as layout
from utils.auth import admin_required

admin_layout_bp = Blueprint("admin_layout", __name__)
public_layout_bp = Blueprint("public_layout", __name__)


@public_layout_bp.get("/navbar")
def public_navbar():
    return layout.get_navbar_settings()


@public_layout_bp.get("/footer")
def public_footer():
    return layout.get_footer_settings()


@admin_layout_bp.get("/navbar")
@admin_required
def admin_get_navbar():
    return layout.get_navbar_settings()


@admin_layout_bp.put("/navbar")
@admin_required
def admin_put_navbar():
    return layout.update_navbar_settings()


@admin_layout_bp.get("/footer")
@admin_required
def admin_get_footer():
    return layout.get_footer_settings()


@admin_layout_bp.put("/footer")
@admin_required
def admin_put_footer():
    return layout.update_footer_settings()
