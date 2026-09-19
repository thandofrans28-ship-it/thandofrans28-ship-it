# The system, and where `life` fits

You already run a good system. This tool does not replace any part of it.

| Layer | Tool | What it owns |
|---|---|---|
| Strategy | Notion — **⚡ MATRIC ENDGAME OS** | The target, the arithmetic, the 14 papers, the per-paper checklist |
| Schedule | Google Calendar | Every study block, deadline marker, fixed commitment |
| Accountability | Notion — **Study & Exam Planner** | A block is not done until the row says what it produced |
| Watchlist | Notion — **Bursary & Deadline Tracker** | Every funding opportunity and its state |
| Conversations | Gmail | The only place a reply is ever owed |
| Documents | Google Drive + `Downloads\Bursaries_2027\` | ID, results, CV, proof of address, passport |
| Recall | Anki `Matric 2026` | 2 776 cards |
| **Cross-cutting view** | **`life`** | **The one question none of the above answers alone** |

## The gap this closes

Every tool above is correct about its own slice. None of them can tell you, in
one place, that a funder's request has been sitting unanswered for six days
*while* a scholarship deadline is eleven days out *and* a document that blocks
three overseas applications still is not confirmed.

That is a cross-tool question, and cross-tool questions are where things get
lost. Not through forgetting the plan — through the plan being spread over six
tools that each look fine on their own.

```
$ life brief

  Saturday 19 September 2026   · synced today

NEXT PAPER
──────────
  26d  IT P1 — Practical  09:00-12:00  2026-10-15
  14 papers left · every free day belongs to the next one.

DEADLINES — NEXT 14 DAYS
────────────────────────
  when  what                  with      next action
  11d   Example scholarship   Funder    Apply — needs a campus ID

WAITING ON YOU
──────────────
     age  what                        do
  !  6d   Stage-2 assessment          Complete the link they sent
  !  4d   Document not yet confirmed  Blocks three overseas applications
```

*(Illustrative output. Real entries live in `~/.life/store.json`, never here.)*

## Why the CLI does not call the connectors itself

It could. It should not.

Gmail, Calendar and Notion are reached over MCP, which needs an authenticated
agent session — not a shell. Building an OAuth client into the CLI would mean
storing refresh tokens on disk next to a public repo, for a tool whose whole
job is to be *trustworthy about private data*.

So the split is:

- **Claude** does the network half. It already holds the connections.
- **`life`** does the deterministic half: offline, testable, no credentials,
  no network access, no surprises.

They meet at one JSON payload:

```bash
# Claude reads Gmail + Calendar + Notion, then:
life sync payload.json
```

`sync` accepts a file or stdin, replaces only the keys present, reports any it
does not recognise, and stamps `synced_at`. `life brief` warns when that stamp
gets old, so a stale snapshot announces itself rather than quietly misleading you.

To refresh it, ask Claude:

> Sync my life store — check Gmail for replies I owe, Calendar for deadlines
> in the next month, and the Notion Bursary Tracker for status changes.

## Privacy

`thandofrans28-ship-it/thandofrans28-ship-it` is your **public** profile repo.
Anyone can read it.

- Personal data lives in `~/.life/store.json` — outside the repo, `0600`, owned
  by a `0700` directory.
- `.gitignore` blocks `store.json`, `.life/` and `data/` as a second line of defence.
- **A PreToolUse hook blocks `git commit`** when the staged diff contains an ID
  number, a mark, an application reference, a bank number or a store file
  (`scripts/check_no_personal_data.py`, wired in `.claude/settings.json`).
  Documentation is advisory; this is not.
- CI re-scans every tracked file with `--all`, because a fresh checkout stages
  nothing and a diff-based scan there would pass without proving anything.
- A test (`test_repo_contains_no_personal_store`) fails the suite if a store is
  ever staged.
- `seed/` holds only facts that are already public: the IEB timetable and which
  connector owns which job. No marks, no ID number, no application references.

Your ID number, marks and application reference numbers must never be committed
here. If you want them version-controlled, use a **private** repo.

## Commands

| Command | Answers |
|---|---|
| `life brief` | What do I need to know right now? *(default)* |
| `life doctor` | What is stale, missing or blocking? *(exit 1 on a hard problem)* |
| `life marks` | Where am I against UCT 500 and SU 620, and what is each subject worth? |
| `life deadlines` | Everything dated, nearest first |
| `life apps` | The funding pipeline by stage |
| `life exams` | Papers remaining |
| `life connectors` | Which tool owns which job, and what is broken |
| `life sync` | Take a fresh snapshot from Claude |

`life doctor` exits non-zero when something is genuinely blocking, so it works
in a shell prompt or a login script:

```bash
# ~/.bashrc
life brief
```
