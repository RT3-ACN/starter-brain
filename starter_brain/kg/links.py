"""Generate ## Related wikilink sections from YAML relations."""
from __future__ import annotations
import re
from starter_brain.kg.graph import Brain

RELATED_PATTERN = re.compile(r"(?:\n|^)## Related\n.*", re.DOTALL)

def _build_related_section(relations: list[dict]) -> str:
    if not relations:
        return ""
    lines = ["\n## Related"]
    for rel in relations:
        target = rel.get("target", "")
        slug = target.split("/")[-1] if "/" in target else target
        rel_type = rel.get("type", "REFERENCES")
        lines.append(f"- {rel_type}: [[{target}|{slug}]]")
    return "\n".join(lines) + "\n"

def regenerate_links(brain: Brain) -> int:
    count = 0
    for entity in brain.list_entities():
        entity_id = entity.get("id", "")
        relations = entity.get("relations", [])
        body = entity.get("body", "")
        new_body = RELATED_PATTERN.sub("", body).rstrip("\n")
        related = _build_related_section(relations)
        if related:
            new_body = new_body + "\n" + related
        if new_body != body.rstrip("\n"):
            brain.update_entity(entity_id, body=new_body + "\n" if new_body else "")
            count += 1
    return count
