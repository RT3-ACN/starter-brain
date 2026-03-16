from starter_brain.kg.graph import Brain, BrainError
from starter_brain.kg.relations import validate_relation, check_acyclicity, CycleError


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_validate_relation_target_exists(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="target", name="Target", author="testuser")
    validate_relation(brain, {"type": "REFERENCES", "target": "topics/target"})


def test_validate_relation_target_missing(tmp_path):
    brain = make_brain(tmp_path)
    import pytest
    with pytest.raises(BrainError, match="not found"):
        validate_relation(brain, {"type": "REFERENCES", "target": "topics/nonexistent"})


def test_acyclicity_no_cycle(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser")
    brain.create_entity(type="topic", slug="b", name="B", author="testuser")
    brain.create_entity(type="topic", slug="c", name="C", author="testuser",
                        relations=[{"type": "DEPENDS_ON", "target": "topics/b"}])
    check_acyclicity(brain, source_id="topics/a", relation_type="DEPENDS_ON", target_id="topics/b")


def test_acyclicity_detects_cycle(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser",
                        relations=[{"type": "DEPENDS_ON", "target": "topics/b"}])
    brain.create_entity(type="topic", slug="b", name="B", author="testuser")
    import pytest
    with pytest.raises(CycleError):
        check_acyclicity(brain, source_id="topics/b", relation_type="DEPENDS_ON", target_id="topics/a")


def test_acyclicity_transitive_cycle(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser",
                        relations=[{"type": "DEPENDS_ON", "target": "topics/b"}])
    brain.create_entity(type="topic", slug="b", name="B", author="testuser",
                        relations=[{"type": "DEPENDS_ON", "target": "topics/c"}])
    brain.create_entity(type="topic", slug="c", name="C", author="testuser")
    import pytest
    with pytest.raises(CycleError):
        check_acyclicity(brain, source_id="topics/c", relation_type="DEPENDS_ON", target_id="topics/a")


def test_non_acyclic_relation_skips_check(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="a", name="A", author="testuser",
                        relations=[{"type": "REFERENCES", "target": "topics/b"}])
    brain.create_entity(type="topic", slug="b", name="B", author="testuser")
    check_acyclicity(brain, source_id="topics/b", relation_type="REFERENCES", target_id="topics/a")
