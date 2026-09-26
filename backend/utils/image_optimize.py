"""Resize/compress CMS uploads in place. Does not change the public URL."""

from pathlib import Path

MAX_EDGE = 1920


def optimize_upload_file(path: Path) -> None:
    ext = path.suffix.lower().lstrip(".")
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        return

    try:
        from PIL import Image
    except ImportError:
        return

    try:
        with Image.open(path) as image:
            image.load()
            has_alpha = image.mode in {"RGBA", "LA", "P"}
            if ext in {"jpg", "jpeg"} and image.mode not in {"RGB", "L"}:
                image = image.convert("RGB")
            elif ext == "png" and image.mode == "P":
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")

            if max(image.size) > MAX_EDGE:
                image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)

            save_kwargs = {}
            if ext in {"jpg", "jpeg"}:
                save_kwargs = {
                    "format": "JPEG",
                    "quality": 82,
                    "optimize": True,
                    "progressive": True,
                }
            elif ext == "webp":
                save_kwargs = {"format": "WEBP", "quality": 82, "method": 4}
            else:
                save_kwargs = {"format": "PNG", "optimize": True}
                if has_alpha and image.mode != "RGBA":
                    image = image.convert("RGBA")

            image.save(path, **save_kwargs)
    except Exception:
        # Keep the original bytes if optimization fails.
        return
