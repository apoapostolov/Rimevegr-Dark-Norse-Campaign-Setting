import village_politics as vp


def _seed_settlements():
    return [
        {"name": "Frostfjord Hollow", "standing_with_band": 0, "feud_level": 0},
        {"name": "Ironholm", "standing_with_band": 0, "feud_level": 0},
        {"name": "Deepholm", "standing_with_band": 0, "feud_level": 0},
        {"name": "Grimholt", "standing_with_band": 0, "feud_level": 0},
    ]


def _seed_band():
    return {"band": {"day_of_year": 88, "morale": 2, "bounty_silver": 0, "bounty_tier": None}}


def test_atrocity_severity_three_applies_penalties_and_posts_bounty(monkeypatch):
    settlements = _seed_settlements()
    band_state = _seed_band()

    monkeypatch.setattr(vp, "_load_settlements_list", lambda: (settlements, ""))
    monkeypatch.setattr(vp, "_save_settlements_list", lambda _s, _h="": None)
    monkeypatch.setattr(vp, "_load_band_bs", lambda: band_state)
    monkeypatch.setattr(vp, "_save_band_bs", lambda data: None)

    result = vp.cmd_atrocity("Frostfjord Hollow", severity=3, rumor_range=2, loot_silver=0)

    assert result["direct_penalty"] == -2
    assert result["rumor_penalty"] == -1
    assert result["bounty_posted"] is True
    assert result["bounty_silver"] == 75
    assert result["morale_delta"] == -1



def test_bounty_tier_assignment(monkeypatch):
    band_state = _seed_band()
    monkeypatch.setattr(vp, "_load_band_bs", lambda: band_state)
    monkeypatch.setattr(vp, "_save_band_bs", lambda data: None)

    result = vp.cmd_bounty(amount=85, target_band="Voss's Black Axes")

    assert result["total_bounty"] == 85
    assert result["tier"] == "regional_hunters"



def test_feud_stage_maps_numeric_level(monkeypatch):
    settlements = _seed_settlements()
    settlements[0]["feud_level"] = 2

    monkeypatch.setattr(vp, "_load_settlements_list", lambda: (settlements, ""))

    result = vp.cmd_feud_stage("Frostfjord Hollow")

    assert result["feud_level"] == 2
    assert result["stage"] == "Coordinating"
