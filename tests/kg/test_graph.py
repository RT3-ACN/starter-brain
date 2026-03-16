import os
import tempfile
from pathlib import Path
from starter_brain.kg.graph import Brain

SAMPLE_ENTITY = """\
---
type: topic
id: topics/machine-learning
name: Machine Learning
created: 2026-03-16
updated: 2026-03-16
author: testuser
status: active
confidence: null
importance: 5
tags: [ai, ml]
relations:
  - type: REFERENCES
    target: topics/neural-networks
---

## Notes
ML is great.
"""


def make_brain(tmp_path):
    """Create a Brain pointed at a temp knowledge/ dir."""
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_create_and_read_entity(tmp_path):
    brain = make_brain(tmp_path)
    entity = brain.create_entity(
        type="topic",
        slug="machine-learning",
        name="Machine Learning",
        author="testuser",
        tags=["ai", "ml"],
        body="## Notes\nML is great.\n",
    )
    assert entity["id"] == "topics/machine-learning"
    assert entity["name"] == "Machine Learning"

    read_back = brain.read_entity("topics/machine-learning")
    assert read_back["name"] == "Machine Learning"
    assert read_back["tags"] == ["ai", "ml"]
    assert "ML is great" in read_back["body"]


def test_create_entity_writes_file(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="test", name="Test", author="testuser")
    path = brain.knowledge_dir / "entities" / "topics" / "test.md"
    assert path.exists()
    content = path.read_text()
    assert "type: topic" in content
    assert "id: topics/test" in content


def test_list_entities_by_type(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser")
    brain.create_entity(type="topic", slug="b", name="B", author="testuser")
    brain.create_entity(type="decision", slug="c", name="C", author="testuser")
    topics = brain.list_entities("topic")
    assert len(topics) == 2
    all_entities = brain.list_entities()
    assert len(all_entities) == 3


def test_update_entity(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="x", name="X", author="testuser")
    brain.update_entity("topics/x", name="X Updated", tags=["new"])
    updated = brain.read_entity("topics/x")
    assert updated["name"] == "X Updated"
    assert updated["tags"] == ["new"]


def test_delete_entity(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="gone", name="Gone", author="testuser")
    brain.delete_entity("topics/gone")
    path = brain.knowledge_dir / "entities" / "topics" / "gone.md"
    assert not path.exists()


def test_custom_type_creates_directory(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="campaign", slug="launch", name="Launch", author="testuser")
    path = brain.knowledge_dir / "entities" / "campaigns" / "launch.md"
    assert path.exists()


def test_atomic_write(tmp_path):
    """Entity write should not leave partial files on error."""
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="safe", name="Safe", author="testuser")
    path = brain.knowledge_dir / "entities" / "topics" / "safe.md"
    assert path.exists()
    # No .tmp files left behind
    tmp_files = list(brain.knowledge_dir.rglob("*.tmp"))
    assert len(tmp_files) == 0
