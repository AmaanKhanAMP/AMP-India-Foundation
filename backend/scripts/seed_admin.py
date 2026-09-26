"""Create the default CMS admin user.

Usage (from backend/ with venv active):
  python scripts/seed_admin.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.cms_models import AdminUser
from utils.auth import hash_password


def main():
    app = create_app()
    with app.app_context():
        email = os.getenv("ADMIN_EMAIL", "admin@ampindiafoundation.org").strip().lower()
        password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
        name = os.getenv("ADMIN_NAME", "AIF Admin")

        existing = AdminUser.query.filter_by(email=email).first()
        if existing:
            print(f"Admin already exists: {email}")
            return

        admin = AdminUser(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin: {email}")
        print("Change the password after first login.")


if __name__ == "__main__":
    main()
