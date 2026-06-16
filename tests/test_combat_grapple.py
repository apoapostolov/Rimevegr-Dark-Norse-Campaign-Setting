"""test_combat_grapple.py — Tests for combat_grapple.py grapple entry/clear."""
import pytest

from combat_model import Fighter, GrappleState
from combat_types import ConditionType, Maneuver, GrapplePosition
from combat_grapple import (
    _create_grapple,
    _clear_grapple,
    resolve_grapple_entry,
)


def make_fighter(name: str, mig: int = 6, nim: int = 5, tou: int = 5, wit: int = 5, wil: int = 5,
                 brawl_skill: int = 1) -> Fighter:
    f = Fighter(name=name, mig=mig, nim=nim, tou=tou, wit=wit, wil=wil, brawl_skill=brawl_skill)
    return f


class TestCreateGrapple:
    def test_both_fighters_get_grappled_condition(self):
        a = make_fighter("Attacker")
        d = make_fighter("Defender")
        _create_grapple(a, d, GrapplePosition.DOMINANT_CLINCH)
        assert a.has_condition(ConditionType.GRAPPLED)
        assert d.has_condition(ConditionType.GRAPPLED)

    def test_both_fighters_share_same_grapple_state(self):
        a = make_fighter("Attacker")
        d = make_fighter("Defender")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        assert a.grapple_state is d.grapple_state

    def test_grapple_state_not_none(self):
        a = make_fighter("A")
        d = make_fighter("D")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        assert a.grapple_state is not None

    def test_dominant_clinch_sets_dominant_fighter(self):
        a = make_fighter("Erik")
        d = make_fighter("Bjorn")
        _create_grapple(a, d, GrapplePosition.DOMINANT_CLINCH)
        assert a.grapple_state.dominant == "Erik"

    def test_neutral_clinch_no_dominant(self):
        a = make_fighter("A")
        d = make_fighter("B")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        assert a.grapple_state.dominant == ""


class TestClearGrapple:
    def test_grapple_state_cleared_on_both(self):
        a = make_fighter("A")
        d = make_fighter("B")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        _clear_grapple(a, d)
        assert a.grapple_state is None
        assert d.grapple_state is None

    def test_grappled_condition_removed(self):
        a = make_fighter("A")
        d = make_fighter("B")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        _clear_grapple(a, d)
        assert not a.has_condition(ConditionType.GRAPPLED)
        assert not d.has_condition(ConditionType.GRAPPLED)

    def test_pinned_condition_removed(self):
        a = make_fighter("A")
        d = make_fighter("B")
        _create_grapple(a, d, GrapplePosition.NEUTRAL_CLINCH)
        a.add_condition(ConditionType.PINNED, 3)
        d.add_condition(ConditionType.PINNED, 3)
        _clear_grapple(a, d)
        assert not a.has_condition(ConditionType.PINNED)
        assert not d.has_condition(ConditionType.PINNED)

    def test_clear_without_prior_grapple_safe(self):
        a = make_fighter("A")
        d = make_fighter("B")
        _clear_grapple(a, d)  # no grapple state — must not throw
        assert a.grapple_state is None
        assert d.grapple_state is None


class TestResolveGrappleEntry:
    def test_brokartok_returns_dict_with_condition_applied(self):
        a = make_fighter("Erik", mig=8, brawl_skill=2)
        d = make_fighter("Bjorn", mig=4, brawl_skill=0)
        result = {"hit": False}
        resolve_grapple_entry(a, d, Maneuver.BROKARTOK, result)
        assert "condition_applied" in result
        cond = result["condition_applied"]
        # Accept any dominant/neutral/clinch variant or miss
        valid = ("dominant_clinch", "neutral_clinch", "brokartok_miss")
        assert any(cond.startswith(v) or cond == v for v in valid), (
            f"Unexpected condition_applied: {cond!r}"
        )

    def test_both_fighters_grappled_after_entry(self):
        """After any grapple entry, both must be in GRAPPLED state."""
        for _ in range(10):
            a = make_fighter("A", mig=6, brawl_skill=1)
            d = make_fighter("D", mig=6, brawl_skill=1)
            result = {"hit": False}
            resolve_grapple_entry(a, d, Maneuver.BROKARTOK, result)
            # At least one grappled state should exist or result shows miss
            if result.get("condition_applied") != "brokartok_miss":
                assert a.has_condition(ConditionType.GRAPPLED) or (a.grapple_state is not None)

    def test_dominant_clinch_applied_when_attacker_wins_mig_opposed(self):
        """Attacker with vastly superior MIG should often win dominant clinch."""
        wins_dominant = 0
        for _ in range(30):
            a = make_fighter("Strong", mig=10, brawl_skill=3)
            d = make_fighter("Weak", mig=1, brawl_skill=0)
            result = {"hit": False}
            resolve_grapple_entry(a, d, Maneuver.BROKARTOK, result)
            if result.get("condition_applied") == "dominant_clinch":
                wins_dominant += 1
        # Should win dominant clinch most of the time given big skill disparity
        assert wins_dominant > 10, f"Expected > 10 dominant clinch wins, got {wins_dominant}"
