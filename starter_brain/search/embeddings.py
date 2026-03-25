"""Semantic search using sentence-transformers + hnswlib.

Requires: pip install 'starter-brain[search]'
  which installs: numpy, sentence-transformers, hnswlib
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starter_brain.kg.graph import Brain

_INDEX_FILE = ".semantic_index.json"
_VECTORS_FILE = ".semantic_vectors.bin"
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_index_paths(brain: "Brain") -> tuple[Path, Path]:
    return (
        brain.knowledge_dir / _INDEX_FILE,
        brain.knowledge_dir / _VECTORS_FILE,
    )


def _entity_text(entity: dict) -> str:
    """Combine name, tags, and body into a single string for embedding."""
    parts = [entity.get("name", "")]
    tags = entity.get("tags") or []
    if tags:
        parts.append(" ".join(str(t) for t in tags))
    body = entity.get("body", "").strip()
    if body:
        parts.append(body[:2000])  # cap body length
    return " ".join(parts)


def build_semantic_index(brain: "Brain", model_name: str = _MODEL_NAME) -> Path:
    """Build (or rebuild) the HNSW semantic index for all entities.

    Writes two files into knowledge_dir:
      .semantic_index.json  — id→position mapping + metadata
      .semantic_vectors.bin — hnswlib index file
    Returns the path to the JSON manifest.
    """
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
        import hnswlib
    except ImportError as exc:
        raise ImportError(
            "Semantic search requires: pip install 'starter-brain[search]'\n"
            f"Missing: {exc}"
        ) from exc

    all_entities = brain.list_entities()
    if not all_entities:
        raise ValueError("No entities found in brain — nothing to index.")

    # Skip entities missing an id (malformed frontmatter)
    entities = [e for e in all_entities if e.get("id")]
    if not entities:
        raise ValueError("No valid entities with IDs found.")

    model = SentenceTransformer(model_name)
    texts = [_entity_text(e) for e in entities]
    ids = [e["id"] for e in entities]

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    n = len(entities)

    # Build HNSW index
    index = hnswlib.Index(space="cosine", dim=dim)
    index.init_index(max_elements=max(n * 2, 100), ef_construction=200, M=16)
    index.add_items(embeddings, list(range(n)))
    index.set_ef(50)

    index_path, vectors_path = _get_index_paths(brain)
    index.save_index(str(vectors_path))

    manifest = {
        "model": model_name,
        "dim": dim,
        "count": n,
        "ids": ids,
    }
    index_path.write_text(json.dumps(manifest, indent=2))

    return index_path


def semantic_search(
    brain: "Brain",
    query: str,
    limit: int = 10,
    model_name: str = _MODEL_NAME,
) -> list[dict]:
    """Run semantic search against the HNSW index.

    Automatically builds the index if it doesn't exist.
    Returns up to `limit` entities, each with a `_distance` key (0=identical, 2=opposite).
    """
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
        import hnswlib
    except ImportError as exc:
        raise ImportError(
            "Semantic search requires: pip install 'starter-brain[search]'\n"
            f"Missing: {exc}"
        ) from exc

    index_path, vectors_path = _get_index_paths(brain)

    # Build index if missing or stale
    if not index_path.exists() or not vectors_path.exists():
        build_semantic_index(brain, model_name=model_name)

    manifest = json.loads(index_path.read_text())
    ids = manifest["ids"]
    dim = manifest["dim"]
    stored_model = manifest.get("model", model_name)

    model = SentenceTransformer(stored_model)
    index = hnswlib.Index(space="cosine", dim=dim)
    index.load_index(str(vectors_path), max_elements=len(ids) * 2)
    index.set_ef(50)

    query_vec = model.encode([query], convert_to_numpy=True)
    k = min(limit, len(ids))
    labels, distances = index.knn_query(query_vec, k=k)

    results = []
    for pos, dist in zip(labels[0], distances[0]):
        entity_id = ids[pos]
        try:
            entity = brain.read_entity(entity_id)
            entity["_distance"] = float(dist)
            results.append(entity)
        except Exception:
            continue

    return results
