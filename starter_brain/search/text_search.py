"""Full-text search across entities — always available, no extra dependencies."""
from __future__ import annotations
from starter_brain.kg.graph import Brain

def text_search(brain: Brain, query: str, limit: int = 20) -> list[dict]:
    query_lower = query.lower()
    results = []
    for entity in brain.list_entities():
        score = 0
        name = entity.get("name", "").lower()
        tags = " ".join(entity.get("tags", [])).lower()
        body = entity.get("body", "").lower()
        if query_lower in name:
            score += 3
        if query_lower in tags:
            score += 2
        if query_lower in body:
            score += 1
        if score > 0:
            results.append({**entity, "_score": score})
    results.sort(key=lambda x: x["_score"], reverse=True)
    return results[:limit]
