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

GitHub MCP:

- Use GitHub's official MCP server for live GitHub context when available.
- Prefer the remote GitHub MCP server with OAuth through LiteLLM when using Claude through LiteLLM.
- Use Claude.ai's built-in GitHub connector when working directly in Claude.ai and the connector is available.
- Do not require Docker Desktop for this workflow. Avoid local stdio/Docker MCP unless the user explicitly asks for that runtime.
- Fetch authored commits, pull requests, reviews, issue comments, issue activity, merged PRs, and workflow runs for the target date.
- Preserve repository names, authorship, timestamps, PR/commit/issue URLs, and workflow links.
- Configure only the toolsets needed for review evidence: `context`, `repos`, `issues`, `pull_requests`, and optionally `actions`.

## GitHub MCP Setup With SSO For LiteLLM + Claude

Use this path when the user runs Claude through LiteLLM and does not want Docker Desktop.

```yaml
mcp_servers:
  github_mcp:
    url: "https://api.githubcopilot.com/mcp"
    transport: "http"
    auth_type: oauth2
```

After adding the server, restart LiteLLM and complete the OAuth flow from the LiteLLM MCP server UI or the MCP-capable client. If the GitHub organization requires SSO, complete the organization SSO prompt before using tools against private org repositories.

For deployments that require explicit OAuth client credentials:

```yaml
mcp_servers:
  github_mcp:
    url: "https://api.githubcopilot.com/mcp"
    transport: "http"
    auth_type: oauth2
    client_id: os.environ/GITHUB_OAUTH_CLIENT_ID
    client_secret: os.environ/GITHUB_OAUTH_CLIENT_SECRET
```

Use environment variables or the LiteLLM secret store for client credentials. Do not commit OAuth client secrets or access tokens.

## Claude.ai Setup

Use Claude.ai's GitHub connector when available:

1. Open Claude.ai settings.
2. Connect GitHub from Connectors or Integrations.
3. Complete GitHub login and any organization SSO prompt.
4. Ask Claude.ai for the target repository and date range in performance-review format.

Claude.ai does not use repository-local MCP config files. If the user needs the exact `performance-review` skill behavior in Claude.ai, paste or upload the skill instructions and tell Claude.ai to follow them while using the connected GitHub account.

Example prompt:

```text
Using my connected GitHub account, summarize my work in OWNER/REPO from YYYY-MM-DD to YYYY-MM-DD in performance review format. Include source links, grouped daily accomplishments, blockers, collaboration, and review-ready bullets.
```

### SSO troubleshooting

- `Resource protected by organization SAML enforcement`: re-run the OAuth flow and complete organization SSO.
- `Repository not found`: confirm repo owner/name, private repo access, org membership, and SSO authorization.
- `Bad credentials`: re-login through LiteLLM/Claude.ai or rotate credentials in the LiteLLM secret store.
- No tools appear in Claude.ai: confirm the GitHub connector is enabled for the plan/workspace; Claude.ai may expose connectors differently than LiteLLM MCP.
- Missing PRs or commits: check that the token has private repo access and that date filtering uses the user's local timezone.

## GitHub Evidence Collection For Days

For each date:

1. Resolve the date window in the user's timezone.
2. Query target repositories for authored commits within the window.
3. Query PRs created, updated, reviewed, commented on, or merged by the user within the window.
4. Query issues assigned, closed, commented on, or referenced by the user within the window.
5. Query workflow runs only when CI/CD status is part of the accomplishment or blocker.
6. Normalize results into `references/evidence-schema.md`.
7. Deduplicate by URL and commit SHA. If a PR includes commits already captured, keep the PR as the main item and attach commit details only when they add useful evidence.
8. For date ranges, summarize each day first, then roll up themes across days.

Workday:

- Fetch goals only when the response needs goal alignment.
- Do not write Workday goal details into daily OneNote pages unless explicitly requested.
