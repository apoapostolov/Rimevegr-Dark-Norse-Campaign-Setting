import yaml

import magic


def _write_practitioners(path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "practitioners": [
                    {
                        "name": "Audun",
                        "tradition": "galdr",
                        "rank": 4,
                        "years_active": "~20",
                        "total_willpower_spent": 40,
                        "tou": 3,
                        "wil": 3,
                        "stage": "pre_onset",
                    }
                ]
            },
            f,
            sort_keys=False,
        )



def test_degrade_practitioner_advances_stage_and_persists(tmp_path, monkeypatch):
    prac_file = tmp_path / "practitioners.yaml"
    _write_practitioners(prac_file)

    monkeypatch.setattr(magic, "_PRACTITIONERS_FILE", prac_file)
    monkeypatch.setattr("random.randint", lambda _a, _b: 1)

    result = magic.cmd_degrade_practitioner("Audun")

    assert result["advanced"] is True
    assert result["new_stage"] == "onset"

    stored = yaml.safe_load(prac_file.read_text(encoding="utf-8"))
    p = stored["practitioners"][0]
    assert p["stage"] == "onset"
    assert p["years_active"] == 21



def test_practitioner_add_and_duplicate_guard(tmp_path, monkeypatch):
    prac_file = tmp_path / "practitioners.yaml"
    prac_file.write_text("practitioners: []\n", encoding="utf-8")

    monkeypatch.setattr(magic, "_PRACTITIONERS_FILE", prac_file)

    added = magic.cmd_practitioner_add(
        "Test", "galdr", years_active=5, tou=3, wil=4, base_rank=2
    )
    dup = magic.cmd_practitioner_add(
        "Test", "galdr", years_active=5, tou=3, wil=4, base_rank=2
    )

    assert added["added"] == "Test"
    assert "error" in dup



def test_annual_tick_returns_one_result_per_practitioner(tmp_path, monkeypatch):
    prac_file = tmp_path / "practitioners.yaml"
    with open(prac_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "practitioners": [
                    {
                        "name": "A",
                        "tradition": "galdr",
                        "rank": 3,
                        "years_active": 5,
                        "total_willpower_spent": 0,
                        "tou": 4,
                        "wil": 4,
                        "stage": "pre_onset",
                    },
                    {
                        "name": "B",
                        "tradition": "seidr",
                        "rank": 3,
                        "years_active": 30,
                        "total_willpower_spent": 50,
                        "tou": 3,
                        "wil": 3,
                        "stage": "early",
                    },
                ]
            },
            f,
            sort_keys=False,
        )

    monkeypatch.setattr(magic, "_PRACTITIONERS_FILE", prac_file)
    monkeypatch.setattr("random.randint", lambda _a, _b: 100)

    results = magic.cmd_annual_tick()

    assert len(results) == 2
    assert {r["practitioner"] for r in results} == {"A", "B"}


def test_attempt_galdr_uses_scaled_blood_and_stamina_costs(monkeypatch):
    monkeypatch.setattr("random.randint", lambda _a, _b: 1)

    result = magic.attempt_galdr(
        wyrd=3,
        rune_lore=3,
        rank=4,
        max_hp=25,
        max_stamina=23,
    )

    assert result["cost"]["hp_blood"] == 6
    assert result["cost"]["stamina"] == 6


def test_kvaedi_overdraw_turns_negative_stamina_into_hp_loss():
    result = magic.apply_kvaedi_exertion(
        rank=4,
        kvaedi_quality=4,
        current_stamina=2,
        current_hp=10,
        max_stamina=23,
    )

    assert result["stamina_after"] == -5
    assert result["hp_loss_from_overdraw"] == 5
    assert result["hp_after"] == 5
    assert result["dark_effects_unlocked"] is True


def test_zero_hp_while_singing_triggers_divine_stroke():
    result = magic.apply_kvaedi_exertion(
        rank=5,
        kvaedi_quality=4,
        current_stamina=1,
        current_hp=7,
        max_stamina=25,
    )

    assert result["hp_after"] == 0
    assert result["divine_stroke"] is True


def test_active_village_wards_reduce_max_hp_pool():
    result = magic.compute_protection_reserve(base_max_hp=25, protection_ranks=[4, 3])

    assert result["max_hp_tax"] == 7
    assert result["effective_max_hp"] == 18
    assert result["condition"] == "sickly_and_weak"
