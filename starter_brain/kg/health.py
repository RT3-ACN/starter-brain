"""Validate knowledge graph integrity."""
from __future__ import annotations
from starter_brain.kg.graph import Brain, REQUIRED_FIELDS, BrainError

def check_health(brain: Brain) -> dict:
    errors = []
    warnings = []
    entity_ids: set[str] = set()
    entity_count = 0

    for f in brain.entities_dir.rglob("*.md"):
        entity_count += 1
        try:
            entity = brain._parse_file(f)
        except BrainError as e:
            errors.append(f"Parse error in {f}: {e}")
            continue
        eid = entity.get("id", "")
        for field in REQUIRED_FIELDS:
            if field not in entity or entity[field] is None:
                errors.append(f"{eid or f.name}: missing required field '{field}'")
        if eid in entity_ids:
            errors.append(f"Duplicate entity ID: {eid}")
        entity_ids.add(eid)
        for rel in entity.get("relations", []):
            target = rel.get("target", "")
            target_path = brain._entity_path(target)
            if not target_path.exists():
                errors.append(f"{eid}: broken relation {rel.get('type', '?')} -> {target}")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {"entities": entity_count, "ids": len(entity_ids)},
    }
