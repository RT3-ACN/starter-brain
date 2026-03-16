from starter_brain.kg.graph import Brain
from starter_brain.search.text_search import text_search


def make_brain(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / ".brainrc").write_text("version: 1\nauthor: testuser\ncreated: 2026-03-16\nsearch: false\n")
    return Brain(kdir)


def test_search_by_name(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="Machine Learning", author="testuser")
    brain.create_entity(type="topic", slug="db", name="Databases", author="testuser")
    results = text_search(brain, "machine")
    assert len(results) == 1
    assert results[0]["id"] == "topics/ml"


def test_search_by_tag(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="ML", author="testuser", tags=["artificial-intelligence"])
    results = text_search(brain, "artificial")
    assert len(results) == 1


def test_search_by_body(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="ML", author="testuser", body="Deep neural networks are fascinating.\n")
    results = text_search(brain, "neural")
    assert len(results) == 1


def test_search_no_results(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="ML", author="testuser")
    results = text_search(brain, "zzzznotfound")
    assert len(results) == 0


def test_search_case_insensitive(tmp_path):
    brain = make_brain(tmp_path)
    brain.create_entity(type="topic", slug="ml", name="Machine Learning", author="testuser")
    results = text_search(brain, "MACHINE")
    assert len(results) == 1
