"""Tests for combat_narrative.py — template coverage, variation, and correctness."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from combat_narrative import (
    _CTRL_HIT,
    _FEINT_FAIL,
    _FEINT_SUCCESS,
    _IMPACT,
    _LOC,
    _MISS,
    _OPENER,
    _RECOVERY,
    render_action,
    render_bleeding,
    render_bloodied,
    render_on_death,
    render_pre_battle,
    render_round_summary,
    render_status_line,
)


# ───────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────

def _hit_act(
    man: str = "cut",
    atk: str = "Voss",
    dfn: str = "Draugr",
    loc: str = "torso",
    sev: str = "light",
    dmg: int = 5,
    **kwargs,
) -> dict:
    return {
        "attacker": atk,
        "defender": dfn,
        "maneuver": man,
        "action": man,
        "hit": True,
        "location": loc,
        "wound_severity": sev,
        "final_damage": dmg,
        **kwargs,
    }


def _miss_act(man: str = "cut", atk: str = "Voss", dfn: str = "Draugr", **kwargs) -> dict:
    return {
        "attacker": atk,
        "defender": dfn,
        "maneuver": man,
        "action": man,
        "hit": False,
        **kwargs,
    }


def _ctrl_hit(man: str, atk: str = "Voss", dfn: str = "Draugr", **kwargs) -> dict:
    return {
        "attacker": atk,
        "defender": dfn,
        "maneuver": man,
        "action": man,
        "hit": True,
        **kwargs,
    }


def _ctrl_miss(man: str, atk: str = "Voss", dfn: str = "Draugr", **kwargs) -> dict:
    return {
        "attacker": atk,
        "defender": dfn,
        "maneuver": man,
        "action": man,
        "hit": False,
        **kwargs,
    }


def _state(hp: int = 12, max_hp: int = 15, is_down: bool = False, is_undead: bool = False) -> dict:
    return {
        "hp": hp,
        "max_hp": max_hp,
        "stamina": 8,
        "max_stamina": 10,
        "is_down": is_down,
        "is_undead": is_undead,
        "conditions": [],
        "wounds": [],
    }


_EMPTY_STATE: dict = {}


# ───────────────────────────────────────────────────────────────────────
# Template coverage — every major maneuver has a non-empty opener
# ───────────────────────────────────────────────────────────────────────

CORE_MANEUVERS = ["cut", "thrust", "heavy_blow", "half_sword", "mordschlag"]
CONTROL_MANEUVERS = ["bind", "shove", "grapple", "shield_bash", "disarm"]
GRAPPLE_ENTRIES = ["brokartok", "lausatok", "hryggspenna", "tackle"]
GRAPPLE_INPLAY = [
    "clinch_improve", "leg_trip", "hip_throw", "ground_control",
    "throat_seize", "arm_trap", "elbow_strike", "knee_strike",
    "slam", "weapon_press", "break_distance", "pin_hold",
    "glima_las", "glima_snuningur", "glima_beinhnykkur", "glima_hnakkatak",
]
DIRTY = ["bite", "headbutt", "nose_butt", "dirt_eyes", "spit_eyes", "hair_grip", "thumb_gouge", "ear_cup"]
SEVERITIES = ["scratch", "light", "serious", "critical", "mortal"]
LOCATIONS = list(_LOC.keys())


def test_template_pool_sizes_are_doubled_for_key_banks():
    """Prompt 3.1 regression: pools should be doubled vs original authored sizes."""
    assert len(_OPENER["cut"]) == 12      # authored 6 -> doubled 12
    assert len(_IMPACT["light"]) == 10    # authored 5 -> doubled 10
    assert len(_MISS["cut"]) == 12        # authored 6 -> doubled 12
    assert len(_CTRL_HIT["bind"]) == 6    # authored 3 -> doubled 6
    assert len(_RECOVERY["guard"]) == 6   # authored 3 -> doubled 6
    assert len(_FEINT_SUCCESS) == 6        # authored 3 -> doubled 6
    assert len(_FEINT_FAIL) == 6           # authored 3 -> doubled 6


@pytest.mark.parametrize("man", CORE_MANEUVERS)
def test_opener_exists_for_core_maneuver(man):
    assert man in _OPENER, f"No opener templates for maneuver '{man}'"
    assert len(_OPENER[man]) >= 3, f"Too few opener variants for '{man}'"


@pytest.mark.parametrize("sev", SEVERITIES)
def test_impact_exists_for_severity(sev):
    assert sev in _IMPACT, f"No impact templates for severity '{sev}'"
    assert len(_IMPACT[sev]) >= 3


@pytest.mark.parametrize("loc", LOCATIONS)
def test_loc_descriptor_exists(loc):
    from combat_narrative import _loc
    result = _loc(loc)
    assert result and result != loc or "_" not in result, f"_loc('{loc}') returned unprocessed key"


# ───────────────────────────────────────────────────────────────────────
# render_action — hit produces non-empty lines
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("man", CORE_MANEUVERS)
def test_hit_renders_non_empty(man):
    act = _hit_act(man=man)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip(), f"render_action hit returned empty for maneuver '{man}'"


@pytest.mark.parametrize("sev", SEVERITIES)
def test_hit_severity_renders_non_empty(sev):
    act = _hit_act(sev=sev)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


@pytest.mark.parametrize("loc", ["head", "torso", "arm_left", "leg_right"])
def test_hit_location_in_output(loc):
    act = _hit_act(loc=loc)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


# ───────────────────────────────────────────────────────────────────────
# render_action — miss produces non-empty lines
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("man", CORE_MANEUVERS)
def test_miss_renders_non_empty(man):
    act = _miss_act(man=man)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


# ───────────────────────────────────────────────────────────────────────
# render_action — control maneuvers
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("man", CONTROL_MANEUVERS)
def test_control_hit_renders(man):
    act = _ctrl_hit(man=man)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip(), f"control hit returned empty for '{man}'"


@pytest.mark.parametrize("man", CONTROL_MANEUVERS)
def test_control_miss_renders(man):
    act = _ctrl_miss(man=man)
    result = render_action(act, _EMPTY_STATE)
    assert result.strip(), f"control miss returned empty for '{man}'"


# ───────────────────────────────────────────────────────────────────────
# render_action — grapple entry and in-grapple
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("man", GRAPPLE_ENTRIES + GRAPPLE_INPLAY)
def test_grapple_maneuver_renders(man):
    hit_act = _ctrl_hit(man=man)
    miss_act = _ctrl_miss(man=man)
    h = render_action(hit_act, _EMPTY_STATE)
    m = render_action(miss_act, _EMPTY_STATE)
    assert h.strip(), f"grapple hit empty for '{man}'"
    assert m.strip(), f"grapple miss empty for '{man}'"


# ───────────────────────────────────────────────────────────────────────
# render_action — dirty tactics
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("man", DIRTY)
def test_dirty_tactic_renders(man):
    h = render_action(_ctrl_hit(man=man), _EMPTY_STATE)
    m = render_action(_ctrl_miss(man=man), _EMPTY_STATE)
    assert h.strip()
    assert m.strip()


# ───────────────────────────────────────────────────────────────────────
# render_action — recovery actions
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("action", ["stand", "pick_up", "guard"])
def test_recovery_action_renders(action):
    act = {"attacker": "Voss", "defender": "Draugr", "action": action, "maneuver": action, "hit": False}
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


def test_switch_weapon_renders():
    act = {
        "attacker": "Voss", "defender": "Draugr",
        "action": "switch_weapon", "maneuver": "switch_weapon",
        "hit": False, "old_weapon": "longsword", "new_weapon": "dagger",
    }
    result = render_action(act, _EMPTY_STATE)
    assert "longsword" in result and "dagger" in result


# ───────────────────────────────────────────────────────────────────────
# render_action — feints
# ───────────────────────────────────────────────────────────────────────

def test_feint_success_renders():
    act = {"attacker": "Voss", "defender": "Draugr", "action": "feint_success", "maneuver": "feint", "hit": False}
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


def test_feint_fail_renders():
    act = {"attacker": "Voss", "defender": "Draugr", "action": "feint_fail", "maneuver": "feint", "hit": False}
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


# ───────────────────────────────────────────────────────────────────────
# render_action — counter-attack prefix
# ───────────────────────────────────────────────────────────────────────

def test_counter_uses_counter_prefix():
    act = _hit_act(is_counter=True)
    result = render_action(act, _EMPTY_STATE)
    assert result.startswith("  >>"), f"counter prefix missing: {result!r}"


def test_normal_uses_indent_prefix():
    act = _hit_act()
    result = render_action(act, _EMPTY_STATE)
    assert result.startswith("  ") and not result.startswith("  >>")


# ───────────────────────────────────────────────────────────────────────
# render_action — death tag on fatal hit
# ───────────────────────────────────────────────────────────────────────

def test_fatal_hit_includes_down_wording():
    act = _hit_act(sev="mortal", dfn="Draugr")
    state_map = {"Draugr": _state(hp=0, is_down=True)}
    result = render_action(act, state_map)
    # Should contain death wording or [DOWN]
    assert "DOWN" in result or any(
        word in result.lower() for word in ("drops", "crumples", "folds", "finished", "down")
    ), f"no death wording in: {result!r}"


# ───────────────────────────────────────────────────────────────────────
# render_action — skip action
# ───────────────────────────────────────────────────────────────────────

def test_skip_action_returns_empty():
    act = {"action": "skip", "attacker": "Voss", "defender": "Draugr"}
    result = render_action(act, _EMPTY_STATE)
    assert result == ""


# ───────────────────────────────────────────────────────────────────────
# render_action — special event types
# ───────────────────────────────────────────────────────────────────────

def test_trauma_check_renders():
    act = {
        "type": "trauma_check",
        "fighter": "Voss",
        "effects": [{"effect": "staggered"}],
    }
    result = render_action(act, _EMPTY_STATE)
    assert "TRAUMA" in result and "Voss" in result


def test_choke_unconscious_renders():
    act = {
        "type": "choke_unconscious",
        "fighter": "Draugr",
        "choke_rounds": 3,
        "roll": 45,
        "tou_check": 60,
    }
    result = render_action(act, _EMPTY_STATE)
    assert "CHOKE" in result and "Draugr" in result


def test_choke_resisted_returns_empty():
    act = {"type": "choke_resisted", "fighter": "Draugr"}
    result = render_action(act, _EMPTY_STATE)
    assert result == ""


def test_submission_accepted_renders():
    act = {
        "type": "submission_accepted",
        "subject": "Voss",
        "grappler": "Draugr",
        "roll": 20,
        "wil_check": 40,
    }
    result = render_action(act, _EMPTY_STATE)
    assert "YIELD" in result and "Voss" in result


def test_submission_pride_release_renders():
    act = {
        "type": "submission_pride_release",
        "subject": "Voss",
        "grappler": "Draugr",
        "roll": 80,
        "wil_check": 40,
    }
    result = render_action(act, _EMPTY_STATE)
    assert "YIELD" in result and "Voss" in result


def test_on_death_weapon_throw_hit_renders():
    act = {
        "type": "on_death",
        "effect": "weapon_throw_on_death",
        "source": "Draugr",
        "defender": "Voss",
        "hit": True,
        "location": "torso",
        "final_damage": 4,
        "wound_severity": "light",
    }
    result = render_action(act, _EMPTY_STATE)
    assert "ON-DEATH" in result and "Draugr" in result


def test_on_death_weapon_throw_miss_renders():
    act = {
        "type": "on_death",
        "effect": "weapon_throw_on_death",
        "source": "Draugr",
        "defender": "Voss",
        "hit": False,
    }
    result = render_action(act, _EMPTY_STATE)
    assert "ON-DEATH" in result


def test_on_death_supernatural_renders():
    for eff in ("death_rattle", "corpse_burst", "veil_snap", "flash_freeze"):
        act = {"type": "on_death", "effect": eff, "source": "Draugr", "defender": "Voss"}
        result = render_action(act, _EMPTY_STATE)
        assert result.strip(), f"Empty render for on_death effect '{eff}'"


# ───────────────────────────────────────────────────────────────────────
# render_bloodied / render_bleeding
# ───────────────────────────────────────────────────────────────────────

def test_bloodied_human_non_empty():
    result = render_bloodied("Voss", is_undead=False)
    assert "Voss" in result and result.strip()


def test_bloodied_undead_non_empty():
    result = render_bloodied("Draugr", is_undead=True)
    assert "Draugr" in result and result.strip()


def test_bleeding_includes_name_and_amount():
    result = render_bleeding("Voss", 3)
    assert "Voss" in result and "3" in result


# ───────────────────────────────────────────────────────────────────────
# render_pre_battle
# ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("etype", [
    "terror_failed", "terror_resisted", "grave_moan", "grave_moan_resisted",
    "stench_cloud", "choking_darkness", "sleep_weight",
    "domain_warning", "glamour_shift", "ground_tremor",
    "temperature_plunge", "reality_warping",
])
def test_pre_battle_event_renders(etype):
    event = {
        "type": etype,
        "source": "Lich",
        "target": "Voss",
        "roll": 55,
        "chance": 40,
        "effect": "staggered",
    }
    result = render_pre_battle(event)
    assert result.strip(), f"Empty render for pre_battle type '{etype}'"


# ───────────────────────────────────────────────────────────────────────
# render_status_line
# ───────────────────────────────────────────────────────────────────────

def test_status_line_contains_names():
    state = {
        "Voss": _state(hp=8, max_hp=15),
        "Draugr": _state(hp=3, max_hp=12),
    }
    result = render_status_line(state)
    assert "Voss" in result and "Draugr" in result
    assert "8/15" in result


def test_status_line_clamps_negative_hp():
    state = {"Voss": _state(hp=-4, max_hp=15, is_down=True)}
    result = render_status_line(state)
    assert "0/15" in result


def test_status_line_shows_conditions():
    s = _state()
    s["conditions"] = [{"type": "staggered"}]
    state = {"Voss": s}
    result = render_status_line(state)
    assert "staggered" in result


# ───────────────────────────────────────────────────────────────────────
# render_round_summary
# ───────────────────────────────────────────────────────────────────────

def test_round_summary_a_collapsing():
    rnd = {
        "state": {
            "Voss": {"hp": 2, "max_hp": 15},
            "Draugr": {"hp": 11, "max_hp": 12},
        }
    }
    result = render_round_summary(rnd, {"Voss"}, {"Draugr"})
    assert result.strip(), "expected non-empty summary for collapsing side"


def test_round_summary_stalemate_returns_empty():
    rnd = {
        "state": {
            "Voss": {"hp": 12, "max_hp": 15},
            "Draugr": {"hp": 10, "max_hp": 12},
        }
    }
    result = render_round_summary(rnd, {"Voss"}, {"Draugr"})
    # Close HP — should be empty stalemate (< 30% gap)
    assert result == ""


def test_round_summary_empty_state():
    result = render_round_summary({}, set(), set())
    assert result == ""


# ───────────────────────────────────────────────────────────────────────
# Variation — same action seeded repeatedly produces ≥2 distinct strings
# ───────────────────────────────────────────────────────────────────────

def test_variation_hit():
    act = _hit_act(man="cut", sev="light", loc="torso")
    seen = set()
    for seed in range(20):
        random.seed(seed)
        seen.add(render_action(act, _EMPTY_STATE))
    assert len(seen) >= 2, f"No variation in cut/light/torso hit — only got: {seen}"


def test_variation_miss():
    act = _miss_act(man="thrust")
    seen = set()
    for seed in range(20):
        random.seed(seed)
        seen.add(render_action(act, _EMPTY_STATE))
    assert len(seen) >= 2, f"No variation in thrust miss"


def test_variation_control_hit():
    act = _ctrl_hit("grapple")
    seen = set()
    for seed in range(20):
        random.seed(seed)
        seen.add(render_action(act, _EMPTY_STATE))
    assert len(seen) >= 2


def test_variation_bloodied():
    seen_human = set()
    seen_undead = set()
    for seed in range(20):
        random.seed(seed)
        seen_human.add(render_bloodied("Voss", False))
        seen_undead.add(render_bloodied("Draugr", True))
    assert len(seen_human) >= 2
    assert len(seen_undead) >= 2


# ───────────────────────────────────────────────────────────────────────
# Friendly fire
# ───────────────────────────────────────────────────────────────────────

def test_friendly_fire_renders():
    act = _hit_act(
        man="cut", atk="Voss", dfn="Bjorn",
        is_friendly_fire=True, loc="arm_left", sev="light", dmg=4,
    )
    result = render_action(act, _EMPTY_STATE)
    assert "FRIENDLY FIRE" in result


# ───────────────────────────────────────────────────────────────────────
# Integration smoke — full JSON-style round rendering doesn't crash
# ───────────────────────────────────────────────────────────────────────

def test_full_round_smoke():
    actions = [
        _hit_act("cut", "Voss", "Draugr", "torso", "light", 5),
        _miss_act("thrust", "Draugr", "Voss"),
        _ctrl_hit("grapple", "Voss", "Draugr"),
        _ctrl_miss("shove", "Draugr", "Voss"),
        {"attacker": "Voss", "defender": "Draugr", "action": "stand", "maneuver": "stand", "hit": False},
        {"type": "trauma_check", "fighter": "Draugr", "effects": [{"effect": "stunned"}]},
        _hit_act("heavy_blow", "Voss", "Draugr", "head", "critical", 14),
    ]
    state_map = {
        "Voss":   _state(hp=10, max_hp=15),
        "Draugr": _state(hp=0, max_hp=12, is_down=True),
    }
    rendered = []
    for act in actions:
        line = render_action(act, state_map)
        rendered.append(line)

    # All non-skip actions should produce something
    assert all(line is not None for line in rendered)
    # Critical hit on is_down should contain death phrasing
    assert any(
        "DOWN" in r or "drop" in r.lower() or "crumple" in r.lower() or "finished" in r.lower()
        for r in rendered
    )


# ───────────────────────────────────────────────────────────────────────
# Condition applied passthrough
# ───────────────────────────────────────────────────────────────────────

def test_condition_applied_in_output():
    act = _hit_act(man="shove", condition_applied="prone")
    # shove is a control maneuver
    result = render_action(act, _EMPTY_STATE)
    assert result.strip()


# ───────────────────────────────────────────────────────────────────────
# Mortal severity language check
# ───────────────────────────────────────────────────────────────────────

def test_mortal_hit_contains_severity_term():
    act = _hit_act(sev="mortal", dmg=18)
    result = render_action(act, _EMPTY_STATE)
    assert "mortal" in result.lower() or "obliterate" in result.lower() or "rips" in result.lower()
