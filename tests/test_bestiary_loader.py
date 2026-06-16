"""test_bestiary_loader.py — Tests for bestiary_loader.py (Batch 1)."""

import pathlib
import pytest

# ── the bestiary data directory ─────────────────────────────────────────────
DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "bestiary"

from bestiary_loader import (
    entry_to_fighter,
    load_all_bestiaries,
    load_enemy,
    parse_armor_text,
    pick_weapon_from_gear,
    pick_weapon_skill,
)


# ── parse_armor_text ──────────────────────────────────────────────────────────

class TestParseArmorText:
    """parse_armor_text converts YAML armor strings to numeric AR values."""

    def test_no_protection_none(self):
        result = parse_armor_text({"torso": "None", "head": "None"})
        assert result["torso"] == 0
        assert result["head"] == 0

    def test_burial_shroud(self):
        result = parse_armor_text({"torso": "Burial Shroud", "head": "None"})
        assert result["torso"] == 0
        assert result["head"] == 0

    def test_leather_jerkin(self):
        result = parse_armor_text({"torso": "Leather Jerkin"})
        assert result["torso"] == 1

    def test_fused_rusted_mail(self):
        result = parse_armor_text({"torso": "Fused Rusted Mail"})
        assert result["torso"] == 4

    def test_ancient_lamellar(self):
        result = parse_armor_text({"torso": "Ancient Lamellar"})
        assert result["torso"] == 4

    def test_corroded_helmet(self):
        result = parse_armor_text({"head": "Corroded Helmet"})
        assert result["head"] == 2
        assert result["torso"] == 0

    def test_steel_helm(self):
        result = parse_armor_text({"head": "Steel Helm"})
        assert result["head"] == 3

    def test_stone_skin_both_slots(self):
        result = parse_armor_text({"torso": "Stone Skin (natural, as plate)"})
        assert result["torso"] == 5
        assert result["head"] == 5

    def test_thick_hide_ar2(self):
        result = parse_armor_text({"torso": "Thick Hide (AR 2)"})
        assert result["torso"] == 2

    def test_dense_hide_ar3(self):
        result = parse_armor_text({"torso": "Dense Hide (AR 3)"})
        assert result["torso"] == 3

    def test_incorporeal_zero(self):
        result = parse_armor_text({"torso": "Incorporeal"})
        assert result["torso"] == 0

    def test_empty_dict(self):
        result = parse_armor_text({})
        assert all(v == 0 for v in result.values())

    def test_rotted_leather_over_mail(self):
        result = parse_armor_text({"torso": "Rotted Leather over Mail Fragments"})
        assert result["torso"] == 2

    def test_bronze_crown_helm(self):
        result = parse_armor_text({"head": "Bronze Crown-Helm"})
        assert result["head"] == 3

    def test_ring_mail(self):
        result = parse_armor_text({"torso": "Ring Mail"})
        assert result["torso"] == 3


# ── pick_weapon_skill ────────────────────────────────────────────────────────

class TestPickWeaponSkill:
    def test_brawl_rank_taken(self):
        skills = [{"name": "Brawl", "rank": 3}, {"name": "Stealth", "rank": 4}]
        assert pick_weapon_skill(skills) == 3

    def test_highest_combat_skill_wins(self):
        skills = [{"name": "Brawl", "rank": 2}, {"name": "Swords", "rank": 4}]
        assert pick_weapon_skill(skills) == 4

    def test_non_combat_skills_ignored(self):
        skills = [{"name": "Track", "rank": 5}, {"name": "Stealth", "rank": 4}]
        assert pick_weapon_skill(skills) == 1  # fallback

    def test_empty_skills(self):
        assert pick_weapon_skill([]) == 1

    def test_none_skills(self):
        assert pick_weapon_skill(None) == 1


# ── pick_weapon_from_gear ────────────────────────────────────────────────────

class TestPickWeaponFromGear:
    def test_selects_highest_damage_weapon(self):
        gear = {
            "weapons": [
                {"name": "Claws", "type": "natural", "speed": 3, "base_damage": 6},
                {"name": "Bite",  "type": "natural", "speed": 2, "base_damage": 7},
            ]
        }
        name, dmg, speed, wtype = pick_weapon_from_gear(gear)
        assert name == "Bite"
        assert dmg == 7

    def test_fallback_to_unarmed_when_empty(self):
        name, dmg, speed, wtype = pick_weapon_from_gear({})
        assert wtype == "unarmed"
        assert dmg == 3

    def test_natural_type_normalised_to_unarmed(self):
        gear = {"weapons": [{"name": "Jaws", "type": "natural", "speed": 4, "base_damage": 4}]}
        _, _, _, wtype = pick_weapon_from_gear(gear)
        assert wtype == "unarmed"

    def test_sword_type_passthrough(self):
        gear = {"weapons": [{"name": "Blade", "type": "sword", "speed": 3, "base_damage": 6}]}
        _, _, _, wtype = pick_weapon_from_gear(gear)
        assert wtype == "sword"


# ── load_all_bestiaries ──────────────────────────────────────────────────────

class TestLoadAllBestiaries:
    def test_contains_expected_ids(self):
        catalogue = load_all_bestiaries(DATA_DIR)
        for expected_id in [
            "ANI_WOLF_01", "ANI_BEAR_01",
            "UND_DRAUGR_01", "UND_DRAUGR_05",
            "UND_HAUG_01",
        ]:
            assert expected_id in catalogue, f"Missing: {expected_id}"

    def test_all_entries_have_id(self):
        catalogue = load_all_bestiaries(DATA_DIR)
        assert len(catalogue) > 10

    def test_missing_dir_returns_empty(self):
        result = load_all_bestiaries("/nonexistent/path")
        assert result == {}


# ── load_enemy / entry_to_fighter ────────────────────────────────────────────

class TestLoadEnemyFiver:
    """Five creatures across different files and categories load without error."""

    def test_ani_wolf_01_loads(self):
        f = load_enemy("ANI_WOLF_01", DATA_DIR)
        assert f.name == "Timber Wolf"
        assert f.mig == 4
        assert f.nim == 6

    def test_ani_bear_02_loads(self):
        f = load_enemy("ANI_BEAR_02", DATA_DIR)
        assert f.name == "Cave Bear"
        assert f.weapon_base == 9  # Crushing Bite wins over Massive Claws (8)
        assert f.armor["torso"] == 3  # Dense Hide (AR 3)
        assert f.armor["head"] == 2   # Thick Skull (AR 2)

    def test_und_draugr_01_loads(self):
        f = load_enemy("UND_DRAUGR_01", DATA_DIR)
        assert f.is_undead is True
        assert "unfeeling" in f.traits

    def test_und_draugr_03_has_shield(self):
        f = load_enemy("UND_DRAUGR_03", DATA_DIR)
        assert f.shield_def > 0
        assert f.shield_skill > 0
        assert f.armor["torso"] == 2   # Rotted Leather over Mail Fragments
        assert f.armor["head"] == 2    # Corroded Helmet

    def test_sup_spirit_01_loads(self):
        f = load_enemy("SUP_SPIRIT_01", DATA_DIR)
        assert f.name == "Mara"
        assert f.mig == 2
        assert f.wil == 8

    def test_hum_bandit_01_loads(self):
        catalogue = load_all_bestiaries(DATA_DIR)
        if "HUM_BANDIT_01" not in catalogue:
            pytest.skip("HUM_BANDIT_01 not present in humans.yaml")
        f = load_enemy("HUM_BANDIT_01", DATA_DIR)
        assert f.weapon_base >= 1


# ── UND_DRAUGR_05 specific assertions ────────────────────────────────────────

class TestDraugr05:
    """load_enemy('UND_DRAUGR_05') produces Fighter with expected traits and fields."""

    def setup_method(self):
        self.fighter = load_enemy("UND_DRAUGR_05", DATA_DIR)

    def test_is_undead(self):
        assert self.fighter.is_undead is True

    def test_ancient_resilience_in_traits(self):
        assert "ancient_resilience" in self.fighter.traits

    def test_bleeding_in_resistances(self):
        assert "bleeding" in self.fighter.resistances

    def test_terrifying_presence_in_traits(self):
        assert "terrifying_presence" in self.fighter.traits

    def test_stats_correct(self):
        assert self.fighter.mig == 7
        assert self.fighter.tou == 7
        assert self.fighter.wil == 6

    def test_armor_ancient_lamellar(self):
        assert self.fighter.armor["torso"] == 4  # Ancient Lamellar

    def test_explicit_hp_used(self):
        # YAML sets hp: 18, so Fighter.hp should be 18 not compute_max_hp result
        assert self.fighter.hp == 18


# ── resistance tag normalisation ─────────────────────────────────────────────

class TestResistanceNormalisation:
    """Tags with spaces (legacy YAML) are normalised to underscore form."""

    def test_physical_weapons_with_space_normalised(self):
        entry = {
            "id": "TEST_01",
            "name": "Test",
            "stats": {"MIG": 3, "NIM": 3, "TOU": 3, "WIT": 3, "WIL": 3},
            "gear": {},
            "resistances": ["physical weapons", "cold"],
        }
        f = entry_to_fighter(entry)
        assert "physical_weapons" in f.resistances
        assert "physical weapons" not in f.resistances
        assert "cold" in f.resistances
