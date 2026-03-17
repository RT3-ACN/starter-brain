# Changelog

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
