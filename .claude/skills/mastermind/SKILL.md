---
name: mastermind
description: Turn a long, voice-dictated "improve everything" request into ranked, verified action. Fans research out to Sonnet researcher agents, fact-checks what an action depends on, does what is reversible, drafts what is not, and reports what changed. Use when Thando asks for help across many areas at once ("do everything", "improve my life", "be the mastermind", money + applications + groceries + Claude in one message).
---

# Mastermind: from a ramble to verified action

A dictated request is a list of goals in disguise, plus the ones Thando did
not think to say. The job is to find all of them, do the reversible ones,
prepare the rest for one tap, and never hand over an unchecked fact.

## 1. Extract

Write the goals as one line each, in Thando's words where possible. Then add
the goals the context implies but the message skipped: the next paper, a
deadline inside 14 days, a reply owed. Say which ones you added.

## 2. Rank

Order by how soon it bites, times what being wrong costs. During finals the
next paper outranks everything that can wait until after the last one. A
funding deadline outranks a nicer tool. Drop anything that does not move one
of: exams, funding, admission, money, health, faith practice.

## 3. Look before advising

Read the live state before you recommend anything: run the `life-sync` skill,
or `./life brief` and `./life doctor` against the existing store. Advice
that ignores what is already in Gmail or Notion is noise.

## 4. Fan out

One `researcher` agent per independent question, launched together in the
background. Each starts cold, so give it everything: who Thando is, today's
date, the exact question, the scratchpad output path, and the rule that every
claim carries a URL and a status. Keep orchestration and judgment for
yourself; give the agents the reading.

## 5. Fact-check

Before a date, amount or eligibility rule drives an action, send it to the
`fact-checker` agent, or open the primary source yourself. Never act on
`UNVERIFIED`. Lead the report with anything that came back `CORRECTED` or
`STALE`.

## 6. Act, in three tiers

| Tier | What | Examples |
|---|---|---|
| Do | Reversible and private | Scratchpad notes, `life sync`, Gmail **drafts**, a private Notion page, a draft PR |
| Prepare, then ask | Leaves Thando's hands | Sending email, submitting an application, sharing a file, deleting anything |
| Never | Cannot be taken back, or is not yours to do | Personal data in this repo; paying, signing up or applying in Thando's name |

Permission settings back this up: send, share and delete tools are on `ask`.

## 7. Report

1. What changed (with links).
2. What needs Thando's tap, each with the one-line reason.
3. The next three actions, each with a date.
4. What you could not verify.

Short sentences. No praise, no recap of the request.
