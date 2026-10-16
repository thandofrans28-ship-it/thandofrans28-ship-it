"""Tests for the SessionStart hook. Dates are pinned; the timetable is public."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "scripts" / "session_start.py"

spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def test_names_the_next_paper_and_how_far_away_it_is():
    out = hook.orientation(date(2026, 10, 16))
    assert "Friday 16 October 2026" in out
    assert "FSM P1 (Standard) in 3 days" in out
    assert "13 papers left; the last is on 2026-11-19" in out


def test_says_today_and_tomorrow_in_words():
    assert "in 1 days" not in hook.orientation(date(2026, 10, 18))
    assert "tomorrow" in hook.orientation(date(2026, 10, 18))
    assert "Mathematics P1 today" in hook.orientation(date(2026, 10, 26))


def test_counts_a_single_remaining_paper_in_the_singular():
    assert "1 paper left" in hook.orientation(date(2026, 11, 19))


def test_says_nothing_about_exams_once_they_are_over():
    out = hook.orientation(date(2026, 11, 20))
    assert out == "Today is Friday 20 November 2026 (SAST)."


def test_cloud_session_pins_the_timezone(tmp_path, monkeypatch):
    env_file = tmp_path / "env"
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
    monkeypatch.setattr(hook.importlib.util, "find_spec", lambda name: object())  # pytest present
    hook.prepare_cloud()
    assert env_file.read_text() == "export TZ=Africa/Johannesburg\n"


def test_local_session_changes_nothing(tmp_path, monkeypatch):
    env_file = tmp_path / "env"
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
    hook.prepare_cloud()
    assert not env_file.exists()


def test_hook_exits_zero_and_prints_the_date():
    r = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                       env={"LIFE_TODAY": "2026-10-16", "PATH": "/usr/bin:/bin"}, timeout=30)
    assert r.returncode == 0
    assert r.stdout.startswith("Today is Friday 16 October 2026")


def test_hook_survives_a_bad_date_override():
    r = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                       env={"LIFE_TODAY": "not-a-date", "PATH": "/usr/bin:/bin"}, timeout=30)
    assert r.returncode == 0
