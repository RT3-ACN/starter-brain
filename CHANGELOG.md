# Changelog

## 0.3.0 — 2026-03-25

### Bug fixes
- **Singular entity paths** — `create_entity` and `list_entities` in `graph.py` now use singular type folder names (`topic/`, `person/`, `decision/`) instead of plural (`topics/`, `people/`, `decisions/`). Resolves folder fragmentation where entities were scattered across both plural and singular directories depending on whether they were created via CLI, MCP, or manually. `brain_save_entity` in the MCP server updated to match.
- `DEFAULT_TYPES` constant updated to singular names throughout.
- `cmd_init` creates singular folders on new brain initialization.

### New commands
- `brain stats` — prints total entity count, relation count, and a breakdown by entity type. Matches the `brain_stats` MCP tool which was already available to Claude Code but had no CLI equivalent.

### Docs
- README: added three Mermaid diagrams — **System Architecture** (how `~/knowledge/`, CLI, MCP, Obsidian, and Claude Code connect), **Session Lifecycle** (Orient → Work → Capture → Index loop), and **Entity & Relation Model** (all 8 types with example relation patterns).

## 0.2.0 — 2026-03-25

### New seed patterns
- `patterns/diagram-freshness` — `sources:` field convention + audit script pattern for detecting stale process docs and diagrams. Three-layer system: data (frontmatter), detection (mtime comparison), trigger (session integration).
- `patterns/auto-memory` — Four-type persistent memory layer (user, feedback, project, reference) with MEMORY.md index. Persists *how to work with this person* across sessions, compounding faster than entity-level knowledge.

### Updated seeds
- `patterns/session-workflow` — capture phase now references diagram staleness check and links to `diagram-freshness` and `auto-memory` patterns.

### Updated templates
- `CLAUDE.md.tmpl` — added auto-memory type guide (user/feedback/project/reference) and diagram staleness check instructions to the session-end workflow.

### Updated docs
- README "What to Build Next" — added Week 3 diagram staleness entry and new Week 4 section on skills/hook orchestration layer (session-start hook, session-close skill, auto-memory layer, PostToolUse hooks).

## 0.1.0 — 2026-03-17

Initial release.

### Features
- File-based knowledge graph with YAML frontmatter entities
- 12-command CLI (`brain init/create/show/list/search/semantic/episode/map/link/index/health/mcp`)
- MCP server with 8 tools for Claude Code integration
- Auto-generates CLAUDE.md on `brain init` for Claude Code context
- `--with-mcp` flag auto-configures `~/.claude/mcp.json`
- Obsidian-compatible: wikilinks, graph view, vault-ready directory structure
- Atomic writes (tempfile + os.replace)
- Entity types: topic, insight, decision, pattern, person, project, research, hypothesis (any string accepted)
- Relation types: REFERENCES, INFORMS, DERIVED_FROM, SUPERSEDED_BY, CONTRADICTS, etc. (any string accepted)
- Episode logging with daily rollup files
- Health checker for integrity validation
- Text search across all entities
- Semantic search stub (requires `[search]` extra with torch)
- Templates with seed entities for new brains

### Architecture
- Pure Python, single dependency (pyyaml)
- MCP optional (`pip install starter-brain[mcp]`)
- Semantic search optional (`pip install starter-brain[search]`)
- Zero cloud dependencies, zero API keys, zero telemetry
- 38 tests passing
