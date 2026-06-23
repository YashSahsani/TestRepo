# Performance Review Hackathon Prototype

This repo contains a Claude/Codex-style skill package plus a Python prototype for daily and date-range performance-review summaries.

## Demo Commands

```bash
python3 -m performance_review.cli daily --demo
python3 -m performance_review.cli date 2026-06-23 --demo
python3 -m performance_review.cli range 2026-06-01 2026-06-23 --demo --goals demo_data/goals/workday_goals.txt --okrs demo_data/goals/okrs.txt
python3 -m performance_review.cli backfill --from 2026-01-01 --to 2026-06-23 --demo
python3 -m performance_review.cli search "cache" --demo
```

The demo uses local fixture data and writes a OneNote-like Markdown cache under `demo_cache/`. Live MCP connectors can be wired by adapting MCP responses into the evidence schema documented in `performance-review/references/evidence-schema.md`.

## Artifact Layout

- `performance-review/SKILL.md`: reusable skill instructions.
- `performance_review/`: Python CLI and summarization prototype.
- `demo_data/`: fixture evidence, goals, and OKRs for video demos.
- `demo_cache/`: generated local stand-in for OneNote pages.
