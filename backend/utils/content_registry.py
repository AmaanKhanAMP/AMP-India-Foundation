"""Registry of CMS content modules for trash, stats, and media cleanup.

Add future modules here (About, Blogs, Projects, etc.) so Trash and soft-delete
work automatically without rewriting controllers.
"""

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

CONTENT_RESOURCES = [
    {
        "resource": "hero-banners",
        "module": "Hero Banners",
        "model": HeroBanner,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "home-projects",
        "module": "Home Projects",
        "model": HomeProject,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "home-gallery",
        "module": "Photo Gallery",
        "model": HomeGalleryItem,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "home-events",
        "module": "Home Events",
        "model": HomeEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "testimonials",
        "module": "Testimonials",
        "model": Testimonial,
        "image_fields": ["profile_image"],
        "title_attr": "name",
    },
    {
        "resource": "featured-events",
        "module": "Featured Events",
        "model": FeaturedEvent,
        "image_fields": ["banner_image"],
        "title_attr": "title",
    },
    {
        "resource": "upcoming-events",
        "module": "Upcoming Events",
        "model": UpcomingEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "past-events",
        "module": "Past Events",
        "model": PastEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    # Legacy slug — same model/table (kept for trash restore of older deletes)
    {
        "resource": "gallery-items",
        "module": "Past Events",
        "model": PastEvent,
        "image_fields": ["image_url"],
        "title_attr": "title",
    },
    {
        "resource": "navbar-items",
        "module": "Navbar",
        "model": NavbarItem,
        "image_fields": [],
        "title_attr": "label",
    },
    {
        "resource": "footer-links",
        "module": "Footer Links",
        "model": FooterLink,
        "image_fields": [],
        "title_attr": "label",
    },
    {
        "resource": "footer-focus",
        "module": "Footer Focus",
        "model": FooterFocusItem,
        "image_fields": [],
        "title_attr": "title",
    },
]


def get_resource_meta(resource):
    for entry in CONTENT_RESOURCES:
        if entry["resource"] == resource:
            return entry
    return None


def get_model_meta(model):
    for entry in CONTENT_RESOURCES:
        if entry["model"] is model:
            return entry
    return None
