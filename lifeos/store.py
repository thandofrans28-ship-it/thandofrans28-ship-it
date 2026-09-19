"""On-disk JSON store.

Personal data lives under LIFE_HOME (default ``~/.life``), never in the repo.
The repo is public; the store is not. ``seed/`` in the repo holds only facts
that are already public — the IEB exam timetable and the connector registry.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

_EMPTY: dict[str, Any] = {
    "schema": SCHEMA_VERSION,
    "profile": {},
    "marks": {},
    "exams": [],
    "deadlines": [],
    "applications": [],
    "open_loops": [],
    "projects": [],
    "documents": [],
    "synced_at": None,
}


def home() -> Path:
    """Directory holding the personal store. Override with ``LIFE_HOME``."""
    return Path(os.environ.get("LIFE_HOME", Path.home() / ".life")).expanduser()


def path() -> Path:
    return home() / "store.json"


def load() -> dict[str, Any]:
    """Read the store, returning an empty skeleton when it does not exist."""
    p = path()
    if not p.exists():
        return json.loads(json.dumps(_EMPTY))
    with p.open(encoding="utf-8") as fh:
        data = json.load(fh)
    # Forward-compatible: fill in keys added since the file was written.
    for key, default in _EMPTY.items():
        data.setdefault(key, json.loads(json.dumps(default)))
    return data


def save(data: dict[str, Any]) -> Path:
    """Write the store atomically, creating LIFE_HOME with private permissions."""
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p.parent, 0o700)
    except OSError:
        pass  # best effort; Windows and some mounts do not support it
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    tmp.replace(p)
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    return p
