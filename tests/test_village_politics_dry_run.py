import yaml

import village_politics as vp


def _write_yaml(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)


def test_personal_bounty_dry_run_does_not_write(tmp_path, monkeypatch):
    settlements_file = tmp_path / "settlements.yaml"
    band_state_file = tmp_path / "band_state.yaml"

    _write_yaml(settlements_file, {"settlements": [{"name": "Frostfjord Hollow", "standing_with_band": 0, "feud_level": 0}]})
    _write_yaml(
        band_state_file,
        {
            "band": {"day_of_year": 77, "history": []},
            "members": [
                {
                    "name": "Kell Hook",
                    "rank": "named_man",
                    "personal_crimes": [],
                    "personal_bounty_silver": 0,
                    "personal_bounty_tier": None,
                    "outlaw_status": False,
                }
            ],
        },
    )

    monkeypatch.setattr(vp, "SETTLEMENTS_FILE", settlements_file)
    monkeypatch.setattr(vp, "_BAND_STATE_FILE", band_state_file)
    monkeypatch.setattr(vp, "_DRY_RUN", True)

    result = vp.cmd_personal_bounty(
        member_name="Kell Hook",
        amount=120,
        issuer="Frostfjord Hollow",
        reason="Blood feud",
    )

    assert result["personal_bounty_silver"] == 120
    assert result["personal_bounty_tier"] == "regional_hunters"

    with open(band_state_file, "r", encoding="utf-8") as f:
        saved = yaml.safe_load(f)
    member = saved["members"][0]
    assert member["personal_bounty_silver"] == 0
    assert member["personal_bounty_tier"] is None
