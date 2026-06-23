# MCP Integration Notes

The prototype is intentionally connector-agnostic. Live environments should adapt MCP responses into the evidence schema rather than coupling summarization to MCP-specific payloads.

Recommended connector responsibilities:

- `fetch_day(date)`: return normalized evidence items for exactly one local date.
- `coverage()`: return source health and auth status for GitHub, ADO, M365, and Workday.
- `source_name`: one of `github`, `ado`, `m365`, `workday`.

Microsoft 365:

- Use Graph-backed MCP access for Teams messages, SharePoint/OneDrive activity, meeting transcripts, and OneNote pages.
- OneNote writes should target notebook `Performance Reviews`, section `<person> - <year>`, page `YYYY-MM-DD`.
- Store summaries, snippets, and links; do not store full meeting transcripts by default.

Azure DevOps:

- Fetch assigned work items, state transitions, comments, PRs, commits, and build/release activity for the target date.
- Prefer web URLs back to work items, PRs, and commits.

GitHub:

- Fetch authored commits, PRs, reviews, issue comments, and merged PRs for the target date.
- Preserve repository names and PR/commit URLs.

Workday:

- Fetch goals only when the response needs goal alignment.
- Do not write Workday goal details into daily OneNote pages unless explicitly requested.
