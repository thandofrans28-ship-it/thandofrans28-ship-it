#!/usr/bin/env python3
"""Block personal data from reaching this public repo.

The repo is thandofrans28-ship-it/thandofrans28-ship-it — the PUBLIC profile
repo. Marks, ID numbers and bursary application references must never be
committed here. `docs/LIFE_OS.md` says so, but prose is advisory; this is not.

Run standalone to scan the staged diff:
    python3 scripts/check_no_personal_data.py

Scan every tracked file instead (what CI does):
    python3 scripts/check_no_personal_data.py --all

The Claude Code PreToolUse hook in .claude/settings.json passes --hook, which
reads the tool call from stdin and only acts on `git commit`. That flag is
explicit on purpose: deciding by isatty() blocks forever in any non-TTY caller
that pipes nothing, which is most of them.

Note what this does NOT cover: it is a Claude Code hook, not a git hook, so a
commit made by hand in a terminal bypasses it, as does any write that goes
straight to the GitHub API. CI's --all scan is the backstop, and on a public
repo a post-push scan is detection rather than prevention.
"""

from __future__ import annotations

import json
import pathlib
import shlex
import re
import subprocess
import sys

# Each rule: (label, compiled pattern). Kept deliberately narrow — a noisy
# guard gets disabled, and a disabled guard protects nothing.
RULES: list[tuple[str, re.Pattern[str]]] = [
    # The first six digits are YYMMDD, so validating the month and day costs
    # nothing and removes the one false positive that showed up in practice:
    # a JavaScript epoch-millisecond timestamp is also 13 digits.
    ("SA ID number", re.compile(
        r"\b\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\s?\d{4}\s?\d{2}\s?\d\b")),
    ("bursary/application reference", re.compile(r"\b\d{2}[A-Z]{2}\d{5,}[A-Z]?\b")),
    # Two narrow rules beat one wide one. A subject sitting right next to a
    # percentage is a mark; a subject in the same sentence as any percentage is
    # usually prose ("Maths past papers are 40% of the run"). The second rule
    # catches the phrasing the first is too tight for ("English ... at 66%").
    ("subject mark", re.compile(
        r"\b(English|Mathematics|Maths|Physical Sciences|PhysSci|Life Sciences|"
        r"Afrikaans|Information Technology|Life Orientation)\b[\s:=-]{0,4}\b([4-9]\d)\s?%")),
    ("reported mark", re.compile(
        r"\b(got|scored|achieved|sitting at|currently at|mark(?:ed)?(?: of)?|"
        r"result(?: of)?|average(?: of)?)\b\D{0,10}?\b([4-9]\d)\s?%", re.I)),
    ("personal store file", re.compile(r"(^|/)store\.json\b")),
    ("bank/account number", re.compile(r"\b(?:acc(?:ount)?|iban)\W{0,3}\d{8,}\b", re.I)),
]

# Paths where a match is expected and harmless. Deliberately two files, not two
# directories: tests/ is exactly where realistic-looking fixtures accumulate, so
# exempting all of it left the one place a real value could sit unscanned.
# tests/test_guard.py is exempt because its fixtures must match these patterns
# by design; every other test file is ordinary scanned content.
ALLOWLIST = re.compile(r"^(tests/test_guard\.py$|scripts/check_no_personal_data\.py$)")


def staged_diff() -> str:
    return subprocess.run(
        ["git", "diff", "--cached", "--unified=0"],
        capture_output=True, text=True, check=False,
    ).stdout


def staged_paths() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    ).stdout
    return [p for p in out.splitlines() if p]


def scan_tracked() -> list[str]:
    """Scan every tracked file's full contents, not just the staged diff.

    CI uses this: a fresh checkout has nothing staged, so a diff-based scan
    there would pass trivially and prove nothing.

    `git ls-files` reads the index, so staged-but-uncommitted files are
    included too — which is why this does not consult staged_paths() first.
    Doing so narrowed --all to the staged set whenever anything was staged.
    """
    findings: list[str] = []
    for path in tracked_paths():
        if ALLOWLIST.match(path):
            continue
        for label, pattern in RULES:
            if label == "personal store file" and pattern.search(path):
                findings.append(f"{path}: {label}")
        try:
            text = pathlib.Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # binary or unreadable; nothing to match
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern in RULES:
                if label == "personal store file":
                    continue
                m = pattern.search(line)
                if m:
                    findings.append(f"{path}:{number}: {label} — {m.group(0)[:40]!r}")
    return findings


def tracked_paths() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True,
                         text=True, check=False).stdout
    return [p for p in out.splitlines() if p]


# `git commit` options that consume the following token as their value. Without
# this, the message in `git commit -m wip` reads as a pathspec.
_VALUE_OPTIONS = {
    "-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c",
    "--reedit-message", "--author", "--date", "-S", "--gpg-sign", "-t",
    "--template", "--cleanup", "--trailer", "--fixup", "--squash", "-u",
    "--untracked-files", "--pathspec-from-file",
}


def commit_reaches_beyond_the_index(command: str) -> bool:
    """True when this `git commit` can include content that was never staged.

    `git diff --cached` is blind to `-a`, to `--amend`, and to an explicit
    pathspec — which is how an ID number in a tracked-but-unstaged file walks
    straight into a public repo.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True  # unparsable quoting: scan widely rather than guess

    try:
        i = tokens.index("commit")
    except ValueError:
        return False
    args = tokens[i + 1:]

    skip_next = False
    for n, tok in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if tok == "--":
            return len(args) > n + 1        # everything after -- is a pathspec
        if tok.startswith("--"):
            name = tok.split("=", 1)[0]
            if name in ("--all", "--amend"):
                return True
            if name in _VALUE_OPTIONS and "=" not in tok:
                skip_next = True
            continue
        if tok.startswith("-") and len(tok) > 1:
            if "a" in tok[1:]:              # -a, -am, -av ...
                return True
            if tok in _VALUE_OPTIONS or tok[-1:] in ("m", "F", "C", "c", "t", "u"):
                skip_next = True
            continue
        return True                          # a bare token is a pathspec
    return False


def scan() -> list[str]:
    """Return human-readable findings for staged content."""
    findings: list[str] = []

    for path in staged_paths():
        if ALLOWLIST.match(path):
            continue
        for label, pattern in RULES:
            if label == "personal store file" and pattern.search(path):
                findings.append(f"{path}: {label}")

    current = ""
    for line in staged_diff().splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        if ALLOWLIST.match(current):
            continue
        for label, pattern in RULES:
            if label == "personal store file":
                continue
            m = pattern.search(line)
            if m:
                snippet = m.group(0)[:40]
                findings.append(f"{current}: {label} — {snippet!r}")
    return findings


def _report(findings: list[str]) -> int:
    """Print findings and return the exit code: 2 blocks the tool call."""
    if not findings:
        return 0
    print("BLOCKED: personal data in this commit.", file=sys.stderr)
    print("This repo is PUBLIC. Marks, ID numbers and application references "
          "belong in ~/.life/, never here.\n", file=sys.stderr)
    for f in dict.fromkeys(findings):  # de-duplicate, keep order
        print(f"  • {f}", file=sys.stderr)
    print("\nRemove it, or move the value into the local store.", file=sys.stderr)
    return 2


def main() -> int:
    # Hook mode: stdin carries the tool call. Only guard `git commit`.
    if "--hook" in sys.argv[1:]:
        raw = sys.stdin.read().strip()
        if not raw:
            return 0
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return 0  # not a tool call we understand; stay out of the way
        command = (payload.get("tool_input") or {}).get("command", "")
        if "git commit" not in command:
            return 0
        if commit_reaches_beyond_the_index(command):
            # Scan the index AND every tracked file, because this commit can
            # carry content the index never saw.
            findings = list(dict.fromkeys(scan() + scan_tracked()))
            return _report(findings)

    return _report(scan_tracked() if "--all" in sys.argv[1:] else scan())


if __name__ == "__main__":
    sys.exit(main())
