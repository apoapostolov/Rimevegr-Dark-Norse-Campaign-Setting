"""Tests for the weapon reach and distance management system (PROPOSAL_003)."""
import pytest
from combat_sim import (
    Fighter,
    Maneuver,
    ConditionType,
    DIST_GRAPPLE, DIST_CLOSE, DIST_MELEE, DIST_LONG,
    WEAPON_REACH_TABLE,
    get_weapon_reach,
    compute_reach_penalty,
    preferred_distance_band,
    resolve_fighter_action,
    run_duel,
)


# ───────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────

def make_fighter(name, weapon_type, weapon_base=6, weapon_skill=2, distance=DIST_MELEE):
    f = Fighter(
        name=name,
        mig=5, nim=5, tou=5, wit=5, wil=5,
        weapon_type=weapon_type,
        weapon_base=weapon_base,
        weapon_skill=weapon_skill,
    )
    f.current_distance = distance
    return f


# ───────────────────────────────────────────────────────────────────────
# compute_reach_penalty
# ───────────────────────────────────────────────────────────────────────

class TestComputeReachPenalty:
    def test_sword_at_melee_no_penalty(self):
        mod, fouled, override = compute_reach_penalty("sword", DIST_MELEE)
        assert mod == 0
        assert fouled is False
        assert override is None

    def test_sword_at_close_no_penalty(self):
        mod, fouled, override = compute_reach_penalty("sword", DIST_CLOSE)
        assert mod == 0

    def test_sword_at_grapple_penalty(self):
        mod, fouled, override = compute_reach_penalty("sword", DIST_GRAPPLE)
        assert mod == -15
        assert fouled is False

    def test_sword_at_long_penalty(self):
        mod, fouled, override = compute_reach_penalty("sword", DIST_LONG)
        assert mod == -20
        assert fouled is False

    def test_spear_at_melee_no_penalty(self):
        mod, fouled, override = compute_reach_penalty("spear", DIST_MELEE)
        assert mod == 0
        assert fouled is False

    def test_spear_at_long_no_penalty(self):
        mod, fouled, override = compute_reach_penalty("spear", DIST_LONG)
        assert mod == 0

    def test_spear_fouled_at_close(self):
        mod, fouled, override = compute_reach_penalty("spear", DIST_CLOSE)
        assert fouled is True
        assert mod == -30
        assert override == 3

    def test_spear_fouled_at_grapple(self):
        mod, fouled, override = compute_reach_penalty("spear", DIST_GRAPPLE)
        assert fouled is True
        assert override == 3

    def test_great_sword_fouled_at_grapple(self):
        mod, fouled, override = compute_reach_penalty("great_sword", DIST_GRAPPLE)
        assert fouled is True
        assert override == 3

    def test_great_sword_not_fouled_at_close(self):
        mod, fouled, override = compute_reach_penalty("great_sword", DIST_CLOSE)
        assert fouled is False

    def test_dagger_at_melee_penalty(self):
        mod, fouled, override = compute_reach_penalty("dagger", DIST_MELEE)
        assert mod == -20
        assert fouled is False

    def test_dagger_at_long_heavy_penalty(self):
        mod, fouled, override = compute_reach_penalty("dagger", DIST_LONG)
        assert mod == -40

    def test_unarmed_at_grapple_no_penalty(self):
        mod, fouled, override = compute_reach_penalty("unarmed", DIST_GRAPPLE)
        assert mod == 0

    def test_unarmed_at_close_penalty(self):
        mod, fouled, override = compute_reach_penalty("unarmed", DIST_CLOSE)
        assert mod == -20

    def test_unarmed_at_melee_heavy_penalty(self):
        mod, fouled, override = compute_reach_penalty("unarmed", DIST_MELEE)
        assert mod == -40

    def test_unknown_weapon_falls_back_to_generic(self):
        mod, fouled, override = compute_reach_penalty("unknown_type", DIST_MELEE)
        mod_ref, _, _ = compute_reach_penalty("generic", DIST_MELEE)
        assert mod == mod_ref

    def test_long_axe_fouled_at_grapple(self):
        mod, fouled, override = compute_reach_penalty("long_axe", DIST_GRAPPLE)
        assert fouled is True

    def test_hand_axe_never_fouled(self):
        for band in range(4):
            _, fouled, _ = compute_reach_penalty("hand_axe", band)
            assert fouled is False


# ───────────────────────────────────────────────────────────────────────
# get_weapon_reach
# ───────────────────────────────────────────────────────────────────────

class TestGetWeaponReach:
    def test_unarmed_reach_0(self):
        assert get_weapon_reach("unarmed") == 0

    def test_dagger_reach_1(self):
        assert get_weapon_reach("dagger") == 1

    def test_sword_reach_3(self):
        assert get_weapon_reach("sword") == 3

    def test_spear_reach_5(self):
        assert get_weapon_reach("spear") == 5

    def test_great_sword_reach_4(self):
        assert get_weapon_reach("great_sword") == 4

    def test_fallback_generic(self):
        assert get_weapon_reach("totally_unknown") == get_weapon_reach("generic")


# ───────────────────────────────────────────────────────────────────────
# Fighter.__post_init__ weapon_reach auto-set
# ───────────────────────────────────────────────────────────────────────

class TestFighterWeaponReach:
    def test_spear_fighter_reach_auto(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="spear")
        assert f.weapon_reach == 5

    def test_sword_fighter_reach_auto(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="sword")
        assert f.weapon_reach == 3

    def test_unarmed_fighter_reach_auto(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="unarmed")
        assert f.weapon_reach == 0

    def test_manual_override_preserved(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="sword", weapon_reach=5)
        assert f.weapon_reach == 5

    def test_default_current_distance_is_melee(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="sword")
        assert f.current_distance == DIST_MELEE


# ───────────────────────────────────────────────────────────────────────
# preferred_distance_band
# ───────────────────────────────────────────────────────────────────────

class TestPreferredDistanceBand:
    def test_unarmed_prefers_grapple(self):
        assert preferred_distance_band("unarmed") == DIST_GRAPPLE

    def test_spear_prefers_long(self):
        assert preferred_distance_band("spear") == DIST_LONG

    def test_sword_prefers_melee_or_close(self):
        pref = preferred_distance_band("sword")
        assert DIST_CLOSE <= pref <= DIST_MELEE

    def test_great_sword_prefers_long(self):
        pref = preferred_distance_band("great_sword")
        assert pref >= DIST_MELEE


# ───────────────────────────────────────────────────────────────────────
# STEP_IN / STEP_BACK actions
# ───────────────────────────────────────────────────────────────────────

class TestDistanceManeuvers:
    def _do_action(self, attacker, defender, maneuver):
        return resolve_fighter_action(attacker, defender, maneuver, Maneuver.CUT)

    def test_step_in_decrements_distance(self):
        a = make_fighter("A", "dagger", distance=DIST_MELEE)
        d = make_fighter("D", "sword", distance=DIST_MELEE)
        res = self._do_action(a, d, Maneuver.STEP_IN)
        assert res["action"] == "step_in"
        assert res["new_distance"] == DIST_CLOSE
        assert res["hit"] is False

    def test_step_back_increments_distance(self):
        a = make_fighter("A", "spear", distance=DIST_MELEE)
        d = make_fighter("D", "sword", distance=DIST_MELEE)
        res = self._do_action(a, d, Maneuver.STEP_BACK)
        assert res["action"] == "step_back"
        assert res["new_distance"] == DIST_LONG
        assert res["hit"] is False

    def test_step_in_cannot_go_below_grapple(self):
        a = make_fighter("A", "unarmed", distance=DIST_GRAPPLE)
        d = make_fighter("D", "dagger", distance=DIST_GRAPPLE)
        res = self._do_action(a, d, Maneuver.STEP_IN)
        assert res["new_distance"] == DIST_GRAPPLE

    def test_step_back_cannot_go_above_long(self):
        a = make_fighter("A", "spear", distance=DIST_LONG)
        d = make_fighter("D", "sword", distance=DIST_LONG)
        res = self._do_action(a, d, Maneuver.STEP_BACK)
        assert res["new_distance"] == DIST_LONG

    def test_step_in_costs_1_stamina(self):
        a = make_fighter("A", "dagger", distance=DIST_MELEE)
        d = make_fighter("D", "sword", distance=DIST_MELEE)
        stamina_before = a.stamina
        self._do_action(a, d, Maneuver.STEP_IN)
        assert a.stamina == stamina_before - 1

    def test_step_back_costs_1_stamina(self):
        a = make_fighter("A", "spear", distance=DIST_CLOSE)
        d = make_fighter("D", "dagger", distance=DIST_CLOSE)
        stamina_before = a.stamina
        self._do_action(a, d, Maneuver.STEP_BACK)
        assert a.stamina == stamina_before - 1


# ───────────────────────────────────────────────────────────────────────
# Reach penalty applied in attack resolution
# ───────────────────────────────────────────────────────────────────────

class TestReachPenaltyInAttack:
    def test_spear_at_close_has_haft_only_flag(self):
        a = make_fighter("A", "spear", weapon_base=6, distance=DIST_CLOSE)
        d = make_fighter("D", "sword", distance=DIST_CLOSE)
        # Run many iterations to hit diverse outcomes
        haft_seen = False
        for _ in range(50):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if res.get("haft_only"):
                haft_seen = True
                break
        assert haft_seen, "spear at CLOSE should produce haft_only flag"

    def test_dagger_at_long_has_reach_penalty(self):
        a = make_fighter("A", "dagger", distance=DIST_LONG)
        d = make_fighter("D", "spear", distance=DIST_LONG)
        res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
        assert res.get("reach_penalty", 0) <= -20

    def test_sword_at_melee_no_reach_penalty(self):
        a = make_fighter("A", "sword", distance=DIST_MELEE)
        d = make_fighter("D", "sword", distance=DIST_MELEE)
        for _ in range(20):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            assert res.get("reach_penalty", 0) == 0


# ───────────────────────────────────────────────────────────────────────
# Grapple entry distance gate
# ───────────────────────────────────────────────────────────────────────

class TestGrappleEntryDistanceGate:
    def test_grapple_entry_blocked_at_melee(self):
        a = make_fighter("A", "unarmed", distance=DIST_MELEE)
        assert not a.can_maneuver(Maneuver.BROKARTOK)
        assert not a.can_maneuver(Maneuver.LAUSATOK)
        assert not a.can_maneuver(Maneuver.TACKLE)

    def test_grapple_entry_available_at_close(self):
        a = make_fighter("A", "unarmed", distance=DIST_CLOSE)
        assert a.can_maneuver(Maneuver.BROKARTOK)
        assert a.can_maneuver(Maneuver.LAUSATOK)

    def test_grapple_entry_available_at_grapple_band(self):
        a = make_fighter("A", "unarmed", distance=DIST_GRAPPLE)
        assert a.can_maneuver(Maneuver.TACKLE)

    def test_legacy_grapple_blocked_at_melee(self):
        a = make_fighter("A", "dagger", distance=DIST_MELEE)
        assert not a.can_maneuver(Maneuver.GRAPPLE)

    def test_legacy_grapple_available_at_close(self):
        a = make_fighter("A", "dagger", distance=DIST_CLOSE)
        assert a.can_maneuver(Maneuver.GRAPPLE)

    def test_grapple_blocked_at_long(self):
        a = make_fighter("A", "unarmed", distance=DIST_LONG)
        assert not a.can_maneuver(Maneuver.BROKARTOK)
        assert not a.can_maneuver(Maneuver.TACKLE)


# ───────────────────────────────────────────────────────────────────────
# can_maneuver step_in / step_back
# ───────────────────────────────────────────────────────────────────────

class TestStepManeuverAvailability:
    def test_step_in_available_to_all_weapons(self):
        for wt in ["sword", "spear", "dagger", "unarmed", "hand_axe", "great_sword"]:
            f = make_fighter("f", wt)
            assert f.can_maneuver(Maneuver.STEP_IN), f"{wt} should have step_in"

    def test_step_back_available_to_all_weapons(self):
        for wt in ["sword", "spear", "dagger", "unarmed", "long_axe"]:
            f = make_fighter("f", wt)
            assert f.can_maneuver(Maneuver.STEP_BACK), f"{wt} should have step_back"


# ───────────────────────────────────────────────────────────────────────
# run_duel integration — distance tracking
# ───────────────────────────────────────────────────────────────────────

class TestRunDuelDistanceTracking:
    def test_duel_includes_distance_band_in_rounds(self):
        a = Fighter(name="sword_a", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="sword", weapon_base=7, weapon_skill=2)
        b = Fighter(name="spear_b", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="spear", weapon_base=6, weapon_skill=2)
        result = run_duel(a, b, max_rounds=5)
        for rnd in result["round_log"]:
            assert "distance_band" in rnd
            assert 0 <= rnd["distance_band"] <= 3

    def test_starting_distance_respected(self):
        a = Fighter(name="a", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="sword", weapon_base=7)
        b = Fighter(name="b", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="sword", weapon_base=7)
        result = run_duel(a, b, max_rounds=1, starting_distance=DIST_CLOSE)
        first_round_start = result["round_log"][0]["distance_band"]
        # First round starts at CLOSE, may shift during the round
        assert first_round_start <= DIST_MELEE  # no further than MELEE from CLOSE start

    def test_duel_can_complete_between_mismatched_weapons(self):
        """Dagger vs spear — dagger must close; game should be able to finish."""
        a = Fighter(name="dagger_a", mig=6, nim=6, tou=5, wit=5, wil=5,
                    weapon_type="dagger", weapon_base=4, weapon_skill=3)
        b = Fighter(name="spear_b", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="spear", weapon_base=6, weapon_skill=2)
        result = run_duel(a, b, max_rounds=30)
        assert result["winner"] in ("dagger_a", "spear_b", "stalemate", "mutual_kill")

    def test_free_step_in_logged_in_actions(self):
        """After a missed attack by long weapon, short weapon fighter should step in free."""
        free_reactions_seen = False
        for _ in range(100):
            a = Fighter(name="spear_a", mig=5, nim=5, tou=5, wit=5, wil=4,
                        weapon_type="spear", weapon_base=6, weapon_skill=1)
            b = Fighter(name="dagger_b", mig=5, nim=5, tou=5, wit=5, wil=4,
                        weapon_type="dagger", weapon_base=4, weapon_skill=1)
            result = run_duel(a, b, max_rounds=5)
            for rnd in result["round_log"]:
                for act in rnd["actions"]:
                    if act.get("free_reaction") and act.get("maneuver") == "step_in":
                        free_reactions_seen = True
                        break
            if free_reactions_seen:
                break
        assert free_reactions_seen, "Expected free step_in reactions over 100 trials"


# ───────────────────────────────────────────────────────────────────────
# WEAPON_REACH_TABLE completeness
# ───────────────────────────────────────────────────────────────────────

class TestWeaponReachTableCompleteness:
    REQUIRED_WEAPONS = [
        "unarmed", "dagger", "seax", "hand_axe", "mace",
        "sword", "great_sword", "long_axe", "spear",
        "generic", "improvised", "shield",
    ]

    def test_all_weapons_present(self):
        for w in self.REQUIRED_WEAPONS:
            assert w in WEAPON_REACH_TABLE, f"{w} missing from WEAPON_REACH_TABLE"

    def test_reach_tiers_ordered_correctly(self):
        order = ["unarmed", "dagger", "seax", "hand_axe", "sword", "great_sword", "spear"]
        reaches = [WEAPON_REACH_TABLE[w]["reach"] for w in order]
        assert reaches == sorted(reaches), "Reach tiers should be non-decreasing by weapon size"

    def test_foul_band_less_than_min_band_for_long_weapons(self):
        for w in ["great_sword", "long_axe", "spear"]:
            data = WEAPON_REACH_TABLE[w]
            assert data["foul_band"] < data["min_band"], \
                f"{w} foul_band should be inside min_band"
