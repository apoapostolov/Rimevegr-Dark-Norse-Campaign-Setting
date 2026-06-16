from combat_grapple import advance_choke_round, check_submission_yield
from combat_model import Fighter, GrappleState
from combat_sim import check_trauma_conditions
from combat_types import ConditionType


def _fighter(name, wil=3, tou=3):
    return Fighter(name=name, mig=5, nim=5, tou=tou, wit=4, wil=wil)


def test_advance_choke_round_can_render_unconscious(monkeypatch):
    gs = GrappleState(choke_rounds=3)
    defender = _fighter("Defender", tou=3)
    actions = []

    monkeypatch.setattr("random.randint", lambda _a, _b: 100)

    unconscious = advance_choke_round(gs, defender, actions)

    assert unconscious is True
    assert any(a.get("type") == "choke_unconscious" for a in actions)



def test_submission_yield_success_captures_subject(monkeypatch):
    grappler = _fighter("Grappler", wil=10)
    subject = _fighter("Subject", wil=3)
    subject.max_hp = 20
    subject.hp = 5
    subject.add_condition(ConditionType.PINNED, -1)
    gs = GrappleState(choke_rounds=2)
    actions = []

    monkeypatch.setattr("random.randint", lambda _a, _b: 1)

    captured = check_submission_yield(grappler, subject, gs, actions)

    assert captured is True
    assert any(a.get("type") == "submission_accepted" for a in actions)



def test_submission_yield_failed_releases_for_pride(monkeypatch):
    grappler = _fighter("Grappler", wil=1)
    subject = _fighter("Subject", wil=3)
    subject.max_hp = 20
    subject.hp = 4
    subject.add_condition(ConditionType.CHOKED, -1)
    subject.add_condition(ConditionType.PINNED, -1)
    gs = GrappleState(choke_rounds=4)
    actions = []

    monkeypatch.setattr("random.randint", lambda _a, _b: 100)

    captured = check_submission_yield(grappler, subject, gs, actions)

    assert captured is False
    assert gs.choke_rounds == 0
    assert any(a.get("type") == "submission_pride_release" for a in actions)



def test_trauma_flinch_sickness_applies_init_penalty():
    fighter = _fighter("Ubbe", wil=3)
    opponent = _fighter("Raider", wil=3)
    fighter.trauma_conditions = [{"condition": "flinch_sickness", "severity": "mild", "wil": 3}]

    result = check_trauma_conditions(fighter, opponent, {"round": 1})

    assert fighter.init_penalty == -5
    assert any(e.get("condition") == "flinch_sickness" for e in result["effects"])



def test_trauma_battle_shock_can_skip_round(monkeypatch):
    fighter = _fighter("Ubbe", wil=1)
    opponent = _fighter("Raider", wil=3)
    fighter.trauma_conditions = [{"condition": "battle_shock", "severity": "moderate", "wil": 1}]

    seq = iter([100, 4])
    monkeypatch.setattr("random.randint", lambda _a, _b: next(seq))

    result = check_trauma_conditions(fighter, opponent, {"round": 1})

    assert result["skip_round"] is True
    assert fighter.has_condition(ConditionType.STAGGERED)
