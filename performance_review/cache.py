from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from .models import DailySummary, EvidenceItem


SearchHit = tuple[Path, EvidenceItem]


class LocalOneNoteCache:
    """Markdown stand-in for OneNote during the video demo."""

    def __init__(self, root: Path, person: str) -> None:
        self.root = root
        self.person = person

    def page_path(self, day: date) -> Path:
        return self.root / "Performance Reviews" / f"{self.person} - {day.year}" / f"{day.isoformat()}.md"

    def exists(self, day: date) -> bool:
        return self.page_path(day).exists()

    def write_summary(self, summary: DailySummary) -> Path:
        path = self.page_path(summary.day)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_daily_markdown(summary), encoding="utf-8")
        return path

    def read_summary(self, day: date) -> DailySummary | None:
        path = self.page_path(day)
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        marker = "<!-- performance-review-json\n"
        if marker not in text:
            return None
        raw = text.split(marker, 1)[1].split("\n-->", 1)[0]
        payload = json.loads(raw)
        return DailySummary(
            day=date.fromisoformat(payload["day"]),
            person=payload["person"],
            generated_at=datetime.fromisoformat(payload["generated_at"]),
            bullets=list(payload["bullets"]),
            evidence=[EvidenceItem.from_dict(item) for item in payload["evidence"]],
            missing_sources=list(payload["missing_sources"]),
            source_counts=dict(payload["source_counts"]),
        )

    def search(self, query: str) -> list[Path]:
        needle = query.lower()
        if not self.root.exists():
            return []
        matches: list[Path] = []
        for path in self.root.rglob("*.md"):
            if needle in path.read_text(encoding="utf-8").lower():
                matches.append(path)
        return sorted(matches)

    def search_evidence(self, query: str) -> list[SearchHit]:
        needle = query.lower()
        hits: list[SearchHit] = []
        for summary in self.iter_summaries():
            page = self.page_path(summary.day)
            for item in summary.evidence:
                haystack = " ".join(
                    [
                        item.title,
                        item.snippet or "",
                        item.project or "",
                        " ".join(item.tags),
                        item.url or "",
                    ]
                ).lower()
                if needle in haystack:
                    hits.append((page, item))
        return hits

    def iter_summaries(self) -> list[DailySummary]:
        if not self.root.exists():
            return []
        summaries: list[DailySummary] = []
        for path in sorted(self.root.rglob("*.md")):
            try:
                day = date.fromisoformat(path.stem)
            except ValueError:
                continue
            summary = self.read_summary(day)
            if summary:
                summaries.append(summary)
        return summaries


def render_daily_markdown(summary: DailySummary) -> str:
    lines = [
        f"# {summary.day.isoformat()}",
        "",
        f"Person: {summary.person}",
        f"Generated: {summary.generated_at.isoformat()}",
        "",
        "## Summary",
        "",
    ]
    if summary.bullets:
        lines.extend(f"- {bullet}" for bullet in summary.bullets)
    else:
        lines.append("- No captured work evidence for this date.")

    lines.extend(["", "## Source Coverage", ""])
    for source, count in sorted(summary.source_counts.items()):
        lines.append(f"- {source}: {count} item(s)")
    for source in summary.missing_sources:
        lines.append(f"- {source}: missing or not connected")

    lines.extend(["", "## Evidence", ""])
    if summary.evidence:
        lines.append("| Source | Kind | Title | Link | Snippet |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in summary.evidence:
            title = _escape_table(item.title)
            link = f"[link]({item.url})" if item.url else ""
            snippet = _escape_table((item.snippet or "")[:500])
            lines.append(f"| {item.source} | {item.kind} | {title} | {link} | {snippet} |")
    else:
        lines.append("No source evidence captured.")

    lines.extend(
        [
            "",
            "<!-- performance-review-json",
            json.dumps(summary.to_dict(), indent=2),
            "-->",
            "",
        ]
    )
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
