"""Episode logging — daily activity journals."""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path


def log_episode(knowledge_dir, author, episode_type, summary, entities=None, importance=5):
    knowledge_dir = Path(knowledge_dir)
    episodes_dir = knowledge_dir / "episodes"
    episodes_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    path = episodes_dir / f"{today}.md"
    now = datetime.now().strftime("%H:%M")
    entry = f"\n## {author} | {now} | {episode_type} | importance:{importance}\n"
    entry += f"{summary}\n"
    if entities:
        entry += f"Entities: {', '.join(entities)}\n"
    if path.exists():
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {today}\n{entry}")
    return path


def read_episodes(knowledge_dir, date_filter=None):
    knowledge_dir = Path(knowledge_dir)
    episodes_dir = knowledge_dir / "episodes"
    if not episodes_dir.exists():
        return []
    results = []
    pattern = re.compile(r"^## (\S+) \| (\d{2}:\d{2}) \| (\S+) \| importance:(\d+)$")
    files = sorted(episodes_dir.glob("*.md"))
    if date_filter:
        files = [f for f in files if f.stem == date_filter]
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        current_entry = None
        for line in lines:
            m = pattern.match(line)
            if m:
                if current_entry:
                    results.append(current_entry)
                current_entry = {"date": f.stem, "author": m.group(1), "time": m.group(2),
                                 "type": m.group(3), "importance": int(m.group(4)), "summary": "", "entities": []}
            elif current_entry:
                if line.startswith("Entities: "):
                    current_entry["entities"] = [e.strip() for e in line[10:].split(",")]
                elif line.strip():
                    current_entry["summary"] += line + "\n"
        if current_entry:
            results.append(current_entry)
    return results
