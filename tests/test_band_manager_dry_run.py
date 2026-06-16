import yaml

import band_manager


def _write_state(path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "band": {
                    "name": "Voss's Black Axes",
                    "oath_break_count": 0,
                    "oath_breaker": False,
                    "day_of_year": 10,
                    "history": [],
                },
                "members": [
                    {
                        "name": "Gest Ledger",
                        "rank": "named_man",
                        "personal_bounty_silver": 180,
                        "personal_bounty_tier": "professional_hunters",
                        "outlaw_status": True,
                        "personal_crimes": [],
                    }
                ],
            },
            f,
            sort_keys=False,
        )


def test_oath_break_dry_run_does_not_write(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    result = band_manager.cmd_oath_break(state_path=str(state_file), dry_run=True)
    assert result["oath_break_count"] == 1
    assert result["dry_run"] is True

    with open(state_file, "r", encoding="utf-8") as f:
        saved = yaml.safe_load(f)
    assert saved["band"]["oath_break_count"] == 0
    assert saved["band"]["oath_breaker"] is False


def test_named_man_pardon_dry_run_does_not_write(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    result = band_manager.cmd_named_man_pardon_check(
        member_name="Gest Ledger",
        witness_rep=3,
        silver_paid=100,
        state_path=str(state_file),
        dry_run=True,
    )

    assert result["success"] is True
    assert result["new_bounty"] == 80
    assert result["dry_run"] is True

    with open(state_file, "r", encoding="utf-8") as f:
        saved = yaml.safe_load(f)
    member = saved["members"][0]
    assert member["personal_bounty_silver"] == 180
    assert member["outlaw_status"] is True
