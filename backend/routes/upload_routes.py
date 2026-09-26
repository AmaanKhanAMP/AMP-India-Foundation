"""File upload endpoint for CMS media."""

import os
import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from utils.auth import admin_required
from utils.image_optimize import optimize_upload_file
from utils.uploads import send_cached_upload

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_dir() -> Path:
    base = Path(current_app.root_path) / "uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base


@upload_bp.post("")
@admin_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file provided."}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"success": False, "message": "Empty filename."}), 400
    if not _allowed(file.filename):
        return jsonify({"success": False, "message": "File type not allowed."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    folder = request.form.get("folder", "general")
    dest_dir = _upload_dir() / secure_filename(folder)
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / name
    file.save(path)
    optimize_upload_file(path)

    url = f"/uploads/{secure_filename(folder)}/{name}"
    return jsonify({"success": True, "url": url, "filename": name}), 201


@upload_bp.get("/<path:filepath>")
def serve_upload(filepath):
    # Served via app route registered separately; kept for blueprint completeness
    return send_cached_upload(_upload_dir(), filepath)
