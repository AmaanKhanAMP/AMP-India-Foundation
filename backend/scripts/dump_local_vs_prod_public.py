"""Dump local CMS tables and compare against published production API."""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pymysql
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

PROD = os.getenv("PROD_API_URL", "https://aif-backend-6jwe.onrender.com").rstrip("/")

TABLES = [
    "hero_banners",
    "home_projects",
    "home_gallery_items",
    "testimonials",
    "featured_events",
    "upcoming_events",
    "gallery_items",
    "navbar_settings",
    "navbar_items",
    "footer_settings",
    "footer_links",
]

PUBLIC = {
    "hero_banners": "/api/content/hero-banners",
    "home_projects": "/api/content/home-projects",
    "home_gallery_items": "/api/content/home-gallery",
    "testimonials": "/api/content/testimonials",
    "featured_events": "/api/content/featured-events",
    "upcoming_events": "/api/content/upcoming-events",
    "gallery_items": "/api/content/past-events",
    "navbar_items": "/api/content/navbar-items",
    "footer_links": "/api/content/footer-links",
}


def jsonable(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return v


def title_of(row):
    for k in ("title", "name", "label", "logo_alt", "cta_heading"):
        if row.get(k):
            return str(row[k])
    return f"id={row.get('id')}"


def image_of(row):
    for k in ("image_url", "banner_image", "profile_image", "logo_url"):
        if row.get(k):
            return str(row[k])
    return ""


def fp(table, row):
    return "|".join(
        [
            table,
            title_of(row).strip().lower(),
            image_of(row).strip().lower(),
            str(row.get("href") or row.get("event_date") or row.get("parent_key") or "").strip().lower(),
        ]
    )


def main():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "aif_cms"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    local = {}
    with conn.cursor() as cur:
        for table in TABLES:
            cur.execute(f"SELECT * FROM `{table}`")
            local[table] = [{k: jsonable(v) for k, v in r.items()} for r in (cur.fetchall() or [])]
    conn.close()

    session = requests.Session()
    public = {}
    for table, path in PUBLIC.items():
        try:
            res = session.get(f"{PROD}{path}", timeout=90)
            res.raise_for_status()
            public[table] = (res.json().get("data") or [])
        except Exception as exc:
            public[table] = {"_error": type(exc).__name__}

    try:
        nav = session.get(f"{PROD}/api/layout/navbar", timeout=90).json()
        public["navbar_settings"] = [nav.get("data") or nav]
    except Exception as exc:
        public["navbar_settings"] = {"_error": type(exc).__name__}
    try:
        foot = session.get(f"{PROD}/api/layout/footer", timeout=90).json()
        data = foot.get("data") or foot
        public["footer_settings"] = [data] if isinstance(data, dict) else data
    except Exception as exc:
        public["footer_settings"] = {"_error": type(exc).__name__}

    report = {"local": {}, "production_published": {}, "notes": []}
    for table in TABLES:
        lrows = local[table]
        lalive = [r for r in lrows if not r.get("is_deleted")]
        ldeleted = [r for r in lrows if r.get("is_deleted")]
        unsplash = [
            r
            for r in lrows
            if re.search(r"unsplash", image_of(r), re.I)
        ]
        report["local"][table] = {
            "total": len(lrows),
            "alive": len(lalive),
            "deleted": len(ldeleted),
            "unsplash": len(unsplash),
            "alive_rows": [
                {
                    "id": r.get("id"),
                    "title": title_of(r),
                    "image": image_of(r),
                    "status": r.get("status"),
                    "href": r.get("href"),
                    "event_date": r.get("event_date"),
                    "display_order": r.get("display_order"),
                }
                for r in lalive
            ],
            "deleted_rows": [
                {"id": r.get("id"), "title": title_of(r), "image": image_of(r)}
                for r in ldeleted
            ],
        }
        prows = public.get(table) or []
        if isinstance(prows, dict) and prows.get("_error"):
            report["production_published"][table] = {"error": prows["_error"]}
            continue
        if table == "footer_settings" and prows and isinstance(prows[0], dict) and "useful_links" in prows[0]:
            # layout payload is a bundle; count 1 settings row
            report["production_published"][table] = {
                "count": 1,
                "ids": [prows[0].get("id")],
                "titles": [prows[0].get("cta_heading")],
            }
            continue
        report["production_published"][table] = {
            "count": len(prows),
            "ids": [r.get("id") for r in prows],
            "titles": [title_of(r) for r in prows],
            "images": [image_of(r) for r in prows],
        }
        local_fps = {fp(table, r) for r in lalive}
        extra = [r for r in prows if fp(table, r) not in local_fps]
        missing = []
        prod_fps = {fp(table, r) for r in prows}
        for r in lalive:
            if fp(table, r) not in prod_fps:
                missing.append(title_of(r))
        report["production_published"][table]["not_in_local"] = [title_of(r) for r in extra]
        report["production_published"][table]["missing_from_production_published"] = missing
        ids = [r.get("id") for r in prows if r.get("id") is not None]
        if ids and (max(ids) > len(ids) or min(ids) > 1):
            report["notes"].append(
                f"{table}: published ids={ids} (max={max(ids)}, count={len(ids)}) "
                "— gaps usually mean old/dummy rows still exist as draft or trash."
            )

    out = ROOT / "scripts" / "_cms_local_vs_prod_public.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
