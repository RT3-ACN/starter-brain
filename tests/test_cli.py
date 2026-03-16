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


def test_init(tmp_path):
    rc, out, _ = run_brain("init", str(tmp_path / "knowledge"), "--author", "testuser")
    assert rc == 0
    assert (tmp_path / "knowledge" / ".brainrc").exists()
    assert (tmp_path / "knowledge" / "entities" / "topics").is_dir()
    assert (tmp_path / "knowledge" / "README.md").exists()
    assert (tmp_path / "knowledge" / "entities" / "topics" / "starter-brain.md").exists()


def test_create_and_show(tmp_path):
    run_brain("init", str(tmp_path / "knowledge"), "--author", "testuser")
    kdir = str(tmp_path / "knowledge")
    rc, out, _ = run_brain("create", "topic", "ml", "--name", "Machine Learning", "--dir", kdir)
    assert rc == 0
    rc, out, _ = run_brain("show", "topics/ml", "--dir", kdir)
    assert rc == 0
    assert "Machine Learning" in out


def test_list(tmp_path):
    run_brain("init", str(tmp_path / "knowledge"), "--author", "testuser")
    kdir = str(tmp_path / "knowledge")
    run_brain("create", "topic", "a", "--name", "A", "--dir", kdir)
    run_brain("create", "topic", "b", "--name", "B", "--dir", kdir)
    rc, out, _ = run_brain("list", "topic", "--dir", kdir)
    assert rc == 0
    assert "A" in out
    assert "B" in out


def test_search(tmp_path):
    run_brain("init", str(tmp_path / "knowledge"), "--author", "testuser")
    kdir = str(tmp_path / "knowledge")
    run_brain("create", "topic", "ml", "--name", "Machine Learning", "--dir", kdir)
    rc, out, _ = run_brain("search", "machine", "--dir", kdir)
    assert rc == 0
    assert "Machine Learning" in out


def test_health(tmp_path):
    run_brain("init", str(tmp_path / "knowledge"), "--author", "testuser")
    kdir = str(tmp_path / "knowledge")
    rc, out, _ = run_brain("health", "--dir", kdir)
    assert rc == 0
    assert "0 errors" in out.lower() or "healthy" in out.lower()
