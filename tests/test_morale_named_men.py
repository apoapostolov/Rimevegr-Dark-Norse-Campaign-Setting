import morale


def test_loyalty_tick_erodes_per_30_days():
    band = {
        "day_of_year": 95,
        "members": [
            {
                "name": "Kell Hook",
                "status": "active",
                "loyalty": 4,
                "agenda_last_advanced_day": 30,
            }
        ],
    }

    rows = morale.loyalty_tick(band, captain_wil=7, command_skill=3, band_morale=4)

    assert rows[0]["change"] == -2
    assert band["members"][0]["loyalty"] == 2


def test_agenda_advance_sets_day_and_bumps_loyalty():
    band = {
        "day_of_year": 120,
        "members": [
            {
                "name": "Ubbe Ironside",
                "status": "active",
                "loyalty": 4,
                "agenda": "gain command",
                "agenda_last_advanced_day": 80,
            }
        ],
    }

    result = morale.agenda_advance(band, "Ubbe Ironside")

    assert result["new_loyalty"] == 5
    assert band["members"][0]["agenda_last_advanced_day"] == 120


def test_named_man_defect_marks_left_and_writes_note():
    band = {
        "members": [
            {
                "name": "Lump",
                "status": "active",
                "loyalty": 1,
                "trigger": "captain_broke_oath",
                "agenda": "be_free",
            }
        ]
    }

    result = morale.named_man_defect(band, "Lump", "Left in the night")

    assert result["new_status"] == "left"
    assert band["members"][0]["status"] == "left"
    assert "Left in the night" in band["members"][0]["notes"][-1]
