---
type: pattern
id: patterns/decision-capture
name: Decision Capture
created: ${date}
updated: ${date}
author: ${author}
status: active
confidence: 90
importance: 8
tags: [meta, decisions, documentation]
relations:
  - type: DERIVED_FROM
    target: patterns/session-workflow
---

## Pattern

A good decision entity has three things: **what was decided**, **why** (reasoning + alternatives), and **current status**.

Most decision capture fails because it records the outcome but not the reasoning. Six months later, no one knows if the constraint that drove the choice still applies.

## Template

```markdown
## Decision
[One sentence: what was chosen or agreed]

## Context
[What problem or question this was responding to]

## Rationale
[Why this over the alternatives — be specific about the tradeoffs]

## Alternatives Considered
- [Option A] — rejected because [reason]
- [Option B] — rejected because [reason]

## Consequences
[What this enables or constrains going forward]

## Status
active | superseded by [link] | archived
```

## What Makes a Bad Decision Entity

- "We decided to use X" — no why, useless later
- Alternatives not recorded — can't evaluate if conditions change
- Status never updated when the decision was revisited
- Too long — if it needs a full doc, link to the doc; keep the entity as the summary

## When to Create One

Any time a non-obvious choice is made that a future version of you (or a teammate) would wonder about. If it took more than 5 minutes to decide, it's worth capturing.

## When to Update One

When the decision is revisited or reversed — update status and add a note explaining what changed. Don't delete; set `status: superseded` and link to the new decision.

## Related
- DERIVED_FROM: [[patterns/session-workflow|session-workflow]]
