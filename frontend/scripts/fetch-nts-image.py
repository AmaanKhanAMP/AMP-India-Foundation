import re
import urllib.parse
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parents[1] / "src" / "assets" / "past-events" / "nts-2024.jpg"
PAGES = [
    "https://www.ampindia.org/latest-happenings/AMP-NTS-Results-2024",
    "https://ampindia.org/latest-happenings/AMP-NTS-Results-2024",
    "https://ampindia.org/latest-happenings/AMP-Launches-5th-National-Talent-Search-2024",
]
PAT = re.compile(r"""(?:src|content)=["']([^"']+\.(?:jpg|jpeg|png|webp))["']""", re.I)
SKIP = re.compile(r"logo|thumb65|boy\.png|favicon|icon|sprite", re.I)


def absolutize(src: str) -> str:
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return "https://ampindia.org" + src
    return src


def encode(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, urllib.parse.quote(parts.path, safe="/"), parts.query, parts.fragment)
    )


for page in PAGES:
    print("PAGE", page)
    try:
        req = urllib.request.Request(page, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    except Exception as exc:
        print("  ERR", exc)
        continue
    cands = []
    for m in PAT.findall(html):
        src = absolutize(m)
        if SKIP.search(src):
            continue
        if src not in cands:
            cands.append(src)
    for c in cands:
        print(" ", c)
    pick = None
    for c in cands:
        if "HappeningBanner" in c:
            pick = c.replace("/thumb703x250/", "/")
            break
    if not pick and cands:
        pick = cands[0]
    if not pick:
        continue
    data = urllib.request.urlopen(
        urllib.request.Request(encode(pick), headers={"User-Agent": "Mozilla/5.0"}),
        timeout=45,
    ).read()
    DEST.write_bytes(data)
    print("SAVED", DEST, len(data), "from", pick)
    break
else:
    raise SystemExit("No NTS image found")
