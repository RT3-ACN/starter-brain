# Contributing to starter-brain

## Branch Rules

**`main` is protected.** Direct pushes are blocked. All changes go through a pull request with at least one review approval before merging.

## Workflow

```bash
# 1. Branch off main
git checkout main && git pull
git checkout -b your-branch-name

# 2. Make changes, commit
git add -p   # stage intentionally, not blindly
git commit -m "short description of what and why"

# 3. Push and open PR
git push -u origin your-branch-name
gh pr create --title "..." --body "..."

# 4. Get a review, address feedback, merge
```

## Commit Style

- **Prefix:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- **Subject line:** imperative, lowercase, ≤72 chars — "add diagram-freshness seed pattern"
- **Body (optional):** the *why*, not the *what* — what problem does this solve?

## PR Requirements

- Describe what changed and why in the PR body
- Link to any issue it closes
- Tests pass: `pytest`
- If adding a seed pattern: include an example, explain when to apply it

## What Goes in Seeds vs Code

| Change | Seeds (`templates/`) | Code (`starter_brain/`) |
|--------|---------------------|------------------------|
| New workflow pattern | ✅ seed pattern | ❌ |
| New brain behavior | ❌ | ✅ |
| Improved template text | ✅ | ❌ |
| New CLI command | ❌ | ✅ |
| New MCP tool | ❌ | ✅ |

## Tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
pytest
```

Tests live in `tests/`. Add a test for any new code path. Seed-only changes don't require new tests.

## Versioning

Follows semantic versioning. Update `CHANGELOG.md` with every PR:
- **patch** (0.1.x) — bug fixes, doc improvements
- **minor** (0.x.0) — new features, new seed patterns
- **major** (x.0.0) — breaking changes to CLI, MCP API, or entity format
