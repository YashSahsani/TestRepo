from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Protocol

from .models import EvidenceItem


class EvidenceConnector(Protocol):
    source_name: str

    def fetch_day(self, day: date) -> list[EvidenceItem]:
        """Return normalized evidence for one local date."""


class DemoConnector:
    source_name = "demo"

    def __init__(self, fixture_dir: Path) -> None:
        self.fixture_dir = fixture_dir

    def fetch_day(self, day: date) -> list[EvidenceItem]:
        fixture = self.fixture_dir / f"{day.isoformat()}.json"
        if not fixture.exists():
            return []

        payload = json.loads(fixture.read_text(encoding="utf-8"))
        items: list[EvidenceItem] = []
        for source_items in payload.values():
            for item in source_items:
                items.append(EvidenceItem.from_dict(item))
        return dedupe_evidence(items)


def dedupe_evidence(items: list[EvidenceItem]) -> list[EvidenceItem]:
    seen: set[str] = set()
    deduped: list[EvidenceItem] = []
    for item in sorted(items, key=lambda entry: (entry.timestamp or "", entry.source, entry.title)):
        if item.stable_key in seen:
            continue
        seen.add(item.stable_key)
        deduped.append(item)
    return deduped


class McpConnectorPlaceholder:
    """Adapter boundary for live MCP connectors.

    Claude.ai, Codex, and local MCP clients expose MCP tools differently. Keep live
    calls outside the summarizer and convert each MCP response into EvidenceItem.
    """

    def __init__(self, source_name: str) -> None:
        self.source_name = source_name

    def fetch_day(self, day: date) -> list[EvidenceItem]:
        raise NotImplementedError(
            f"Wire {self.source_name} MCP responses into EvidenceItem for {day.isoformat()}."
        )
