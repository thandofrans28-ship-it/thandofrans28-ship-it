#!/usr/bin/env python3
"""SessionStart hook: make a fresh session ready, and say what day it is.

Claude Code runs this when a session starts (wired in .claude/settings.json).
Two jobs:

1. In a cloud session (CLAUDE_CODE_REMOTE=true) the container is fresh.
   Install pytest, because the first command in CLAUDE.md fails without it,
   and pin the session to SAST: the container clock is UTC, so after 22:00
   `life` would otherwise disagree with the calendar about what day it is.
2. Print a short orientation. A SessionStart hook's stdout is added to
   Claude's context, so every session starts knowing the date and how far
   away the next paper is, before anyone types a word.

It reads only public facts (seed/exams.json), never the personal store:
whatever this prints lands in a transcript. It always exits 0, because a
setup hiccup must never stop a session from starting.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = "Africa/Johannesburg"


def today() -> date:
    """Today in SAST, overridable with LIFE_TODAY=YYYY-MM-DD like `life`."""
    override = os.environ.get("LIFE_TODAY")
    if override:
        return date.fromisoformat(override)
    return datetime.now(ZoneInfo(TZ)).date()


def prepare_cloud() -> None:
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as fh:
            fh.write(f"export TZ={TZ}\n")
    if importlib.util.find_spec("pytest") is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pytest"],
                       capture_output=True, timeout=180, check=False)


def orientation(on: date) -> str:
    papers = json.loads((ROOT / "seed" / "exams.json").read_text(encoding="utf-8"))["papers"]
    left = sorted((p for p in papers if date.fromisoformat(p["date"]) >= on),
                  key=lambda p: p["date"])
    lines = [f"Today is {on:%A %d %B %Y} (SAST)."]
    if left:
        nxt = left[0]
        days = (date.fromisoformat(nxt["date"]) - on).days
        when = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"
        lines.append(
            f"Matric finals are running: next paper {nxt['paper']} {when} "
            f"({nxt['date']} {nxt.get('time', '')}). {len(left)} "
            f"paper{'s' if len(left) != 1 else ''} left; the last is on {left[-1]['date']}.")
        lines.append("Protect study time: finish small things completely, and park big "
                     "builds until after the last paper unless Thando insists.")
    return "\n".join(lines)


def main() -> int:
    try:
        prepare_cloud()
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        print(orientation(today()))
    except (OSError, ValueError, KeyError):
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
