import json
from starter_brain.kg.graph import Brain
from starter_brain.kg.index import build_index


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_build_index(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="ML", author="testuser", tags=["ai"])
    brain.create_entity(type="decision", slug="use-ml", name="Use ML", author="testuser")
    index_path = build_index(brain)
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert "topics/ml" in data
    assert data["topics/ml"]["name"] == "ML"
    assert data["topics/ml"]["tags"] == ["ai"]
    assert "decisions/use-ml" in data
