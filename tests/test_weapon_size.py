"""Tests for the weapon size and terrain constraint system (PROPOSAL_004)."""
import pytest
import random
from combat_sim import (
    Fighter,
    Maneuver,
    ConditionType,
    DIST_GRAPPLE, DIST_CLOSE, DIST_MELEE, DIST_LONG,
    WEAPON_SIZE_TABLE,
    TERRAIN_SPACE_CLASS,
    TERRAIN_SIZE_ATTACK_MODS,
    TERRAIN_SIZE_STAMINA_EXTRA,
    get_weapon_size,
    get_space_class,
    compute_terrain_penalty,
    terrain_stamina_extra,
    resolve_fighter_action,
    run_duel,
    run_skirmish,
)


# ───────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────

def make_fighter(name, weapon_type, terrain="open", weapon_base=6, weapon_skill=2,
                 distance=DIST_MELEE):
    f = Fighter(
        name=name,
        mig=5, nim=5, tou=5, wit=5, wil=5,
        weapon_type=weapon_type,
        weapon_base=weapon_base,
        weapon_skill=weapon_skill,
        terrain_context=terrain,
    )
    f.current_distance = distance
    return f


# ───────────────────────────────────────────────────────────────────────
# get_weapon_size
# ───────────────────────────────────────────────────────────────────────

class TestGetWeaponSize:
    def test_unarmed_size_0(self):
        assert get_weapon_size("unarmed") == 0

    def test_dagger_size_1(self):
        assert get_weapon_size("dagger") == 1

    def test_seax_size_1(self):
        assert get_weapon_size("seax") == 1

    def test_hand_axe_size_2(self):
        assert get_weapon_size("hand_axe") == 2

    def test_mace_size_2(self):
        assert get_weapon_size("mace") == 2

    def test_sword_size_3(self):
        assert get_weapon_size("sword") == 3

    def test_great_sword_size_4(self):
        assert get_weapon_size("great_sword") == 4

    def test_long_axe_size_4(self):
        assert get_weapon_size("long_axe") == 4

    def test_spear_size_5(self):
        assert get_weapon_size("spear") == 5

    def test_unknown_falls_back_to_generic(self):
        assert get_weapon_size("mystery_weapon") == get_weapon_size("generic")

    def test_size_tiers_monotone_by_weapon_class(self):
        assert (get_weapon_size("unarmed")
                < get_weapon_size("dagger")
                < get_weapon_size("sword")
                < get_weapon_size("great_sword")
                < get_weapon_size("spear"))


# ───────────────────────────────────────────────────────────────────────
# get_space_class
# ───────────────────────────────────────────────────────────────────────

class TestGetSpaceClass:
    def test_open_is_free(self):
        assert get_space_class("open") == "free"

    def test_stone_is_free(self):
        assert get_space_class("stone") == "free"

    def test_interior_is_moderate(self):
        assert get_space_class("interior") == "moderate"

    def test_ship_is_moderate(self):
        assert get_space_class("ship") == "moderate"

    def test_narrow_is_tight(self):
        assert get_space_class("narrow") == "tight"

    def test_forest_dense_is_tight(self):
        assert get_space_class("forest_dense") == "tight"

    def test_crowd_is_packed(self):
        assert get_space_class("crowd") == "packed"

    def test_barrow_is_very_tight(self):
        assert get_space_class("barrow") == "very_tight"

    def test_low_ceiling_is_very_tight(self):
        assert get_space_class("low_ceiling") == "very_tight"

    def test_unknown_defaults_to_free(self):
        assert get_space_class("moon_surface") == "free"


# ───────────────────────────────────────────────────────────────────────
# compute_terrain_penalty
# ───────────────────────────────────────────────────────────────────────

class TestComputeTerrainPenalty:
    # Free terrain — no penalties
    def test_all_weapons_no_penalty_in_open(self):
        for wt in ["unarmed", "dagger", "sword", "spear", "great_sword"]:
            assert compute_terrain_penalty(wt, "open") == 0

    # Moderate terrain
    def test_sword_moderate_penalty(self):
        assert compute_terrain_penalty("sword", "interior") == -5

    def test_great_sword_moderate_penalty(self):
        assert compute_terrain_penalty("great_sword", "interior") == -15

    def test_spear_moderate_penalty(self):
        assert compute_terrain_penalty("spear", "interior") == -25

    def test_dagger_no_penalty_moderate(self):
        assert compute_terrain_penalty("dagger", "interior") == 0

    # Tight terrain
    def test_unarmed_bonus_tight(self):
        assert compute_terrain_penalty("unarmed", "narrow") == 5

    def test_dagger_bonus_tight(self):
        assert compute_terrain_penalty("dagger", "narrow") == 5

    def test_sword_penalty_tight(self):
        assert compute_terrain_penalty("sword", "narrow") == -10

    def test_great_sword_penalty_tight(self):
        assert compute_terrain_penalty("great_sword", "narrow") == -25

    def test_spear_heavy_penalty_tight(self):
        assert compute_terrain_penalty("spear", "narrow") == -40

    # Very tight terrain
    def test_unarmed_bonus_very_tight(self):
        assert compute_terrain_penalty("unarmed", "barrow") == 10

    def test_dagger_bonus_very_tight(self):
        assert compute_terrain_penalty("dagger", "barrow") == 15

    def test_sword_penalty_very_tight(self):
        assert compute_terrain_penalty("sword", "barrow") == -20

    def test_great_sword_heavy_penalty_very_tight(self):
        assert compute_terrain_penalty("great_sword", "barrow") == -40

    def test_spear_extreme_penalty_very_tight(self):
        assert compute_terrain_penalty("spear", "barrow") == -60

    # Packed terrain
    def test_dagger_small_bonus_packed(self):
        assert compute_terrain_penalty("dagger", "crowd") == 5

    def test_spear_significant_penalty_packed(self):
        assert compute_terrain_penalty("spear", "crowd") == -30

    def test_penalty_worsens_with_weapon_size_in_tight(self):
        sizes = ["dagger", "sword", "great_sword", "spear"]
        pens = [compute_terrain_penalty(w, "narrow") for w in sizes]
        # Penalty worsens (more negative) as weapon size increases; small weapons
        # get a bonus (+), so values go high→low: sorted descending.
        assert pens == sorted(pens, reverse=True), f"expected desc: {pens}"


# ───────────────────────────────────────────────────────────────────────
# terrain_stamina_extra
# ───────────────────────────────────────────────────────────────────────

class TestTerrainStaminaExtra:
    def test_no_extra_in_open(self):
        for wt in ["spear", "great_sword", "sword", "dagger", "unarmed"]:
            assert terrain_stamina_extra(wt, "open") == 0

    def test_large_weapon_extra_in_moderate(self):
        assert terrain_stamina_extra("great_sword", "interior") == 1
        assert terrain_stamina_extra("spear", "interior") == 1

    def test_large_weapon_extra_in_tight(self):
        assert terrain_stamina_extra("great_sword", "narrow") == 2
        assert terrain_stamina_extra("spear", "narrow") == 3

    def test_large_weapon_extra_in_very_tight(self):
        assert terrain_stamina_extra("great_sword", "barrow") == 3
        assert terrain_stamina_extra("spear", "barrow") == 4

    def test_small_weapons_no_extra_moderate(self):
        assert terrain_stamina_extra("dagger", "interior") == 0
        assert terrain_stamina_extra("unarmed", "interior") == 0

    def test_sword_extra_in_tight(self):
        assert terrain_stamina_extra("sword", "narrow") == 1

    def test_dagger_no_extra_even_very_tight(self):
        assert terrain_stamina_extra("dagger", "barrow") == 0


# ───────────────────────────────────────────────────────────────────────
# Fighter.weapon_size auto-set
# ───────────────────────────────────────────────────────────────────────

class TestFighterWeaponSizeAutoSet:
    def test_spear_auto_size_5(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="spear")
        assert f.weapon_size == 5

    def test_sword_auto_size_3(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="sword")
        assert f.weapon_size == 3

    def test_unarmed_auto_size_0(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5, weapon_type="unarmed")
        assert f.weapon_size == 0

    def test_manual_override_preserved(self):
        f = Fighter(name="f", mig=5, nim=5, tou=5, wit=5, wil=5,
                    weapon_type="sword", weapon_size=5)
        assert f.weapon_size == 5

    def test_to_dict_includes_weapon_size(self):
        f = make_fighter("f", "great_sword")
        d = f.to_dict()
        assert "weapon_size" in d
        assert d["weapon_size"] == 4


# ───────────────────────────────────────────────────────────────────────
# can_maneuver terrain gates
# ───────────────────────────────────────────────────────────────────────

class TestCanManeuverTerrainGates:
    def test_heavy_blow_blocked_very_tight(self):
        f = make_fighter("f", "great_sword", terrain="barrow")
        assert not f.can_maneuver(Maneuver.HEAVY_BLOW)

    def test_heavy_blow_blocked_low_ceiling(self):
        f = make_fighter("f", "sword", terrain="low_ceiling")
        assert not f.can_maneuver(Maneuver.HEAVY_BLOW)

    def test_heavy_blow_allowed_tight(self):
        f = make_fighter("f", "sword", terrain="narrow")
        assert f.can_maneuver(Maneuver.HEAVY_BLOW)

    def test_heavy_blow_allowed_open(self):
        f = make_fighter("f", "great_sword", terrain="open")
        assert f.can_maneuver(Maneuver.HEAVY_BLOW)

    def test_step_back_blocked_very_tight(self):
        f = make_fighter("f", "sword", terrain="barrow")
        assert not f.can_maneuver(Maneuver.STEP_BACK)

    def test_step_back_blocked_low_ceiling(self):
        f = make_fighter("f", "dagger", terrain="low_ceiling")
        assert not f.can_maneuver(Maneuver.STEP_BACK)

    def test_step_back_allowed_tight(self):
        f = make_fighter("f", "spear", terrain="narrow")
        assert f.can_maneuver(Maneuver.STEP_BACK)

    def test_step_back_allowed_open(self):
        f = make_fighter("f", "spear", terrain="open")
        assert f.can_maneuver(Maneuver.STEP_BACK)

    def test_step_in_always_available(self):
        """STEP_IN (closing) works even without retreat room."""
        for terrain in ["barrow", "low_ceiling", "narrow", "open"]:
            f = make_fighter("f", "spear", terrain=terrain)
            assert f.can_maneuver(Maneuver.STEP_IN), f"STEP_IN should work in {terrain}"

    def test_cut_always_available_in_tight(self):
        f = make_fighter("f", "sword", terrain="narrow")
        assert f.can_maneuver(Maneuver.CUT)


# ───────────────────────────────────────────────────────────────────────
# Terrain penalty applied in resolve_attack
# ───────────────────────────────────────────────────────────────────────

class TestTerrainPenaltyInAttack:
    def test_spear_in_barrow_has_terrain_penalty(self):
        a = make_fighter("A", "spear", terrain="barrow")
        d = make_fighter("D", "dagger", terrain="barrow")
        found = False
        for _ in range(30):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if "terrain_penalty" in res:
                assert res["terrain_penalty"] == -60
                found = True
                break
        assert found, "spear in barrow should always show terrain_penalty=-60"

    def test_dagger_in_barrow_has_positive_terrain_mod(self):
        # Fresh fighters each iteration — reusing dead fighters gives 'skip' results
        found = False
        for _ in range(20):
            a = make_fighter("A", "dagger", terrain="barrow")
            d = make_fighter("D", "spear", terrain="barrow")
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if res.get("action") == "skip":
                continue
            assert res.get("terrain_penalty", 0) == 15
            found = True
            break
        assert found, "should get a valid (non-skip) action within 20 tries"

    def test_sword_in_open_no_terrain_penalty(self):
        a = make_fighter("A", "sword", terrain="open")
        d = make_fighter("D", "sword", terrain="open")
        for _ in range(20):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            assert "terrain_penalty" not in res

    def test_spear_in_barrow_gets_haft_only(self):
        a = make_fighter("A", "spear", terrain="barrow")
        d = make_fighter("D", "sword", terrain="barrow")
        a.current_distance = DIST_MELEE  # not reach-fouled, but terrain haft-only
        haft_seen = False
        for _ in range(30):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if res.get("haft_only"):
                haft_seen = True
                break
        assert haft_seen, "spear in barrow at MELEE should be haft-only (terrain rule)"


# ───────────────────────────────────────────────────────────────────────
# Prone + large weapon penalty
# ───────────────────────────────────────────────────────────────────────

class TestProneLargeWeaponPenalty:
    def _set_prone(self, fighter):
        fighter.add_condition(ConditionType.PRONE, 3)

    def test_great_sword_prone_has_size_penalty(self):
        a = make_fighter("A", "great_sword", terrain="open")
        d = make_fighter("D", "sword", terrain="open")
        self._set_prone(a)
        found = False
        for _ in range(30):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if "prone_size_penalty" in res:
                assert res["prone_size_penalty"] == -15  # (4-3)*15
                found = True
                break
        assert found

    def test_spear_prone_larger_penalty(self):
        a = make_fighter("A", "spear", terrain="open")
        d = make_fighter("D", "sword", terrain="open")
        self._set_prone(a)
        found = False
        for _ in range(30):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            if "prone_size_penalty" in res:
                assert res["prone_size_penalty"] == -30  # (5-3)*15
                found = True
                break
        assert found

    def test_sword_prone_no_size_penalty(self):
        a = make_fighter("A", "sword", terrain="open")
        d = make_fighter("D", "sword", terrain="open")
        self._set_prone(a)
        for _ in range(20):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            assert "prone_size_penalty" not in res

    def test_dagger_prone_no_size_penalty(self):
        a = make_fighter("A", "dagger", terrain="open")
        d = make_fighter("D", "sword", terrain="open")
        self._set_prone(a)
        for _ in range(20):
            res = resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
            assert "prone_size_penalty" not in res


# ───────────────────────────────────────────────────────────────────────
# Stamina surcharge in restricted terrain
# ───────────────────────────────────────────────────────────────────────

class TestTerrainStaminaCharge:
    def test_spear_in_barrow_costs_extra_stamina(self):
        a = make_fighter("A", "spear", terrain="barrow")
        d = make_fighter("D", "sword", terrain="barrow")
        extra = terrain_stamina_extra("spear", "barrow")  # should be 4
        assert extra == 4
        stamina_before = a.stamina
        resolve_fighter_action(a, d, Maneuver.CUT, Maneuver.GUARD)
        # Base CUT cost + stance extra + terrain extra consumed
        # At least terrain extra should be reflected
        assert a.stamina <= stamina_before - extra

    def test_dagger_in_barrow_no_extra_stamina(self):
        a = make_fighter("A", "dagger", terrain="barrow")
        d = make_fighter("D", "spear", terrain="barrow")
        extra = terrain_stamina_extra("dagger", "barrow")
        assert extra == 0

    def test_great_sword_in_interior_extra_1(self):
        extra = terrain_stamina_extra("great_sword", "interior")
        assert extra == 1


# ───────────────────────────────────────────────────────────────────────
# run_duel — terrain effects visible in round log
# ───────────────────────────────────────────────────────────────────────

class TestRunDuelTerrainEffects:
    def test_spear_vs_dagger_barrow_dagger_advantage(self):
        """Over many duels in a barrow, dagger should win significantly more often."""
        spear_wins = 0
        dagger_wins = 0
        random.seed(42)
        for _ in range(200):
            a = Fighter(name="spear_a", mig=5, nim=5, tou=5, wit=5, wil=5,
                        weapon_type="spear", weapon_base=6, weapon_skill=2,
                        terrain_context="barrow")
            b = Fighter(name="dagger_b", mig=5, nim=5, tou=5, wit=5, wil=5,
                        weapon_type="dagger", weapon_base=4, weapon_skill=2,
                        terrain_context="barrow")
            result = run_duel(a, b, max_rounds=30)
            if result["winner"] == "spear_a":
                spear_wins += 1
            elif result["winner"] == "dagger_b":
                dagger_wins += 1
        # Dagger should win meaningfully more than spear in barrow
        assert dagger_wins > spear_wins * 1.5, (
            f"Expected dagger advantage in barrow; got spear={spear_wins}, dagger={dagger_wins}")

    def test_spear_vs_dagger_open_spear_advantage(self):
        """In open terrain, spear should win more often — reverse of the barrow case."""
        spear_wins = 0
        dagger_wins = 0
        random.seed(99)
        for _ in range(200):
            a = Fighter(name="spear_a", mig=5, nim=5, tou=5, wit=5, wil=5,
                        weapon_type="spear", weapon_base=6, weapon_skill=2,
                        terrain_context="open")
            b = Fighter(name="dagger_b", mig=5, nim=5, tou=5, wit=5, wil=5,
                        weapon_type="dagger", weapon_base=4, weapon_skill=2,
                        terrain_context="open")
            result = run_duel(a, b, max_rounds=30)
            if result["winner"] == "spear_a":
                spear_wins += 1
            elif result["winner"] == "dagger_b":
                dagger_wins += 1
        assert spear_wins > dagger_wins, (
            f"Expected spear advantage in open; got spear={spear_wins}, dagger={dagger_wins}")


# ───────────────────────────────────────────────────────────────────────
# run_skirmish — auto-crowd upgrade
# ───────────────────────────────────────────────────────────────────────

class TestSkirmishAutoCrowd:
    def test_auto_crowd_upgrades_open_terrain(self):
        side_a = [make_fighter(f"a{i}", "sword", terrain="open") for i in range(3)]
        side_b = [make_fighter(f"b{i}", "sword", terrain="open") for i in range(3)]
        run_skirmish(side_a, side_b, max_rounds=1)
        for f in side_a + side_b:
            assert f.terrain_context == "crowd", \
                f"{f.name} should be auto-upgraded to 'crowd'"

    def test_auto_crowd_does_not_override_restrictive_terrain(self):
        side_a = [make_fighter(f"a{i}", "sword", terrain="barrow") for i in range(3)]
        side_b = [make_fighter(f"b{i}", "sword", terrain="barrow") for i in range(3)]
        run_skirmish(side_a, side_b, max_rounds=1)
        for f in side_a + side_b:
            assert f.terrain_context == "barrow", \
                "barrow should not be downgraded by auto-crowd"

    def test_small_skirmish_not_upgraded(self):
        side_a = [make_fighter("a0", "sword", terrain="open"),
                  make_fighter("a1", "sword", terrain="open")]
        side_b = [make_fighter("b0", "sword", terrain="open"),
                  make_fighter("b1", "sword", terrain="open")]
        run_skirmish(side_a, side_b, max_rounds=1)
        for f in side_a + side_b:
            assert f.terrain_context == "open", \
                "4-fighter skirmish should stay 'open'"


# ───────────────────────────────────────────────────────────────────────
# Friendly fire
# ───────────────────────────────────────────────────────────────────────

class TestFriendlyFire:
    def test_friendly_fire_can_occur_in_packed_terrain(self):
        """Over many trials, a large-weapon miss in packed terrain should produce FF."""
        ff_seen = False
        random.seed(7)
        for _ in range(300):
            side_a = [
                make_fighter("spear_a", "spear", terrain="crowd", weapon_base=6),
                make_fighter("sword_a", "sword", terrain="crowd"),
            ]
            side_b = [make_fighter("dagger_b", "dagger", terrain="crowd")]
            result = run_skirmish(side_a, side_b, max_rounds=3)
            for rnd in result["round_log"]:
                for act in rnd["actions"]:
                    if act.get("is_friendly_fire"):
                        ff_seen = True
                        break
            if ff_seen:
                break
        assert ff_seen, "Friendly fire should occur over 300 trials with spear in crowd"

    def test_small_weapon_no_friendly_fire(self):
        """Daggers (sz 1) should never produce friendly fire regardless of terrain."""
        random.seed(13)
        for _ in range(200):
            side_a = [make_fighter("a", "dagger", terrain="crowd"),
                      make_fighter("a2", "dagger", terrain="crowd")]
            side_b = [make_fighter("b", "sword", terrain="crowd")]
            result = run_skirmish(side_a, side_b, max_rounds=5)
            for rnd in result["round_log"]:
                for act in rnd["actions"]:
                    assert not act.get("is_friendly_fire"), \
                        "dagger should never produce friendly fire"

    def test_friendly_fire_target_is_ally(self):
        """When FF occurs, the defender should be on the same team as the attacker."""
        random.seed(21)
        side_a_names = {"spear_a", "sword_a1", "sword_a2"}
        for _ in range(500):
            side_a = [
                make_fighter("spear_a",  "spear",   terrain="crowd", weapon_base=6),
                make_fighter("sword_a1", "sword",   terrain="crowd"),
                make_fighter("sword_a2", "sword",   terrain="crowd"),
            ]
            side_b = [make_fighter("b", "sword", terrain="crowd")]
            result = run_skirmish(side_a, side_b, max_rounds=3)
            for rnd in result["round_log"]:
                for act in rnd["actions"]:
                    if act.get("is_friendly_fire"):
                        # attacker and defender must both be in side_a
                        assert act["attacker"] in side_a_names, "FF attacker not in side_a"
                        assert act["defender"] in side_a_names, "FF target not in side_a"
                        return  # found one, test passes


# ───────────────────────────────────────────────────────────────────────
# WEAPON_SIZE_TABLE completeness
# ───────────────────────────────────────────────────────────────────────

class TestWeaponSizeTableCompleteness:
    REQUIRED = [
        "unarmed", "dagger", "seax", "hand_axe", "mace",
        "sword", "generic", "improvised", "shield",
        "great_sword", "long_axe", "spear",
    ]

    def test_all_weapons_present(self):
        for w in self.REQUIRED:
            assert w in WEAPON_SIZE_TABLE, f"{w} missing from WEAPON_SIZE_TABLE"

    def test_sizes_in_valid_range(self):
        for w, s in WEAPON_SIZE_TABLE.items():
            assert 0 <= s <= 5, f"{w} size {s} out of range 0–5"

    def test_all_size_keys_in_attack_mod_tables(self):
        for space, size_dict in TERRAIN_SIZE_ATTACK_MODS.items():
            for sz in range(6):
                assert sz in size_dict, f"size {sz} missing from TERRAIN_SIZE_ATTACK_MODS[{space}]"

    def test_all_size_keys_in_stamina_extra_tables(self):
        for space, size_dict in TERRAIN_SIZE_STAMINA_EXTRA.items():
            for sz in range(6):
                assert sz in size_dict, f"size {sz} missing from TERRAIN_SIZE_STAMINA_EXTRA[{space}]"
