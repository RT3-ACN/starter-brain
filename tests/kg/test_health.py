from starter_brain.kg.graph import Brain
from starter_brain.kg.health import check_health


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_healthy_brain(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser")
    report = check_health(brain)
    assert report["ok"] is True
    assert len(report["errors"]) == 0


def test_broken_relation(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser",
                        relations=[{"type": "REFERENCES", "target": "topics/nonexistent"}])
    report = check_health(brain)
    assert report["ok"] is False
    assert any("nonexistent" in e for e in report["errors"])


def test_missing_required_field(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="bad", name="Bad", author="testuser")
    path = brain.entities_dir / "topics" / "bad.md"
    content = path.read_text()
    content = content.replace("name: Bad\n", "")
    path.write_text(content)
    report = check_health(brain)
    assert report["ok"] is False
    assert any("name" in e for e in report["errors"])
