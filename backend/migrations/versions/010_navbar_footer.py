"""Navbar + Footer CMS tables seeded from current frontend hardcoded content.

Revision ID: 010_navbar_footer
Revises: 009_section_visibility
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa


revision = "010_navbar_footer"
down_revision = "009_section_visibility"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "navbar_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("logo_url", sa.String(length=500), nullable=False),
        sa.Column("logo_alt", sa.String(length=120), nullable=False),
        sa.Column("logo_link", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "navbar_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("href", sa.String(length=500), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.Column("item_key", sa.String(length=80), nullable=True),
        sa.Column("parent_key", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_navbar_items_item_key", "navbar_items", ["item_key"])
    op.create_index("ix_navbar_items_parent_key", "navbar_items", ["parent_key"])
    op.create_index("ix_navbar_items_status", "navbar_items", ["status"])
    op.create_index("ix_navbar_items_display_order", "navbar_items", ["display_order"])
    op.create_index("ix_navbar_items_is_deleted", "navbar_items", ["is_deleted"])

    op.create_table(
        "footer_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cta_heading", sa.Text(), nullable=False),
        sa.Column("cta_button_text", sa.String(length=80), nullable=False),
        sa.Column("cta_button_link", sa.String(length=500), nullable=False),
        sa.Column("about_heading", sa.String(length=80), nullable=False),
        sa.Column("about_text", sa.Text(), nullable=False),
        sa.Column("about_link_text", sa.String(length=80), nullable=False),
        sa.Column("about_link_href", sa.String(length=500), nullable=False),
        sa.Column("useful_links_heading", sa.String(length=80), nullable=False),
        sa.Column("recent_focus_heading", sa.String(length=80), nullable=False),
        sa.Column("contact_heading", sa.String(length=80), nullable=False),
        sa.Column("address_label", sa.String(length=80), nullable=False),
        sa.Column("address_text", sa.Text(), nullable=False),
        sa.Column("phone_label", sa.String(length=80), nullable=False),
        sa.Column("phone_text", sa.String(length=80), nullable=False),
        sa.Column("email_label", sa.String(length=80), nullable=False),
        sa.Column("email_text", sa.String(length=120), nullable=False),
        sa.Column("follow_heading", sa.String(length=80), nullable=False),
        sa.Column("facebook_url", sa.String(length=500), nullable=False),
        sa.Column("instagram_url", sa.String(length=500), nullable=False),
        sa.Column("copyright_text", sa.String(length=255), nullable=False),
        sa.Column("copyright_highlight", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "footer_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("href", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_footer_links_status", "footer_links", ["status"])
    op.create_index("ix_footer_links_display_order", "footer_links", ["display_order"])
    op.create_index("ix_footer_links_is_deleted", "footer_links", ["is_deleted"])

    op.create_table(
        "footer_focus_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("href", sa.String(length=500), nullable=False),
        sa.Column("date_label", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_footer_focus_items_status", "footer_focus_items", ["status"])
    op.create_index("ix_footer_focus_items_display_order", "footer_focus_items", ["display_order"])
    op.create_index("ix_footer_focus_items_is_deleted", "footer_focus_items", ["is_deleted"])

    # Seed from current frontend hardcoded content
    op.execute(
        """
        INSERT INTO navbar_settings
          (logo_url, logo_alt, logo_link, created_at, updated_at)
        VALUES
          ('/assets/logo.png', 'AMP Logo', '/', UTC_TIMESTAMP(), UTC_TIMESTAMP())
        """
    )

    nav_items = [
        (1, "HOME", "/home", "link", None, None),
        (2, "ABOUT US", "/about", "link", None, None),
        (3, "PROJECTS", "/projects/education", "dropdown", "projects", None),
        (4, "Education", "/projects/education", "link", None, "projects"),
        (5, "Medical Relief", "/projects/medical", "link", None, "projects"),
        (6, "Employment Support", "/projects/employment", "link", None, "projects"),
        (7, "Economic Empowerment", "/projects/empowerment", "link", None, "projects"),
        (8, "Student Mentorship", "/projects/mentorship", "link", None, "projects"),
        (9, "Employment Training", "/projects/training", "link", None, "projects"),
        (10, "EVENTS", "/events", "link", None, None),
        (11, "VOLUNTEER", "/volunteer", "link", None, None),
        (12, "SUPPORT US", "/support-us", "link", None, None),
        (13, "CONTACT", "/contact", "link", None, None),
    ]
    for order, label, href, item_type, item_key, parent_key in nav_items:
        ik = f"'{item_key}'" if item_key else "NULL"
        pk = f"'{parent_key}'" if parent_key else "NULL"
        op.execute(
            f"""
            INSERT INTO navbar_items
              (label, href, item_type, item_key, parent_key, status, display_order,
               is_deleted, created_at, updated_at)
            VALUES
              ('{label}', '{href}', '{item_type}', {ik}, {pk}, 'published', {order},
               0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        )

    about = (
        "AMP India Foundation is a non-profit organization dedicated to regularise "
        "and scale up socio-economic development welfare activities. We empower "
        "underprivileged youth through sustainable educational models, rigorous training, "
        "and professional mentorship."
    ).replace("'", "''")

    op.execute(
        f"""
        INSERT INTO footer_settings (
          cta_heading, cta_button_text, cta_button_link,
          about_heading, about_text, about_link_text, about_link_href,
          useful_links_heading, recent_focus_heading, contact_heading,
          address_label, address_text, phone_label, phone_text,
          email_label, email_text, follow_heading, facebook_url, instagram_url,
          copyright_text, copyright_highlight, created_at, updated_at
        ) VALUES (
          'Join Our Mission to Empower Lives Through Education & Employment.',
          'BECOME A VOLUNTEER',
          '/volunteer',
          'ABOUT US',
          '{about}',
          'READ MORE →',
          '/about',
          'USEFUL LINKS',
          'RECENT FOCUS',
          'GET IN TOUCH',
          '📍 Address:',
          'AMP India Foundation, Mumbai, Maharashtra, India.',
          '📞 Phone:',
          '+91 93200 60093',
          '✉️ Email:',
          'info@ampindia.org',
          'FOLLOW US',
          'https://www.facebook.com/ampindiafoundation/',
          'https://www.instagram.com/ampindiafoundation/',
          'Copyrights © 2026 All Rights Reserved. Powered by ',
          'AMP India Foundation',
          UTC_TIMESTAMP(),
          UTC_TIMESTAMP()
        )
        """
    )

    footer_links = [
        (1, "Home", "/"),
        (2, "About Us", "/about"),
        (3, "What We Do", "/what-we-do"),
        (4, "Projects", "/projects"),
        (5, "Events", "/events"),
        (6, "Join Us / Volunteer", "/volunteer"),
        (7, "Support Us", "/support-us"),
        (8, "Contact", "/contact"),
        (9, "Terms & Conditions", "/terms-and-conditions"),
    ]
    for order, label, href in footer_links:
        safe_label = label.replace("'", "''")
        op.execute(
            f"""
            INSERT INTO footer_links
              (label, href, status, display_order, is_deleted, created_at, updated_at)
            VALUES
              ('{safe_label}', '{href}', 'published', {order}, 0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        )

    focus_items = [
        (1, "National Talent Search Examination", "/projects/education", "July 2026"),
        (2, "Employability Training Programs", "/projects/training", "June 2026"),
        (3, "Higher Education Scholarship Distribution", "/projects/education", "May 2026"),
    ]
    for order, title, href, date_label in focus_items:
        op.execute(
            f"""
            INSERT INTO footer_focus_items
              (title, href, date_label, status, display_order, is_deleted, created_at, updated_at)
            VALUES
              ('{title}', '{href}', '{date_label}', 'published', {order},
               0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        )


def downgrade():
    op.drop_table("footer_focus_items")
    op.drop_table("footer_links")
    op.drop_table("footer_settings")
    op.drop_table("navbar_items")
    op.drop_table("navbar_settings")
