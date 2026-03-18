---
type: topic
id: topics/knowledge-capture
name: Knowledge Capture
created: ${date}
updated: ${date}
author: ${author}
status: active
importance: 7
tags: [meta, knowledge-graph, productivity]
relations:
  - type: REFERENCES
    target: patterns/session-workflow
  - type: REFERENCES
    target: patterns/decision-capture
---

## What's Worth Capturing

**High value:**
- Decisions with rationale — especially why alternatives were rejected
- Patterns that recur across projects
- Project context that would take 10+ minutes to reconstruct
- Insights that changed how you understand a domain
- People's preferences, expertise, and working style

**Low value:**
- Ephemeral status ("working on X right now")
- Things obvious from reading the code or a doc
- Meeting summaries that don't contain a decision
- Information that expires within days

## The Compound Interest Principle

An entity written today may save 20 minutes 3 months from now when the context is completely gone. The question: *"Would this save meaningful time or prevent a mistake in a future session that has no memory of today?"*

If yes, write it. If no, don't — noise is the enemy.

## Noise Is the Enemy

A brain full of low-quality entities is worse than a small, dense brain. When in doubt, write less but write it well. Review periodically:

```bash
brain health    # find orphan entities and integrity issues
brain list      # scan for stale or vague entries
```

Archive (`status: archived`) or delete entities that are no longer relevant rather than leaving them to accumulate.

## The Minimum Viable Entity

Every entity needs: a clear name, a specific body (not just "notes on X"), and at least one relation to another entity. An orphan entity with no relations is a signal it's either too vague or not connected to anything that matters.

## Related
- REFERENCES: [[patterns/session-workflow|session-workflow]]
- REFERENCES: [[patterns/decision-capture|decision-capture]]
