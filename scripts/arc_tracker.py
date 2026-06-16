#!/usr/bin/env python3
"""Narrative arc tracker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WORKSPACE = ROOT / "workspace"
JOURNAL = WORKSPACE / "journal.md"


VOLUME_FILES = [
    DATA / "volumes" / "volume_arcs.yaml",
    DATA / "volumes" / "volumes_1_3.yaml",
    DATA / "volumes" / "volumes_4_7.yaml",
    DATA / "volumes" / "volumes_8_10.yaml",
]


def _load_yaml(path: Path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _band():
    return _load_yaml(DATA / "band_state.yaml")


def status() -> dict:
    b = _band().get("band", {})
    day = int(b.get("day_of_year", 1))
    year = int(b.get("year", 312))
    # rough seasonal volume progression mapping
    volume = 1 + max(0, (day - 1) // 36)
    volume = min(10, volume)
    arc_phase = "RISING ACTION" if day < 120 else "MID-ARC" if day < 240 else "ENDGAME"
    dangling = len(threads().get("threads", []))
    cold = len(threads(cold_days=30).get("threads", []))
    return {
        "day": day,
        "year": year,
        "volume": volume,
        "arc_phase": arc_phase,
        "dangling_threads": dangling,
        "cold_threads": cold,
    }


def _events() -> list[dict]:
    out = []
    events_dir = DATA / "events"
    if not events_dir.exists():
        return out
    for p in events_dir.glob("*.yaml"):
        data = _load_yaml(p)
        out.extend(data.get("events", []))
    return out


def threads(cold_days: int | None = None) -> dict:
    b = _band().get("band", {})
    today = int(b.get("day_of_year", 1))
    out = []
    for e in _events():
        if e.get("chain") and not e.get("resolved", False):
            day = int(e.get("day", today))
            age = max(0, today - day)
            if cold_days is None or age >= cold_days:
                out.append({
                    "id": e.get("id"),
                    "chain": e.get("chain"),
                    "title": e.get("title"),
                    "age_days": age,
                })
    return {"threads": sorted(out, key=lambda x: (-x["age_days"], x["id"]))}


def volume_map() -> dict:
    rows = []
    for vf in VOLUME_FILES:
        if not vf.exists():
            continue
        data = _load_yaml(vf)
        rows.append({"file": vf.name, "keys": list(data.keys())[:10]})
    return {"volumes": rows}


def chapter_types() -> dict:
    counts: dict[str, int] = {}
    if JOURNAL.exists():
        for ln in JOURNAL.read_text(encoding="utf-8").splitlines():
            if "CHAP_" in ln:
                t = ln.split("CHAP_")[-1].split("]")[0].split()[0]
                counts[t] = counts.get(t, 0) + 1
    return {"chapter_types": counts}


def character_arc(npc: str) -> dict:
    hits = []
    if JOURNAL.exists():
        for ln in JOURNAL.read_text(encoding="utf-8").splitlines():
            if npc.lower() in ln.lower():
                hits.append(ln)
    return {"npc": npc, "entries": hits[-20:]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Arc tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("threads")
    p.add_argument("--cold", type=int)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("volume-map")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("chapter-types")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("character-arc")
    p.add_argument("--npc", required=True)
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "status":
        out = status()
    elif args.cmd == "threads":
        out = threads(args.cold)
    elif args.cmd == "volume-map":
        out = volume_map()
    elif args.cmd == "chapter-types":
        out = chapter_types()
    else:
        out = character_arc(args.npc)

    if getattr(args, "json", False):
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
