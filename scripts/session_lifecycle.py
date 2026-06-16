#!/usr/bin/env python3
"""Session lifecycle manager: start/end/undo."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "workspace"
MEMORY = WORKSPACE / "memory"
BACKUPS = WORKSPACE / "backups"
DISCUSSIONS = WORKSPACE / "discussions"
MAILBOX = WORKSPACE / "mailbox"
JOURNAL = WORKSPACE / "journal.md"
DATA = ROOT / "data"
BAND_FILE = DATA / "band_state.yaml"


_DRY_RUN = False


def _load_band() -> dict:
    with open(BAND_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _save_band(payload: dict) -> None:
    if _DRY_RUN:
        return
    with open(BAND_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)


def _tail(path: Path, n: int = 3) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    # ignore title line
    body = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    return body[-n:]


def cmd_start(chapter: int | None = None, dry_run: bool = False) -> dict:
    from world_state import build_report, as_text
    from band_weekly_tick import load_history

    memory_tail: dict[str, list[str]] = {}
    for agent_dir in sorted(MEMORY.glob("*/decisions.md")):
        memory_tail[agent_dir.parent.name] = _tail(agent_dir, 3)

    unread = []
    for box in sorted(MAILBOX.glob("*")):
        if not box.is_dir():
            continue
        for msg in box.glob("*.md"):
            mark = msg.with_suffix(msg.suffix + ".read")
            if not mark.exists():
                unread.append(str(msg.relative_to(ROOT)))
                if not dry_run:
                    mark.touch()

    open_discussions = []
    for md in DISCUSSIONS.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        if "status: OPEN" in text:
            open_discussions.append(str(md.relative_to(ROOT)))

    weekly = load_history(1)
    report = build_report()

    return {
        "chapter": chapter,
        "memory_tail": memory_tail,
        "world_state": as_text(report),
        "weekly_digest": weekly,
        "unread_mail": unread,
        "open_discussions": open_discussions,
        "checklist": "Memory ✓ | World ✓ | Mail ✓ | Discussions ✓",
    }


def _backup_name(chapter: int | None) -> str:
    ch = f"ch{int(chapter):02d}" if chapter is not None else "ch00"
    return f"{date.today().isoformat()}_{ch}"


def _append_computer_decision(entry: str) -> None:
    p = MEMORY / "computer" / "decisions.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("# Computer — Decision Log\n\n", encoding="utf-8")
    with open(p, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def _append_journal(line: str) -> None:
    if not JOURNAL.exists():
        JOURNAL.write_text("# Iron Ledger — Campaign Journal\n\n", encoding="utf-8")
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def cmd_end(chapter: int | None, day_advance: int, treasury_delta: int, food_delta: int,
            contract_status: str | None, note: str | None,
            dry_run: bool = False) -> dict:
    tag = _backup_name(chapter)
    backup = BACKUPS / tag / "data"
    if not dry_run:
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(DATA, backup, dirs_exist_ok=True)

    payload = _load_band()
    band = payload.get("band", {})

    band["day_of_year"] = int(band.get("day_of_year", 1)) + int(day_advance)
    band["treasury_silver"] = int(band.get("treasury_silver", 0)) + int(treasury_delta)

    if contract_status and isinstance(band.get("current_contract"), dict):
        band["current_contract"]["status"] = contract_status

    notes = band.get("notes") or []
    if food_delta:
        notes.append(f"Food delta this session: {food_delta:+d}")
    if note:
        notes.append(note)
    band["notes"] = notes

    payload["band"] = band
    if not dry_run:
        _save_band(payload)

    ch = f"ch{int(chapter):02d}" if chapter is not None else "ch00"
    dec_line = f"[{date.today().isoformat()} {ch}] SESSION_END — day+{day_advance}, treasury {treasury_delta:+d}, food {food_delta:+d}. {note or ''}".strip()
    if not dry_run:
        _append_computer_decision(dec_line)
        _append_journal(f"[{date.today().isoformat()}] [CHAPTER_END] {ch} — {note or 'Session ended.'}")

    return {
        "backup": str((BACKUPS / tag).relative_to(ROOT)),
        "chapter": chapter,
        "day_of_year": band.get("day_of_year"),
        "treasury_silver": band.get("treasury_silver"),
        "note": note,
        "dry_run": dry_run,
    }


def cmd_undo(backup: str | None, dry_run: bool = False) -> dict:
    items = sorted([p for p in BACKUPS.glob("*") if p.is_dir()])
    if not items:
        return {"backups": []}
    if backup is None:
        return {"backups": [p.name for p in items]}

    target = BACKUPS / backup / "data"
    if not target.exists():
        return {"error": f"Backup not found: {backup}"}

    safety = BACKUPS / f"{date.today().isoformat()}_pre_restore" / "data"
    if not dry_run:
        safety.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(DATA, safety, dirs_exist_ok=True)
        shutil.copytree(target, DATA, dirs_exist_ok=True)
    return {"restored": backup, "safety_backup": str(safety.parent.relative_to(ROOT))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Session lifecycle")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview outcomes without writing files",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start")
    p.add_argument("--chapter", type=int)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("end")
    p.add_argument("--chapter", type=int)
    p.add_argument("--day-advance", type=int, default=0)
    p.add_argument("--treasury-delta", type=int, default=0)
    p.add_argument("--food-delta", type=int, default=0)
    p.add_argument("--contract-status", choices=["complete", "failed"])
    p.add_argument("--note")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("undo")
    p.add_argument("--backup")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    global _DRY_RUN
    _DRY_RUN = bool(getattr(args, "dry_run", False))

    if args.cmd == "start":
        out = cmd_start(args.chapter, dry_run=_DRY_RUN)
    elif args.cmd == "end":
        out = cmd_end(
            args.chapter,
            args.day_advance,
            args.treasury_delta,
            args.food_delta,
            args.contract_status,
            args.note,
            dry_run=_DRY_RUN,
        )
    else:
        out = cmd_undo(args.backup, dry_run=_DRY_RUN)

    if getattr(args, "json", False):
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        if args.cmd == "start":
            print(out["world_state"])
            print(f"Unread mail: {len(out['unread_mail'])}")
            print(f"Open discussions: {len(out['open_discussions'])}")
            print(out["checklist"])
        elif args.cmd == "end":
            print(f"Backup: {out['backup']}")
            print(f"Day: {out['day_of_year']} | Treasury: {out['treasury_silver']}s")
        else:
            if "error" in out:
                print(out["error"])
            elif "restored" in out:
                print(f"Restored: {out['restored']}")
            else:
                for b in out["backups"]:
                    print(b)


if __name__ == "__main__":
    main()
