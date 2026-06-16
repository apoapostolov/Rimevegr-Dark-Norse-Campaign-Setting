"""Prompt 5 tests — formation warfare, morale contagion, and rout/pursuit dynamics."""

from __future__ import annotations

import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from combat_model import Fighter
from combat_sim import _update_formation_and_morale, run_skirmish
from combat_types import Stance


def _fighter(name: str, **kwargs) -> Fighter:
    base = dict(
        name=name,
        mig=5,
        nim=5,
        tou=5,
        wit=5,
        wil=5,
        weapon_skill=2,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        max_hp=50,
        hp=50,
    )
    base.update(kwargs)
    return Fighter(**base)


def _team(prefix: str, n: int, **kwargs) -> list[Fighter]:
    return [_fighter(f"{prefix}{i}", **kwargs) for i in range(n)]


def _avg_cohesion(side: dict) -> float:
    vals = [s.get("cohesion_score", 0) for s in side.values()]
    return sum(vals) / max(1, len(vals))


def test_shield_wall_vs_loose_line_shows_durability_gap():
    random.seed(51)
    side_a = _team("A", 8, formation="shield_wall", weapon_type="spear")
    side_b = _team("B", 8, formation="loose_line", weapon_type="sword")

    result = run_skirmish(side_a, side_b, max_rounds=6, combat_mode="skirmish")

    a_cohesion = _avg_cohesion(result["side_a"])
    b_cohesion = _avg_cohesion(result["side_b"])

    assert a_cohesion > b_cohesion, (
        f"Expected shield wall to hold cohesion better; got A={a_cohesion:.2f}, B={b_cohesion:.2f}"
    )


def test_leader_down_triggers_measurable_morale_drop():
    side = [
        _fighter("Captain", is_commander=True, is_down=True, morale_score=70, cohesion_score=70),
        _fighter("A1", morale_score=70, cohesion_score=70),
        _fighter("A2", morale_score=70, cohesion_score=70),
        _fighter("A3", morale_score=70, cohesion_score=70),
    ]
    enemies = [_fighter("E1"), _fighter("E2"), _fighter("E3")]

    before = {f.name: f.morale_score for f in side if not f.is_down}
    actions: list[dict] = []

    _update_formation_and_morale(
        side,
        enemies,
        incoming_attackers={"A1": ["E1"], "A2": ["E2"], "A3": ["E3"]},
        actions=actions,
        round_num=1,
    )

    after = {f.name: f.morale_score for f in side if not f.is_down}
    assert sum(after.values()) < sum(before.values())


def test_flank_collapse_cascades_locally(monkeypatch):
    # Force cascade branch probability checks to succeed.
    monkeypatch.setattr("random.random", lambda: 0.0)

    side = [
        _fighter("Break", cohesion_score=12, morale_score=12, formation="shield_wall", rout_state="steady"),
        _fighter("Wing1", cohesion_score=60, morale_score=60, rout_state="wavering"),
        _fighter("Wing2", cohesion_score=60, morale_score=60, rout_state="steady"),
    ]
    enemies = [_fighter("E1"), _fighter("E2"), _fighter("E3")]

    actions: list[dict] = []
    _update_formation_and_morale(
        side,
        enemies,
        incoming_attackers={"Break": ["E1", "E2", "E3"]},
        actions=actions,
        round_num=1,
    )

    shock_events = [a for a in actions if a.get("type") == "morale_shock"]
    assert shock_events, "Expected morale_shock events after local breakpoint"


def test_pursuit_can_backfire_with_overextension(monkeypatch):
    # Force pursue + overextend branch to fire when eligible.
    monkeypatch.setattr("random.random", lambda: 0.0)

    chaser = _fighter(
        "Chaser",
        formation="loose_line",
        cohesion_score=20,
        morale_score=65,
        stance=Stance.AGGRESSIVE,
        mig=7,
        weapon_skill=4,
    )
    routed = _fighter(
        "Routed",
        rout_state="rout",
        formation="broken",
        cohesion_score=8,
        morale_score=8,
        nim=2,
        max_hp=70,
        hp=70,
    )

    result = run_skirmish([chaser], [routed], max_rounds=1, combat_mode="skirmish")
    events = [a for a in result["round_log"][0]["actions"] if a.get("type") == "pursuit_event"]

    assert any(e.get("result") == "overextended" for e in events), "Expected overextended pursuit event"
    assert result["side_a"]["Chaser"]["cohesion_score"] <= 12
