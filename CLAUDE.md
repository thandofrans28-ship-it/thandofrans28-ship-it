# thandofrans28-ship-it

Thando's GitHub profile repo. It also holds `life`, a CLI that reports what is
true today across Notion, Google Calendar, Gmail and Drive.

## IMPORTANT: this repository is PUBLIC

Marks, ID numbers, bursary application references, bank details and the
personal store must never be committed. They live in `~/.life/store.json`.
A PreToolUse hook blocks `git commit` when the staged diff contains them
(`scripts/check_no_personal_data.py`). If it fires, fix the content — do not
work around the hook.

`seed/` is for facts that are already public: the IEB exam timetable, and
which connector owns which job.

## Commands

```bash
python3 -m pytest tests/ -q                     # the whole suite, ~0.1s
./life brief                                    # default view
LIFE_HOME=/tmp/x LIFE_TODAY=2026-09-19 ./life brief   # pin store and date
python3 scripts/check_no_personal_data.py       # scan the staged diff
python3 scripts/check_no_personal_data.py --all # scan every tracked file (CI)
```

## Architecture

The CLI never touches the network. Connectors are MCP-only, so Claude does the
network half — reads Gmail, Calendar and Notion, builds a JSON payload — and
`life sync` merges it into the local store. Keep it that way: no HTTP client,
no credentials on disk.

`lifeos/scoring.py` holds the UCT FPS and Stellenbosch selection-score
formulas. They decide a university application, so changes need a test that
pins the arithmetic. Test fixtures are synthetic; never use real marks.

## Conventions

- Stdlib only. No runtime dependencies.
- Work on `claude/*` branches, open PRs as drafts.
- Verify before pushing: the suite plus `./life brief` against an empty store.
