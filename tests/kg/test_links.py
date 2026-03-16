from starter_brain.kg.graph import Brain
from starter_brain.kg.links import regenerate_links


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_regenerate_links_adds_related_section(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser",
                        relations=[{"type": "REFERENCES", "target": "topics/b"}])
    brain.create_entity(type="topic", slug="b", name="B", author="testuser")
    regenerate_links(brain)
    content = (brain.entities_dir / "topics" / "a.md").read_text()
    assert "## Related" in content
    assert "[[topics/b|b]]" in content


def test_regenerate_links_idempotent(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="x", name="X", author="testuser",
                        relations=[{"type": "INFORMS", "target": "decisions/y"}])
    brain.create_entity(type="decision", slug="y", name="Y", author="testuser")
    regenerate_links(brain)
    content1 = (brain.entities_dir / "topics" / "x.md").read_text()
    regenerate_links(brain)
    content2 = (brain.entities_dir / "topics" / "x.md").read_text()
    assert content1 == content2
