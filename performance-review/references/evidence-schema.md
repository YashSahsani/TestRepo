# Evidence Schema

Normalize source activity into this shape before summarization:

```json
{
  "date": "2026-06-23",
  "source": "github | ado | m365 | workday | okr",
  "kind": "commit | pull_request | work_item | teams_message | meeting_transcript | document | goal | other",
  "title": "Human-readable source item title",
  "timestamp": "2026-06-23T15:04:05-04:00",
  "url": "https://...",
  "snippet": "Short evidence snippet, not a full private document or transcript",
  "people": ["optional names"],
  "project": "optional project/repo/team",
  "tags": ["optional", "labels"]
}
```

Rules:

- Keep snippets under 500 characters by default.
- Preserve source URLs whenever available.
- Store enough context for performance-review evidence without dumping full transcripts.
- Deduplicate by stable URL plus title plus timestamp when source IDs are unavailable.
- Mark missing connector coverage explicitly in daily reports.
