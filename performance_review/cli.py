from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from .cache import LocalOneNoteCache
from .connectors import DemoConnector, EvidenceConnector, dedupe_evidence
from .models import DailySummary
from .summarizer import render_daily_response, render_range_response, summarize_day


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-backed performance review summaries.")
    parser.add_argument("--person", default="Yash", help="Person name for the OneNote cache section.")
    parser.add_argument("--cache-dir", default="demo_cache", help="Local OneNote-style cache directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="Summarize today's work.")
    add_common_flags(daily)
    daily.add_argument("--today", default=date.today().isoformat(), help="Override today for demos.")

    single = subparsers.add_parser("date", help="Summarize one date.")
    add_common_flags(single)
    single.add_argument("day")

    range_parser = subparsers.add_parser("range", help="Summarize a date range.")
    add_common_flags(range_parser)
    range_parser.add_argument("start")
    range_parser.add_argument("end")

    backfill = subparsers.add_parser("backfill", help="Populate daily cache pages.")
    add_common_flags(backfill)
    backfill.add_argument("--from", dest="start", required=True)
    backfill.add_argument("--to", dest="end", required=True)

    search = subparsers.add_parser("search", help="Search cached OneNote-style pages.")
    search.add_argument("query")
    search.add_argument("--demo", action="store_true", help="Accepted for script symmetry.")

    args = parser.parse_args()
    cache = LocalOneNoteCache(Path(args.cache_dir), args.person)

    if args.command == "search":
        hits = cache.search_evidence(args.query)
        if not hits:
            print("No cached pages matched.")
            return
        for page, item in hits:
            link = f" | {item.url}" if item.url else ""
            print(f"{item.date.isoformat()} | {item.source}/{item.kind} | {item.title}{link}")
            print(f"  cache: {page}")
        return

    connectors = build_connectors(args)

    if args.command == "daily":
        day = date.fromisoformat(args.today)
        summary = get_or_create_day(cache, connectors, day, args.person, refresh=args.refresh)
        print(render_daily_response(summary, read_optional(args.goals), read_optional(args.okrs)))
        return

    if args.command == "date":
        day = date.fromisoformat(args.day)
        summary = get_or_create_day(cache, connectors, day, args.person, refresh=args.refresh)
        print(render_daily_response(summary, read_optional(args.goals), read_optional(args.okrs)))
        return

    if args.command == "range":
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
        summaries = [
            get_or_create_day(cache, connectors, day, args.person, refresh=args.refresh)
            for day in date_span(start, end)
        ]
        print(render_range_response(start, end, summaries, read_optional(args.goals), read_optional(args.okrs)))
        return

    if args.command == "backfill":
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
        count = 0
        for day in date_span(start, end):
            get_or_create_day(cache, connectors, day, args.person, refresh=args.refresh)
            count += 1
        print(f"Backfilled {count} daily page(s) into {Path(args.cache_dir).resolve()}.")


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--demo", action="store_true", help="Use local fixture data.")
    parser.add_argument("--fixture-dir", default="demo_data/sources", help="Demo source fixture directory.")
    parser.add_argument("--refresh", action="store_true", help="Ignore cache and fetch source evidence again.")
    parser.add_argument("--goals", help="Optional Workday goals export text file.")
    parser.add_argument("--okrs", help="Optional OKR text file.")


def build_connectors(args: argparse.Namespace) -> list[EvidenceConnector]:
    if args.demo:
        return [DemoConnector(Path(args.fixture_dir))]
    raise SystemExit("Live MCP mode is not wired yet. Use --demo or implement MCP adapters in connectors.py.")


def get_or_create_day(
    cache: LocalOneNoteCache,
    connectors: list[EvidenceConnector],
    day: date,
    person: str,
    refresh: bool = False,
) -> DailySummary:
    if not refresh:
        cached = cache.read_summary(day)
        if cached:
            return cached

    evidence = []
    for connector in connectors:
        evidence.extend(connector.fetch_day(day))
    summary = summarize_day(day, person, dedupe_evidence(evidence))
    cache.write_summary(summary)
    return summary


def date_span(start: date, end: date):
    if end < start:
        raise SystemExit("End date must be on or after start date.")
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def read_optional(path: str | None) -> str | None:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
