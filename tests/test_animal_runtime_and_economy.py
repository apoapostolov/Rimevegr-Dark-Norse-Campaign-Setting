from __future__ import annotations

import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

import dog_breeding as db
import horse_breeding as hb
import village_politics as vp
from combat_model import Fighter
from combat_sim import _resolve_mounted_charge, run_skirmish
from combat_types import Maneuver, Stance
from npc_manager import load_all_npcs
from travel import simulate_travel


def _fighter(name: str, **kwargs) -> Fighter:
    base = dict(
        name=name,
        mig=5,
        nim=5,
        tou=5,
        wit=5,
        wil=5,
        weapon_skill=3,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        max_hp=40,
        hp=40,
        stance=Stance.AGGRESSIVE,
        mounted=False,
        mount_condition="steady",
        rider_stability=70,
        terrain="open",
    )
    base.update(kwargs)
    return Fighter(**base)


def test_tick_herd_season_persists_foal(tmp_path):
    herd_file = tmp_path / "horse_herds.yaml"
    herd_file.write_text(
        yaml.safe_dump(
            {
                "horse_herds": [
                    {
                        "herd_id": "test_herd",
                        "horses": [
                            {"name": "Dam", "breed": "moor_runner", "sex": "mare", "age": 7},
                            {"name": "Sire", "breed": "rimefjord_pony", "sex": "stallion", "age": 8},
                        ],
                        "breeding_pairs": [{"dam": "Dam", "sire": "Sire", "target_season": "Y312-S2"}],
                        "foals": [],
                        "breeding_history": [],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    breed_db = hb.load_breed_data(pathlib.Path(__file__).resolve().parents[1] / "data" / "horse_breeds.yaml")

    result = hb.tick_herd_season("test_herd", herd_file=herd_file, breed_db=breed_db, season_id="Y312-S2", seed=7)

    assert result["foals_born"] == 1
    saved = yaml.safe_load(herd_file.read_text(encoding="utf-8"))
    assert saved["horse_herds"][0]["foals"][0]["season_born"] == "Y312-S2"


def test_tick_kennel_season_persists_pup(tmp_path):
    kennel_file = tmp_path / "dog_kennels.yaml"
    kennel_file.write_text(
        yaml.safe_dump(
            {
                "dog_kennels": [
                    {
                        "kennel_id": "test_kennel",
                        "dogs": [
                            {"name": "Dam", "breed": "fjord_hound", "sex": "bitch", "age": 4},
                            {"name": "Sire", "breed": "black_pine_wolfdog", "sex": "dog", "age": 5},
                        ],
                        "breeding_pairs": [{"dam": "Dam", "sire": "Sire", "target_season": "Y312-S2"}],
                        "pups": [],
                        "breeding_history": [],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    breed_db = db.load_breed_data(pathlib.Path(__file__).resolve().parents[1] / "data" / "dog_breeds.yaml")

    result = db.tick_kennel_season(
        "test_kennel", kennel_file=kennel_file, breed_db=breed_db, season_id="Y312-S2", seed=11
    )

    assert result["pups_born"] == 1
    saved = yaml.safe_load(kennel_file.read_text(encoding="utf-8"))
    assert saved["dog_kennels"][0]["pups"][0]["season_born"] == "Y312-S2"


def test_route_throughput_uses_detailed_economy_and_routes():
    state = {
        "current_date": {"day_of_year": 87},
        "feuds": [{"pair": ["Frostfjord Hollow", "Ashen Reach"], "level": 1}],
    }
    detailed = {
        "Frostfjord Hollow": {
            "imports": [{"good": "grain", "urgency": "high"}],
            "exports": [{"good": "dried_cod", "destinations": ["Ashen Reach"], "volume": "high"}],
            "trade_routes": [
                {
                    "to": "Ashen Reach",
                    "route_id": "RTE_001",
                    "goods_flow": "cod out, grain in",
                    "frequency": "weekly",
                }
            ],
        }
    }
    routes = {
        "RTE_001": {
            "id": "RTE_001",
            "seasonal_access": {"autumn": "passable"},
            "trade_traffic": "moderate",
        }
    }

    result = vp.compute_route_throughput(state, "Frostfjord Hollow", detailed, routes)

    assert result["throughput_total"] > 0
    assert result["export_bonus_silver"] > 0
    assert result["food_import_bonus"] > 0


def test_mount_traits_increase_charge_damage():
    rider = _fighter(
        "Rider",
        mounted=True,
        weapon_type="lance",
        mount_traits=["charge_mass"],
        mount_tricks=["mount_charge"],
        mount_mood="eager",
    )
    foot = _fighter("Foot")

    result = _resolve_mounted_charge(
        rider,
        foot,
        defender_maneuver=Maneuver.CUT,
        allied_count=2,
        enemy_count=2,
        actions=[],
        round_num=1,
        horses_allowed=True,
    )

    assert result["bonus_damage"] >= 4


def test_dog_support_is_serialized_in_skirmish_result():
    dogged = _fighter(
        "Dogged",
        dog_companions=[
            {
                "name": "Crow-Fang",
                "role": "war_dog",
                "traits": ["hard_bite"],
                "tricks": ["hold_fast"],
            }
        ],
    )
    foe = _fighter("Foe")

    result = run_skirmish([dogged], [foe], max_rounds=1, horses_allowed=False)

    assert result["side_a"]["Dogged"]["dog_companions"][0]["name"] == "Crow-Fang"


def test_travel_animals_reduce_hazard_penalty(monkeypatch):
    import travel as tr

    monkeypatch.setattr(tr, "generate_weather", lambda season: {"weather": "clear"})
    monkeypatch.setattr(
        tr,
        "check_daily_hazard",
        lambda terrain, weather: {"hazard": "bog", "description": "Bog", "day_penalty": 0.5},
    )

    baseline = simulate_travel(10, "moors", "long_dark", 10, 50)
    aided = simulate_travel(
        10,
        "moors",
        "long_dark",
        10,
        50,
        horse={"has_horse": True, "traits": ["sure_step"], "tricks": ["pick_way"]},
        dogs=[{"role": "tracker", "traits": ["deep_nose"], "tricks": ["trail_blood"]}],
    )

    assert aided["total_days"] <= baseline["total_days"]


def test_rival_npcs_now_expose_richer_horse_and_dog_schema():
    npcs = load_all_npcs()
    ragna = next(n for n in npcs if n.get("call_name") == "Crow-Bride")
    ivor = next(n for n in npcs if n.get("call_name") == "Fen-Eye")

    assert ragna["horse"]["breed"] == "southblood_warhorse"
    assert "mount_charge" in ragna["horse"]["tricks"]
    assert ivor["dogs"][0]["breed"] == "bog_tracker"


def test_generate_narrative_mentions_trade_pressure():
    state = vp.load_state()
    text = vp.generate_narrative(state, 2)
    assert "Trade pressure:" in text
