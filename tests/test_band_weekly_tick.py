import yaml

import band_weekly_tick


def _seed_band_state(path):
    data = {
        "band": {
            "name": "Voss's Black Axes",
            "year": 312,
            "day_of_year": 84,
            "morale": 4,
            "treasury_silver": 50,
            "location": "Frostfjord Hollow",
            "reputation": 2,
        },
        "members": [
            {
                "name": "Voss",
                "rank": "captain",
                "status": "active",
                "wil": 7,
                "skills": {"command": 3},
            },
            {
                "name": "Bjorn",
                "rank": "common",
                "status": "active",
                "loyalty": 3,
                "agenda_last_advanced_day": 84,
            },
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)



def test_run_weekly_tick_dry_run_does_not_write(tmp_path, monkeypatch):
    band_file = tmp_path / "band_state.yaml"
    _seed_band_state(band_file)

    monkeypatch.setattr(
        band_weekly_tick,
        "_forage_fn",
        lambda terrain, foragers, skill, season: {"food_gathered": 12},
    )
    monkeypatch.setattr(
        band_weekly_tick,
        "_contracts_via_subprocess",
        lambda reputation, settlement, season: [{"id": "C001"}],
    )

    summary = band_weekly_tick.run_weekly_tick(
        band_file=str(band_file),
        season="long_dark",
        terrain="forest",
        forager_count=4,
        dry_run=True,
    )

    with open(band_file, "r", encoding="utf-8") as f:
        state_after = yaml.safe_load(f)

    assert summary["saved"] is False
    assert state_after["band"]["day_of_year"] == 84



def test_run_weekly_tick_persists_day_when_not_dry_run(tmp_path, monkeypatch):
    band_file = tmp_path / "band_state.yaml"
    _seed_band_state(band_file)

    monkeypatch.setattr(
        band_weekly_tick,
        "_forage_fn",
        lambda terrain, foragers, skill, season: {"food_gathered": 20},
    )
    monkeypatch.setattr(
        band_weekly_tick,
        "_contracts_via_subprocess",
        lambda reputation, settlement, season: [],
    )
    monkeypatch.setattr(band_weekly_tick, "_append_tick_log", lambda summary: None)
    monkeypatch.setattr(band_weekly_tick, "_append_journal", lambda summary: None)

    summary = band_weekly_tick.run_weekly_tick(
        band_file=str(band_file),
        season="long_dark",
        terrain="forest",
        forager_count=4,
        dry_run=False,
    )

    with open(band_file, "r", encoding="utf-8") as f:
        state_after = yaml.safe_load(f)

    assert summary["saved"] is True
    assert state_after["band"]["day_of_year"] == 91


def test_run_weekly_tick_triggers_seasonal_animals_on_boundary(tmp_path, monkeypatch):
    band_file = tmp_path / "band_state.yaml"
    _seed_band_state(band_file)

    monkeypatch.setattr(
        band_weekly_tick,
        "_forage_fn",
        lambda terrain, foragers, skill, season: {"food_gathered": 20},
    )
    monkeypatch.setattr(
        band_weekly_tick,
        "_contracts_via_subprocess",
        lambda reputation, settlement, season: [],
    )
    monkeypatch.setattr(band_weekly_tick, "_append_tick_log", lambda summary: None)
    monkeypatch.setattr(band_weekly_tick, "_append_journal", lambda summary: None)
    monkeypatch.setattr(
        band_weekly_tick,
        "_run_seasonal_animal_ticks",
        lambda year, day_start, day_end, dry_run: {
            "triggered": True,
            "season_id": "Y312-S2",
            "horse_herds": [{"foals_born": 1}],
            "dog_kennels": [{"pups_born": 2}],
        },
    )

    summary = band_weekly_tick.run_weekly_tick(
        band_file=str(band_file),
        season="long_dark",
        terrain="forest",
        forager_count=4,
        dry_run=False,
    )

    assert summary["steps"]["animals"]["triggered"] is True
    assert summary["steps"]["animals"]["season_id"] == "Y312-S2"
