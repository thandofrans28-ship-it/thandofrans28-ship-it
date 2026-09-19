# Connector audit — September 2026

22 connectors are installed. **13 are connected, 9 are not.** The useful
question is not how many work, but which ones carry weight during the finals.

## Tier 1 — the spine

These four carry the matric campaign. If one breaks, something gets lost.

| Connector | Status | Owns |
|---|---|---|
| Google Calendar | ✅ | 448 events, 24 Sep → 19 Nov. Every study block and deadline marker. |
| Notion | ✅ | MATRIC ENDGAME OS · Bursary & Deadline Tracker · Study & Exam Planner · Weekly Tracker |
| Gmail | ✅ | Every funding conversation. **The only place a reply is ever owed.** |
| Google Drive | ✅ | Document vault — ID, results, CV, proof of address |

All four healthy. Nothing to do.

### The one structural gap

**Gmail is the single point of failure and nothing watches it.**

Calendar and Notion hold what you *planned*. Gmail holds what other people are
*waiting for* — and it has no deadline field, no status, and no tracker.

That asymmetry is the whole problem. A deadline you set yourself gets a
calendar marker, a tracker row and a reminder. A funder asking you for one more
document gets a single unread line in an inbox, and then nothing. Both can lose
you the same award, but only one of them is instrumented.

This is why `life brief` has a **waiting on you** section, and why it sorts by
how long something has been waiting rather than by when it arrived. An item
that has sat for six days is a more urgent signal than one that arrived today.

## Tier 2 — build

| Connector | Status | Note |
|---|---|---|
| github | ✅ | Project repos and this one |
| composio | ✅ | Automation pipelines |
| emergent | ✅ | Agent jobs |
| Supabase | ⚠️ needs reconnect | App backends — reconnect before the next Pathfinda session |
| Vercel | ⚠️ disconnected | Web deploys |

Supabase and Vercel are two clicks each. Worth doing *before* the exam run
starts, because after that every free day belongs to the next paper.

## Tier 3 — design

Figma · Canva · Adobe for creativity · higgsfiled — all ✅.

Adobe is the quietly useful one: application packs want a single merged,
compressed PDF, and `pdf_combine` + `pdf_compress` do that without hunting for
a free online tool that watermarks the output.

## Tier 4 — dormant

Nine connectors are installed but not working: alpha vantage · Atlassian Rovo ·
base44 · Lovable · Microsoft 365 · Slack · Spotify · Strava · Webflow.

**None of them are load-bearing. Recommendation: leave all nine as they are
until the finals are over.**

A half-finished connector costs nothing. Finishing nine of them costs an
evening you do not have, and none of them moves a single admission point.

`alpha vantage` is the only one worth an actual decision, and the decision is
to let it go — market data belonged to the actuarial plan, which the move to
Electrical Engineering has superseded.

## Not connectors, but part of the system

Two tools carry real weight and have no MCP connector at all:

- **Google Tasks** — open application deadlines, already checked against the
  exam timetable so none falls on an exam day.
- **Anki** — the daily interleaving block.

Neither needs one. Tasks is mirrored by Calendar markers and the Notion
tracker; Anki is a daily habit, not a lookup. They are noted here so the map is
honest about everything that is actually running.

## What would genuinely help — and what would not

**Worth it (two clicks):** reconnect Supabase and Vercel.

**Not worth it now:** anything that needs setup. Nine dormant connectors, a new
automation, another tracker. There is already a rewritten Notion OS, a fully
allocated calendar and a mature card deck. The constraint is not tooling.

The highest-leverage action this audit surfaced is not a connector at all:

> **Clear the replies sitting unanswered in Gmail.** Nothing there is blocked
> on a mark. It is blocked on an hour.

Run `life brief` for the current list.

## Re-running this audit

```bash
life connectors        # tier 1–3 and anything unhealthy
life connectors --all  # include the nine dormant ones
life doctor            # flags broken spine/build connectors, exit 1 on blockers
```

Statuses are cached in `seed/connectors.json`. Ask Claude to refresh them when
something changes.
