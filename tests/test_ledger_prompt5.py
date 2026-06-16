import ledger


def _mock_band():
    return {
        "band": {
            "treasury_silver": 10,
            "morale": 4,
            "day_of_year": 84,
            "current_contract": {"status": "none"},
        },
        "members": [
            {
                "name": "Voss",
                "rank": "captain",
                "wit": 6,
                "skills": {"persuade": 2, "intimidate": 2},
            }
        ],
    }


def _mock_settlement(size="village", times_occupied=0):
    return {
        "name": "Ironholm",
        "size": size,
        "population": 120,
        "standing_with_band": 0,
        "feud_level": 0,
        "times_occupied": times_occupied,
    }


def test_tribute_intimidate_always_adds_feud(monkeypatch):
    band_data = _mock_band()
    settlements = [_mock_settlement()]

    monkeypatch.setattr(ledger, "_load_band_yaml", lambda: band_data)
    monkeypatch.setattr(ledger, "_save_band_yaml", lambda data: None)
    monkeypatch.setattr(ledger, "_load_settlements_yaml", lambda: (settlements, ""))
    monkeypatch.setattr(ledger, "_save_settlements_yaml", lambda _s, _h="": None)
    monkeypatch.setattr(
        ledger,
        "_find_settlement_by_name",
        lambda _name: (settlements[0], 0, settlements),
    )
    monkeypatch.setattr("random.randint", lambda _a, _b: 1)

    result = ledger.cmd_tribute("Ironholm", "intimidate")

    assert result["success"] is True
    assert result["feud_delta"] >= 1
    assert result["silver_yield"] > 0



def test_occupation_second_time_downgrades_size(monkeypatch):
    band_data = _mock_band()
    settlements = [_mock_settlement(size="town", times_occupied=1)]

    monkeypatch.setattr(ledger, "_load_band_yaml", lambda: band_data)
    monkeypatch.setattr(ledger, "_save_band_yaml", lambda data: None)
    monkeypatch.setattr(ledger, "_load_settlements_yaml", lambda: (settlements, ""))
    monkeypatch.setattr(ledger, "_save_settlements_yaml", lambda _s, _h="": None)
    monkeypatch.setattr(
        ledger,
        "_find_settlement_by_name",
        lambda _name: (settlements[0], 0, settlements),
    )
    monkeypatch.setattr("random.randint", lambda _a, _b: 3)

    result = ledger.cmd_occupation("Ironholm", weeks=2)

    assert result["permanent_size_downgrade"] is True
    assert settlements[0]["size"] == "large_village"



def test_in_kind_after_week_four_penalizes_morale(monkeypatch):
    band_data = _mock_band()

    monkeypatch.setattr(ledger, "_load_band_yaml", lambda: band_data)
    monkeypatch.setattr(ledger, "_save_band_yaml", lambda data: None)

    result = ledger.cmd_in_kind(week_number=5, quantity=8, good_type="grain")

    assert result["morale_delta"] == -1
    assert result["new_morale"] == 3
