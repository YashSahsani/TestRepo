# Project Files

## Root

- `README.md` - project overview, demo commands, and artifact layout.
- `TEAM_CONTEXT.md` - team and product context for the prototype.
- `pyproject.toml` - Python package metadata and CLI entry point.
- `.gitignore` - generated and local-only file exclusions.
- `.editorconfig` - consistent editor formatting rules.
- `CONTRIBUTING.md` - setup and contribution guidelines.
- `SECURITY.md` - security and data-handling expectations.

## Python package

- `performance_review/cli.py` - command-line entry point.
- `performance_review/summarizer.py` - performance-summary generation logic.
- `performance_review/cache.py` - local Markdown cache handling.
- `performance_review/models.py` - structured data models.
- `performance_review/connectors.py` - connector adaptation layer.
- `performance_review/__init__.py` - package marker.

## Skill package

- `performance-review/SKILL.md` - reusable skill instructions.
- `performance-review/agents/openai.yaml` - agent configuration.
- `performance-review/references/evidence-schema.md` - evidence schema documentation.
- `performance-review/references/mcp-integration.md` - MCP integration guidance.
- `performance-review/references/report-format.md` - report structure documentation.

## Demo data

- `demo_data/goals/workday_goals.txt` - sample Workday-style goals.
- `demo_data/goals/okrs.txt` - sample OKRs.
- `demo_data/sources/2026-06-01.json` - sample evidence fixture.
- `demo_data/sources/2026-06-23.json` - sample evidence fixture.
