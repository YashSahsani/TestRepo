from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime

from .models import DailySummary, EvidenceItem

EXPECTED_SOURCES = ("github", "ado", "m365")


def summarize_day(day: date, person: str, evidence: list[EvidenceItem]) -> DailySummary:
    source_counts = Counter(item.source for item in evidence)
    missing_sources = [source for source in EXPECTED_SOURCES if source_counts[source] == 0]

    by_source: dict[str, list[EvidenceItem]] = defaultdict(list)
    for item in evidence:
        by_source[item.source].append(item)

    bullets: list[str] = []
    for source in sorted(by_source):
        titles = [item.title for item in by_source[source][:3]]
        if len(by_source[source]) > 3:
            titles.append(f"{len(by_source[source]) - 3} more")
        bullets.append(f"{source}: " + "; ".join(titles))

    return DailySummary(
        day=day,
        person=person,
        generated_at=datetime.now().astimezone(),
        bullets=bullets,
        evidence=evidence,
        missing_sources=missing_sources,
        source_counts=dict(source_counts),
    )


def render_daily_response(summary: DailySummary, goals: str | None = None, okrs: str | None = None) -> str:
    lines = [f"# Work Summary: {summary.day.isoformat()}", ""]
    lines.extend(["## Summary", ""])
    lines.extend(_bullet_lines(summary.bullets or ["No captured work evidence for this date."]))
    lines.extend(["", "## Evidence", ""])
    lines.extend(_evidence_lines(summary.evidence[:8]))

    collaboration = [
        item for item in summary.evidence if item.source == "m365" or item.kind in {"review", "meeting_transcript"}
    ]
    if collaboration:
        lines.extend(["", "## Collaboration", ""])
        lines.extend(_evidence_lines(collaboration[:5]))

    if goals or okrs:
        lines.extend(["", "## Goal / OKR Alignment", ""])
        lines.extend(_alignment_lines(summary.evidence, goals, okrs))

    lines.extend(["", "## Review-Ready Bullets", ""])
    lines.extend(_review_bullets(summary.evidence))

    if summary.missing_sources:
        lines.extend(["", "## Missing Sources", ""])
        lines.extend(_bullet_lines([f"{source} was not available in the cache or fixture data." for source in summary.missing_sources]))

    return "\n".join(lines)


def render_range_response(
    start: date,
    end: date,
    summaries: list[DailySummary],
    goals: str | None = None,
    okrs: str | None = None,
) -> str:
    all_evidence = [item for summary in summaries for item in summary.evidence]
    source_counts = Counter(item.source for item in all_evidence)
    lines = [f"# Work Summary: {start.isoformat()} to {end.isoformat()}", ""]
    lines.extend(["## Executive Summary", ""])
    if all_evidence:
        lines.extend(
            _bullet_lines(
                [
                    f"Captured {len(all_evidence)} evidence item(s) across {len(summaries)} day(s).",
                    "Source coverage: "
                    + ", ".join(f"{source} {count}" for source, count in sorted(source_counts.items())),
                    "Primary work themes: " + ", ".join(_top_tags_or_projects(all_evidence)),
                ]
            )
        )
    else:
        lines.append("- No captured work evidence for this range.")

    lines.extend(["", "## Themes", ""])
    themes = _group_by_project(all_evidence)
    if themes:
        for project, items in themes.items():
            lines.append(f"- {project}: {len(items)} item(s), including {items[0].title}")
    else:
        lines.append("- No themes found.")

    if goals or okrs:
        lines.extend(["", "## Goal / OKR Alignment", ""])
        lines.extend(_alignment_lines(all_evidence, goals, okrs))

    lines.extend(["", "## Evidence Highlights", ""])
    lines.extend(_evidence_lines(all_evidence[:12]))
    lines.extend(["", "## Potential Review Bullets", ""])
    lines.extend(_review_bullets(all_evidence))
    return "\n".join(lines)


def _bullet_lines(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values]


def _evidence_lines(items: list[EvidenceItem]) -> list[str]:
    if not items:
        return ["- No evidence available."]
    lines: list[str] = []
    for item in items:
        link = f" ([source]({item.url}))" if item.url else ""
        snippet = f" - {item.snippet}" if item.snippet else ""
        lines.append(f"- {item.source}/{item.kind}: {item.title}{link}{snippet}")
    return lines


def _alignment_lines(items: list[EvidenceItem], goals: str | None, okrs: str | None) -> list[str]:
    context = []
    if goals:
        context.extend(_keywords(goals))
    if okrs:
        context.extend(_keywords(okrs))
    if not context:
        return ["- No goal or OKR text provided."]

    matched: list[str] = []
    for item in items:
        haystack = " ".join([item.title, item.snippet or "", item.project or "", " ".join(item.tags)]).lower()
        hits = [keyword for keyword in context if keyword in haystack]
        if hits:
            matched.append(f"{item.title}: aligns with {', '.join(sorted(set(hits))[:3])}")

    return _bullet_lines(matched[:8] or ["No direct keyword alignment found; treat this as supporting work unless manually mapped."])


def _review_bullets(items: list[EvidenceItem]) -> list[str]:
    if not items:
        return ["- No review-ready bullets can be generated without evidence."]

    grouped = _group_by_project(items)
    bullets = []
    for project, project_items in list(grouped.items())[:5]:
        verbs = {
            "pull_request": "delivered",
            "commit": "implemented",
            "work_item": "advanced",
            "meeting_transcript": "drove alignment on",
            "teams_message": "coordinated",
            "document": "documented",
        }
        verb = verbs.get(project_items[0].kind, "contributed to")
        bullets.append(f"- {verb.capitalize()} {project} with {len(project_items)} source-backed contribution(s).")
    return bullets


def _group_by_project(items: list[EvidenceItem]) -> dict[str, list[EvidenceItem]]:
    grouped: dict[str, list[EvidenceItem]] = defaultdict(list)
    for item in items:
        grouped[item.project or item.source].append(item)
    return dict(sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0])))


def _top_tags_or_projects(items: list[EvidenceItem]) -> list[str]:
    values = Counter()
    for item in items:
        if item.project:
            values[item.project] += 1
        for tag in item.tags:
            values[tag] += 1
    return [value for value, _ in values.most_common(5)] or ["general delivery"]


def _keywords(text: str) -> list[str]:
    stop = {
        "and",
        "for",
        "the",
        "with",
        "from",
        "that",
        "this",
        "into",
        "okr",
        "goal",
        "objective",
        "key",
        "result",
    }
    words = []
    for raw in text.lower().replace("/", " ").replace("-", " ").split():
        word = "".join(ch for ch in raw if ch.isalnum())
        if len(word) >= 4 and word not in stop:
            words.append(word)
    return sorted(set(words))
