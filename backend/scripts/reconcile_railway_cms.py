"""Compare local MySQL CMS tables to production (Railway via Render API) and optionally clean.

Local DB (backend/.env) is the source of truth.
Production is the live API at NEXT_PUBLIC_API_URL / default Render backend.

Usage (from backend/):
  python scripts/reconcile_railway_cms.py           # report only
  python scripts/reconcile_railway_cms.py --apply   # delete extras on production
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pymysql
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

PROD_API = os.getenv("PROD_API_URL", "https://aif-backend-6jwe.onrender.com").rstrip("/")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# Railway public MySQL proxy (MySQL Workbench connection "Railway")
RAILWAY_HOST = os.getenv("RAILWAY_DB_HOST", "tokaido.proxy.rlwy.net")
RAILWAY_PORT = int(os.getenv("RAILWAY_DB_PORT", "36711"))
RAILWAY_USER = os.getenv("RAILWAY_DB_USER", "root")
RAILWAY_NAME = os.getenv("RAILWAY_DB_NAME", "railway")
RAILWAY_PASSWORD = os.getenv("RAILWAY_DB_PASSWORD") or os.getenv("DB_PASSWORD", "")

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

# admin API resource slug for row-based CMS modules (not singletons)
RESOURCE = {
    "hero_banners": "hero-banners",
    "home_projects": "home-projects",
    "home_gallery_items": "home-gallery",
    "testimonials": "testimonials",
    "featured_events": "featured-events",
    "upcoming_events": "upcoming-events",
    "gallery_items": "past-events",
    "navbar_items": "navbar-items",
    "footer_links": "footer-links",
}

UNSPLASH_RE = re.compile(r"unsplash\.com|images\.unsplash", re.I)
DUMMY_RE = re.compile(
    r"\b(lorem|ipsum|dummy|placeholder|demo slide|sample event|test banner)\b",
    re.I,
)


def jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def connect_local():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "aif_cms"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def connect_railway():
    kwargs = dict(
        host=RAILWAY_HOST,
        port=RAILWAY_PORT,
        user=RAILWAY_USER,
        password=RAILWAY_PASSWORD,
        database=RAILWAY_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=20,
    )
    try:
        return pymysql.connect(**kwargs, ssl={"ssl": {}})
    except Exception:
        return pymysql.connect(**kwargs)


def fetch_table(conn, table: str) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM `{table}`")
        rows = cur.fetchall() or []
    return [{k: jsonable(v) for k, v in row.items()} for row in rows]


def image_of(row: dict) -> str:
    for key in ("image_url", "banner_image", "profile_image", "logo_url"):
        val = row.get(key)
        if val:
            return str(val)
    return ""


def title_of(row: dict) -> str:
    for key in ("title", "name", "label", "logo_alt", "cta_heading"):
        val = row.get(key)
        if val:
            return str(val)
    return f"id={row.get('id')}"


def fingerprint(table: str, row: dict) -> str:
    img = image_of(row).strip().lower()
    title = title_of(row).strip().lower()
    extra = str(
        row.get("href")
        or row.get("event_date")
        or row.get("parent_key")
        or row.get("phone_text")
        or ""
    ).strip().lower()
    if table in {"navbar_settings", "footer_settings"}:
        return f"{table}|singleton|{img}|{title}|{extra}"
    return f"{table}|{title}|{img}|{extra}"


def is_dummy(row: dict) -> bool:
    blob = " ".join(
        str(row.get(k) or "")
        for k in (
            "title",
            "name",
            "label",
            "subtitle",
            "description",
            "message",
            "image_url",
            "banner_image",
            "profile_image",
        )
    )
    return bool(UNSPLASH_RE.search(blob) or DUMMY_RE.search(blob))


def login_prod() -> str:
    res = requests.post(
        f"{PROD_API}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=60,
    )
    res.raise_for_status()
    data = res.json()
    if not data.get("success") or not data.get("token"):
        raise RuntimeError(data.get("message") or "Production admin login failed")
    return data["token"]


def prod_get(token: str, path: str) -> Any:
    res = requests.get(
        f"{PROD_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=90,
    )
    res.raise_for_status()
    return res.json()


def prod_delete(token: str, path: str) -> dict:
    res = requests.delete(
        f"{PROD_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=90,
    )
    try:
        return res.json()
    except Exception:
        return {"success": res.ok, "status": res.status_code, "text": res.text[:240]}


def fetch_production(token: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {t: [] for t in TABLES}

    for table, slug in RESOURCE.items():
        payload = prod_get(token, f"/api/admin/content/{slug}")
        out[table] = payload.get("data") or []

    nav = prod_get(token, "/api/admin/layout/navbar")
    footer = prod_get(token, "/api/admin/layout/footer")
    nav_data = nav.get("data") or nav
    footer_data = footer.get("data") or footer
    if isinstance(nav_data, dict) and nav_data.get("id") is not None:
        out["navbar_settings"] = [nav_data]
    if isinstance(footer_data, dict) and footer_data.get("id") is not None:
        settings = {k: v for k, v in footer_data.items() if k not in {"useful_links", "recent_focus"}}
        out["footer_settings"] = [settings]
        if footer_data.get("useful_links") and not out["footer_links"]:
            out["footer_links"] = footer_data["useful_links"]

    trash = prod_get(token, "/api/admin/content/trash")
    out["_trash"] = trash.get("data") or []
    return out


def summarize_row(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "title": title_of(row),
        "image": image_of(row) or None,
        "status": row.get("status"),
        "is_deleted": row.get("is_deleted"),
        "display_order": row.get("display_order"),
        "href": row.get("href"),
        "event_date": row.get("event_date"),
    }


def analyze(local: dict[str, list[dict]], prod: dict[str, list[dict]]) -> dict:
    report = {"tables": {}, "totals": {}}
    total_remove = 0
    total_keep = 0
    total_dup = 0

    trash = prod.get("_trash") or []
    trash_by_table: dict[str, list[dict]] = defaultdict(list)
    slug_to_table = {v: k for k, v in RESOURCE.items()}
    slug_to_table["gallery-items"] = "gallery_items"
    for item in trash:
        table = slug_to_table.get(item.get("resource") or item.get("module") or "", "")
        if table:
            trash_by_table[table].append(item)

    for table in TABLES:
        local_rows = local.get(table) or []
        prod_rows = prod.get(table) or []
        local_alive = [r for r in local_rows if not r.get("is_deleted")]
        local_fps = {fingerprint(table, r) for r in local_alive}

        seen_fp: dict[str, list[dict]] = defaultdict(list)
        for r in prod_rows:
            seen_fp[fingerprint(table, r)].append(r)

        duplicates = []
        for fp, group in seen_fp.items():
            if len(group) > 1:
                duplicates.append(
                    {
                        "fingerprint": fp,
                        "ids": [g.get("id") for g in group],
                        "rows": [summarize_row(g) for g in group],
                    }
                )

        to_remove = []
        to_keep = []
        dummy = []
        unsplash = []
        not_in_local = []

        # For each fingerprint, keep one matching local; extras are duplicates.
        kept_fp: set[str] = set()
        for row in sorted(prod_rows, key=lambda r: (r.get("display_order") or 0, r.get("id") or 0)):
            fp = fingerprint(table, row)
            img = image_of(row)
            dummy_hit = is_dummy(row)
            unsplash_hit = bool(UNSPLASH_RE.search(img))
            in_local = fp in local_fps
            already = fp in kept_fp

            reason = None
            if dummy_hit:
                dummy.append(summarize_row(row))
                reason = "dummy_or_demo"
            elif unsplash_hit:
                unsplash.append(summarize_row(row))
                reason = "unsplash_or_stock"
            elif not in_local:
                not_in_local.append(summarize_row(row))
                reason = "not_in_local_source_of_truth"
            elif already:
                reason = "duplicate_of_finalized_row"
            else:
                kept_fp.add(fp)
                to_keep.append(summarize_row(row))
                continue

            to_remove.append({**summarize_row(row), "reason": reason})

        trash_rows = [
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "resource": t.get("resource") or t.get("module"),
                "deleted_at": t.get("deleted_at"),
            }
            for t in trash_by_table.get(table, [])
        ]

        report["tables"][table] = {
            "local_count": len(local_alive),
            "local_including_deleted": len(local_rows),
            "production_alive_count": len(prod_rows),
            "production_trash_count": len(trash_rows),
            "duplicates_found": duplicates,
            "dummy_demo": dummy,
            "unsplash_stock": unsplash,
            "not_in_local": not_in_local,
            "old_or_extra_to_remove": to_remove,
            "trash_to_purge": trash_rows,
            "final_records_that_will_remain": to_keep,
        }
        total_remove += len(to_remove) + len(trash_rows)
        total_keep += len(to_keep)
        total_dup += len(duplicates)

    report["totals"] = {
        "rows_to_remove_alive": sum(len(v["old_or_extra_to_remove"]) for v in report["tables"].values()),
        "trash_to_purge": sum(len(v["trash_to_purge"]) for v in report["tables"].values()),
        "duplicates_groups": total_dup,
        "final_alive_rows_after_cleanup": total_keep,
        "local_alive_rows": sum(len([r for r in (local.get(t) or []) if not r.get("is_deleted")]) for t in TABLES),
    }
    return report


def sql_prod_bundle(conn) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    trash = []
    for table in TABLES:
        rows = fetch_table(conn, table)
        alive = []
        for row in rows:
            if row.get("is_deleted"):
                trash.append(
                    {
                        "id": row.get("id"),
                        "title": title_of(row),
                        "resource": RESOURCE.get(table, table),
                        "module": RESOURCE.get(table, table),
                        "deleted_at": row.get("deleted_at"),
                        "_table": table,
                    }
                )
            else:
                alive.append(row)
        out[table] = alive
    out["_trash"] = trash
    return out


def apply_sql_cleanup(conn, report: dict) -> dict:
    actions = []
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        for table in TABLES:
            info = report["tables"][table]
            ids = [row["id"] for row in info["old_or_extra_to_remove"] if row.get("id") is not None]
            ids += [row["id"] for row in info["trash_to_purge"] if row.get("id") is not None]
            ids = sorted(set(ids))
            if not ids:
                continue
            placeholders = ",".join(["%s"] * len(ids))
            cur.execute(f"DELETE FROM `{table}` WHERE id IN ({placeholders})", ids)
            actions.append({"table": table, "deleted_ids": ids, "rowcount": cur.rowcount})
        cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
    return {"actions": actions}


def verify_sql(local: dict[str, list[dict]], conn) -> list[dict]:
    prod = sql_prod_bundle(conn)
    rows = []
    for table in TABLES:
        local_alive = [r for r in (local.get(table) or []) if not r.get("is_deleted")]
        prod_alive = prod.get(table) or []
        local_fps = sorted(fingerprint(table, r) for r in local_alive)
        prod_fps = sorted(fingerprint(table, r) for r in prod_alive)
        rows.append(
            {
                "table": table,
                "local_count": len(local_alive),
                "production_count": len(prod_alive),
                "counts_match": len(local_alive) == len(prod_alive),
                "fingerprints_match": local_fps == prod_fps,
                "production_trash": len([t for t in (prod.get("_trash") or []) if t.get("_table") == table]),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Permanently remove extra production rows")
    args = parser.parse_args()

    print("Connecting to local MySQL (source of truth)...")
    local_conn = connect_local()
    local = {table: fetch_table(local_conn, table) for table in TABLES}
    local_conn.close()

    print(f"Connecting to Railway MySQL at {RAILWAY_HOST}:{RAILWAY_PORT}/{RAILWAY_NAME} ...")
    try:
        rail_conn = connect_railway()
    except Exception as exc:
        print(f"Railway SQL connection failed: {type(exc).__name__}: {exc}")
        raise

    prod = sql_prod_bundle(rail_conn)
    report = analyze(local, prod)
    _print_report(report)

    if not args.apply:
        print("\nDry run only. Re-run with --apply to delete extras on Railway.")
        rail_conn.close()
        return 0

    print("\nApplying SQL cleanup on Railway...")
    result = apply_sql_cleanup(rail_conn, report)
    print(json.dumps(result, indent=2))
    verification = verify_sql(local, rail_conn)
    print("\n===== POST-CLEANUP VERIFICATION =====")
    print(json.dumps(verification, indent=2, ensure_ascii=False))
    (ROOT / "scripts" / "_cms_reconcile_verify.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    rail_conn.close()
    return 0 if all(v["counts_match"] and v["production_trash"] == 0 for v in verification) else 1


def _print_report(report: dict) -> None:
    out_path = ROOT / "scripts" / "_cms_reconcile_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote report: {out_path}")
    print("\n===== PRE-CLEANUP REPORT =====")
    for table, info in report["tables"].items():
        print(
            f"\n[{table}] local={info['local_count']} "
            f"prod_alive={info['production_alive_count']} "
            f"trash={info['production_trash_count']} "
            f"remove={len(info['old_or_extra_to_remove'])} "
            f"dup_groups={len(info['duplicates_found'])} "
            f"keep={len(info['final_records_that_will_remain'])}"
        )
        for row in info["old_or_extra_to_remove"]:
            print(f"  REMOVE id={row['id']} {row.get('reason')}: {row.get('title')}")
        for row in info["trash_to_purge"]:
            print(f"  PURGE TRASH id={row['id']}: {row.get('title')}")
        for row in info["final_records_that_will_remain"]:
            print(f"  KEEP id={row['id']}: {row.get('title')}")
    print("\nTOTALS:", json.dumps(report["totals"], indent=2))


if __name__ == "__main__":
    sys.exit(main())
