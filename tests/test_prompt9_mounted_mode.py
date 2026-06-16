"""Prompt 9 tests — mounted combat, anti-cavalry counters, and dismount flow."""

from __future__ import annotations

import pathlib
import random
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from combat_model import Fighter
from combat_sim import _resolve_mounted_charge
from combat_types import Maneuver, Stance


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
        max_hp=40,
        hp=40,
        mounted=False,
        mount_condition="steady",
        rider_stability=70,
        mount_fatigue=0,
        stance=Stance.BALANCED,
        terrain="open",
    )
    base.update(kwargs)
    return Fighter(**base)


def test_open_field_charge_produces_first_contact_spike():
    random.seed(91)
    rider = _fighter("Rider", mounted=True, weapon_type="lance", stance=Stance.AGGRESSIVE, weapon_skill=4)
    foot = _fighter("Foot", weapon_type="sword", stance=Stance.BALANCED)

    actions: list[dict] = []
    state = _resolve_mounted_charge(
        rider,
        foot,
        defender_maneuver=Maneuver.CUT,
        allied_count=4,
        enemy_count=4,
        actions=actions,
        round_num=1,
    )

    assert state["charged"], "Expected mounted charge window in open-field setup"
    assert state["attack_mod"] > 0
    assert state["bonus_damage"] >= 2
    assert any(a.get("type") == "mount_charge" for a in actions)


def test_braced_spear_reduces_mounted_success_materially():
    trials = 40
    open_attack_mod = 0
    open_bonus = 0
    brace_attack_mod = 0
    brace_bonus = 0
    brace_successes = 0

    for i in range(trials):
        random.seed(9200 + i)
        rider_a = _fighter("RiderA", mounted=True, weapon_type="lance", stance=Stance.AGGRESSIVE, weapon_skill=4)
        no_brace = _fighter("NoBrace", weapon_type="sword", stance=Stance.BALANCED)
        act_a: list[dict] = []
        out_no_brace = _resolve_mounted_charge(
            rider_a,
            no_brace,
            defender_maneuver=Maneuver.CUT,
            allied_count=4,
            enemy_count=4,
            actions=act_a,
            round_num=1,
        )
        open_attack_mod += out_no_brace["attack_mod"]
        open_bonus += out_no_brace["bonus_damage"]

        random.seed(9200 + i)
        rider_b = _fighter("RiderB", mounted=True, weapon_type="lance", stance=Stance.AGGRESSIVE, weapon_skill=4)
        brace = _fighter("Brace", weapon_type="spear", stance=Stance.DEFENSIVE, weapon_skill=4)
        act_b: list[dict] = []
        out_brace = _resolve_mounted_charge(
            rider_b,
            brace,
            defender_maneuver=Maneuver.GUARD,
            allied_count=4,
            enemy_count=4,
            actions=act_b,
            round_num=1,
        )
        brace_attack_mod += out_brace["attack_mod"]
        brace_bonus += out_brace["bonus_damage"]
        brace_successes += sum(1 for a in act_b if a.get("type") == "anti_cavalry_brace" and a.get("success"))

    assert brace_successes > 0
    assert brace_attack_mod < open_attack_mod
    assert brace_bonus <= open_bonus


def test_tight_terrain_cavalry_underperforms_open_terrain():
    random.seed(93)
    open_rider = _fighter("OpenRider", mounted=True, weapon_type="lance", stance=Stance.AGGRESSIVE, terrain="open")
    foot_open = _fighter("FootOpen")
    open_actions: list[dict] = []
    out_open = _resolve_mounted_charge(
        open_rider,
        foot_open,
        defender_maneuver=Maneuver.CUT,
        allied_count=4,
        enemy_count=4,
        actions=open_actions,
        round_num=1,
    )

    random.seed(93)
    tight_rider = _fighter("TightRider", mounted=True, weapon_type="lance", stance=Stance.AGGRESSIVE, terrain="dense_forest")
    foot_tight = _fighter("FootTight")
    tight_actions: list[dict] = []
    out_tight = _resolve_mounted_charge(
        tight_rider,
        foot_tight,
        defender_maneuver=Maneuver.CUT,
        allied_count=4,
        enemy_count=4,
        actions=tight_actions,
        round_num=1,
    )

    assert out_tight["attack_mod"] <= out_open["attack_mod"]
    assert out_tight["bonus_damage"] <= out_open["bonus_damage"]


def test_forced_dismount_creates_vulnerability_window(monkeypatch: pytest.MonkeyPatch):
    # Force all probabilistic branches toward charge + brace success + dismount path.
    monkeypatch.setattr(random, "random", lambda: 0.0)

    rider = _fighter(
        "Rider",
        mounted=True,
        weapon_type="lance",
        stance=Stance.AGGRESSIVE,
        rider_stability=25,
    )
    bracer = _fighter("Bracer", weapon_type="spear", stance=Stance.DEFENSIVE, weapon_skill=4)

    actions: list[dict] = []
    _resolve_mounted_charge(
        rider,
        bracer,
        defender_maneuver=Maneuver.GUARD,
        allied_count=4,
        enemy_count=4,
        actions=actions,
        round_num=1,
    )

    assert rider.mounted is False
    assert rider.dismount_vulnerability_rounds > 0
    assert any(a.get("type") == "dismount_event" for a in actions)
