#!/usr/bin/env python3
"""Append-only campaign journal CLI."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "workspace" / "journal.md"
BAND = ROOT / "data" / "band_state.yaml"


def _band_day() -> int:
    with open(BAND, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return int(data.get("band", {}).get("day_of_year", 1))


def _ensure_journal() -> None:
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    if not JOURNAL.exists():
        JOURNAL.write_text("# Iron Ledger — Campaign Journal\n\n", encoding="utf-8")


def record(entry_type: str, chapter: int | None, npc: str | None, contract: str | None,
           outcome: str | None, payment: int | None, note: str) -> str:
    _ensure_journal()
    day = _band_day()
    ch = f"Ch{chapter:02d}" if chapter is not None else ""
    parts = [f"[Day {day:03d}]", f"[{entry_type.upper()}]"]
    if ch:
        parts.append(ch)
    line = " ".join(parts) + "."
    body = []
    if npc:
        body.append(f"NPC: {npc}.")
    if contract:
        body.append(f"Contract: {contract}.")
    if outcome:
        body.append(f"Outcome: {outcome}.")
    if payment is not None:
        body.append(f"Payment: {payment} silver.")
    if note:
        body.append(note)
    full = line + "\n  " + " ".join(body)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(full + "\n")
    return full


def _lines() -> list[str]:
    if not JOURNAL.exists():
        return []
    return [ln for ln in JOURNAL.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]


def timeline(last: int | None = None) -> list[str]:
    lines = _lines()
    return lines[-last:] if last else lines


def filter_log(key: str, val: str) -> list[str]:
    return [ln for ln in _lines() if val.lower() in ln.lower()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Campaign journal")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("record")
    p.add_argument("--type", required=True)
    p.add_argument("--chapter", type=int)
    p.add_argument("--npc")
    p.add_argument("--contract")
    p.add_argument("--outcome")
    p.add_argument("--payment", type=int)
    p.add_argument("--note", required=True)

    p = sub.add_parser("timeline")
    p.add_argument("--last", type=int)

    p = sub.add_parser("npc-log")
    p.add_argument("--name", required=True)

    sub.add_parser("contract-log")
    sub.add_parser("chapter-log")

    args = parser.parse_args()

    if args.cmd == "record":
        print(record(args.type, args.chapter, args.npc, args.contract, args.outcome, args.payment, args.note))
    elif args.cmd == "timeline":
        for ln in timeline(args.last):
            print(ln)
    elif args.cmd == "npc-log":
        for ln in filter_log("npc", args.name):
            print(ln)
    elif args.cmd == "contract-log":
        for ln in filter_log("contract", "contract"):
            print(ln)
    elif args.cmd == "chapter-log":
        for ln in filter_log("chapter", "CHAPTER"):
            print(ln)


if __name__ == "__main__":
    main()
