---
type: pattern
id: patterns/diagram-freshness
name: Diagram Freshness
created: ${date}
updated: ${date}
author: ${author}
status: active
confidence: 90
importance: 7
tags: [meta, diagrams, documentation, maintenance]
relations:
  - type: DERIVED_FROM
    target: patterns/session-workflow
  - type: INFORMS
    target: patterns/decision-capture
---

## Pattern

**Every diagram has a `sources:` field. An audit detects when sources change.** Diagrams built from external documents (decks, PDFs, data files) drift silently. The source changes; the diagram doesn't. This pattern makes staleness visible.

## The Three-Layer System

**Layer 1 — Data (frontmatter)**

Add a `sources:` field to every diagram or document file that was built from a source:

```yaml
---
name: "Process Flow"
slug: my-process-flow
updated: 2026-03-25
sources:
  - ~/Documents/Project/source-file.pptx
  - ~/Documents/Project/data-export.xlsx
---
```

Use `sources: []` as a placeholder when the source is unknown — this marks the diagram as untracked rather than falsely current.

**Layer 2 — Detection (audit script)**

A script compares each source file's `mtime` against the diagram's `updated` date:

- 🔴 **STALE** — source modified after `updated` date → rebuild needed
- 🟡 **UNTRACKED** — `sources: []` → source unknown, may be stale
- 🟢 **OK** — sources older than or equal to `updated` → current

Run it with:
```bash
python3 diagram_audit.py ~/knowledge/diagrams/
```

**Layer 3 — Trigger (session integration)**

Wire the audit into your session-close workflow so stale diagrams are surfaced as open items at the end of every session.

## Why `sources:` and Not Just `updated:`

`updated:` only tells you when you last touched the diagram. It doesn't tell you whether the *source* has changed since then. A diagram can have a recent `updated:` date but still be stale if the source file changed after your last edit.

## What Counts as a Source

Good sources to track:
- Client deliverables (PPTX, PDF, DOCX) that diagrams visualize
- Data files (XLS, CSV) that diagrams summarize
- Config files or directories that diagrams reflect (e.g., `~/.claude/settings.json`)
- External processes or systems where changes drive diagram updates

Poor sources (don't track these):
- Directories that change constantly — check specific files instead
- Your own diagrams — these are outputs, not inputs
- The brain itself — if the diagram *is* the brain, it doesn't need a source

## The Minimum Viable Audit

```python
import os, re, datetime

def check_diagram(path):
    with open(path) as f:
        content = f.read()
    updated_match = re.search(r'updated: (\d{4}-\d{2}-\d{2})', content)
    sources_match = re.search(r'sources:\n((?:  - .+\n?)*)', content)
    if not sources_match:
        return 'untracked'
    updated = datetime.date.fromisoformat(updated_match.group(1)) if updated_match else None
    sources = [s.strip('- ').strip() for s in sources_match.group(1).strip().splitlines()]
    if not sources:
        return 'untracked'
    for src in sources:
        expanded = os.path.expanduser(src)
        if os.path.exists(expanded):
            mtime = datetime.date.fromtimestamp(os.path.getmtime(expanded))
            if updated and mtime > updated:
                return 'stale'
    return 'ok'
```

## Signals You Need This

- A diagram shows a process that was changed six months ago
- You can't remember if a diagram was built from the current version of a deck
- Client deliverables change frequently and your documentation doesn't keep up
- You have 20+ diagrams and can't tell which ones are trustworthy

## Related
- DERIVED_FROM: [[patterns/session-workflow|session-workflow]]
- INFORMS: [[patterns/decision-capture|decision-capture]]
