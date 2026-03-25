"""brain CLI — thin wrapper over starter_brain library."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from string import Template

import yaml

from starter_brain.kg.graph import Brain, BrainError
from starter_brain.kg.episodes import log_episode
from starter_brain.kg.index import build_index
from starter_brain.kg.links import regenerate_links
from starter_brain.kg.health import check_health
from starter_brain.search.text_search import text_search


def _get_templates_dir() -> Path:
    # First check inside the package (pip install)
    pkg_path = Path(__file__).parent / "templates"
    if pkg_path.exists():
        return pkg_path
    # Fallback to dev layout (repo root)
    dev_path = Path(__file__).parent.parent / "templates"
    if dev_path.exists():
        return dev_path
    return pkg_path


TEMPLATES_DIR = _get_templates_dir()


def cmd_init(args):
    kdir = Path(args.path or "./knowledge")
    if kdir.exists() and (kdir / ".brainrc").exists():
        print(f"Brain already exists at {kdir}")
        return 1

    kdir.mkdir(parents=True, exist_ok=True)
    entities_dir = kdir / "entities"
    for subdir in ["topic", "insight", "research", "decision", "pattern", "person", "project", "hypothesis"]:
        (entities_dir / subdir).mkdir(parents=True, exist_ok=True)
    (kdir / "episodes").mkdir(exist_ok=True)

    author = args.author or _prompt_author()
    today = date.today().isoformat()

    brainrc = {"version": 1, "author": author, "created": today, "search": False}
    (kdir / ".brainrc").write_text(yaml.dump(brainrc, default_flow_style=False))

    tmpl_path = TEMPLATES_DIR / "README.md.tmpl"
    if tmpl_path.exists():
        tmpl = Template(tmpl_path.read_text())
        (kdir / "README.md").write_text(tmpl.substitute(date=today, author=author))
    else:
        (kdir / "README.md").write_text(f"# Knowledge Graph\nCreated {today} by {author}\n")

    # Create CLAUDE.md for Claude Code integration
    claude_tmpl = TEMPLATES_DIR / "CLAUDE.md.tmpl"
    if claude_tmpl.exists():
        claude_md = Template(claude_tmpl.read_text()).substitute(date=today, author=author)
        (kdir / "CLAUDE.md").write_text(claude_md)

    brain = Brain(kdir)
    seeds_dir = TEMPLATES_DIR / "seeds"
    if seeds_dir.exists():
        for seed_file in seeds_dir.rglob("*.md"):
            content = Template(seed_file.read_text()).substitute(date=today, author=author)
            rel_path = seed_file.relative_to(seeds_dir)
            dest = entities_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)
    else:
        brain.create_entity(type="topic", slug="starter-brain", name="Starter Brain", author=author,
                            body="## Notes\nThis is your knowledge graph.\n")

    build_index(brain)

    print(f"Brain initialized at {kdir.resolve()}")
    print(f"Open '{kdir}' as an Obsidian vault to see your brain.")

    if args.with_mcp:
        _setup_mcp(kdir)

    return 0


def _prompt_author() -> str:
    if sys.stdin.isatty():
        return input("Username (for entity authorship): ").strip() or "user"
    return "user"


def _setup_mcp(kdir: Path):
    mcp_path = Path.home() / ".claude" / "mcp.json"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    config = {}
    if mcp_path.exists():
        config = json.loads(mcp_path.read_text())
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["starter-brain"] = {
        "command": "brain",
        "args": ["mcp", "serve", "--dir", str(kdir.resolve())],
    }
    mcp_path.write_text(json.dumps(config, indent=2))
    print(f"MCP configured at {mcp_path}")


def cmd_create(args):
    brain = Brain(args.dir)
    brainrc = _load_brainrc(brain.knowledge_dir)
    author = brainrc.get("author", "user")

    name = args.name
    if not name and sys.stdin.isatty():
        name = input("Name: ").strip()
    if not name:
        name = args.slug.replace("-", " ").title()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    try:
        entity = brain.create_entity(type=args.type, slug=args.slug, name=name, author=author, tags=tags)
        print(f"Created {entity['id']}: {entity['name']}")
    except BrainError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_show(args):
    brain = Brain(args.dir)
    try:
        entity = brain.read_entity(args.id)
    except BrainError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"# {entity['name']}")
    print(f"Type: {entity['type']}  |  Status: {entity['status']}  |  Author: {entity['author']}")
    if entity.get("tags"):
        print(f"Tags: {', '.join(entity['tags'])}")
    rels = entity.get("relations", [])
    if rels:
        print(f"Relations: {len(rels)}")
        for r in rels:
            print(f"  {r['type']} -> {r['target']}")
    body = entity.get("body", "").strip()
    if body:
        print(f"\n{body}")
    return 0


def cmd_list(args):
    brain = Brain(args.dir)
    entities = brain.list_entities(args.type)
    if not entities:
        print("No entities found.")
        return 0
    for e in entities:
        status = e.get("status", "")
        print(f"  {e['id']:40s} {e['name']:30s} [{status}]")
    print(f"\n{len(entities)} entities")
    return 0


def cmd_search(args):
    brain = Brain(args.dir)
    results = text_search(brain, args.query)
    if not results:
        print("No results.")
        return 0
    for r in results:
        print(f"  {r['id']:40s} {r['name']}")
    print(f"\n{len(results)} results")
    return 0


def cmd_semantic(args):
    try:
        from starter_brain.search.embeddings import semantic_search
    except ImportError:
        print("Semantic search requires starter-brain[search]. Install with: pip install starter-brain[search]")
        return 1
    brain = Brain(args.dir)
    results = semantic_search(brain, args.query)
    if not results:
        print("No results.")
        return 0
    for r in results:
        dist = r.get("_distance", "")
        print(f"  {r['id']:40s} {r['name']}  ({dist:.3f})" if dist else f"  {r['id']:40s} {r['name']}")
    print(f"\n{len(results)} results")
    return 0


def cmd_episode(args):
    kdir = Path(args.dir)
    brainrc = _load_brainrc(kdir)
    author = brainrc.get("author", "user")
    path = log_episode(kdir, author, args.type or "reflection", args.summary)
    print(f"Episode logged to {path.name}")
    return 0


def cmd_link(args):
    brain = Brain(args.dir)
    count = regenerate_links(brain)
    print(f"Updated {count} entities")
    return 0


def cmd_index(args):
    brain = Brain(args.dir)
    path = build_index(brain)
    count = len(json.loads(path.read_text()))
    print(f"Index rebuilt: {count} entities in {path.name}")
    return 0


def cmd_health(args):
    brain = Brain(args.dir)
    report = check_health(brain)
    if report["ok"]:
        print(f"Healthy. {report['stats']['entities']} entities, 0 errors.")
    else:
        print(f"{len(report['errors'])} errors found:")
        for e in report["errors"]:
            print(f"  - {e}")
    return 0 if report["ok"] else 1


def cmd_stats(args):
    brain = Brain(args.dir)
    entities = brain.list_entities()
    type_counts: dict[str, int] = {}
    relation_count = 0
    for e in entities:
        t = e.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        relation_count += len(e.get("relations", []))
    print(f"Entities: {len(entities)}  |  Relations: {relation_count}")
    print()
    for t, count in sorted(type_counts.items()):
        print(f"  {t:20s} {count}")
    return 0


def cmd_map(args):
    brain = Brain(args.dir)
    try:
        entity = brain.read_entity(args.id)
    except BrainError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    visited = set()
    _print_map(brain, args.id, args.depth, visited, indent=0)
    return 0


def _print_map(brain, entity_id, depth, visited, indent):
    if entity_id in visited or depth < 0:
        return
    visited.add(entity_id)
    try:
        entity = brain.read_entity(entity_id)
    except BrainError:
        print(" " * indent + f"[missing] {entity_id}")
        return
    prefix = " " * indent
    print(f"{prefix}{entity['name']} ({entity_id})")
    if depth > 0:
        for rel in entity.get("relations", []):
            print(f"{prefix}  --{rel['type']}--> ", end="")
            _print_map(brain, rel["target"], depth - 1, visited, indent + 4)


def _load_brainrc(kdir: Path) -> dict:
    rc_path = Path(kdir) / ".brainrc"
    if rc_path.exists():
        return yaml.safe_load(rc_path.read_text()) or {}
    return {}


def main():
    parser = argparse.ArgumentParser(prog="brain", description="starter-brain knowledge graph")
    _default_dir = str(Path("~/knowledge").expanduser())
    parser.add_argument("--dir", default=_default_dir, help="Path to knowledge/ directory")
    sub = parser.add_subparsers(dest="command")

    # Shared parent with --dir for subcommands that need it
    dir_parent = argparse.ArgumentParser(add_help=False)
    dir_parent.add_argument("--dir", default=_default_dir, help="Path to knowledge/ directory")

    p_init = sub.add_parser("init", help="Initialize a new brain")
    p_init.add_argument("path", nargs="?", help="Path for knowledge/ directory")
    p_init.add_argument("--author", help="Your username")
    p_init.add_argument("--with-mcp", action="store_true", help="Configure Claude Code MCP")

    p_create = sub.add_parser("create", help="Create an entity", parents=[dir_parent])
    p_create.add_argument("type", help="Entity type")
    p_create.add_argument("slug", help="URL-safe identifier")
    p_create.add_argument("--name", help="Human-readable name")
    p_create.add_argument("--tags", help="Comma-separated tags")

    p_show = sub.add_parser("show", help="Show an entity", parents=[dir_parent])
    p_show.add_argument("id", help="Entity ID")

    p_list = sub.add_parser("list", help="List entities", parents=[dir_parent])
    p_list.add_argument("type", nargs="?", help="Filter by type")

    p_search = sub.add_parser("search", help="Full-text search", parents=[dir_parent])
    p_search.add_argument("query", help="Search query")

    p_semantic = sub.add_parser("semantic", help="Semantic search (requires [search])", parents=[dir_parent])
    p_semantic.add_argument("query", help="Search query")

    p_episode = sub.add_parser("episode", help="Log an episode", parents=[dir_parent])
    p_episode.add_argument("summary", help="Episode summary")
    p_episode.add_argument("--type", help="Episode type (default: reflection)")

    p_map = sub.add_parser("map", help="Mind map", parents=[dir_parent])
    p_map.add_argument("id", help="Seed entity ID")
    p_map.add_argument("--depth", type=int, default=2, help="Hops to traverse")

    sub.add_parser("link", help="Regenerate wikilinks", parents=[dir_parent])
    sub.add_parser("index", help="Rebuild index.json", parents=[dir_parent])
    sub.add_parser("health", help="Validate brain integrity", parents=[dir_parent])
    sub.add_parser("stats", help="Entity and relation counts by type", parents=[dir_parent])

    p_mcp = sub.add_parser("mcp", help="MCP server", parents=[dir_parent])
    p_mcp.add_argument("action", choices=["serve"], help="MCP action")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "init": cmd_init,
        "create": cmd_create,
        "show": cmd_show,
        "list": cmd_list,
        "search": cmd_search,
        "semantic": cmd_semantic,
        "episode": cmd_episode,
        "map": cmd_map,
        "link": cmd_link,
        "index": cmd_index,
        "health": cmd_health,
        "stats": cmd_stats,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    elif args.command == "mcp":
        if args.action == "serve":
            from starter_brain.mcp.server import serve
            serve(args.dir)
            return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
