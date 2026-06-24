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
- Prefer the remote GitHub MCP server with OAuth when the MCP host supports remote servers and OAuth.
- Use the local Docker MCP server with a GitHub personal access token when the host does not support remote OAuth or when a local stdio server is required.
- Fetch authored commits, pull requests, reviews, issue comments, issue activity, merged PRs, and workflow runs for the target date.
- Preserve repository names, authorship, timestamps, PR/commit/issue URLs, and workflow links.
- Configure only the toolsets needed for review evidence: `context`, `repos`, `issues`, `pull_requests`, and optionally `actions`.

## GitHub MCP Setup With SSO

### Recommended remote OAuth setup

Use this when the MCP host supports remote MCP servers and browser OAuth.

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

After adding the server, start the MCP host's auth flow and complete GitHub login in the browser. If the organization requires SSO, complete the organization SSO prompt before using tools against private org repositories.

### Local Docker setup with SSO-authorized token

Use this when the MCP host needs a local stdio server.

1. Create a GitHub personal access token with the minimum scopes needed for the target repos. For private repository performance review work, start with `repo`; add `read:org` only when org/team context is needed.
2. If the GitHub organization uses SSO, authorize the token for that organization in GitHub: Settings -> Developer settings -> Personal access tokens -> Configure SSO -> Authorize.
3. Do not commit the token. Store it in the MCP host credential prompt, environment variable, or local secret store.
4. Configure the local server:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github_token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ],
  "servers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e",
        "GITHUB_TOOLSETS",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}",
        "GITHUB_TOOLSETS": "context,repos,issues,pull_requests,actions"
      }
    }
  }
}
```

### SSO troubleshooting

- `Resource protected by organization SAML enforcement`: authorize the token for the organization or re-run the OAuth flow and complete organization SSO.
- `Repository not found`: confirm repo owner/name, private repo access, org membership, and SSO authorization.
- `Bad credentials`: rotate the token or re-login through the MCP host.
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
