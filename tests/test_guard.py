"""Tests for the personal-data guard.

The guard is the only thing standing between a public repo and Thando's ID
number, so it needs to fail loudly when it stops working. These tests drive
the module's `scan()` against a throwaway git repo rather than the real one.

Every identifier and every mark below is invented. This file is the single
allowlisted path, so nothing here is scanned — which is exactly why it must
never carry a real value. The patterns match on shape, not on any particular
number, so synthetic fixtures exercise them exactly as real ones would.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "scripts" / "check_no_personal_data.py"

spec = importlib.util.spec_from_file_location("guard", GUARD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

# Invented, never a real number. Shape only: 13 digits, which is all the
# pattern checks — there is no checksum, so coverage is identical.
FAKE_ID = "990101 5555 08 1"
FAKE_ID_COMPACT = "9901015555081"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A real git repo with one staged file, whose content the test sets."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)

    def stage(content: str, name: str = "notes.md") -> None:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", name], cwd=tmp_path, check=True)

    monkeypatch.chdir(tmp_path)
    return stage


@pytest.mark.parametrize("content,label", [
    (f"My ID is {FAKE_ID} okay", "SA ID number"),
    (f"ID {FAKE_ID_COMPACT} here", "SA ID number"),
    ("Reference 27FR92964T for UWC", "bursary/application reference"),
    ("Mathematics 52% this term", "subject mark"),
    ("Physical Sciences: 48%", "subject mark"),
    ("English is sitting at 59%", "reported mark"),
    ("I got 63% for Maths", "reported mark"),
    ("my average of 71% this term", "reported mark"),
    ("account 1234567890 for the bursary", "bank/account number"),
])
def test_guard_catches_personal_data(repo, content, label):
    repo(content)
    findings = guard.scan()
    assert any(label in f for f in findings), f"missed {label!r} in {content!r}"


@pytest.mark.parametrize("content", [
    "The CLI has 30 tests and runs in 0.10s",
    "Target FPS is 500 out of 600",
    "Version 1.2.3 released 2026-09-19",
    "Physical Sciences is the highest-leverage subject",   # no number attached
    "commit 990101a is the fix",                           # too short for an ID
    # Prose that names a subject near a percentage but reports no mark. These
    # are the false positives that would get the guard switched off.
    "Mathematics past papers are 40% of the run",
    "Physical Sciences P1 weighting is 21,6% of the paper",
    "electric circuits set at 21,6% against a 15% syllabus weighting",
    "Afrikaans Afdeling B is 60% format",
])
def test_guard_allows_ordinary_prose(repo, content):
    repo(content)
    assert guard.scan() == [], f"false positive on {content!r}"


def test_guard_flags_a_staged_store_file(repo):
    repo("{}", name="store.json")
    assert any("personal store file" in f for f in guard.scan())


def test_guard_scans_test_files_other_than_its_own(repo):
    """Only this file is exempt.

    The allowlist used to cover all of tests/, which is where realistic-looking
    fixtures naturally accumulate — and a real ID sat there unscanned as a
    result. Any other test file is ordinary scanned content.
    """
    repo(f"My ID is {FAKE_ID}", name="tests/test_x.py")
    assert any("SA ID number" in f for f in guard.scan())


def test_guard_still_exempts_this_file(repo):
    """test_guard.py itself must stay exempt, or its own fixtures trip it."""
    repo(f"My ID is {FAKE_ID}", name="tests/test_guard.py")
    assert guard.scan() == []


def test_guard_clean_on_empty_stage(repo):
    assert guard.scan() == []


def _run(args: list[str], stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), *args],
        input=stdin, capture_output=True, text=True,
    )


def test_hook_mode_blocks_git_commit(repo):
    repo(f"My ID is {FAKE_ID}")
    r = _run(["--hook"], '{"tool_input":{"command":"git commit -m wip"}}')
    assert r.returncode == 2
    assert "BLOCKED" in r.stderr


def test_hook_mode_ignores_other_commands(repo):
    repo(f"My ID is {FAKE_ID}")
    r = _run(["--hook"], '{"tool_input":{"command":"git status"}}')
    assert r.returncode == 0 and r.stderr == ""


def test_hook_mode_fails_open_on_junk(repo):
    """A malformed payload must not wedge every Bash call in the session."""
    r = _run(["--hook"], "this is not json")
    assert r.returncode == 0


def test_hook_mode_fails_open_on_empty_stdin(repo):
    r = _run(["--hook"], "")
    assert r.returncode == 0


def test_cli_mode_does_not_block_on_absent_stdin(repo):
    """Regression: deciding hook mode by isatty() hung forever here."""
    repo("nothing sensitive")
    r = subprocess.run([sys.executable, str(GUARD)], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=20)
    assert r.returncode == 0


def test_scan_all_reads_file_contents_not_just_the_diff(repo):
    """CI runs --all: a fresh checkout stages nothing, so a diff scan is blind."""
    repo(f"My ID is {FAKE_ID}")
    subprocess.run(["git", "commit", "-qm", "x"], check=True)
    assert guard.scan() == []                 # nothing staged any more
    assert guard.scan_tracked() != []         # but the file is still tracked


def test_scan_all_covers_tracked_files_while_something_is_staged(repo):
    """--all means all.

    scan_tracked() used to start `staged_paths() or tracked_paths()`, so once
    anything was staged it quietly stopped looking at everything else.
    """
    repo(f"My ID is {FAKE_ID}", name="committed.md")
    subprocess.run(["git", "commit", "-qm", "x"], check=True)
    repo("nothing sensitive", name="staged.md")   # staged, and clean
    assert any("committed.md" in f for f in guard.scan_tracked())


def test_scan_all_reports_line_numbers(repo):
    repo(f"clean line\nMy ID is {FAKE_ID}\n")
    subprocess.run(["git", "commit", "-qm", "x"], check=True)
    assert any(":2:" in f for f in guard.scan_tracked())


def test_scan_all_survives_binary_files(repo):
    repo("ok")
    (Path.cwd() / "blob.bin").write_bytes(b"\x00\xff\xfe binary \x00")
    subprocess.run(["git", "add", "blob.bin"], check=True)
    guard.scan_tracked()  # must not raise


# ── regressions found in code review of PR #2 ────────────────────────────────

@pytest.mark.parametrize("command", [
    "git commit -am wip",
    "git commit -a -m wip",
    "git commit --all -m wip",
    "git commit --amend --no-edit",
    "git commit notes.md -m wip",
    "git commit -- notes.md",
])
def test_hook_blocks_commits_that_reach_past_the_index(repo, command):
    """`git diff --cached` is blind to -a, --amend and an explicit pathspec,
    so an ID in a tracked-but-unstaged file used to sail through."""
    repo(f"My ID is {FAKE_ID}")
    subprocess.run(["git", "commit", "-qm", "seed"], check=True)
    Path("notes.md").write_text(f"My ID is {FAKE_ID}\nplus an edit\n")
    r = _run(["--hook"], '{"tool_input":{"command":"%s"}}' % command)
    assert r.returncode == 2, f"{command!r} bypassed the guard"


@pytest.mark.parametrize("command", [
    "git commit -m wip",
    "git commit -m 'a longer message here'",
    "git commit --message=hello",
    "git commit",
])
def test_hook_allows_plain_staged_only_commits(repo, command):
    """A commit message must not be mistaken for a pathspec — over-blocking is
    how a guard gets switched off."""
    repo("nothing sensitive")
    subprocess.run(["git", "commit", "-qm", "seed"], check=True)
    Path("notes.md").write_text(f"My ID is {FAKE_ID}\n")   # unstaged only
    r = _run(["--hook"], '{"tool_input":{"command":"%s"}}' % command)
    assert r.returncode == 0, f"{command!r} was blocked but stages nothing"


def test_scan_all_ignores_whatever_happens_to_be_staged(repo):
    """`staged_paths() or tracked_paths()` turned a repo-wide scan into a
    staged-only one as soon as any unrelated file was staged."""
    repo(f"My ID is {FAKE_ID}", name="dirty.md")
    subprocess.run(["git", "commit", "-qm", "seed"], check=True)
    Path("clean.md").write_text("nothing here")
    subprocess.run(["git", "add", "clean.md"], check=True)
    assert any("dirty.md" in f for f in guard.scan_tracked())
