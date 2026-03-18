---
type: pattern
id: patterns/session-workflow
name: Session Workflow
created: ${date}
updated: ${date}
author: ${author}
status: active
confidence: 95
importance: 9
tags: [meta, workflow, productivity]
relations:
  - type: INFORMS
    target: patterns/decision-capture
---

## Pattern

**Orient → Work → Capture.** Every session has three phases.

### 1. Orient (start of session)

Before touching anything, check the brain for relevant context:

```bash
brain search "project or topic"
brain show projects/relevant-project
```

Or in Claude Code: *"Check the brain for context on [project/topic] before we start."*

Read recent episodes. Don't start from scratch if prior knowledge exists — the whole point of the brain is that you don't have to.

### 2. Work

Do the work. When Claude makes meaningful decisions or discovers useful patterns, those are candidates to save. You don't need to interrupt flow — flag them mentally and capture at the end.

### 3. Capture (end of session)

Log an episode — even one sentence:

```bash
brain episode "What was worked on, what was decided, what was learned"
```

Then ask: did anything change that needs a saved entity updated? New decision? Project status shifted? Pattern discovered?

Run: `brain index && brain link`

## Why This Matters

The brain only accumulates value if you write to it. Most of the value is actually in the act of writing — it forces clarity about what you decided and why. The retrieval is almost secondary.

## Signals You Skipped This

- You explain the same context to Claude that you explained last week
- You can't remember why a past decision was made
- Claude contradicts a prior decision because it has no record of it

## Related
- INFORMS: [[patterns/decision-capture|decision-capture]]
