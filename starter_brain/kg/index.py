"""Build index.json — reverse lookup from entity ID to metadata."""
from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from starter_brain.kg.graph import Brain

def build_index(brain: Brain) -> Path:
    index = {}
    for entity in brain.list_entities():
        entity_id = entity.get("id", "")
        index[entity_id] = {
            "name": entity.get("name", ""),
            "type": entity.get("type", ""),
            "path": str(brain._entity_path(entity_id).relative_to(brain.knowledge_dir)),
            "tags": entity.get("tags", []),
            "status": entity.get("status", "active"),
        }
    index_path = brain.knowledge_dir / "index.json"
    fd, tmp = tempfile.mkstemp(dir=brain.knowledge_dir, suffix=".tmp")
    try:
        os.write(fd, json.dumps(index, indent=2, ensure_ascii=False).encode("utf-8"))
    finally:
        os.close(fd)
    try:
        os.replace(tmp, index_path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return index_path
