"""Upload file helpers — safe permanent deletion when media is unreferenced."""

from pathlib import Path
from urllib.parse import urlparse

from flask import current_app, send_from_directory

from utils.content_registry import CONTENT_RESOURCES

UPLOAD_CACHE_CONTROL = "public, max-age=31536000, immutable"
# Skip Pillow work on already-small files (typical optimized uploads).
OPTIMIZE_ON_SERVE_MIN_BYTES = 400_000


def send_cached_upload(directory, filepath):
    """Serve a CMS upload with long-lived cache headers.

    UUID filenames are immutable. Large existing originals are compressed in
    place on first request so Vercel does not pull multi-megabyte files.
    """
    root = Path(directory)
    candidate = (root / filepath).resolve()
    try:
        if candidate.is_file() and str(candidate).startswith(str(root.resolve())):
            if candidate.stat().st_size >= OPTIMIZE_ON_SERVE_MIN_BYTES:
                from utils.image_optimize import optimize_upload_file

                optimize_upload_file(candidate)
    except OSError:
        pass

    response = send_from_directory(directory, filepath, max_age=31536000, conditional=True)
    response.headers["Cache-Control"] = UPLOAD_CACHE_CONTROL
    return response


def normalize_media_path(url):
    """Return a comparable path key for an uploaded media URL."""
    if not url or not isinstance(url, str):
        return None
    value = url.strip()
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).path or ""
    if not value.startswith("/"):
        value = f"/{value}"
    # Only manage files under /uploads/
    if "/uploads/" not in value and not value.startswith("/uploads"):
        return None
    return value


def media_is_referenced(url, exclude_model=None, exclude_id=None):
    """True if any content row (including trashed) still references this URL."""
    key = normalize_media_path(url)
    if not key:
        return True  # external / unknown — do not delete

    candidates = {key, key.lstrip("/"), url.strip()}
    for entry in CONTENT_RESOURCES:
        model = entry["model"]
        for field in entry["image_fields"]:
            column = getattr(model, field, None)
            if column is None:
                continue
            query = model.query.filter(column.in_(list(candidates)))
            if exclude_model is model and exclude_id is not None:
                query = query.filter(model.id != exclude_id)
            if query.first():
                return True
    return False


def delete_upload_file(url):
    """Delete a local upload file from disk if it exists under UPLOAD_FOLDER."""
    key = normalize_media_path(url)
    if not key:
        return False
    # key like /uploads/hero-banners/uuid.jpg
    relative = key.split("/uploads/", 1)[-1] if "/uploads/" in key else key.lstrip("/")
    root = Path(current_app.config.get("UPLOAD_FOLDER", Path(current_app.root_path) / "uploads"))
    path = (root / relative).resolve()
    try:
        if not str(path).startswith(str(root.resolve())):
            return False
        if path.is_file():
            path.unlink()
            return True
    except OSError:
        return False
    return False


def cleanup_item_media(item, image_fields, exclude_self=True):
    """Remove uploaded files for an item that are no longer referenced elsewhere."""
    deleted = []
    for field in image_fields:
        url = getattr(item, field, None)
        if not url:
            continue
        referenced = media_is_referenced(
            url,
            exclude_model=item.__class__ if exclude_self else None,
            exclude_id=item.id if exclude_self else None,
        )
        if not referenced and delete_upload_file(url):
            deleted.append(url)
    return deleted
