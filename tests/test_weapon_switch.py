"""Tests for weapon switching (SWITCH_WEAPON maneuver) — see PROPOSAL_004."""
import pytest

from combat_sim import (
    Fighter,
    Maneuver,
    ConditionType,
    Condition,
    DIST_CLOSE, DIST_MELEE,
    get_weapon_size,
    get_weapon_reach,
    resolve_fighter_action,
)
from combat_ai import choose_maneuver


# ───────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────

def _fighter(weapon_type="spear", terrain="open", distance=DIST_MELEE,
             secondary=None):
    """Make a minimal Fighter instance for switch tests."""
    f = Fighter(
        name="A",
        mig=5, nim=5, tou=5, wit=5, wil=5,
        weapon_type=weapon_type,
        weapon_base=8,
        weapon_speed=3,
        weapon_skill=2,
        terrain_context=terrain,
        secondary_weapons=secondary or [],
    )
    f.current_distance = distance
    return f


def _opponent(weapon_type="sword"):
    o = Fighter(
        name="B",
        mig=5, nim=5, tou=5, wit=5, wil=5,
        weapon_type=weapon_type,
        weapon_base=6,
        weapon_speed=3,
        weapon_skill=2,
    )
    o.current_distance = DIST_MELEE
    return o


# ───────────────────────────────────────────────────────────────────────
# can_maneuver
# ───────────────────────────────────────────────────────────────────────

class TestCanManeuverSwitch:
    def test_false_when_no_secondary(self):
        f = _fighter()
        assert not f.can_maneuver(Maneuver.SWITCH_WEAPON)

    def test_true_when_secondary_available(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter(secondary=sec)
        assert f.can_maneuver(Maneuver.SWITCH_WEAPON)

    def test_false_when_grappled(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter(secondary=sec)
        f.conditions.append(Condition(type=ConditionType.GRAPPLED, remaining_rounds=-1))
        assert not f.can_maneuver(Maneuver.SWITCH_WEAPON)

    def test_false_when_pinned(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter(secondary=sec)
        f.conditions.append(Condition(type=ConditionType.PINNED, remaining_rounds=-1))
        assert not f.can_maneuver(Maneuver.SWITCH_WEAPON)

    def test_true_when_disarmed_with_secondary(self):
        """Drawing a backup is valid even while the DISARMED condition is active."""
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter(secondary=sec)
        f.conditions.append(Condition(type=ConditionType.DISARMED, remaining_rounds=-1))
        assert f.can_maneuver(Maneuver.SWITCH_WEAPON)


# ───────────────────────────────────────────────────────────────────────
# switch_to_best_secondary
# ───────────────────────────────────────────────────────────────────────

class TestSwitchToBestSecondary:
    def test_returns_none_when_no_secondary(self):
        f = _fighter()
        assert f.switch_to_best_secondary() is None

    def test_swaps_weapons_correctly(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        old_type = f.weapon_type

        result = f.switch_to_best_secondary()

        assert result is not None
        assert result["old_type"] == old_type
        assert result["new_type"] == "seax"
        assert f.weapon_type == "seax"
        assert f.weapon_base == 5

    def test_old_weapon_pushed_to_secondary(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        f.switch_to_best_secondary()

        assert len(f.secondary_weapons) == 1
        assert f.secondary_weapons[0]["type"] == "spear"

    def test_weapon_reach_and_size_update(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        f.switch_to_best_secondary()

        assert f.weapon_reach == get_weapon_reach("seax")
        assert f.weapon_size == get_weapon_size("seax")

    def test_prefer_size_selects_smaller_weapon(self):
        """When prefer_size=2 is given, a dagger should be chosen over a sword."""
        sec = [
            {"type": "sword", "base": 7, "speed": 3},
            {"type": "dagger", "base": 4, "speed": 2},
        ]
        f = _fighter("spear", secondary=sec)
        result = f.switch_to_best_secondary(prefer_size=2)

        assert result is not None
        # dagger size is 1 (≤2); sword size is 3 (>2) — must pick dagger
        assert result["new_type"] == "dagger"

    def test_prefer_size_falls_back_when_none_match(self):
        """When no secondary fits prefer_size, pick highest base damage."""
        sec = [
            {"type": "sword", "base": 7, "speed": 3},
            {"type": "long_axe", "base": 9, "speed": 2},
        ]
        f = _fighter("spear", secondary=sec)
        result = f.switch_to_best_secondary(prefer_size=1)  # nothing ≤ size 1

        assert result is not None
        # fallback to overall highest damage
        assert result["new_type"] == "long_axe"

    def test_double_switch_roundtrip(self):
        """Two consecutive switches should return to the original weapon."""
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        f.switch_to_best_secondary()
        f.switch_to_best_secondary()

        assert f.weapon_type == "spear"


# ───────────────────────────────────────────────────────────────────────
# resolve_fighter_action
# ───────────────────────────────────────────────────────────────────────

class TestResolveSwitch:
    def test_action_is_switch_weapon(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        o = _opponent()
        r = resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert r["action"] == "switch_weapon"
        assert r["hit"] is False

    def test_new_weapon_in_result(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        o = _opponent()
        r = resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert r["new_weapon"] == "seax"
        assert r["old_weapon"] == "spear"

    def test_fighter_weapon_updated_after_resolve(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        o = _opponent()
        resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert f.weapon_type == "seax"

    def test_fallback_to_guard_when_secondary_empty(self):
        """If secondary list is empty at resolution time, falls back to GUARD."""
        f = _fighter("spear", secondary=[])
        # Manually bypass can_maneuver by not checking it here
        o = _opponent()
        # We have to resolve directly; but can_maneuver is False so we call it directly
        # Simulate impossible state by temporarily bypassing
        f.secondary_weapons = []
        r = resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert r["action"] == "guard"

    def test_clears_disarmed_condition(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        f.conditions.append(Condition(type=ConditionType.DISARMED, remaining_rounds=-1))
        o = _opponent()
        resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert not f.has_condition(ConditionType.DISARMED)

    def test_stamina_cost_is_one(self):
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", secondary=sec)
        o = _opponent()
        before = f.stamina
        resolve_fighter_action(f, o, Maneuver.SWITCH_WEAPON, Maneuver.GUARD)
        assert f.stamina == before - 1


# ───────────────────────────────────────────────────────────────────────
# AI — choose_maneuver
# ───────────────────────────────────────────────────────────────────────

class TestAIChooseSwitch:
    def test_ai_switches_when_fouled(self):
        """Spear at CLOSE is reach-fouled; AI should choose SWITCH_WEAPON."""
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("spear", terrain="open", distance=DIST_CLOSE, secondary=sec)
        o = _opponent()
        o.current_distance = DIST_CLOSE
        # Run many times — should always switch (deterministic trigger)
        results = {choose_maneuver(f, o) for _ in range(30)}
        assert Maneuver.SWITCH_WEAPON in results

    def test_ai_switches_in_tight_terrain_with_large_weapon(self):
        """Great sword (size 4) in very_tight terrain with seax secondary → SWITCH_WEAPON."""
        sec = [{"type": "seax", "base": 5, "speed": 2}]
        f = _fighter("great_sword", terrain="barrow", distance=DIST_MELEE, secondary=sec)
        o = _opponent()
        o.current_distance = DIST_MELEE
        results = {choose_maneuver(f, o) for _ in range(30)}
        assert Maneuver.SWITCH_WEAPON in results

    def test_ai_does_not_switch_without_secondary(self):
        """No secondary → SWITCH_WEAPON should never appear."""
        f = _fighter("spear", terrain="barrow", distance=DIST_CLOSE, secondary=[])
        o = _opponent()
        o.current_distance = DIST_CLOSE
        for _ in range(50):
            assert choose_maneuver(f, o) != Maneuver.SWITCH_WEAPON

    def test_ai_does_not_switch_dagger_in_tight(self):
        """A small weapon (dagger, size 1) in tight terrain has no reason to switch."""
        sec = [{"type": "spear", "base": 9, "speed": 3}]  # larger secondary
        f = _fighter("dagger", terrain="barrow", distance=DIST_MELEE, secondary=sec)
        o = _opponent()
        o.current_distance = DIST_MELEE
        # Dagger size is 1 < 4, so tight-terrain trigger should not fire
        for _ in range(50):
            assert choose_maneuver(f, o) != Maneuver.SWITCH_WEAPON


# ───────────────────────────────────────────────────────────────────────
# bestiary_loader — secondary weapons populated
# ───────────────────────────────────────────────────────────────────────

class TestBestiarySecondaryWeapons:
    def test_single_weapon_entry_no_secondary(self):
        from bestiary_loader import pick_secondary_weapons_from_gear
        gear = {"weapons": [{"type": "spear", "base_damage": 8, "speed": 3}]}
        assert pick_secondary_weapons_from_gear(gear) == []

    def test_two_weapons_returns_lower_damage_as_secondary(self):
        from bestiary_loader import pick_secondary_weapons_from_gear
        gear = {"weapons": [
            {"type": "spear", "base_damage": 8, "speed": 3},
            {"type": "seax",  "base_damage": 5, "speed": 2},
        ]}
        sec = pick_secondary_weapons_from_gear(gear)
        assert len(sec) == 1
        assert sec[0]["type"] == "seax"
        assert sec[0]["base"] == 5

    def test_shield_not_included_as_secondary(self):
        from bestiary_loader import pick_secondary_weapons_from_gear
        gear = {"weapons": [
            {"type": "sword",  "base_damage": 7, "speed": 3},
            {"type": "shield", "base_damage": 2, "speed": 1},
        ]}
        sec = pick_secondary_weapons_from_gear(gear)
        assert sec == []

    def test_three_weapons_returns_two_secondaries_sorted(self):
        from bestiary_loader import pick_secondary_weapons_from_gear
        gear = {"weapons": [
            {"type": "spear",    "base_damage": 8, "speed": 3},
            {"type": "sword",    "base_damage": 7, "speed": 3},
            {"type": "dagger",   "base_damage": 4, "speed": 2},
        ]}
        sec = pick_secondary_weapons_from_gear(gear)
        assert len(sec) == 2
        assert sec[0]["type"] == "sword"   # higher damage first
        assert sec[1]["type"] == "dagger"

    def test_entry_to_fighter_populates_secondary(self):
        from bestiary_loader import entry_to_fighter
        entry = {
            "id": "TEST_01",
            "name": "Test Warrior",
            "stats": {"MIG": 5, "NIM": 5, "TOU": 5, "WIT": 4, "WIL": 4},
            "gear": {
                "weapons": [
                    {"type": "spear",  "name": "Spear",  "base_damage": 8, "speed": 3},
                    {"type": "seax",   "name": "Seax",   "base_damage": 5, "speed": 2},
                ]
            },
            "skills": [],
            "resistances": [],
            "sim_traits": [],
        }
        f = entry_to_fighter(entry)
        assert f.weapon_type == "spear"
        assert len(f.secondary_weapons) == 1
        assert f.secondary_weapons[0]["type"] == "seax"
