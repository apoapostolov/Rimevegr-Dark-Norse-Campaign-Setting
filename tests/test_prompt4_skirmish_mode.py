"""Prompt 4 tests — skirmish perception economy, mode boundaries, and directional lethality."""

from __future__ import annotations

import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from combat_model import Fighter
from combat_sim import resolve_attack, run_skirmish
from combat_targeting import (
    build_perception_snapshot,
    choose_skirmish_target_perception,
    resolve_order_state,
)
from combat_types import Maneuver


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
    )
    base.update(kwargs)
    return Fighter(**base)


def _team(prefix: str, n: int, **kwargs) -> list[Fighter]:
    return [_fighter(f"{prefix}{i}", **kwargs) for i in range(n)]


def test_auto_mode_threshold_10_vs_11():
    random.seed(11)
    # 10 combatants -> normal
    r10 = run_skirmish(_team("A", 5), _team("B", 5), max_rounds=1, combat_mode="auto")
    assert r10["combat_mode"] == "normal"

    # 11 combatants -> skirmish
    r11 = run_skirmish(_team("A", 6), _team("B", 5), max_rounds=1, combat_mode="auto")
    assert r11["combat_mode"] == "skirmish"


def test_manual_mode_override_supersedes_auto():
    random.seed(12)
    # 11 combatants but forced normal
    forced_normal = run_skirmish(_team("A", 6), _team("B", 5), max_rounds=1, combat_mode="normal")
    assert forced_normal["combat_mode"] == "normal"

    # 8 combatants but forced skirmish
    forced_sk = run_skirmish(_team("A", 4), _team("B", 4), max_rounds=1, combat_mode="skirmish")
    assert forced_sk["combat_mode"] == "skirmish"


def test_mode_isolation_normal_has_no_prompt4_awareness_events():
    random.seed(13)
    result = run_skirmish(_team("A", 3), _team("B", 3), max_rounds=2, combat_mode="auto")
    assert result["combat_mode"] == "normal"

    for rnd in result["round_log"]:
        for act in rnd.get("actions", []):
            assert act.get("type") not in {"awareness_update", "order_friction"}
            assert "attack_vector" not in act


def test_skirmish_mode_emits_awareness_events():
    random.seed(14)
    side_a = [_fighter("Cmd", traits=["rally_allies"], weapon_skill=3, wil=7, wit=7)] + _team("A", 5)
    side_b = _team("B", 5)
    result = run_skirmish(side_a, side_b, max_rounds=1, combat_mode="auto")
    assert result["combat_mode"] == "skirmish"

    found = False
    for rnd in result["round_log"]:
        for act in rnd.get("actions", []):
            if act.get("type") == "awareness_update":
                found = True
                break
    assert found, "Expected awareness_update events in skirmish mode"


def test_unseen_target_exclusion_before_detection():
    random.seed(15)
    attacker = _fighter(
        "Scout",
        attention_budget_base=1,
        awareness=1,
        discipline=1,
        current_target_name="E0",
        turns_on_target=2,
    )
    enemies = [_fighter(f"E{i}") for i in range(4)]

    chosen, meta = choose_skirmish_target_perception(
        attacker,
        enemies,
        ally_assignments={},
        active_orders={},
        round_num=1,
        incoming_threats=[],
        local_noise=3,
    )

    perceived = set(meta.get("perceived", []))
    unseen = {e.name for e in enemies} - perceived
    assert chosen.name in perceived
    assert chosen.name not in unseen


def test_command_friction_high_vs_low_discipline():
    random.seed(16)
    disciplined = _fighter("Disc", discipline=3, order_reliability=0.9, stress_load=10)
    chaotic = _fighter("Chaos", traits=["frenzy"], order_reliability=0.2, stress_load=60)

    disc_clear = 0
    chaos_clear = 0
    N = 300
    for _ in range(N):
        if resolve_order_state(disciplined, True, local_noise=4) == "received_clear":
            disc_clear += 1
        if resolve_order_state(chaotic, True, local_noise=4) == "received_clear":
            chaos_clear += 1

    assert disc_clear > chaos_clear


def test_rear_modifiers_increase_hit_rate_statistically():
    random.seed(17)
    trials = 250
    front_hits = 0
    rear_hits = 0

    for _ in range(trials):
        a = _fighter("Atk", mig=6, weapon_skill=3)
        d = _fighter("Def", nim=6, shield_skill=2, shield_def=10)

        front = resolve_attack(a, d, Maneuver.CUT, Maneuver.GUARD, {})
        if front.get("hit"):
            front_hits += 1

    for _ in range(trials):
        a = _fighter("Atk", mig=6, weapon_skill=3)
        d = _fighter("Def", nim=6, shield_skill=2, shield_def=10)

        a.action_attack_mod = 20
        d.action_defense_mod = -25
        rear = resolve_attack(a, d, Maneuver.CUT, Maneuver.GUARD, {})
        if rear.get("hit"):
            rear_hits += 1

    assert rear_hits > front_hits + 20, (
        f"Expected rear setup to out-hit front significantly, got front={front_hits}, rear={rear_hits}"
    )


def test_late_detection_pipeline_surfaces_incoming_threat():
    random.seed(18)
    actor = _fighter("Def", attention_budget_base=1, awareness=1, discipline=1)
    enemies = [_fighter("E0"), _fighter("E1"), _fighter("E2"), _fighter("E3")]

    # First pass: no incoming threat hint
    snap1 = build_perception_snapshot(actor, enemies, incoming_threats=[], local_noise=3, round_num=1)

    # Second pass: E3 attacks from blind side and should become focused/noticed
    snap2 = build_perception_snapshot(actor, enemies, incoming_threats=["E3"], local_noise=3, round_num=2)

    first_visible = set(snap1["focused"] + snap1["noticed"])
    second_visible = set(snap2["focused"] + snap2["noticed"])

    assert "E3" not in first_visible or "E3" in second_visible
    assert "E3" in second_visible
