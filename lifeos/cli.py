"""Command dispatch for ``life``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from . import __version__, store
from .render import c, countdown, heading, table, urgency
from .scoring import improvement_plan, su_selection, uct_fps

SEED = Path(__file__).resolve().parent.parent / "seed"


# ── helpers ───────────────────────────────────────────────────────────────────

def today() -> date:
    """Today, overridable with LIFE_TODAY=YYYY-MM-DD for testing."""
    override = os.environ.get("LIFE_TODAY")
    return date.fromisoformat(override) if override else date.today()


def days_until(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        return (date.fromisoformat(iso[:10]) - today()).days
    except ValueError:
        return None


def load_seed(name: str) -> dict[str, Any]:
    p = SEED / f"{name}.json"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def papers(data: dict) -> list[dict]:
    """Exam papers from the store, falling back to the committed timetable."""
    return data.get("exams") or load_seed("exams").get("papers", [])


def upcoming(items: list[dict], key: str, within: int | None = None) -> list[dict]:
    """Items dated today or later, nearest first. ``within`` caps the horizon."""
    out = []
    for it in items:
        d = days_until(it.get(key))
        if d is None or d < 0:
            continue
        if within is not None and d > within:
            continue
        out.append({**it, "_days": d})
    return sorted(out, key=lambda i: i["_days"])


def empty_store_notice() -> str:
    return (
        c("  The store is empty.", "yellow")
        + "\n  Run "
        + c("life init", "bold")
        + " to create it, then ask Claude to sync your connectors into it.\n  See docs/LIFE_OS.md."
    )


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_brief(args, data):
    t = today()
    print(c(f"\n  {t.strftime('%A %d %B %Y')}", "bold"), end="")
    synced = data.get("synced_at")
    if synced:
        age = days_until(synced)
        note = "today" if age == 0 else f"{abs(age)}d ago" if age is not None else synced
        print(c(f"   · synced {note}", "grey" if (age or 0) > -3 else "yellow"))
    else:
        print(c("   · never synced", "yellow"))

    # The next paper, and what today belongs to.
    nxt = upcoming(papers(data), "date")
    if nxt:
        p = nxt[0]
        print(heading("next paper"))
        print(table([[countdown(p["_days"]), c(p["paper"], "bold"), p.get("time", ""), p["date"]]]))
        remaining = len(nxt)
        print(c(f"  {remaining} paper{'s' if remaining != 1 else ''} left · every free day belongs to the next one.", "grey"))

    # Anything due inside a fortnight.
    soon = upcoming(data.get("deadlines", []), "due", within=args.within)
    print(heading(f"deadlines — next {args.within} days"))
    if soon:
        print(table(
            [[countdown(d["_days"]), c(d.get("what", "?"), "bold" if d["_days"] <= 7 else ""),
              d.get("owner", ""), d.get("action", "")] for d in soon],
            ["when", "what", "with", "next action"],
        ))
    else:
        print(c("  Nothing inside the horizon.", "grey"))

    # Replies owed — the failure mode that loses funding on admin, not marks.
    loops = sorted(
        [l for l in data.get("open_loops", []) if not l.get("done")],
        key=lambda l: (-(l.get("priority") == "high"), l.get("waiting_since") or ""),
    )
    if loops:
        print(heading("waiting on you"))
        rows = []
        for l in loops:
            since = days_until(l.get("waiting_since"))
            age = c(f"{abs(since)}d", "red" if since is not None and abs(since) >= 5 else "yellow") if since is not None else ""
            flag = c("!", "red", "bold") if l.get("priority") == "high" else " "
            rows.append([flag, age, c(l.get("what", "?"), "bold"), l.get("action", "")])
        print(table(rows, ["", "age", "what", "do"]))

    print()
    return 0


def cmd_exams(args, data):
    rows = []
    for p in upcoming(papers(data), "date"):
        note = "" if p.get("certifying", True) else c("not for certification", "grey")
        rows.append([countdown(p["_days"]), p["date"], c(p["paper"], "bold"), p.get("time", ""), note])
    print(heading("finals — papers remaining"))
    print(table(rows, ["when", "date", "paper", "time", ""]) if rows else c("  All papers written.", "green"))
    free = []
    for d in load_seed("exams").get("free_days_inside_run", []):
        left = days_until(d)
        if left is not None and left >= 0:
            free.append(d)
    if free:
        print(c(f"\n  Printed free days inside the run: {', '.join(free)}", "grey"))
    print()
    return 0


def cmd_deadlines(args, data):
    items = data.get("deadlines", [])
    if not items:
        print(heading("deadlines"))
        print(empty_store_notice())
        print()
        return 0
    live = upcoming(items, "due", within=args.within)
    print(heading("deadlines"))
    print(table(
        [[countdown(d["_days"]), d["due"], c(d.get("what", "?"), "bold"),
          d.get("owner", ""), d.get("status", ""), d.get("action", "")] for d in live],
        ["when", "date", "what", "with", "status", "next action"],
    ))
    past = [i for i in items if (days_until(i.get("due")) is not None
                                 and days_until(i["due"]) < 0)]
    undated = [i for i in items if days_until(i.get("due")) is None]
    if undated:
        print(heading("no usable date"))
        print(table([[countdown(None), c(i.get("what", "?"), "bold"),
                      str(i.get("due", "")), i.get("action", "")] for i in undated]))
    if past and args.all:
        print(heading("closed"))
        print(table([[d["due"], d.get("what", "?"), d.get("status", "")] for d in past]))
    elif past:
        print(c(f"\n  {len(past)} past deadline(s) hidden — use --all.", "grey"))
    print()
    return 0


def cmd_apps(args, data):
    apps = data.get("applications", [])
    print(heading("application pipeline"))
    if not apps:
        print(empty_store_notice())
        print()
        return 0
    order = {"blocked": 0, "action-needed": 1, "in-progress": 2, "submitted": 3, "verified": 4, "closed": 5}
    colour = {"blocked": "red", "action-needed": "yellow", "in-progress": "cyan",
              "submitted": "blue", "verified": "green", "closed": "grey"}
    rows = []
    for a in sorted(apps, key=lambda a: (order.get(a.get("stage", ""), 9), a.get("name", ""))):
        stage = a.get("stage", "?")
        rows.append([c(stage, colour.get(stage, "grey")), c(a.get("name", "?"), "bold"), a.get("note", "")])
    print(table(rows, ["stage", "application", "note"]))
    print()
    return 0


def cmd_projects(args, data):
    """Repositories, ranked by whether anything is blocking them.

    A repo's real state is not its last commit. It is whether something
    outside the code — an unverified account, an unsigned key, a store
    review — is stopping the work from reaching anyone.
    """
    projects = data.get("projects", [])
    print(heading("projects"))
    if not projects:
        print(empty_store_notice())
        print()
        return 0

    order = {"blocked": 0, "live": 1, "active": 2, "dormant": 3, "archived": 4}
    colour = {"blocked": "red", "live": "green", "active": "cyan",
              "dormant": "yellow", "archived": "grey"}

    rows = []
    for p in sorted(projects, key=lambda p: (order.get(p.get("status", ""), 9),
                                             p.get("name", ""))):
        status = p.get("status", "?")
        age = days_until(p.get("last_push"))
        idle = c(f"{abs(age)}d", "grey" if age is None or abs(age) < 30 else "yellow") if age is not None else ""
        rows.append([c(status, colour.get(status, "grey")), c(p.get("name", "?"), "bold"),
                     idle, p.get("note", "")])
    print(table(rows, ["status", "project", "idle", "note"]))

    blockers = [p for p in projects if p.get("blocker")]
    if blockers:
        print(heading("blocked on"))
        for p in blockers:
            print(f"  {c('✗', 'red')} {c(p['name'], 'bold')} — {p['blocker']}")
    print()
    return 0


def cmd_marks(args, data):
    marks = data.get("marks", {})
    if not marks:
        print(heading("admission arithmetic"))
        print(empty_store_notice())
        print()
        return 0

    fps, su = uct_fps(marks), su_selection(marks)

    print(heading("current marks"))
    print(table([[s, f"{v}%"] for s, v in sorted(marks.items(), key=lambda kv: -kv[1])]))

    print(heading("uct — bsc(eng) electrical & computer"))
    if fps.clear:
        verdict = c("Band A guarantee met", "green", "bold")
    elif fps.gap:
        verdict = c(f"{fps.gap} points short", "yellow", "bold")
    else:
        # Target met, but a subject minimum is not — say which.
        verdict = c(f"target met, but {', '.join(fps.failed_gates)}", "red", "bold")
    print(f"  FPS {c(str(fps.total), 'bold')} / 600   target {fps.target}   {verdict}")
    print(c(f"  counting: {', '.join(f'{s} {v}' for s, v in fps.counting.items())}", "grey"))
    for gate, ok in fps.gates.items():
        print(f"  {c('✓', 'green') if ok else c('✗', 'red')} {gate}")

    print(heading("stellenbosch — beng electrical & electronic"))
    verdict = c("threshold met", "green", "bold") if su.meets_target else c(f"{su.gap} points short", "yellow", "bold")
    print(f"  Score {c(str(su.total), 'bold')} / 800   threshold {su.target}   {verdict}")
    if fps.partial or su.partial:
        print(c("  Estimated from an incomplete transcript — fewer subjects than "
                "the formula expects.", "yellow"))

    targets = data.get("profile", {}).get("mark_targets", {})
    if targets:
        plan = improvement_plan(marks, targets)
        print(heading("what each subject is worth"))
        print(table(
            [[c(r["subject"], "bold"), f"{r['from']}→{r['to']}", f"+{r['marks_needed']} marks",
              c(f"FPS +{r['fps_gain']}", "green" if r["fps_gain"] else "grey"),
              c(f"SU +{r['su_gain']}", "green" if r["su_gain"] else "grey")] for r in plan],
            ["subject", "lift", "cost", "buys", ""],
        ))
        print(c("  Ranked by FPS gain. A subject outside the counting six buys nothing at UCT.", "grey"))
    print()
    return 0


def cmd_connectors(args, data):
    reg = load_seed("connectors").get("connectors", [])
    healthy = {"connected"}
    print(heading("connectors"))
    for tier in ("spine", "build", "design", "dormant"):
        rows = [r for r in reg if r.get("tier") == tier]
        if not rows:
            continue
        if tier == "dormant" and not args.all:
            print(c(f"\n  dormant: {len(rows)} connector(s) hidden — use --all.", "grey"))
            continue
        print(c(f"\n  {tier}", "bold"))
        print(table([
            [c("●", "green" if r["status"] in healthy else "yellow"), c(r["name"], "bold"),
             r["status"], r.get("owns", "")] for r in rows
        ]))
    broken = [r for r in reg if r.get("tier") != "dormant" and r["status"] not in healthy]
    if broken:
        print(c(f"\n  {len(broken)} active connector(s) need attention: "
                + ", ".join(r["name"] for r in broken), "yellow"))
    print()
    return 0


def cmd_doctor(args, data):
    """What is stale, missing or blocking."""
    problems: list[tuple[str, str]] = []

    synced = days_until(data.get("synced_at"))
    if data.get("synced_at") is None:
        problems.append(("warn", "Store has never been synced — ask Claude to refresh it."))
    elif synced is not None and abs(synced) > 7:
        problems.append(("warn", f"Store last synced {abs(synced)} days ago."))

    for d in data.get("documents", []):
        if not d.get("have"):
            sev = "fail" if d.get("blocking") else "warn"
            problems.append((sev, f"Missing document: {d.get('name')}"
                                  + (" — blocks overseas applications" if d.get("blocking") else "")))

    for l in data.get("open_loops", []):
        if l.get("done"):
            continue
        age = days_until(l.get("waiting_since"))
        if age is not None and abs(age) >= 5:
            problems.append(("fail" if l.get("priority") == "high" else "warn",
                             f"{abs(age)} days unanswered: {l.get('what')}"))

    for p in data.get("projects", []):
        if p.get("blocker"):
            problems.append(("fail", f"{p.get('name')} is blocked: {p['blocker']}"))

    for d in upcoming(data.get("deadlines", []), "due", within=3):
        problems.append(("fail", f"Due in {d['_days']}d: {d.get('what')}"))

    reg = load_seed("connectors").get("connectors", [])
    for r in reg:
        if r.get("tier") in ("spine", "build") and r["status"] != "connected":
            problems.append(("warn", f"Connector {r['name']} is {r['status']}."))

    print(heading("doctor"))
    if not problems:
        print(c("  Nothing to flag.", "green"))
    else:
        for sev, msg in sorted(problems, key=lambda p: p[0] != "fail"):
            print(f"  {c('✗', 'red') if sev == 'fail' else c('!', 'yellow')} {msg}")
    print()
    return 1 if any(s == "fail" for s, _ in problems) else 0


def cmd_init(args, data):
    p = store.path()
    if p.exists() and not args.force:
        print(c(f"  Store already exists at {p} — use --force to reset.", "yellow"))
        return 1
    fresh = store.load() if not p.exists() else json.loads(json.dumps(store._EMPTY))
    fresh["exams"] = load_seed("exams").get("papers", [])
    written = store.save(fresh)
    print(c(f"  Created {written}", "green"))
    print(c("  Personal data lives here, never in the repo. Ask Claude to sync connectors into it.", "grey"))
    return 0


def cmd_sync(args, data):
    """Merge a JSON payload into the store.

    The CLI cannot reach MCP connectors itself. Claude reads Gmail, Calendar
    and Notion, then pipes a payload here — so the CLI stays deterministic and
    offline, and the network half is done by the agent that already has auth.
    """
    try:
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        print(c(f"  Cannot read {args.file}: {exc.strerror}", "red"))
        return 1
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(c(f"  Not valid JSON: {exc}", "red"))
        return 1
    if not isinstance(payload, dict):
        print(c("  Payload must be a JSON object.", "red"))
        return 1

    unknown = set(payload) - set(store._EMPTY)
    if unknown:
        print(c(f"  Ignoring unknown keys: {', '.join(sorted(unknown))}", "yellow"))

    changed = []
    for key in store._EMPTY:
        if key in payload:
            data[key] = payload[key]
            changed.append(key)
    data["synced_at"] = datetime.now().astimezone().date().isoformat()
    store.save(data)
    print(c(f"  Synced {', '.join(changed) or 'nothing'} → {store.path()}", "green"))
    return 0


COMMANDS = {
    "brief": cmd_brief, "exams": cmd_exams, "deadlines": cmd_deadlines,
    "apps": cmd_apps, "marks": cmd_marks, "connectors": cmd_connectors,
    "projects": cmd_projects,
    "doctor": cmd_doctor, "init": cmd_init, "sync": cmd_sync,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="life",
        description="One command for what is true today. Reads a local snapshot "
                    "of Notion, Calendar, Gmail and Drive; never writes to them.",
    )
    p.add_argument("--version", action="version", version=f"life {__version__}")
    sub = p.add_subparsers(dest="command")

    b = sub.add_parser("brief", help="today: next paper, deadlines, replies owed (default)")
    b.add_argument("--within", type=int, default=14, help="deadline horizon in days (default 14)")

    sub.add_parser("exams", help="remaining final papers")

    d = sub.add_parser("deadlines", help="every tracked deadline")
    d.add_argument("--within", type=int, default=None,
                   help="horizon in days (default: no limit)")
    d.add_argument("--all", action="store_true", help="include past deadlines")

    sub.add_parser("apps", help="application pipeline by stage")
    sub.add_parser("projects", help="repositories and what is blocking them")
    sub.add_parser("marks", help="UCT FPS and Stellenbosch selection score")

    cn = sub.add_parser("connectors", help="connector registry and health")
    cn.add_argument("--all", action="store_true", help="include dormant connectors")

    sub.add_parser("doctor", help="what is stale, missing or blocking")

    i = sub.add_parser("init", help="create the personal store")
    i.add_argument("--force", action="store_true", help="overwrite an existing store")

    s = sub.add_parser("sync", help="merge a JSON payload into the store")
    s.add_argument("file", nargs="?", default="-", help="path, or - for stdin (default)")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "brief"
    if command == "brief" and not hasattr(args, "within"):
        args.within = 14
    data = store.load()
    try:
        return COMMANDS[command](args, data)
    except (ValueError, KeyError) as exc:
        print(c(f"  {exc}", "red"))
        return 1
