# starter-brain

A file-based knowledge graph for humans and AI.

Your knowledge lives as markdown files with YAML frontmatter. Browse it in Obsidian. Let Claude Code read and write to it via MCP. Both human and AI contributions live in the same graph.

## Install

```bash
pip install starter-brain
```

For Claude Code MCP integration:
```bash
pip install "starter-brain[mcp]"
```

## Quick Start

```bash
# Initialize a new knowledge graph
brain init ./knowledge --author yourname

# Connect to Claude Code (adds MCP to ~/.claude/mcp.json)
brain init ./knowledge --author yourname --with-mcp
```

Open `knowledge/` as an Obsidian vault. Done.

## What You Get

### CLI (`brain` command)

```bash
brain create topic ml --name "Machine Learning" --tags ai,ml
brain show topics/ml
brain list topic
brain search "neural networks"
brain map topics/ml --depth 2
brain episode "Researched embedding models today"
brain link          # regenerate Obsidian wikilinks
brain index         # rebuild search index
brain health        # validate integrity
```

### MCP Server (8 tools for Claude Code)

After `--with-mcp` setup, Claude Code gets these tools:

| Tool | What it does |
|---|---|
| `brain_search` | Keyword search across entities |
| `brain_semantic_search` | Similarity search (requires `[search]` extra) |
| `brain_graph_search` | Semantic search + relationship expansion |
| `brain_mind_map` | Walk N hops from a seed entity |
| `brain_entity` | Read a specific entity |
| `brain_save_entity` | Create or update an entity |
| `brain_episode` | Log a session note or learning |
| `brain_stats` | Knowledge graph overview |

### Obsidian Plugin

Copy `obsidian-plugin/` into your vault. Features:
- Entity Creator modal
- Relation Browser
- Episode Logger
- Health Warnings

## Entity Format

Every entity is a markdown file in `knowledge/entities/{type}/{slug}.md`:

```yaml
---
type: topic
id: topics/machine-learning
name: Machine Learning
created: 2026-03-16
updated: 2026-03-16
author: yourname
status: active
confidence: 80
importance: 7
tags: [ai, ml]
relations:
  - type: REFERENCES
    target: topics/neural-networks
---

## Notes

Your content here. Supports full markdown.

## Related

- [[topics/neural-networks]]
```

### Entity Types

Built-in defaults: `topic`, `insight`, `decision`, `pattern`, `person`, `project`, `research`, `hypothesis`. Any string is accepted — unknown types pass through with a warning, not an error.

### Relation Types

`REFERENCES`, `INFORMS`, `DERIVED_FROM`, `SUPERSEDED_BY`, `CONTRADICTS`, `DEPENDS_ON`, `PART_OF`, `USES_TOPIC`, `CREATED_BY`. Any string accepted.

## Semantic Search (optional)

```bash
pip install "starter-brain[search]"
brain semantic "deep learning architectures"
```

Pulls `sentence-transformers` + `hnswlib` (~2GB). Core install is ~5MB (pyyaml only).

## Architecture

- **File format IS the API.** No database. CLI, MCP, and Obsidian all read/write the same markdown files.
- **Atomic writes** — entity files use `tempfile + os.replace`. No corruption on crash.
- **Zero cloud dependencies** — everything runs locally. No API keys needed for core features.
- **MCP via stdio** — no network ports opened. Safe for corporate environments.

## Development

```bash
git clone <repo-url>
cd starter-brain
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
pytest
```

## License

MIT
