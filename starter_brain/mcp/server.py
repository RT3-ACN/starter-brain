"""MCP server exposing starter-brain tools to Claude Code."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from starter_brain.kg.graph import Brain, BrainError, pluralize_type, singularize_type
from starter_brain.kg.episodes import log_episode
from starter_brain.kg.index import build_index
from starter_brain.kg.links import regenerate_links
from starter_brain.search.text_search import text_search


def _load_brainrc(kdir: Path) -> dict:
    rc_path = kdir / ".brainrc"
    if rc_path.exists():
        return yaml.safe_load(rc_path.read_text()) or {}
    return {}


def handle_brain_search(brain: Brain, params: dict) -> list[dict]:
    query = params.get("query", "")
    limit = params.get("limit", 20)
    results = text_search(brain, query, limit=limit)
    return [{"id": r["id"], "name": r["name"], "type": r["type"], "tags": r.get("tags", [])} for r in results]


def handle_brain_semantic_search(brain: Brain, params: dict) -> list[dict]:
    try:
        from starter_brain.search.embeddings import semantic_search
        return semantic_search(brain, params.get("query", ""), n=params.get("limit", 10))
    except ImportError:
        return [{"error": "Semantic search requires starter-brain[search]."}]


def handle_brain_graph_search(brain: Brain, params: dict) -> list[dict]:
    try:
        from starter_brain.search.graph_search import graph_search
        return graph_search(brain, params.get("query", ""), n=params.get("limit", 5), depth=params.get("depth", 2))
    except ImportError:
        return [{"error": "Graph search requires starter-brain[search]."}]


def handle_brain_mind_map(brain: Brain, params: dict) -> dict:
    entity_id = params.get("id", "")
    depth = params.get("depth", 2)
    visited = {}
    edges = []
    _walk(brain, entity_id, depth, visited, edges)
    return {"nodes": visited, "edges": edges}


def _walk(brain, entity_id, depth, visited, edges):
    if entity_id in visited or depth < 0:
        return
    try:
        entity = brain.read_entity(entity_id)
    except BrainError:
        visited[entity_id] = {"name": "[missing]", "type": "unknown"}
        return
    visited[entity_id] = {"name": entity["name"], "type": entity.get("type", "")}
    if depth > 0:
        for rel in entity.get("relations", []):
            target = rel["target"]
            edges.append({"source": entity_id, "type": rel["type"], "target": target})
            _walk(brain, target, depth - 1, visited, edges)


def handle_brain_entity(brain: Brain, params: dict) -> dict:
    entity_id = params.get("id", "")
    entity = brain.read_entity(entity_id)
    return {k: v for k, v in entity.items()}


def handle_brain_save_entity(brain: Brain, kdir: Path, params: dict) -> dict:
    brainrc = _load_brainrc(kdir)
    entity_type = params.get("type", "topic")
    slug = params.get("slug", "")
    name = params.get("name", slug)
    author = params.get("author", brainrc.get("author", "ai"))
    tags = params.get("tags", [])
    relations = params.get("relations", [])
    body = params.get("body", "")

    singular = singularize_type(entity_type)
    plural = pluralize_type(singular)
    entity_id = f"{plural}/{slug}"
    try:
        existing = brain.read_entity(entity_id)
        updated = brain.update_entity(entity_id, name=name, tags=tags, relations=relations, body=body)
        regenerate_links(brain)
        return updated
    except BrainError:
        entity = brain.create_entity(type=entity_type, slug=slug, name=name, author=author,
                                     tags=tags, relations=relations, body=body)
        regenerate_links(brain)
        return entity


def handle_brain_episode(kdir: Path, params: dict) -> str:
    brainrc = _load_brainrc(kdir)
    author = params.get("author", brainrc.get("author", "ai"))
    episode_type = params.get("type", "reflection")
    summary = params.get("summary", "")
    entities = params.get("entities", [])
    importance = params.get("importance", 5)
    path = log_episode(kdir, author, episode_type, summary, entities, importance)
    return f"Episode logged to {path.name}"


def handle_brain_stats(brain: Brain) -> dict:
    entities = brain.list_entities()
    type_counts = {}
    relation_count = 0
    for e in entities:
        t = e.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        relation_count += len(e.get("relations", []))
    return {
        "total_entities": len(entities),
        "by_type": type_counts,
        "total_relations": relation_count,
    }


def serve(knowledge_dir: str):
    """Start the MCP server."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        print("MCP server requires the mcp package. Install with: pip install starter-brain[mcp]", file=sys.stderr)
        sys.exit(1)

    import asyncio

    kdir = Path(knowledge_dir)
    brain = Brain(kdir)
    server = Server("starter-brain")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="brain_search", description="Full-text search across entities",
                 inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, "required": ["query"]}),
            Tool(name="brain_semantic_search", description="Semantic similarity search",
                 inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}}, "required": ["query"]}),
            Tool(name="brain_graph_search", description="Semantic search + BFS expansion",
                 inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 5}, "depth": {"type": "integer", "default": 2}}, "required": ["query"]}),
            Tool(name="brain_mind_map", description="Walk N hops from seed entity via relations",
                 inputSchema={"type": "object", "properties": {"id": {"type": "string"}, "depth": {"type": "integer", "default": 2}}, "required": ["id"]}),
            Tool(name="brain_entity", description="Read a specific entity by ID",
                 inputSchema={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
            Tool(name="brain_save_entity", description="Create or update an entity",
                 inputSchema={"type": "object", "properties": {
                     "type": {"type": "string"}, "slug": {"type": "string"}, "name": {"type": "string"},
                     "tags": {"type": "array", "items": {"type": "string"}},
                     "relations": {"type": "array", "items": {"type": "object"}},
                     "body": {"type": "string"},
                 }, "required": ["type", "slug", "name"]}),
            Tool(name="brain_episode", description="Log an episode entry",
                 inputSchema={"type": "object", "properties": {
                     "summary": {"type": "string"}, "type": {"type": "string", "default": "reflection"},
                     "entities": {"type": "array", "items": {"type": "string"}},
                     "importance": {"type": "integer", "default": 5},
                 }, "required": ["summary"]}),
            Tool(name="brain_stats", description="Knowledge graph statistics",
                 inputSchema={"type": "object", "properties": {}}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "brain_search":
                result = handle_brain_search(brain, arguments)
            elif name == "brain_semantic_search":
                result = handle_brain_semantic_search(brain, arguments)
            elif name == "brain_graph_search":
                result = handle_brain_graph_search(brain, arguments)
            elif name == "brain_mind_map":
                result = handle_brain_mind_map(brain, arguments)
            elif name == "brain_entity":
                result = handle_brain_entity(brain, arguments)
            elif name == "brain_save_entity":
                result = handle_brain_save_entity(brain, kdir, arguments)
            elif name == "brain_episode":
                result = handle_brain_episode(kdir, arguments)
            elif name == "brain_stats":
                result = handle_brain_stats(brain)
            else:
                result = {"error": f"Unknown tool: {name}"}
            return [TextContent(type="text", text=json.dumps(result, default=str))]
        except BrainError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)

    asyncio.run(run())
