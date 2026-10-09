"""Put the backend root on sys.path when pylint is checking backend files only."""

import sys
from pathlib import Path

cwd = Path.cwd()
backend = None
for item in (cwd, *cwd.parents):
    if (item / "app.py").is_file() and (item / "models").is_dir():
        backend = item
        break
    nested = item / "backend"
    if (nested / "app.py").is_file() and (nested / "models").is_dir() and (item / "chatbot").is_dir():
        backend = nested
        break

targets = []
for arg in sys.argv[1:]:
    if arg.startswith("-"):
        continue
    path = Path(arg)
    if not path.is_absolute():
        path = cwd / path
    if path.suffix.lower() == ".py" or path.is_dir():
        targets.append(path)

applicable = False
if backend is not None:
    root = backend.resolve()
    if targets:
        applicable = True
        for path in targets:
            try:
                path.resolve().relative_to(root)
            except (ValueError, OSError):
                applicable = False
                break
    else:
        try:
            cwd.resolve().relative_to(root)
            applicable = True
        except (ValueError, OSError):
            applicable = False

if applicable:
    entry = str(backend.resolve())
    if entry not in sys.path:
        sys.path.insert(0, entry)
