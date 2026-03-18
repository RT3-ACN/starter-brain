# starter-brain

A file-based knowledge graph for humans and AI.

Your knowledge lives as markdown files with YAML frontmatter. Browse it in Obsidian. Let Claude Code read and write to it via MCP. Both human and AI contributions live in the same graph.

---

## Install

```bash
pip install starter-brain
```

For Claude Code MCP integration:
```bash
pip install "starter-brain[mcp]"
```

---

## Quick Start

**1. Initialize**
```bash
brain init ~/knowledge --author yourname --with-mcp
```

This creates your `knowledge/` directory, seeds it with starter entities and patterns, adds a `CLAUDE.md` with instructions for Claude, and registers the MCP server with Claude Code.

**2. Open in Obsidian** (optional but recommended)

Open `~/knowledge` as a vault. Your entities become browsable nodes with visual link graphs.

**3. Start your first session**

Open Claude Code from any project directory and ask:
```
Check the brain for any context on [what you're working on], then let's get started.
```

Claude now has access to your brain via MCP and will search it automatically.

**4. End your first session**

Ask Claude:
```
Log what we worked on and decided today to the brain.
```

Then run:
```bash
brain index && brain link
```

That's the loop. Orient → work → capture. The brain compounds over time.

---

## The Core Habit

The brain is only as useful as what you put in it. Three things make it work:

1. **Check before starting** — ask Claude to search the brain at the start of any substantive session
2. **Capture decisions with reasoning** — not just what was decided, but why, and what alternatives were rejected
3. **Log episodes** — even one sentence per session. `brain episode "what I worked on today"`. The compounding is real.

Your seeds include two patterns (`session-workflow` and `decision-capture`) that explain this in detail.

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

## What to Build Next

Once you have a brain running, here are natural next steps roughly ordered by complexity:

### Week 1 — Build the habit
- **Log episodes daily.** Even one line: `brain episode "what I worked on today"`. The value compounds over time.
- **Create entities for projects you're actively working on.** Link them to topics and decisions as you go.
- **Use `brain map` to spot gaps.** Orphan entities with no relations are knowledge that isn't connected to anything — either link them or ask why they exist.

### Week 2 — Connect Claude Code
- **Let Claude save knowledge during conversations.** With MCP active, tell Claude "save this to the brain" when you learn something worth keeping. It uses `brain_save_entity` and `brain_episode` automatically.
- **Start conversations with context.** Add a line to your project's CLAUDE.md: "Check the brain (`brain_search`) for prior decisions before proposing new approaches."
- **Review what Claude saves.** AI-authored entities should be reviewed. Check `brain list` and scan for anything that's wrong or low-value.

### Week 3 — Automate maintenance
- **Write a cron job** that runs `brain health` and `brain index` daily. Catch integrity issues early.
- **Add `brain link`** to your post-session workflow so Obsidian wikilinks stay current.
- **Build a session-start script** that runs `brain search` for the topic you're about to work on and dumps context into your terminal.

### Beyond — Extension ideas
- **Semantic search** — `pip install starter-brain[search]` adds embedding-based similarity. Good for "what do I know that's related to X?" when keywords aren't enough.
- **Episode consolidation** — Write a script that reads episode logs and creates/updates entities from recurring themes. Turns daily notes into structured knowledge.
- **Multi-brain sync** — Run separate brains for different domains (work, personal, research). Build a merge tool that links entities across brains without copying content.
- **Custom entity types** — The type system is open. Add `meeting`, `bug`, `experiment`, `contact`, `tool` — whatever maps to how you think.
- **Contradiction detection** — Scan relations for entities that `CONTRADICTS` each other or where confidence scores diverge. Surface these for review.
- **Dashboard** — Build a simple web UI over `brain_stats` + `brain_mind_map` to visualize your knowledge graph outside Obsidian.

## Further Reading

Repos and resources worth studying if you want to go deeper on memory, knowledge graphs, and AI orchestration:

### Memory & Knowledge Graphs
| Repo | What it does | Why it's interesting |
|---|---|---|
| [Graphiti](https://github.com/getzep/graphiti) | Temporal knowledge graph for AI agents | Episode-based memory with time decay, contradiction detection, entity deduplication |
| [Mem0](https://github.com/mem0ai/mem0) | Memory layer for AI apps | Automatic memory extraction from conversations, user/session/agent memory scopes |
| [Cognee](https://github.com/topoteretes/cognee) | Knowledge graph from unstructured data | GraphRAG pipeline, entity extraction, relationship inference |
| [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) | Obsidian plugin for semantic links | Embedding-based "find related notes" inside Obsidian |
| [Khoj](https://github.com/khoj-ai/khoj) | AI second brain | Search across markdown/org files, chat with your notes, self-hosted |

### Agent Orchestration
| Repo | What it does | Why it's interesting |
|---|---|---|
| [CAMEL-AI](https://github.com/camel-ai/camel) | Multi-agent framework | Role-playing agents, task decomposition, the engine behind OASIS/MiroFish |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Multi-agent task orchestration | Agent roles, delegation, sequential/parallel task execution |
| [AutoGen](https://github.com/microsoft/autogen) | Multi-agent conversation framework | Conversational agents that collaborate, code execution, human-in-the-loop |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Stateful agent workflows | Graph-based agent orchestration, persistence, human approval gates |
| [Paperclip](https://github.com/ArcadeAI/paperclip) | Agent safety patterns | Budget hard-stops, task ancestry, heartbeat protocols — patterns for agents you can trust |

### MCP (Model Context Protocol)
| Repo | What it does | Why it's interesting |
|---|---|---|
| [MCP Specification](https://github.com/modelcontextprotocol/specification) | The protocol spec | How tools, resources, and prompts are exposed to AI models |
| [MCP Servers](https://github.com/modelcontextprotocol/servers) | Reference server implementations | Filesystem, GitHub, Slack, PostgreSQL — patterns for building your own |
| [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) | Curated list | Find existing MCP servers before building your own |

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
