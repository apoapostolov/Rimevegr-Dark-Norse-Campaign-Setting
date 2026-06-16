#!/usr/bin/env python3
"""Generate team briefing markdown for session start."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from world_state import build_report, as_md
from arc_tracker import status as arc_status
from session_lifecycle import cmd_start
from event_manager import load_all_events
from campaign_journal import timeline
from ledger import cmd_weekly_summary
from magic import cmd_practitioners
from village_politics import cmd_feud_stage

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "workspace"


def generate(chapter_next: int, no_save: bool = False) -> str:
    rep = build_report()
    arc = arc_status()
    sess = cmd_start(chapter_next)

    day = rep["date"]["day"]
    year = rep["date"]["year"]
    upcoming = [e for e in load_all_events() if e.get("year") == year and day <= int(e.get("day", -999)) <= day + 30]
    recent = timeline(last=5)
    weekly = cmd_weekly_summary()
    feud = cmd_feud_stage(rep["location"].split(",")[0].strip())
    prac = cmd_practitioners()

    lines = [
        f"# Team Brief — {date.today().isoformat()} | Next Chapter: {chapter_next:02d}",
        "",
        "## COMPUTER — World State Broadcast",
        "",
        as_md(rep),
        "",
        "## COMPUTER — Narrative Arc Position",
        "",
        f"- Day {arc['day']} Year {arc['year']}",
        f"- Volume {arc['volume']} | {arc['arc_phase']}",
        f"- Dangling: {arc['dangling_threads']} | Cold: {arc['cold_threads']}",
        "",
        "## COMPUTER — Session Checklist",
        "",
        f"- {sess['checklist']}",
        f"- Unread mail consumed: {len(sess['unread_mail'])}",
        f"- Open discussions: {len(sess['open_discussions'])}",
        "",
        "## COMPUTER — Upcoming Events (next 30 days)",
        "",
    ]
    for e in sorted(upcoming, key=lambda x: x.get("day", 0))[:20]:
        lines.append(f"- Day {e.get('day')}: `{e.get('id')}` — {e.get('title')}")

    lines.extend([
        "",
        "## COMPUTER — Recent Journal",
        "",
    ])
    for ln in recent:
        lines.append(f"- {ln}")

    lines.extend([
        "",
        "## ECONOMY / FEUD / MAGIC SNAPSHOT",
        "",
        f"- Weekly treasury: {weekly.get('current_treasury')}s | morale {weekly.get('morale')}",
        f"- Local feud: {feud.get('stage') if isinstance(feud, dict) else 'unknown'}",
        f"- Practitioners tracked: {len(prac)}",
        "",
        "---",
        "",
        "STATUS: TEAM READY. Awaiting synopsis.",
    ])

    text = "\n".join(lines) + "\n"
    if not no_save:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        out = WORKSPACE / f"TEAM_BRIEF_{date.today().isoformat()}_ch{chapter_next:02d}.md"
        out.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent brief generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("generate")
    p.add_argument("--chapter-next", type=int, required=True)
    p.add_argument("--no-save", action="store_true")

    args = parser.parse_args()
    print(generate(args.chapter_next, no_save=args.no_save))


if __name__ == "__main__":
    main()
