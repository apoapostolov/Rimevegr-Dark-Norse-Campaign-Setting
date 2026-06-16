import village_politics as vp


def _seed_band():
    return {
        "band": {
            "day_of_year": 101,
            "history": [],
        },
        "members": [
            {
                "name": "Gest Ledger",
                "rank": "named_man",
                "personal_crimes": [],
                "personal_bounty_silver": 0,
                "personal_bounty_tier": None,
                "outlaw_status": False,
            }
        ],
    }


def test_personal_crime_adds_bounty_and_sets_outlaw(monkeypatch):
    band_state = _seed_band()

    monkeypatch.setattr(vp, "_load_band_bs", lambda: band_state)
    monkeypatch.setattr(vp, "_save_band_bs", lambda data: None)

    result = vp.cmd_personal_crime(
        member_name="Gest Ledger",
        settlement_name="Frostfjord Hollow",
        crime_type="blood_vengeance_killing",
        severity=5,
        witnesses=3,
    )

    assert result["bounty_added"] == 234
    assert result["personal_bounty_silver"] == 234
    assert result["personal_bounty_tier"] == "professional_hunters"
    assert result["outlaw_status"] is True

    member = band_state["members"][0]
    assert len(member["personal_crimes"]) == 1
    assert band_state["band"]["named_man_bounties"]


def test_personal_amnesty_clears_bounty_when_cost_zero(monkeypatch):
    band_state = _seed_band()
    band_state["members"][0]["personal_bounty_silver"] = 160
    band_state["members"][0]["personal_bounty_tier"] = "professional_hunters"
    band_state["members"][0]["outlaw_status"] = True

    monkeypatch.setattr(vp, "_load_band_bs", lambda: band_state)
    monkeypatch.setattr(vp, "_save_band_bs", lambda data: None)

    result = vp.cmd_personal_amnesty(
        member_name="Gest Ledger",
        issuer="Frostfjord Hollow",
        cost=0,
    )

    assert result["old_bounty"] == 160
    assert result["new_bounty"] == 0
    assert result["personal_bounty_tier"] is None
    assert result["outlaw_status"] is False


def test_personal_pressure_reflects_outlaw_status(monkeypatch):
    band_state = _seed_band()
    member = band_state["members"][0]
    member["personal_bounty_silver"] = 200
    member["outlaw_status"] = True
    member["personal_crimes"] = [
        {
            "settlement": "Frostfjord Hollow",
            "crime_type": "murder",
            "severity": 4,
            "witnesses": 2,
            "blood_price_silver": 99,
        }
    ]

    monkeypatch.setattr(vp, "_load_band_bs", lambda: band_state)

    result = vp.cmd_personal_pressure(
        member_name="Gest Ledger",
        settlement_name="Frostfjord Hollow",
    )

    assert result["encounter_risk_bonus"] == 35
    assert result["diplomacy_penalty"] == -25
