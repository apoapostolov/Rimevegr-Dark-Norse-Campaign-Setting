#!/usr/bin/env python3
"""Build chapter scaffold markdown for authors."""

from __future__ import annotations

import argparse
from pathlib import Path

from world_state import build_report, as_md
from arc_tracker import threads

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "workspace"


def scaffold(chapter: int, synopsis: str, chapter_type: str | None = None) -> str:
    rep = build_report()
    th = threads().get("threads", [])[:10]
    ch_dir = WORKSPACE / "drafts" / f"ch{chapter:02d}"
    ch_dir.mkdir(parents=True, exist_ok=True)
    out = ch_dir / "SCAFFOLD.md"

    slots = [
        "Opening pressure scene",
        "Complication / opposition",
        "Decision / cost",
        "Exit hook",
    ]

    lines = [
        f"# Chapter {chapter:02d} Scaffold",
        "",
        f"**Synopsis:** {synopsis}",
        f"**Type:** {chapter_type or 'CHAP_GENERIC'}",
        "",
        "## World State",
        "",
        as_md(rep),
        "",
        "## Scene Slots",
        "",
    ]
    for i, s in enumerate(slots, 1):
        lines.append(f"{i}. {s}")
        lines.append("   - Weather anchor:")
        lines.append("   - Event pressure:")
        lines.append("   - Logistics warning:")

    lines.extend([
        "",
        "## Contract Countdown",
        "",
        f"- Deadline day: {rep['contract'].get('deadline_day')}",
        f"- Days remaining: {rep['contract'].get('days_left')}",
        f"- Flag: {rep['contract'].get('deadline_flag')}",
        "",
        "## Dangling Threads",
        "",
    ])
    for t in th:
        lines.append(f"- {t.get('id')}: {t.get('title')} (age {t.get('age_days')}d)")

    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Chapter scaffolder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scaffold")
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--synopsis", required=True)
    p.add_argument("--type", dest="chapter_type")

    args = parser.parse_args()
    print(scaffold(args.chapter, args.synopsis, args.chapter_type))


if __name__ == "__main__":
    main()
