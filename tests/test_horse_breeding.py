from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import horse_breeding as hb


def _breed_db():
    return hb.load_breed_data(Path(__file__).resolve().parents[1] / "data" / "horse_breeds.yaml")


def test_breed_foal_is_deterministic_for_seed():
    breed_db = _breed_db()
    dam = hb._coerce_parent(
        {
            "name": "Reed-Step",
            "breed": "moor_runner",
            "sex": "mare",
            "speed": 5,
            "wind": 4,
            "foot": 3,
            "nerve": 2,
            "load": 2,
            "sense": 3,
            "bloodline_tags": ["deep_wind", "hot_blooded"],
            "traits": ["fast_break", "long_stride"],
        },
        breed_db,
    )
    sire = hb._coerce_parent(
        {
            "name": "Ice-Mane",
            "breed": "rimefjord_pony",
            "sex": "gelding",
            "speed": 2,
            "wind": 4,
            "foot": 4,
            "nerve": 4,
            "load": 3,
            "sense": 4,
            "bloodline_tags": ["cold_hardy", "good_feet"],
            "traits": ["cold_hardy", "good_feet"],
        },
        breed_db,
    )

    foal_a = hb.breed_foal(dam, sire, breed_db, seed=17)
    foal_b = hb.breed_foal(dam, sire, breed_db, seed=17)

    assert foal_a == foal_b
    assert foal_a["breed"] in {"moor_runner", "rimefjord_pony"}
    assert foal_a["estimated_value_silver"] >= 4
    assert len(foal_a["bloodline_tags"]) >= 1


def test_estimate_horse_value_penalizes_bad_condition_and_vices():
    breed_db = _breed_db()
    horse = hb._coerce_parent(
        {
            "name": "Test Horse",
            "breed": "southblood_warhorse",
            "condition": "wounded",
            "traits": ["hot_blooded", "crowd_sour"],
            "bloodline_tags": ["charge_mass", "strong_back"],
            "tricks": ["stand_fire", "trample_drive"],
        },
        breed_db,
    )

    value = hb.estimate_horse_value(horse, breed_db)
    assert value > 0
    assert value < 100


def test_resolve_parent_from_band_member_reads_live_band_horse():
    breed_db = _breed_db()
    band_file = Path(__file__).resolve().parents[1] / "data" / "band_state.yaml"

    horse = hb.resolve_parent(
        band_file=band_file,
        parent_json=None,
        member_name="Petra Shepherd",
        breed_db=breed_db,
    )

    assert horse["name"] == "Reed-Step"
    assert horse["breed"] == "moor_runner"
    assert horse["speed"] == 5


def test_tick_herd_promotes_old_foal_to_stock(tmp_path):
    herd_file = tmp_path / "horse_herds.yaml"
    herd_file.write_text(
        """
horse_herds:
  - herd_id: test_herd
    horses: []
    breeding_pairs: []
    foals:
      - name: Young-Step
        breed: rimefjord_pony
        age_seasons: 7
        speed: 2
        wind: 4
        foot: 4
        nerve: 4
        load: 3
        sense: 4
    breeding_history: []
""".strip(),
        encoding="utf-8",
    )
    breed_db = _breed_db()

    result = hb.tick_herd_season("test_herd", herd_file=herd_file, breed_db=breed_db, season_id="Y312-S3", seed=1)

    assert result["promoted_to_stock"] == ["Young-Step"]
