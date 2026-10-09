"""Make the backend root importable when a script is run as a file."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
_backend_root = str(BACKEND_ROOT)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)
