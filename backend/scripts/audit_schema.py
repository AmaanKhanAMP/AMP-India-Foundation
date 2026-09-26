"""Compare SQLAlchemy models to the live MySQL schema.

Usage (from backend/ with venv):
  python scripts/audit_schema.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.cms_models import (
    FeaturedEvent,
    FooterFocusItem,
    FooterLink,
    FooterSettings,
    HeroBanner,
    HomeEvent,
    HomeGalleryItem,
    HomeProject,
    NavbarItem,
    NavbarSettings,
    PastEvent,
    SectionVisibility,
    Testimonial,
    UpcomingEvent,
)
from sqlalchemy import inspect, text

MODELS = [
    HeroBanner,
    HomeProject,
    HomeGalleryItem,
    HomeEvent,
    Testimonial,
    FeaturedEvent,
    UpcomingEvent,
    PastEvent,
    NavbarItem,
    NavbarSettings,
    FooterSettings,
    FooterLink,
    FooterFocusItem,
    SectionVisibility,
]


def main() -> int:
    app = create_app()
    mismatches = 0
    with app.app_context():
        insp = inspect(db.engine)
        version = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print(f"alembic_version: {version}\n")

        for model in MODELS:
            table = model.__tablename__
            if not insp.has_table(table):
                print(f"MISSING TABLE  {table}")
                mismatches += 1
                continue

            db_cols = {c["name"] for c in insp.get_columns(table)}
            model_cols = {c.name for c in model.__table__.columns}
            missing_in_db = sorted(model_cols - db_cols)
            extra_in_db = sorted(db_cols - model_cols)

            if missing_in_db or extra_in_db:
                mismatches += 1
                print(f"MISMATCH  {table}")
                if missing_in_db:
                    print(f"  model→DB missing: {missing_in_db}")
                if extra_in_db:
                    print(f"  DB→model extra:   {extra_in_db}")
            else:
                print(f"OK        {table}")

    print()
    if mismatches:
        print(f"FAILED: {mismatches} mismatch(es)")
        return 1
    print("PASSED: models match database schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
