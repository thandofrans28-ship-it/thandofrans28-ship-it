---
name: life-sync
description: Refresh the local life store from Gmail, Google Calendar and Notion, then show the brief. Use when asked to sync the life store, refresh deadlines, or check what is slipping.
---

# Refresh the life store

The `life` CLI has no network access by design. This skill is the network half:
read the connectors, build one JSON payload, merge it, show the result.

## 1. Gather

Run these together, they are independent:

- **Gmail** — `search_threads` with `newer_than:30d -category:promotions
  -category:social in:inbox`. You are looking for threads where **someone is
  waiting on Thando**: a funder asking for a document, a school asking for a
  link, an assessment invite, a chased form. A thread whose last message is
  from them and asks for something is an open loop.
- **Google Calendar** — `list_events` over the next 90 days. Deadline markers
  are all-day events; the description usually carries the real action.
- **Notion** — the `🎓 Bursary & Deadline Tracker` database for status changes,
  and `⚡ MATRIC ENDGAME OS` if the exam plan may have moved.
- **GitHub** — `list_repos`, then last push and CI status per repo. A repo's
  real state is not its last commit: it is whether something *outside* the
  code is stopping the work from reaching anyone — an unverified payments
  profile, an unsigned key, a store review. Green CI on a blocked app is not
  progress. Check Gmail for the platform mail that names the blocker.

## 2. Build the payload

Write JSON with only the keys that changed. Schema:

```json
{
  "profile":      {"name": "", "goal": "", "mark_targets": {"English": 75}},
  "marks":        {"Mathematics": 84},
  "deadlines":    [{"due": "2026-09-30", "what": "", "owner": "", "status": "", "action": ""}],
  "open_loops":   [{"what": "", "waiting_since": "2026-09-13", "priority": "high", "action": ""}],
  "applications": [{"name": "", "stage": "action-needed", "note": ""}],
  "documents":    [{"name": "", "have": false, "blocking": true}],
  "projects":     [{"name": "", "repo": "", "status": "blocked",
                    "last_push": "2026-09-13", "blocker": "", "note": ""}]
}
```

`stage` is one of: `blocked`, `action-needed`, `in-progress`, `submitted`,
`verified`, `closed`. A project's `status` is one of: `blocked`, `live`,
`active`, `dormant`, `archived` — and `blocker` is set only when something
outside the repo is stopping it, which is what `life doctor` fails on. `waiting_since` is the date **they** last wrote, not when
you noticed — the age is the signal.

`action` must be the next physical step, not a restatement. "Upload via the
link in their original email — a reply attachment does not count" is an action.
"Follow up" is not.

## 3. Merge and check

```bash
./life sync payload.json
./life brief
./life projects      # repos, blocked first
./life doctor        # exit 1 means something is blocking
```

## 4. Report

Lead with what is **slipping**, not what is scheduled. Ranked by: an unanswered
reply older than five days, then a deadline inside seven days, then a blocking
document. Say plainly if nothing is slipping.

## Rules

- The payload is personal data. Write it under `$LIFE_HOME` or the scratchpad,
  **never** into the repo — it is public.
- Replace-not-merge: a key you include overwrites that whole list. Carry
  forward entries that are still live, or they vanish.
- Do not send email or edit Notion as part of a sync. Sync reads; a reply is a
  separate, deliberate decision.
