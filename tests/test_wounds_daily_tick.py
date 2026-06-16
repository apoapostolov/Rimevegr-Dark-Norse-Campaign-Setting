import wounds


def _member(name="Bjorn", tou=1):
    return {
        "name": name,
        "status": "active",
        "mig": 5,
        "nim": 5,
        "tou": tou,
        "wit": 4,
        "wil": 4,
        "max_hp": 24,
        "hp": 24,
        "wounds": [],
    }


def test_daily_tick_can_trigger_infection(monkeypatch):
    member = _member(tou=1)
    wounds.wound_apply(
        member,
        location="right_arm",
        sublocation="forearm_outer",
        wound_type="hewn",
        severity="serious",
        damage=5,
        weapon="axe",
    )
    band = {"members": [member]}

    monkeypatch.setattr(wounds.random, "randint", lambda _a, _b: 1)

    events = wounds.advance_all_wounds(band, days=1, rest_quality="active_duty")

    wound = member["wounds"][0]
    assert wound["infected"] is True
    assert any(
        "fester" in c.lower()
        for e in events
        for c in e.get("complications", [])
    )


def test_daily_tick_applies_rest_quality_multiplier(monkeypatch):
    member = _member(tou=10)
    wounds.wound_apply(
        member,
        location="torso",
        sublocation="chest_front",
        wound_type="hewn",
        severity="light",
        damage=2,
        weapon="sword",
    )
    band = {"members": [member]}

    monkeypatch.setattr(wounds.random, "randint", lambda _a, _b: 100)

    wounds.advance_all_wounds(band, days=4, rest_quality="field_rest")
    wound = member["wounds"][0]

    assert wound["healing_day_count"] == 2.0
