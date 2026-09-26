"""Admin + public content API routes for CMS-managed website sections."""

from flask import Blueprint

from controllers import content_controller as cc
from models.cms_models import (
    FeaturedEvent,
    FooterFocusItem,
    FooterLink,
    HeroBanner,
    HomeEvent,
    HomeGalleryItem,
    HomeProject,
    NavbarItem,
    PastEvent,
    Testimonial,
    UpcomingEvent,
)
from utils.auth import admin_required

admin_content_bp = Blueprint("admin_content", __name__)

HERO_FIELDS = [
    "image_url",
    "title",
    "title_accent",
    "subtitle",
    "primary_btn_text",
    "primary_btn_link",
    "secondary_btn_text",
    "secondary_btn_link",
    "display_order",
    "status",
]
PROJECT_FIELDS = [
    "image_url",
    "title",
    "display_order",
    "status",
]
HOME_GALLERY_FIELDS = [
    "image_url",
    "alt_text",
    "title",
    "description",
    "display_order",
    "status",
]
HOME_EVENT_FIELDS = [
    "image_url",
    "title",
    "description",
    "venue",
    "event_date",
    "registration_link",
    "button_text",
    "speaker",
    "display_order",
    "status",
]
TESTIMONIAL_FIELDS = [
    "profile_image",
    "name",
    "designation",
    "organisation",
    "location",
    "message",
    "display_order",
    "status",
]
FEATURED_FIELDS = [
    "banner_image",
    "title",
    "description",
    "venue",
    "event_date",
    "event_time",
    "display_order",
    "status",
]
UPCOMING_FIELDS = [
    "image_url",
    "title",
    "description",
    "venue",
    "event_date",
    "display_order",
    "status",
]
PAST_EVENT_FIELDS = [
    "image_url",
    "title",
    "description",
    "event_date",
    "venue",
    "display_order",
    "status",
]
# Legacy alias
GALLERY_FIELDS = PAST_EVENT_FIELDS
NAVBAR_ITEM_FIELDS = [
    "label",
    "href",
    "item_type",
    "item_key",
    "parent_key",
    "display_order",
    "status",
]
FOOTER_LINK_FIELDS = [
    "label",
    "href",
    "display_order",
    "status",
]
FOOTER_FOCUS_FIELDS = [
    "title",
    "href",
    "date_label",
    "display_order",
    "status",
]


def _register_resource(bp, prefix, model, fields):
    endpoint_base = prefix.replace("-", "_")

    def list_all():
        return cc.list_items(model)

    def get_one(item_id):
        return cc.get_item(model, item_id)

    def create():
        return cc.create_item(model, fields, resource=prefix)

    def update(item_id):
        return cc.update_item(model, item_id, fields, resource=prefix)

    def delete(item_id):
        return cc.delete_item(model, item_id)

    def duplicate(item_id):
        return cc.duplicate_item(model, item_id, fields)

    def reorder():
        return cc.reorder_items(model)

    def publish(item_id):
        return cc.set_status(model, item_id, "published")

    def unpublish(item_id):
        return cc.set_status(model, item_id, "draft")

    def restore(item_id):
        return cc.restore_item(model, item_id)

    def permanent_delete(item_id):
        return cc.permanent_delete_item(model, item_id)

    def bulk():
        return cc.bulk_action(model)

    bp.add_url_rule(
        f"/{prefix}",
        endpoint=f"{endpoint_base}_list",
        view_func=admin_required(list_all),
        methods=["GET"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>",
        endpoint=f"{endpoint_base}_get",
        view_func=admin_required(get_one),
        methods=["GET"],
    )
    bp.add_url_rule(
        f"/{prefix}",
        endpoint=f"{endpoint_base}_create",
        view_func=admin_required(create),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>",
        endpoint=f"{endpoint_base}_update",
        view_func=admin_required(update),
        methods=["PUT"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>",
        endpoint=f"{endpoint_base}_delete",
        view_func=admin_required(delete),
        methods=["DELETE"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>/duplicate",
        endpoint=f"{endpoint_base}_duplicate",
        view_func=admin_required(duplicate),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/reorder",
        endpoint=f"{endpoint_base}_reorder",
        view_func=admin_required(reorder),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>/publish",
        endpoint=f"{endpoint_base}_publish",
        view_func=admin_required(publish),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>/unpublish",
        endpoint=f"{endpoint_base}_unpublish",
        view_func=admin_required(unpublish),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>/restore",
        endpoint=f"{endpoint_base}_restore",
        view_func=admin_required(restore),
        methods=["POST"],
    )
    bp.add_url_rule(
        f"/{prefix}/<int:item_id>/permanent",
        endpoint=f"{endpoint_base}_permanent",
        view_func=admin_required(permanent_delete),
        methods=["DELETE"],
    )
    bp.add_url_rule(
        f"/{prefix}/bulk",
        endpoint=f"{endpoint_base}_bulk",
        view_func=admin_required(bulk),
        methods=["POST"],
    )


# Unified Trash — must register before resource routes that could collide is fine
# (trash is a static path, resources use different prefixes)
@admin_content_bp.get("/trash")
@admin_required
def trash_list():
    return cc.list_trash()


@admin_content_bp.post("/trash/<resource>/<int:item_id>/restore")
@admin_required
def trash_restore(resource, item_id):
    return cc.restore_from_trash(resource, item_id)


@admin_content_bp.delete("/trash/<resource>/<int:item_id>")
@admin_required
def trash_permanent(resource, item_id):
    return cc.permanent_delete_from_trash(resource, item_id)


_register_resource(admin_content_bp, "hero-banners", HeroBanner, HERO_FIELDS)
_register_resource(admin_content_bp, "home-projects", HomeProject, PROJECT_FIELDS)
_register_resource(admin_content_bp, "home-gallery", HomeGalleryItem, HOME_GALLERY_FIELDS)
_register_resource(admin_content_bp, "home-events", HomeEvent, HOME_EVENT_FIELDS)
_register_resource(admin_content_bp, "testimonials", Testimonial, TESTIMONIAL_FIELDS)
_register_resource(admin_content_bp, "featured-events", FeaturedEvent, FEATURED_FIELDS)
_register_resource(admin_content_bp, "upcoming-events", UpcomingEvent, UPCOMING_FIELDS)
_register_resource(admin_content_bp, "past-events", PastEvent, PAST_EVENT_FIELDS)
# Legacy admin slug (same PastEvent / gallery_items table)
_register_resource(admin_content_bp, "gallery-items", PastEvent, PAST_EVENT_FIELDS)
_register_resource(admin_content_bp, "navbar-items", NavbarItem, NAVBAR_ITEM_FIELDS)
_register_resource(admin_content_bp, "footer-links", FooterLink, FOOTER_LINK_FIELDS)
_register_resource(admin_content_bp, "footer-focus", FooterFocusItem, FOOTER_FOCUS_FIELDS)


public_content_bp = Blueprint("public_content", __name__)


@public_content_bp.get("/hero-banners")
def public_hero():
    return cc.list_items(HeroBanner, published_only=True)


@public_content_bp.get("/home-projects")
def public_projects():
    return cc.list_items(HomeProject, published_only=True)


@public_content_bp.get("/home-gallery")
def public_home_gallery():
    return cc.list_items(HomeGalleryItem, published_only=True)


@public_content_bp.get("/home-events")
def public_home_events():
    return cc.list_items(HomeEvent, published_only=True)


@public_content_bp.get("/testimonials")
def public_testimonials():
    return cc.list_items(Testimonial, published_only=True)


@public_content_bp.get("/featured-events")
def public_featured():
    return cc.list_items(FeaturedEvent, published_only=True)


@public_content_bp.get("/upcoming-events")
def public_upcoming():
    return cc.list_items(UpcomingEvent, published_only=True)


@public_content_bp.get("/past-events")
def public_past_events():
    return cc.list_items(PastEvent, published_only=True)


@public_content_bp.get("/gallery-items")
def public_gallery():
    """Legacy alias — same data as /past-events."""
    return cc.list_items(PastEvent, published_only=True)


@public_content_bp.get("/navbar-items")
def public_navbar_items():
    return cc.list_items(NavbarItem, published_only=True)


@public_content_bp.get("/footer-links")
def public_footer_links():
    return cc.list_items(FooterLink, published_only=True)


@public_content_bp.get("/footer-focus")
def public_footer_focus():
    return cc.list_items(FooterFocusItem, published_only=True)
