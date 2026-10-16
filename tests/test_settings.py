"""Pin the Claude Code wiring: hooks that guard a public repo must not drift."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _commands(event: str, tool: str | None = None) -> list[str]:
    out = []
    for entry in SETTINGS["hooks"].get(event, []):
        matcher = entry.get("matcher")
        if tool is not None and not (matcher and re.fullmatch(matcher, tool)):
            continue
        out += [h["command"] for h in entry["hooks"]]
    return out


def test_every_route_into_the_repo_runs_the_privacy_guard():
    for tool in ("Bash", "mcp__github__create_or_update_file", "mcp__github__push_files"):
        assert any("check_no_personal_data.py\" --hook" in c for c in _commands("PreToolUse", tool)), tool


def test_session_start_hook_points_at_a_real_script():
    (command,) = _commands("SessionStart")
    assert "scripts/session_start.py" in command
    assert (ROOT / "scripts" / "session_start.py").exists()


def test_sending_and_deleting_always_needs_a_human_tap():
    ask = set(SETTINGS["permissions"]["ask"])
    for tool in ("mcp__Gmail__send_message", "mcp__Gmail__reply", "mcp__Gmail__forward",
                 "mcp__Google_Drive__share_file"):
        assert tool in ask, tool
    assert not ask & set(SETTINGS["permissions"]["allow"])


def test_project_agents_have_the_required_frontmatter():
    for path in (ROOT / ".claude" / "agents").glob("*.md"):
        head = path.read_text(encoding="utf-8").split("---")[1]
        assert re.search(r"^name: \S+", head, re.M), path.name
        assert re.search(r"^description: .+", head, re.M), path.name
