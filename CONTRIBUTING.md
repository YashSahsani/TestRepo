# Contributing

## Local setup

Use Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## Run the demo

```bash
python3 -m performance_review.cli daily --demo
python3 -m performance_review.cli range 2026-06-01 2026-06-23 --demo --goals demo_data/goals/workday_goals.txt --okrs demo_data/goals/okrs.txt
```

## Before committing

- Keep generated files out of Git.
- Do not commit credentials, tokens, or private employee data.
- Use clear commit messages that explain the behavior change.
- Update documentation when command behavior, data shape, or setup steps change.
