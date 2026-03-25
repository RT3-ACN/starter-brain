---
type: pattern
id: patterns/auto-memory
name: Auto Memory
created: ${date}
updated: ${date}
author: ${author}
status: active
confidence: 95
importance: 9
tags: [meta, memory, ai, workflow]
relations:
  - type: DERIVED_FROM
    target: patterns/session-workflow
  - type: INFORMS
    target: patterns/decision-capture
---

## Pattern

**Four memory types. One index file. Persists across all sessions.** The brain stores knowledge about projects, decisions, and patterns — but it doesn't store knowledge *about the person using it* or *how they want to be worked with*. Auto-memory fills that gap.

## The Four Types

| Type | What it stores | Examples |
|------|---------------|---------|
| `user` | Who the person is — role, expertise, preferences | "senior Go dev, new to React"; "prefers bullet points over paragraphs" |
| `feedback` | How to approach work — what to avoid, what to keep doing | "don't mock the DB"; "stop summarizing after tool calls" |
| `project` | Ongoing work state — what's active, who's involved, key decisions | "merge freeze begins 2026-03-05 for mobile release" |
| `reference` | Where to find things — external systems, dashboards, trackers | "pipeline bugs tracked in Linear project INGEST" |

## File Structure

```
~/.claude/memory/           # or wherever your AI assistant looks
  MEMORY.md                 # index — loaded every session
  user_role.md              # individual memory files
  feedback_testing.md
  project_auth_rewrite.md
  reference_grafana.md
```

### MEMORY.md (the index)

Loaded automatically by the AI at session start. Kept brief — it's a pointer file, not the content.

```markdown
# Memory Index

## User
- [Role & Expertise](user_role.md) — senior engineer, Go focus, new to React

## Feedback
- [Testing approach](feedback_testing.md) — no DB mocks; integration tests only

## Project
- [Auth rewrite](project_auth_rewrite.md) — legal compliance driver, merge by Apr 1

## Reference
- [Grafana oncall board](reference_grafana.md) — api-latency dashboard at grafana.internal/d/api-latency
```

### Individual memory file format

```markdown
---
name: [memory name]
description: [one-line — used to decide relevance, be specific]
type: [user | feedback | project | reference]
---

[memory content]
```

For `feedback` and `project` types, structure as:
- **Rule or fact** (lead with it)
- **Why:** the reason behind it
- **How to apply:** when/where it kicks in

## When to Save

Save automatically — not just when the user says "remember this":

**User memories:** When you learn role, expertise, or preferences (even implicit ones — if they never explain basic Python to you, save that they're a Python expert).

**Feedback memories:** When the user corrects your approach ("no not that", "don't do X") or validates a non-obvious choice ("yes exactly"). Corrections are obvious; validations are quieter but equally important.

**Project memories:** When you learn project state, stakeholders, constraints, or deadlines. Convert relative dates to absolute ones immediately — "Thursday" → "2026-03-05".

**Reference memories:** When you learn where something lives in an external system.

## When NOT to Save

- Code patterns, conventions, architecture — these are in the code
- Git history — `git log` is authoritative
- Debugging solutions — the fix is in the code; the commit has the context
- Anything already in CLAUDE.md
- Ephemeral task details or in-progress work

## Staleness

Project memories decay fast. Check them against current state before acting on them:
- If a memory names a file or function: verify it exists
- If a memory describes project status: check the actual files
- "The memory says X exists" ≠ "X exists now"

## The Compounding Effect

The first few sessions feel redundant — you're writing things you already know. The payoff comes at session 10 when a new conversation picks up exactly where the last one left off without a single re-explanation.

The user/feedback types compound fastest: once the AI knows your role and working style, every session is faster. Feedback memories prevent repeated frustrations.

## Related
- DERIVED_FROM: [[patterns/session-workflow|session-workflow]]
- INFORMS: [[patterns/decision-capture|decision-capture]]
