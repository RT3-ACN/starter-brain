"""Relation validation and acyclicity checking via DFS."""
from __future__ import annotations

from starter_brain.kg.graph import Brain, BrainError, EntityNotFoundError

ACYCLIC_RELATIONS = {"SUPERSEDED_BY", "DEPENDS_ON", "PART_OF"}


class CycleError(BrainError):
    pass


def validate_relation(brain: Brain, relation: dict) -> None:
    target = relation.get("target", "")
    try:
        brain.read_entity(target)
    except EntityNotFoundError:
        raise BrainError(f"Relation target not found: {target}")


def check_acyclicity(brain: Brain, source_id: str, relation_type: str, target_id: str) -> None:
    if relation_type not in ACYCLIC_RELATIONS:
        return
    visited: set[str] = set()
    stack = [target_id]
    while stack:
        current = stack.pop()
        if current == source_id:
            raise CycleError(f"Adding {relation_type} from {source_id} to {target_id} would create a cycle")
        if current in visited:
            continue
        visited.add(current)
        try:
            entity = brain.read_entity(current)
        except EntityNotFoundError:
            continue
        for rel in entity.get("relations", []):
            if rel.get("type") == relation_type:
                stack.append(rel["target"])
