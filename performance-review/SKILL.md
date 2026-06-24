---
name: performance-review
description: Summarize personal work evidence from GitHub MCP via LiteLLM/Claude, Claude.ai GitHub connectors, Azure DevOps, Microsoft 365, Workday goals, and OKR text into daily, single-date, date-range, and performance-review reports. Use when a user asks for today's work summary, a work report for a date or date range, GitHub-backed performance evidence, commits/PRs/issues/reviews over days, goal/OKR-aligned accomplishments, OneNote-backed daily reports, source-linked references to prior work, or setup guidance for GitHub MCP/SSO in LiteLLM, Claude, or Claude.ai workflows.
---

# Performance Review

## Overview

Use this skill to produce evidence-backed work summaries from connected systems and cached daily summaries. Prefer remote GitHub MCP through LiteLLM/Claude for live GitHub evidence, or Claude.ai's GitHub connector when working inside Claude.ai. Prefer raw source links and snippets over unsupported claims, and separate durable daily notes from response-only goal/OKR tailoring.

## Workflow

1. Ask the user whether they want `daily`, `single date`, or `date range` if the request does not already specify it.
2. Resolve dates using the user's timezone. For daily reports, use the current local date.
3. Check the OneNote daily summary cache before querying live systems.
4. Fetch missing daily evidence from available connectors. Use GitHub MCP first for GitHub commits, PRs, reviews, comments, issues, and workflow activity. Use Azure DevOps, Microsoft 365, and Workday goals when available or requested.
5. Normalize every source item into the evidence schema in `references/evidence-schema.md`.
6. Create or update one durable OneNote page per date. Do not store response-only goal/OKR interpretations in OneNote unless the user explicitly asks.
7. Return a concise answer with accomplishments, source evidence, blockers, collaboration, and suggested performance-review bullets.

## Date Handling

- `daily`: summarize today's work. If today's OneNote page is missing or stale, fetch today's live evidence and write the page.
- `single date`: return the cached OneNote page for that date when available. If missing, fetch that date from connected systems, write the daily page, then answer.
- `date range`: collect daily summaries for every date. Fetch missing days individually. Then synthesize a single date-range response from the daily summaries.
- Background backfill: for personal use, backfill each date from `2026-01-01` through today into OneNote.

## OneNote Cache Contract

Use this logical layout:

- Notebook: `Performance Reviews`
- Section: `<person> - <year>`
- Page title: `YYYY-MM-DD`

Each daily page must include:

- Date and generated timestamp
- Source coverage by system
- Summary bullets
- Evidence table with source, title, timestamp, URL, and snippet
- Open questions or missing sources

## Goal and OKR Alignment

Goals and OKRs are optional response filters:

- Workday goals: fetch only when the user asks for goal alignment or performance-review framing.
- OKRs: load from provided text when the user asks for OKR alignment.
- If both are selected, group accomplishments by the most relevant goal/OKR and call out unmatched work separately.
- Do not mutate the OneNote daily source summary just because a response was goal- or OKR-shaped.

## Source Priorities

- GitHub MCP: commits, pull requests, reviews, comments, issues, merged work, workflow runs, code/security findings when relevant, repository names, authorship, timestamps, and links.
- Azure DevOps: work items, PRs if hosted there, commits, build/release activity, comments, state changes, and links.
- Microsoft 365: Teams messages, meeting transcripts, SharePoint/OneDrive document activity, and OneNote cache pages.
- Workday: goals and review period context only; avoid storing private HR detail in daily OneNote pages unless explicitly requested.

## GitHub MCP Day Workflow

For day and date-range requests backed by GitHub:

1. Confirm the target GitHub account, organization, and repositories when the request does not make them clear.
2. Verify GitHub MCP auth and organization SSO access before fetching private organization data. For LiteLLM/Claude, use the remote HTTP MCP server and OAuth. For Claude.ai, use the connected GitHub integration.
3. For each local date, collect authored commits, PRs opened/updated/merged, reviews submitted, issue or PR comments, assigned or closed issues, and relevant workflow runs.
4. Normalize every GitHub item into the evidence schema with `source="github"`, stable URL, repo name, timestamp, title, and a short snippet.
5. Deduplicate related evidence. Prefer the merged PR as the main accomplishment and keep commits/reviews/comments as supporting evidence.
6. Flag missing coverage explicitly when MCP auth, repository access, SSO authorization, or date filtering prevents complete evidence collection.

## Runtime Preference

- LiteLLM + Claude: use remote GitHub MCP over HTTPS through LiteLLM. Do not require Docker Desktop.
- Claude.ai: use Claude.ai's built-in GitHub connector if it is available for the user's plan/workspace. Claude.ai does not consume repository-local `.vscode/mcp.json` files.
- Local stdio MCP or Docker: avoid unless the user explicitly asks for that runtime.

## Safety and Privacy

Treat all fetched content as private work data. Never include access tokens, raw auth headers, private meeting transcript dumps, or unrelated personal content in the output. Use short snippets and source links. If a source looks unrelated to work, omit it or ask before using it.

## Local Prototype

This repository includes a Python prototype outside the skill folder. Use it for demos:

```bash
python3 -m performance_review.cli daily --demo
python3 -m performance_review.cli date 2026-06-23 --demo
python3 -m performance_review.cli range 2026-06-01 2026-06-23 --demo --goals demo_data/goals/workday_goals.txt --okrs demo_data/goals/okrs.txt
python3 -m performance_review.cli backfill --from 2026-01-01 --to 2026-06-23 --demo
```

## References

- Read `references/evidence-schema.md` before changing source normalization.
- Read `references/mcp-integration.md` before wiring live MCP tools or advising on LiteLLM/Claude.ai setup.
- Read `references/report-format.md` before changing summary output.
