from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class EvidenceItem:
    date: date
    source: str
    kind: str
    title: str
    timestamp: datetime | None = None
    url: str | None = None
    snippet: str | None = None
    people: tuple[str, ...] = ()
    project: str | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceItem":
        item_date = date.fromisoformat(payload["date"])
        timestamp_raw = payload.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_raw) if timestamp_raw else None
        return cls(
            date=item_date,
            source=str(payload["source"]),
            kind=str(payload.get("kind", "other")),
            title=str(payload["title"]),
            timestamp=timestamp,
            url=payload.get("url"),
            snippet=payload.get("snippet"),
            people=tuple(payload.get("people", [])),
            project=payload.get("project"),
            tags=tuple(payload.get("tags", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "source": self.source,
            "kind": self.kind,
            "title": self.title,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "url": self.url,
            "snippet": self.snippet,
            "people": list(self.people),
            "project": self.project,
            "tags": list(self.tags),
        }

    @property
    def stable_key(self) -> str:
        return "|".join(
            [
                self.source,
                self.kind,
                self.url or "",
                self.title,
                self.timestamp.isoformat() if self.timestamp else "",
            ]
        )


@dataclass
class DailySummary:
    day: date
    person: str
    generated_at: datetime
    bullets: list[str]
    evidence: list[EvidenceItem] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day.isoformat(),
            "person": self.person,
            "generated_at": self.generated_at.isoformat(),
            "bullets": self.bullets,
            "evidence": [item.to_dict() for item in self.evidence],
            "missing_sources": self.missing_sources,
            "source_counts": self.source_counts,
        }
