"""test_npc_generator.py — Tests for npc_generator.py."""
import pytest

from npc_generator import (
    generate_npc,
    BACKGROUNDS,
    MALE_NAMES,
    FEMALE_NAMES,
    BYNAMES,
    TRIGGERS,
    AGENDAS,
)

REQUIRED_ATTR_KEYS = {"mig", "nim", "tou", "wit", "wil"}
REQUIRED_NPC_KEYS = {"name", "gender", "background", "rank", "skills", "wyr"} | REQUIRED_ATTR_KEYS


class TestGenerateNPC:
    def test_returns_required_keys(self):
        npc = generate_npc("huscarl", "common")
        for key in REQUIRED_NPC_KEYS:
            assert key in npc, f"missing key: {key}"

    def test_all_attrs_in_range(self):
        for _ in range(10):
            npc = generate_npc()
            for attr in REQUIRED_ATTR_KEYS:
                assert 1 <= npc[attr] <= 10, (
                    f"{attr} out of range: {npc[attr]}"
                )

    def test_wyrd_in_range(self):
        for _ in range(20):
            npc = generate_npc()
            assert 1 <= npc["wyr"] <= 4

    def test_background_preserved(self):
        npc = generate_npc("smith", "common")
        assert npc["background"] == "smith"

    def test_rank_preserved(self):
        npc = generate_npc("hunter", "veteran")
        assert npc["rank"] == "veteran"

    def test_named_man_has_trigger_and_agenda(self):
        npc = generate_npc("skald", "named_man")
        assert "trigger" in npc
        assert "agenda" in npc
        assert "loyalty" in npc

    def test_common_lacks_trigger_and_agenda(self):
        npc = generate_npc("farmer", "common")
        assert "trigger" not in npc
        assert "agenda" not in npc

    def test_veteran_higher_attrs_than_common(self):
        """Veterans should generally have higher main attributes."""
        total_common = [
            sum(generate_npc("huscarl", "common")[a] for a in REQUIRED_ATTR_KEYS)
            for _ in range(30)
        ]
        total_veteran = [
            sum(generate_npc("huscarl", "veteran")[a] for a in REQUIRED_ATTR_KEYS)
            for _ in range(30)
        ]
        assert sum(total_veteran) / len(total_veteran) >= sum(total_common) / len(total_common)

    def test_name_is_nonempty_string(self):
        npc = generate_npc()
        assert isinstance(npc["name"], str)
        assert len(npc["name"]) > 0

    def test_gender_is_valid(self):
        for _ in range(20):
            npc = generate_npc()
            assert npc["gender"] in ("male", "female")

    def test_skills_are_positive(self):
        for _ in range(10):
            npc = generate_npc()
            for skill_name, val in npc["skills"].items():
                assert val > 0, f"skill {skill_name} is zero or negative"

    def test_random_background_when_none(self):
        npc = generate_npc(None)
        assert npc["background"] in BACKGROUNDS


class TestBackgrounds:
    def test_all_backgrounds_have_required_keys(self):
        for bg_name, bg_data in BACKGROUNDS.items():
            assert "primary_attr" in bg_data, f"{bg_name} missing primary_attr"
            assert "weak_attr" in bg_data, f"{bg_name} missing weak_attr"
            assert "skills" in bg_data, f"{bg_name} missing skills"
            assert "flavor" in bg_data, f"{bg_name} missing flavor"

    def test_primary_attr_valid(self):
        valid = {"mig", "nim", "tou", "wit", "wil"}
        for bg_name, bg_data in BACKGROUNDS.items():
            assert bg_data["primary_attr"] in valid

    def test_weak_attr_valid(self):
        valid = {"mig", "nim", "tou", "wit", "wil"}
        for bg_name, bg_data in BACKGROUNDS.items():
            assert bg_data["weak_attr"] in valid


class TestNameLists:
    def test_male_names_nonempty(self):
        assert len(MALE_NAMES) > 0

    def test_female_names_nonempty(self):
        assert len(FEMALE_NAMES) > 0

    def test_bynames_nonempty(self):
        assert len(BYNAMES) > 0

    def test_triggers_nonempty(self):
        assert len(TRIGGERS) > 0

    def test_agendas_nonempty(self):
        assert len(AGENDAS) > 0
