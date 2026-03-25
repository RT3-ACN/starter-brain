"""Core knowledge graph — entity CRUD with YAML frontmatter + markdown body."""
from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TYPES = [
    "topic", "insight", "research", "decision",
    "pattern", "person", "project", "hypothesis",
]

# Irregular plurals — add entries here for new irregular types
_PLURAL_MAP = {"person": "people", "hypothesis": "hypotheses", "research": "research"}
_SINGULAR_MAP = {v: k for k, v in _PLURAL_MAP.items()}


def pluralize_type(singular: str) -> str:
    """topic -> topics, person -> people, hypothesis -> hypotheses."""
    if singular in _PLURAL_MAP:
        return _PLURAL_MAP[singular]
    if singular.endswith("s"):
        return singular
    return singular + "s"


def singularize_type(plural: str) -> str:
    """topics -> topic, people -> person, hypotheses -> hypothesis."""
    if plural in _SINGULAR_MAP:
        return _SINGULAR_MAP[plural]
    if plural.endswith("s") and plural not in ("hypotheses",):
        return plural[:-1]
    return plural


REQUIRED_FIELDS = {"type", "id", "name", "created", "updated", "author", "status"}


class BrainError(Exception):
    pass


class EntityNotFoundError(BrainError):
    pass


class Brain:
    """Interface to a knowledge/ directory."""

    def __init__(self, knowledge_dir: str | Path):
        self.knowledge_dir = Path(knowledge_dir).expanduser()
        self.entities_dir = self.knowledge_dir / "entities"

    def _entity_path(self, entity_id: str) -> Path:
        return self.entities_dir / f"{entity_id}.md"

    def _parse_file(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            raise BrainError(f"No YAML frontmatter in {path}")
        parts = text.split("---", 2)
        if len(parts) < 3:
            raise BrainError(f"Malformed frontmatter in {path}")
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2].lstrip("\n")
        meta["body"] = body
        return meta

    def _write_entity(self, path: Path, meta: dict[str, Any], body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = {k: v for k, v in meta.items() if k != "body"}
        content = "---\n" + yaml.dump(fm, default_flow_style=False, sort_keys=False) + "---\n\n" + body

        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            os.write(fd, content.encode("utf-8"))
        finally:
            os.close(fd)
        try:
            os.replace(tmp_path, path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def create_entity(
        self,
        type: str,
        slug: str,
        name: str,
        author: str,
        status: str = "active",
        confidence: int | None = None,
        importance: int = 5,
        tags: list[str] | None = None,
        relations: list[dict] | None = None,
        body: str = "",
    ) -> dict[str, Any]:
        singular = singularize_type(type)
        entity_id = f"{singular}/{slug}"
        today = date.today().isoformat()
        meta = {
            "type": singular,
            "id": entity_id,
            "name": name,
            "created": today,
            "updated": today,
            "author": author,
            "status": status,
            "confidence": confidence,
            "importance": importance,
            "tags": tags or [],
            "relations": relations or [],
        }
        path = self._entity_path(entity_id)
        if path.exists():
            raise BrainError(f"Entity already exists: {entity_id}")
        self._write_entity(path, meta, body)
        meta["body"] = body
        return meta

    def read_entity(self, entity_id: str) -> dict[str, Any]:
        path = self._entity_path(entity_id)
        if not path.exists():
            raise EntityNotFoundError(f"Entity not found: {entity_id}")
        return self._parse_file(path)

    def update_entity(self, entity_id: str, **updates: Any) -> dict[str, Any]:
        entity = self.read_entity(entity_id)
        body = updates.pop("body", entity.get("body", ""))
        for k, v in updates.items():
            entity[k] = v
        entity["updated"] = date.today().isoformat()
        path = self._entity_path(entity_id)
        self._write_entity(path, entity, body)
        entity["body"] = body
        return entity

    def delete_entity(self, entity_id: str) -> None:
        path = self._entity_path(entity_id)
        if not path.exists():
            raise EntityNotFoundError(f"Entity not found: {entity_id}")
        path.unlink()

    def list_entities(self, type_filter: str | None = None) -> list[dict[str, Any]]:
        results = []
        if type_filter:
            dirname = singularize_type(type_filter)
            type_dir = self.entities_dir / dirname
            if not type_dir.exists():
                return []
            for f in sorted(type_dir.glob("*.md")):
                results.append(self._parse_file(f))
        else:
            if not self.entities_dir.exists():
                return []
            for f in sorted(self.entities_dir.rglob("*.md")):
                results.append(self._parse_file(f))
        return results
