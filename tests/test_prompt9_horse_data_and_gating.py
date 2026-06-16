"""Prompt 9 follow-up tests — horse data ingestion and horses_allowed gating."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from band_manager import combat_roster
from combat_model import Fighter
from combat_sim import _resolve_mounted_charge, run_skirmish
from combat_types import Maneuver, Stance
from npc_combat import _extract_mount_state


def _fighter(name: str, **kwargs) -> Fighter:
    base = dict(
        name=name,
        mig=5,
        nim=5,
        tou=5,
        wit=5,
        wil=5,
        weapon_skill=3,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        max_hp=40,
        hp=40,
        stance=Stance.AGGRESSIVE,
        mounted=False,
        mount_condition="steady",
        rider_stability=70,
        terrain="open",
    )
    base.update(kwargs)
    return Fighter(**base)


def test_mounted_charge_disabled_when_horses_not_allowed():
    rider = _fighter("Rider", mounted=True, weapon_type="lance")
    foot = _fighter("Foot")

    out = _resolve_mounted_charge(
        rider,
        foot,
        defender_maneuver=Maneuver.CUT,
        allied_count=4,
        enemy_count=4,
        actions=[],
        round_num=1,
        horses_allowed=False,
    )

    assert out["charged"] is False
    assert out["attack_mod"] == 0
    assert out["bonus_damage"] == 0


def test_run_skirmish_strips_mounted_state_when_horses_disallowed():
    rider_a = _fighter("RiderA", mounted=True, weapon_type="lance")
    rider_b = _fighter("RiderB", mounted=True, weapon_type="lance")

    result = run_skirmish([rider_a], [rider_b], max_rounds=1, horses_allowed=False)

    assert result["horses_allowed"] is False
    assert result["side_a"]["RiderA"]["mounted"] is False
    assert result["side_b"]["RiderB"]["mounted"] is False



def test_band_manager_combat_roster_reads_horse_payload():
    band = {
        "members": [
            {
                "name": "Mounted One",
                "status": "active",
                "mig": 6,
                "nim": 5,
                "tou": 6,
                "wit": 5,
                "wil": 5,
                "weapon_skill": 2,
                "weapon_base": 6,
                "weapon_speed": 3,
                "shield_skill": 1,
                "shield_def": 2,
                "armor": {"head": 0, "torso": 2, "right_arm": 1, "left_arm": 1, "legs": 1, "hands": 0, "feet": 0},
                "horse": {
                    "has_horse": True,
                    "condition": "steady",
                    "rider_stability": 73,
                    "fatigue": 9,
                },
            }
        ]
    }

    roster = combat_roster(band)
    assert roster[0]["mounted"] is True
    assert roster[0]["mount_condition"] == "steady"
    assert roster[0]["rider_stability"] == 73
    assert roster[0]["mount_fatigue"] == 9



def test_npc_mount_state_prefers_explicit_then_band_inference():
    explicit = _extract_mount_state(
        {
            "band": "The Silent Oar",
            "role": "fighter",
            "horse": {"has_horse": True, "condition": "wounded", "rider_stability": 61, "fatigue": 18},
        }
    )
    assert explicit["mounted"] is True
    assert explicit["mount_condition"] == "wounded"

    inferred = _extract_mount_state(
        {
            "band": "The Three Wolves",
            "role": "scout",
        }
    )
    assert inferred["mounted"] is True
    assert inferred["mount_condition"] == "steady"
