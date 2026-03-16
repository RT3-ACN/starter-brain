"""Test MCP tool handler functions directly (not the server transport)."""
import json
from pathlib import Path

from starter_brain.kg.graph import Brain
from starter_brain.mcp.server import (
    handle_brain_entity,
    handle_brain_save_entity,
    handle_brain_search,
    handle_brain_episode,
    handle_brain_stats,
    handle_brain_mind_map,
)


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: ai\ncreated: 2026-03-16\nsearch: false\n")
    (kdir / "episodes").mkdir()
    for d in ["topics", "insights", "decisions"]:
        (kdir / "entities" / d).mkdir(parents=True)
    return Brain(kdir), kdir


def test_save_and_read_entity(tmp_path):
    brain, kdir = make_brain(tmp_path)
    result = handle_brain_save_entity(brain, kdir, {"type": "topic", "slug": "test", "name": "Test Entity"})
    assert result["id"] == "topics/test"
    entity = handle_brain_entity(brain, {"id": "topics/test"})
    assert entity["name"] == "Test Entity"


def test_search(tmp_path):
    brain, kdir = make_brain(tmp_path)
    handle_brain_save_entity(brain, kdir, {"type": "topic", "slug": "ml", "name": "Machine Learning"})
    results = handle_brain_search(brain, {"query": "machine"})
    assert len(results) >= 1


def test_episode(tmp_path):
    brain, kdir = make_brain(tmp_path)
    result = handle_brain_episode(kdir, {"summary": "Did a thing", "type": "task"})
    assert "logged" in result.lower() or "episode" in result.lower()


def test_stats(tmp_path):
    brain, kdir = make_brain(tmp_path)
    handle_brain_save_entity(brain, kdir, {"type": "topic", "slug": "a", "name": "A"})
    handle_brain_save_entity(brain, kdir, {"type": "decision", "slug": "b", "name": "B"})
    stats = handle_brain_stats(brain)
    assert stats["total_entities"] == 2


def test_mind_map(tmp_path):
    brain, kdir = make_brain(tmp_path)
    handle_brain_save_entity(brain, kdir, {
        "type": "topic", "slug": "a", "name": "A",
        "relations": [{"type": "REFERENCES", "target": "topics/b"}],
    })
    handle_brain_save_entity(brain, kdir, {"type": "topic", "slug": "b", "name": "B"})
    result = handle_brain_mind_map(brain, {"id": "topics/a", "depth": 1})
    assert "topics/a" in str(result)
    assert "topics/b" in str(result)
