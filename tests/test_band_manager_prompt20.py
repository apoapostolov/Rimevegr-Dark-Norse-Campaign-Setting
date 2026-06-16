import yaml

import band_manager


def _write_state(path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "band": {
                    "name": "Voss's Black Axes",
                    "day_of_year": 150,
                    "history": [],
                },
                "members": [
                    {
                        "name": "Gest Ledger",
                        "rank": "named_man",
                        "personal_bounty_silver": 180,
                        "personal_bounty_tier": "professional_hunters",
                        "outlaw_status": True,
                        "personal_crimes": [
                            {
                                "crime_type": "murder",
                                "settlement": "Frostfjord Hollow",
                                "blood_price_silver": 180,
                            }
                        ],
                    }
                ],
            },
            f,
            sort_keys=False,
        )


def test_named_man_status_reports_personal_bounty(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    result = band_manager.cmd_named_man_status(
        member_name="Gest Ledger",
        state_path=str(state_file),
    )

    assert result["personal_bounty_silver"] == 180
    assert result["outlaw_status"] is True
    assert result["crime_count"] == 1


def test_named_man_pardon_check_denies_without_enough_score(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    result = band_manager.cmd_named_man_pardon_check(
        member_name="Gest Ledger",
        witness_rep=1,
        silver_paid=20,
        state_path=str(state_file),
    )

    assert result["success"] is False
    assert result["new_bounty"] == 180


def test_named_man_pardon_check_reduces_bounty_on_success(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    result = band_manager.cmd_named_man_pardon_check(
        member_name="Gest Ledger",
        witness_rep=3,
        silver_paid=100,
        state_path=str(state_file),
    )

    assert result["success"] is True
    assert result["old_bounty"] == 180
    assert result["new_bounty"] == 80
    assert result["outlaw_status"] is False
