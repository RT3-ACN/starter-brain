from datetime import date, datetime
from pathlib import Path
from starter_brain.kg.episodes import log_episode, read_episodes


def test_log_episode_creates_file(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / "episodes").mkdir()
    log_episode(knowledge_dir=kdir, author="testuser", episode_type="research",
                summary="Tested episode logging.", entities=["topics/testing"], importance=6)
    today = date.today().isoformat()
    path = kdir / "episodes" / f"{today}.md"
    assert path.exists()
    content = path.read_text()
    assert "testuser" in content
    assert "research" in content
    assert "Tested episode logging." in content
    assert "topics/testing" in content


def test_log_episode_appends(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / "episodes").mkdir()
    log_episode(kdir, "user1", "research", "First entry.", [], 5)
    log_episode(kdir, "user2", "decision", "Second entry.", [], 7)
    today = date.today().isoformat()
    content = (kdir / "episodes" / f"{today}.md").read_text()
    assert "First entry." in content
    assert "Second entry." in content


def test_read_episodes(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    (kdir / "episodes").mkdir()
    log_episode(kdir, "user1", "research", "Entry.", [], 5)
    episodes = read_episodes(kdir)
    assert len(episodes) >= 1
    assert episodes[0]["author"] == "user1"
