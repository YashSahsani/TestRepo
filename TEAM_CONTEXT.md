# Performance Review AI Hackathon Context

## Project Goal

Build a 1-day hackathon prototype for a personal AI performance-review assistant. The assistant gathers work evidence from Azure DevOps, Microsoft 365, GitHub, Workday goals, and OKR text, then produces daily, single-date, and date-range work summaries with source-backed evidence.

The core value is reducing end-of-cycle performance review prep by continuously preserving daily evidence and turning it into review-ready summaries.

## User Flow

The assistant first asks what report the user wants if the request is ambiguous:

- `daily`: summarize today's work.
- `single date`: summarize one selected date.
- `date range`: summarize a selected range.

For all paths, the assistant should prefer cached daily summaries from OneNote. If a requested day is missing, it fetches that day's work evidence from connected systems, writes the daily summary to OneNote, then answers the user.

## Background Job

A background job should backfill and maintain one daily summary per date starting from `2026-01-01` through today.

Logical OneNote structure:

- Notebook: `Performance Reviews`
- Section: `<person> - <year>`
- Page title: `YYYY-MM-DD`

Each daily page should include:

- Generated timestamp
- Source coverage
- Daily summary bullets
- Raw evidence snippets
- Source links
- Missing source warnings

## Sources

Target live sources:

- GitHub MCP/token: commits, PRs, reviews, comments, issues, merged PRs.
- Azure DevOps MCP/SSO: work items, state changes, PRs, commits, comments, build/release activity.
- Microsoft 365 MCP/token: Teams messages, SharePoint/OneDrive activity, meeting transcripts, OneNote pages.
- Workday integration: goals only when goal-aligned reporting is requested.
- OKRs: text file input for demo and MVP.

Current prototype uses local fixture data in `demo_data/` so the video demo can run even if live MCP auth is not ready.

## Evidence Model

Every source item should be normalized before summarization:

```json
{
  "date": "2026-06-23",
  "source": "github | ado | m365 | workday | okr",
  "kind": "commit | pull_request | work_item | teams_message | meeting_transcript | document | goal | other",
  "title": "Human-readable source item title",
  "timestamp": "2026-06-23T15:04:05-04:00",
  "url": "https://...",
  "snippet": "Short source-backed evidence snippet",
  "people": ["optional names"],
  "project": "optional project/repo/team",
  "tags": ["optional", "labels"]
}
```

Rules:

- Keep snippets short; do not store full meeting transcripts by default.
- Preserve links whenever available.
- Do not include tokens, raw auth headers, or unrelated personal content.
- Use evidence-backed language; do not overstate impact.

## Goal and OKR Behavior

Goals and OKRs affect the response only, not the durable OneNote daily cache.

- If the user asks for goal alignment, fetch Workday goals.
- If the user asks for OKR alignment, load OKR text.
- If both are provided, group accomplishments by relevant goal/OKR.
- Unmatched work should be shown separately rather than forced into a goal.

## MVP Scope

For the hackathon demo, the MVP should prove:

1. Daily summary from source evidence.
2. Date-range summary from daily cached pages.
3. OneNote-style cache semantics.
4. Raw evidence snippets and links.
5. Optional goals/OKR-aligned output.
6. Search over cached evidence returning reference links.

Live integrations are useful but not required for the video if fixture-backed flows are clear.

## Current Repo Layout

- `performance-review/SKILL.md`: reusable skill instructions.
- `performance-review/references/`: evidence schema, MCP integration notes, report format.
- `performance_review/`: Python CLI prototype.
- `demo_data/`: fixture data for GitHub, ADO, M365, Workday goals, and OKRs.
- `demo_cache/`: generated local stand-in for OneNote pages; ignored by git.
- `README.md`: runnable demo commands.

## Demo Commands

```bash
python3 -m performance_review.cli daily --demo --today 2026-06-23
python3 -m performance_review.cli date 2026-06-23 --demo
python3 -m performance_review.cli range 2026-06-01 2026-06-23 --demo --goals demo_data/goals/workday_goals.txt --okrs demo_data/goals/okrs.txt
python3 -m performance_review.cli backfill --from 2026-01-01 --to 2026-06-23 --demo
python3 -m performance_review.cli search "cache" --demo
```

## Suggested Team Split

- Connector owner: wire GitHub, ADO, and M365 MCP outputs into the evidence schema.
- OneNote owner: replace local Markdown cache with real OneNote read/write.
- Summarization owner: improve daily/range report quality and goal/OKR alignment.
- Demo owner: record the video flow using fixture data and, if ready, one live connector.
- Security/privacy owner: review token handling, transcript truncation, and safe evidence storage.

## Open Questions

- Which MCP environment will run the final demo: Claude.ai, Claude Code, Codex, or a local Python runner?
- Can the M365 MCP write OneNote pages, or only read from M365 sources?
- How will Workday goals be exposed: MCP, export, API, or manual text?
- Should the background job be local-only for the demo or shown as a scheduled cloud job?
- What is the minimum live connector needed to make the demo credible?

## Recommended Demo Story

1. Show the user asking for today's summary.
2. Show the assistant using cached or freshly fetched evidence.
3. Show a date-range summary with goal/OKR alignment.
4. Show source-linked evidence snippets.
5. Show search over cached daily pages returning references.
6. Explain that live MCP connectors can replace fixtures through the normalized evidence contract.
