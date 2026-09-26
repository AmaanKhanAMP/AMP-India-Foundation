"""Download one relevant photo from each AMP past-event article."""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parents[1] / "src" / "assets" / "past-events"
DEST.mkdir(parents=True, exist_ok=True)

ARTICLES = [
    {
        "file": "srinagar-job-fair.jpg",
        "url": "https://ampindia.org/latest-happenings/AMP's-2nd-Srinagar,-Kashmir-Job-Fair",
    },
    {
        "file": "kolkata-job-fair.jpg",
        "url": "https://ampindia.org/latest-happenings/288-Candidates-Shortlisted-at-AMP-Kolkata-Job-Fair",
    },
    {
        "file": "doddaballapur-job-fair.jpg",
        "url": "https://ampindia.org/latest-happenings/AMP-Mega-Job-Fair-in-Doddaballapur",
    },
    {
        "file": "nanded-job-fair.jpg",
        "url": "https://ampindia.org/latest-happenings/AMP-Mega-Job-Fair-in-Nanded",
    },
    {
        "file": "nts-2024.jpg",
        "url": "https://ampindia.org/latest-happenings/AMP-organises-massive-Talent-Search-Exam",
        "fallbacks": [
            "https://www.ampindia.org/latest-happenings/AMP-organises-massive-Talent-Search-Exam",
            "https://ampindia.org/latest-happenings/AMP-Launches-5th-National-Talent-Search-2024",
        ],
    },
    {
        "file": "mumbai-unity-job-fair-2024.jpg",
        "url": "https://ampindia.org/latest-happenings/AMP-Unity-Job-Fair-at-Mumbai-2024",
    },
]

IMG_ATTR = re.compile(
    r"""(?:src|content|data-src)=["']([^"']+\.(?:jpg|jpeg|png|webp))(?:\?[^"']*)?["']""",
    re.I,
)
SKIP = re.compile(r"logo|thumb65|boy\.png|favicon|icon|avatar|sprite", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as res:
        return res.read().decode("utf-8", "ignore")


def absolutize(src: str, base: str = "https://ampindia.org") -> str:
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return base + src
    return src


def pick_image(html: str) -> str | None:
    candidates: list[str] = []
    for match in IMG_ATTR.findall(html):
        src = absolutize(match)
        if SKIP.search(src):
            continue
        if src not in candidates:
            candidates.append(src)

    # Prefer full HappeningBanner / Storyimg photos over tiny thumbs
    preferred = [
        c
        for c in candidates
        if "HappeningBanner" in c or "Storyimg" in c or "uploads" in c.lower()
    ]
    # Prefer non-thumb703 if a larger path exists; else use banner
    for c in preferred:
        if "thumb703" not in c and "thumb" not in c.lower():
            return c
    if preferred:
        # Try upgrading thumb703x250 -> full path guess
        banner = preferred[0]
        upgraded = banner.replace("/thumb703x250/", "/").replace("/thumb/", "/")
        return upgraded if upgraded != banner else banner
    return candidates[0] if candidates else None


def encode_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def download(url: str, dest: Path) -> None:
    # Try upgraded path first, then original
    urls = [url]
    if "/thumb703x250/" in url:
        urls.insert(0, url.replace("/thumb703x250/", "/"))
    if "/thumb/" in url:
        urls.insert(0, url.replace("/thumb/", "/"))

    last_err: Exception | None = None
    for u in urls:
        try:
            encoded = encode_url(u)
            req = urllib.request.Request(encoded, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as res:
                data = res.read()
            if len(data) < 2000:
                raise ValueError(f"too small: {len(data)} bytes from {encoded}")
            # Keep requested extension; content may be jpeg even if .jpg
            dest.write_bytes(data)
            print(f"OK {dest.name} <- {encoded} ({len(data)} bytes)")
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    raise RuntimeError(f"failed to download {url}: {last_err}")


def main() -> None:
    for article in ARTICLES:
        pages = [article["url"], *article.get("fallbacks", [])]
        image_url = None
        for page in pages:
            try:
                html = fetch(page)
                image_url = pick_image(html)
                print(f"PAGE {article['file']}: {page}")
                print(f"  picked: {image_url}")
                if image_url:
                    break
            except Exception as exc:  # noqa: BLE001
                print(f"PAGE ERR {page}: {exc}")
        if not image_url:
            raise SystemExit(f"No image for {article['file']}")
        download(image_url, DEST / article["file"])


if __name__ == "__main__":
    main()
