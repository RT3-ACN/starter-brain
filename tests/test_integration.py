"""End-to-end: init brain, create entities, search, link, index, health."""
import json
import subprocess
import sys
from pathlib import Path


def run_brain(*args, cwd=None):
    result = subprocess.run(
        [sys.executable, "-m", "starter_brain.cli", *args],
        capture_output=True, text=True, cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


def test_full_workflow(tmp_path):
    kdir = str(tmp_path / "knowledge")

    # Init
    rc, out, _ = run_brain("init", kdir, "--author", "e2e-test")
    assert rc == 0

    # Create entities with relations
    rc, _, _ = run_brain("create", "topic", "ai", "--name", "AI", "--tags", "tech,ml", "--dir", kdir)
    assert rc == 0
    rc, _, _ = run_brain("create", "topic", "ml", "--name", "Machine Learning", "--tags", "tech", "--dir", kdir)
    assert rc == 0
    rc, _, _ = run_brain("create", "decision", "use-ml", "--name", "Use ML for Search", "--dir", kdir)
    assert rc == 0

    # List
    rc, out, _ = run_brain("list", "--dir", kdir)
    assert rc == 0
    assert "entities" in out

    # Search
    rc, out, _ = run_brain("search", "machine", "--dir", kdir)
    assert rc == 0
    assert "Machine Learning" in out

    # Index
    rc, out, _ = run_brain("index", "--dir", kdir)
    assert rc == 0
    index_path = tmp_path / "knowledge" / "index.json"
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert "topics/ai" in data

    # Link
    rc, out, _ = run_brain("link", "--dir", kdir)
    assert rc == 0

    # Episode
    rc, out, _ = run_brain("episode", "Ran integration tests", "--dir", kdir)
    assert rc == 0

    # Health
    rc, out, _ = run_brain("health", "--dir", kdir)
    assert rc == 0

    # Map
    rc, out, _ = run_brain("map", "topics/ai", "--dir", kdir)
    assert rc == 0
    assert "AI" in out
