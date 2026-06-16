"""test_resistances.py — Tests for Batch 3: Resistance System (combat_sim.apply_resistances)."""

import pytest

from combat_model import Fighter
from combat_types import Maneuver
from combat_sim import apply_resistances


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_fighter(**kwargs) -> Fighter:
    defaults = dict(
        name="Test",
        mig=5, nim=5, tou=5, wit=3, wil=3,
        weapon_skill=1, weapon_base=6, weapon_speed=3,
    )
    defaults.update(kwargs)
    return Fighter(**defaults)


# ── physical_weapons resistance ───────────────────────────────────────────────

class TestPhysicalWeaponsResistance:
    """physical_weapons resistance zeroes mundane physical damage."""

    def test_cut_deals_zero(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 0

    def test_heavy_blow_deals_zero(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 12, "physical", Maneuver.HEAVY_BLOW)
        assert result == 0

    def test_thrust_deals_zero(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 6, "physical", Maneuver.THRUST)
        assert result == 0

    def test_fire_damage_bypasses(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 8, "fire", Maneuver.CUT)
        assert result == 8

    def test_cold_damage_bypasses(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 8, "cold", Maneuver.CUT)
        assert result == 8

    def test_supernatural_damage_bypasses(self):
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(defender, 8, "supernatural", Maneuver.CUT)
        assert result == 8

    def test_iron_weapon_property_bypasses(self):
        """Iron weapon property bypasses physical_weapons resistance."""
        defender = _make_fighter(name="Ghost", resistances=["physical_weapons"])
        result = apply_resistances(
            defender, 8, "physical", Maneuver.CUT, weapon_properties=["iron"]
        )
        assert result == 8


# ── cold resistance ───────────────────────────────────────────────────────────

class TestColdResistance:
    """cold resistance halves cold-typed damage."""

    def test_cold_damage_halved(self):
        defender = _make_fighter(name="Draugr", resistances=["cold"])
        result = apply_resistances(defender, 10, "cold", Maneuver.CUT)
        assert result == 5

    def test_cold_damage_rounds_down(self):
        defender = _make_fighter(name="Draugr", resistances=["cold"])
        result = apply_resistances(defender, 7, "cold", Maneuver.CUT)
        assert result == 3

    def test_cold_min_1(self):
        defender = _make_fighter(name="Draugr", resistances=["cold"])
        result = apply_resistances(defender, 1, "cold", Maneuver.CUT)
        assert result == 1

    def test_physical_damage_unaffected(self):
        defender = _make_fighter(name="Draugr", resistances=["cold"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8


# ── cold_immune resistance ────────────────────────────────────────────────────

class TestColdImmuneResistance:
    """cold_immune resistance fully blocks cold damage."""

    def test_cold_damage_zeroed(self):
        defender = _make_fighter(name="IceCrystal", resistances=["cold_immune"])
        result = apply_resistances(defender, 10, "cold", Maneuver.CUT)
        assert result == 0

    def test_physical_still_lands(self):
        defender = _make_fighter(name="IceCrystal", resistances=["cold_immune"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8


# ── piercing resistance ───────────────────────────────────────────────────────

class TestPiercingResistance:
    """piercing resistance halves thrust/piercing damage."""

    def test_thrust_halved(self):
        defender = _make_fighter(name="BloatedDraugr", resistances=["piercing"])
        result = apply_resistances(defender, 10, "physical", Maneuver.THRUST)
        assert result == 5

    def test_cut_unaffected(self):
        defender = _make_fighter(name="BloatedDraugr", resistances=["piercing"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8

    def test_heavy_blow_unaffected(self):
        defender = _make_fighter(name="BloatedDraugr", resistances=["piercing"])
        result = apply_resistances(defender, 8, "physical", Maneuver.HEAVY_BLOW)
        assert result == 8


# ── cutting_weapons resistance ────────────────────────────────────────────────

class TestCuttingWeaponsResistance:
    """cutting_weapons resistance zeroes CUT and HEAVY_BLOW damage (troll stone skin)."""

    def test_cut_zeroed(self):
        defender = _make_fighter(name="Troll", resistances=["cutting_weapons"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 0

    def test_heavy_blow_zeroed(self):
        defender = _make_fighter(name="Troll", resistances=["cutting_weapons"])
        result = apply_resistances(defender, 12, "physical", Maneuver.HEAVY_BLOW)
        assert result == 0

    def test_thrust_unaffected(self):
        defender = _make_fighter(name="Troll", resistances=["cutting_weapons"])
        result = apply_resistances(defender, 8, "physical", Maneuver.THRUST)
        assert result == 8


# ── all_physical resistance ───────────────────────────────────────────────────

class TestAllPhysicalResistance:
    """all_physical resistance zeroes all incoming damage."""

    def test_cut_zeroed(self):
        defender = _make_fighter(name="VeilEntity", resistances=["all_physical"])
        result = apply_resistances(defender, 10, "physical", Maneuver.CUT)
        assert result == 0

    def test_thrust_zeroed(self):
        defender = _make_fighter(name="VeilEntity", resistances=["all_physical"])
        result = apply_resistances(defender, 10, "physical", Maneuver.THRUST)
        assert result == 0

    def test_fire_zeroed(self):
        """all_physical blocks even fire — total immunity."""
        defender = _make_fighter(name="VeilEntity", resistances=["all_physical"])
        result = apply_resistances(defender, 10, "fire", Maneuver.CUT)
        assert result == 0


# ── non-magical weapons resistance ───────────────────────────────────────────

class TestNonMagicalWeaponsResistance:
    """non-magical_weapons resistance halves damage (like ancient_resilience trait)."""

    def test_damage_halved_hyphenated(self):
        defender = _make_fighter(name="AncientDead", resistances=["non-magical_weapons"])
        result = apply_resistances(defender, 10, "physical", Maneuver.CUT)
        assert result == 5

    def test_damage_halved_with_space(self):
        """Spaced variant (normalized by bestiary_loader) also works."""
        defender = _make_fighter(name="AncientDead", resistances=["non-magical weapons"])
        result = apply_resistances(defender, 10, "physical", Maneuver.CUT)
        assert result == 5


# ── bleeding resistance (pass-through) ───────────────────────────────────────

class TestBleedingResistance:
    """bleeding resistance is handled in apply_wound/_update_wound_state, not here."""

    def test_bleeding_tag_does_not_change_damage(self):
        defender = _make_fighter(name="Undead", resistances=["bleeding"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8


# ── pain / pain_penalties resistance ─────────────────────────────────────────

class TestPainResistance:
    """pain / pain_penalties resistance zeroes wound_penalty (handled in model)."""

    def test_pain_tag_does_not_change_damage(self):
        """apply_resistances does not modify damage; effect is in wound_penalty."""
        defender = _make_fighter(name="Bear", resistances=["pain"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8

    def test_pain_penalties_tag_same(self):
        defender = _make_fighter(name="Bear", resistances=["pain_penalties"])
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8

    def test_pain_resistance_sets_wound_penalty_zero(self):
        """Fighter with pain resistance keeps wound_penalty=0 after wounds."""
        fighter = _make_fighter(name="Bear", resistances=["pain"])
        # Inflict wounds to accumulate penalty
        fighter.apply_wound("torso", 6)   # serious
        fighter.apply_wound("torso", 10)  # critical
        assert fighter.wound_penalty == 0

    def test_pain_penalties_sets_wound_penalty_zero(self):
        fighter = _make_fighter(name="Bear", resistances=["pain_penalties"])
        fighter.apply_wound("torso", 6)
        fighter.apply_wound("torso", 10)
        assert fighter.wound_penalty == 0


# ── combined resistances ──────────────────────────────────────────────────────

class TestCombinedResistances:
    """Multiple resistances apply in sequence."""

    def test_cold_and_piercing_on_cold_thrust(self):
        """Cold thrust: cold halves first (cold resistance), then trust halves (piercing)."""
        defender = _make_fighter(name="Draugr", resistances=["cold", "piercing"])
        dmg_start = 12
        result = apply_resistances(defender, dmg_start, "cold", Maneuver.THRUST)
        # cold: 12 → 6 (halved), piercing: 6 → 3 (halved again)
        assert result == 3

    def test_no_resistances_unchanged(self):
        defender = _make_fighter(name="Human")
        result = apply_resistances(defender, 8, "physical", Maneuver.CUT)
        assert result == 8
