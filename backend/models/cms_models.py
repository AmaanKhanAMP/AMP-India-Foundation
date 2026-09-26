from datetime import datetime, timezone

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


class PublishableMixin:
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)


class SoftDeleteMixin:
    """Soft delete / recycle-bin fields shared by CMS content modules."""

    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("admin_users.id"), nullable=True)

    def soft_meta(self):
        return {
            "is_deleted": bool(self.is_deleted),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "deleted_by": self.deleted_by,
        }


class AdminUser(db.Model, TimestampMixin):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="admin")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PasswordResetToken(db.Model):
    """One-time admin password reset tokens."""

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    admin = db.relationship("AdminUser", backref=db.backref("reset_tokens", lazy=True))


class HeroBanner(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "hero_banners"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    title_accent = db.Column(db.String(120), nullable=True)
    subtitle = db.Column(db.Text, nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    description = db.Column(db.Text, nullable=True)
    primary_btn_text = db.Column(db.String(100), nullable=True)
    primary_btn_link = db.Column(db.String(500), nullable=True)
    secondary_btn_text = db.Column(db.String(100), nullable=True)
    secondary_btn_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "title_accent": self.title_accent,
            "subtitle": self.subtitle,
            "primary_btn_text": self.primary_btn_text,
            "primary_btn_link": self.primary_btn_link,
            "secondary_btn_text": self.secondary_btn_text,
            "secondary_btn_link": self.secondary_btn_link,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class HomeProject(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Homepage Latest Projects carousel — image + title only."""

    __tablename__ = "home_projects"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class HomeGalleryItem(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Homepage Photo Gallery tiles — image, alt, title, short description."""

    __tablename__ = "home_gallery_items"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255), nullable=False, default="")
    title = db.Column(db.String(60), nullable=False, default="")
    description = db.Column(db.String(280), nullable=False, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "alt_text": self.alt_text,
            "title": self.title,
            "description": self.description,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class HomeEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Upcoming events shown on the homepage teaser section."""

    __tablename__ = "home_events"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    event_time = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)
    button_text = db.Column(db.String(100), nullable=True)
    speaker = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "registration_link": self.registration_link,
            "button_text": self.button_text,
            "speaker": self.speaker,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class Testimonial(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    profile_image = db.Column(db.String(500), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(255), nullable=True)
    organisation = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_image": self.profile_image,
            "name": self.name,
            "designation": self.designation,
            "organisation": self.organisation,
            "location": self.location,
            "message": self.message,
            "rating": self.rating,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class FeaturedEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    __tablename__ = "featured_events"

    id = db.Column(db.Integer, primary_key=True)
    banner_image = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    event_time = db.Column(db.String(100), nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    category = db.Column(db.String(100), nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    registration_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "banner_image": self.banner_image,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class UpcomingEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Upcoming events on the Events page grid."""

    __tablename__ = "upcoming_events"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    # Legacy columns — kept for existing rows; CMS/API no longer write these fields.
    event_time = db.Column(db.String(100), nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    category = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class PastEvent(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Past Events on the Events page (EventCard grid).

    Table name remains gallery_items so existing Railway/MySQL data is preserved.
    Public/admin API resource slug is past-events.
    """

    __tablename__ = "gallery_items"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Legacy column — kept for existing rows; CMS/API no longer write this field.
    category = db.Column(db.String(100), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    # Legacy columns — kept for existing rows; CMS/API no longer write these fields.
    event_time = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(255), nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)
    # Legacy gallery columns — retained for existing data / mapper fallbacks
    year = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    alt_text = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "event_date": self.event_date,
            "venue": self.venue,
            "year": self.year,
            "location": self.location,
            "alt_text": self.alt_text,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


# Backward-compatible alias (older imports / scripts)
GalleryItem = PastEvent


class SectionVisibility(db.Model, TimestampMixin):
    """Homepage / page section show-hide flags (does not affect content rows)."""

    __tablename__ = "section_visibility"

    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "section_name": self.section_name,
            "is_visible": bool(self.is_visible),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NavbarSettings(db.Model, TimestampMixin):
    """Singleton brand/logo settings for the site navbar (one row)."""

    __tablename__ = "navbar_settings"

    id = db.Column(db.Integer, primary_key=True)
    logo_url = db.Column(db.String(500), nullable=False, default="/assets/logo.png")
    logo_alt = db.Column(db.String(120), nullable=False, default="AMP Logo")
    logo_link = db.Column(db.String(500), nullable=False, default="/")

    def to_dict(self):
        return {
            "id": self.id,
            "logo_url": self.logo_url,
            "logo_alt": self.logo_alt,
            "logo_link": self.logo_link,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NavbarItem(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Top-level nav links and dropdown children (mirrors Navbar.jsx)."""

    __tablename__ = "navbar_items"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(80), nullable=False)
    href = db.Column(db.String(500), nullable=False, default="/#")
    # link = plain item; dropdown = parent with children (e.g. PROJECTS)
    item_type = db.Column(db.String(20), nullable=False, default="link")
    # Unique key for dropdown parents (children reference this via parent_key)
    item_key = db.Column(db.String(80), nullable=True, index=True)
    parent_key = db.Column(db.String(80), nullable=True, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "href": self.href,
            "item_type": self.item_type,
            "item_key": self.item_key,
            "parent_key": self.parent_key,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class FooterSettings(db.Model, TimestampMixin):
    """Singleton footer copy/contact/social/CTA (mirrors Footer.jsx)."""

    __tablename__ = "footer_settings"

    id = db.Column(db.Integer, primary_key=True)
    # Top CTA bar
    cta_heading = db.Column(db.Text, nullable=False)
    cta_button_text = db.Column(db.String(80), nullable=False)
    cta_button_link = db.Column(db.String(500), nullable=False)
    # About column
    about_heading = db.Column(db.String(80), nullable=False)
    about_text = db.Column(db.Text, nullable=False)
    about_link_text = db.Column(db.String(80), nullable=False)
    about_link_href = db.Column(db.String(500), nullable=False)
    # Column headings
    useful_links_heading = db.Column(db.String(80), nullable=False)
    recent_focus_heading = db.Column(db.String(80), nullable=False)
    contact_heading = db.Column(db.String(80), nullable=False)
    # Contact details
    address_label = db.Column(db.String(80), nullable=False)
    address_text = db.Column(db.Text, nullable=False)
    phone_label = db.Column(db.String(80), nullable=False)
    phone_text = db.Column(db.String(80), nullable=False)
    email_label = db.Column(db.String(80), nullable=False)
    email_text = db.Column(db.String(120), nullable=False)
    # Social
    follow_heading = db.Column(db.String(80), nullable=False)
    facebook_url = db.Column(db.String(500), nullable=False)
    instagram_url = db.Column(db.String(500), nullable=False)
    # Bottom bar
    copyright_text = db.Column(db.String(255), nullable=False)
    copyright_highlight = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "cta_heading": self.cta_heading,
            "cta_button_text": self.cta_button_text,
            "cta_button_link": self.cta_button_link,
            "about_heading": self.about_heading,
            "about_text": self.about_text,
            "about_link_text": self.about_link_text,
            "about_link_href": self.about_link_href,
            "useful_links_heading": self.useful_links_heading,
            "recent_focus_heading": self.recent_focus_heading,
            "contact_heading": self.contact_heading,
            "address_label": self.address_label,
            "address_text": self.address_text,
            "phone_label": self.phone_label,
            "phone_text": self.phone_text,
            "email_label": self.email_label,
            "email_text": self.email_text,
            "follow_heading": self.follow_heading,
            "facebook_url": self.facebook_url,
            "instagram_url": self.instagram_url,
            "copyright_text": self.copyright_text,
            "copyright_highlight": self.copyright_highlight,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FooterLink(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Useful Links column items in Footer.jsx."""

    __tablename__ = "footer_links"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(80), nullable=False)
    href = db.Column(db.String(500), nullable=False, default="/")

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "href": self.href,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }


class FooterFocusItem(db.Model, TimestampMixin, PublishableMixin, SoftDeleteMixin):
    """Recent Focus column items in Footer.jsx."""

    __tablename__ = "footer_focus_items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    href = db.Column(db.String(500), nullable=False, default="/")
    date_label = db.Column(db.String(40), nullable=False, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "href": self.href,
            "date_label": self.date_label,
            "display_order": self.display_order,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            **self.soft_meta(),
        }
