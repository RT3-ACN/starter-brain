# starter-brain

A starter-pack memory system — a file-based knowledge graph for humans and AI.

Your knowledge lives as markdown files with YAML frontmatter. Browse it in Obsidian. Let Claude Code read and write to it via MCP. Both human and AI contributions live in the same graph.

## Quick Start

```bash
pip install starter-brain
brain init
```

Open `knowledge/` as an Obsidian vault. Done.

## Connect Claude Code

```bash
brain init --with-mcp
# or manually: brain mcp serve --dir ./knowledge
```

This adds starter-brain to `~/.claude/mcp.json`. Claude can now search, create entities, and log episodes in your knowledge graph.

## CLI

```
brain create topic ml --name "Machine Learning" --tags ai,ml
brain show topics/ml
brain list topic
brain search "neural networks"
brain map topics/ml --depth 2
brain episode "Researched embedding models"
brain link          # regenerate Obsidian wikilinks
brain index         # rebuild search index
brain health        # validate integrity
```

## Semantic Search (optional)

```bash
pip install starter-brain[search]
brain index   # builds embeddings + HNSW index
brain semantic "deep learning architectures"
```

## Obsidian Plugin

Copy `obsidian-plugin/dist/` into your vault's `.obsidian/plugins/starter-brain/` directory.

Features: Entity Creator, Relation Browser, Episode Logger, Health Warnings.

## Format

Every entity is a markdown file in `knowledge/entities/{type}/{slug}.md`:

```yaml
---
type: topic
id: topics/machine-learning
name: Machine Learning
created: 2026-03-16
author: yourname
status: active
tags: [ai, ml]
relations:
  - type: REFERENCES
    target: topics/neural-networks
---
```

Compatible with Kitsune brain format.

## License

MIT
