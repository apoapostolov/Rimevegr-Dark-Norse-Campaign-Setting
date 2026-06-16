from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import dog_breeding as db


def _breed_db():
    return db.load_breed_data(Path(__file__).resolve().parents[1] / "data" / "dog_breeds.yaml")


def test_breed_pup_is_deterministic_for_seed():
    breed_db = _breed_db()
    dam = db.resolve_parent(
        '{"name":"Gale","breed":"fjord_hound","sex":"bitch","nose":4,"speed":3,"grit":3,"bite":2,"sense":4,"voice":4,"bloodline_tags":["weather_sense","homewise"],"traits":["weather_sense","bark_alarm"]}',
        breed_db,
    )
    sire = db.resolve_parent(
        '{"name":"Kveld","breed":"black_pine_wolfdog","sex":"dog","nose":5,"speed":4,"grit":5,"bite":5,"sense":3,"voice":2,"bloodline_tags":["winter_hunter","hard_bite"],"traits":["winter_hunter","hard_bite"]}',
        breed_db,
    )

    pup_a = db.breed_pup(dam, sire, breed_db, seed=23)
    pup_b = db.breed_pup(dam, sire, breed_db, seed=23)

    assert pup_a == pup_b
    assert pup_a["breed"] in {"fjord_hound", "black_pine_wolfdog"}
    assert pup_a["estimated_value_silver"] >= 1
    assert len(pup_a["bloodline_tags"]) >= 1


def test_estimate_dog_value_penalizes_bad_condition_and_vices():
    breed_db = _breed_db()
    dog = db.resolve_parent(
        '{"name":"Snarl","breed":"black_pine_wolfdog","condition":"wounded","traits":["pack_hot","stranger_sour"],"bloodline_tags":["winter_hunter","hard_bite"],"tricks":["hold_thief","heel_fire"]}',
        breed_db,
    )
    value = db.estimate_dog_value(dog, breed_db)

    assert value > 0
    assert value < 30


def test_tick_kennel_promotes_old_pup_to_stock(tmp_path):
    kennel_file = tmp_path / "dog_kennels.yaml"
    kennel_file.write_text(
        """
dog_kennels:
  - kennel_id: test_kennel
    dogs: []
    breeding_pairs: []
    pups:
      - name: Bark-Step
        breed: fjord_hound
        age_seasons: 3
        nose: 4
        speed: 3
        grit: 3
        bite: 2
        sense: 4
        voice: 4
    breeding_history: []
""".strip(),
        encoding="utf-8",
    )
    breed_db = _breed_db()

    result = db.tick_kennel_season("test_kennel", kennel_file=kennel_file, breed_db=breed_db, season_id="Y312-S3", seed=1)

    assert result["promoted_to_stock"] == ["Bark-Step"]
