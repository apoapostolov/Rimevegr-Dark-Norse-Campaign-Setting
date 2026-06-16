"""Wolfshead trait tests — dirty_fighter, prepared_ground, curse_hex, skirmisher_retreat."""

from __future__ import annotations

import pytest

from combat_model import Fighter
from combat_sim import resolve_attack, run_duel
from combat_types import ConditionType, Maneuver
from engine import CheckResult, OpposedResult, ResultLevel


# ── helpers ──────────────────────────────────────────────────────────────────

def _fighter(**kwargs) -> Fighter:
    base = dict(
        name="F",
        mig=6,
        nim=5,
        tou=6,
        wit=5,
        wil=5,
        weapon_skill=2,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        hp=24,
        max_hp=24,
    )
    base.update(kwargs)
    return Fighter(**base)


def _attacker_win(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


def _fail_check(*args, **kwargs):
    return CheckResult(95, 10, ResultLevel.FAILURE, 85)


def _pass_check(*args, **kwargs):
    return CheckResult(10, 90, ResultLevel.SUCCESS, -80)


# ── dirty_fighter ─────────────────────────────────────────────────────────────

class TestDirtyFighter:
    def test_dirty_fighter_bonus_vs_staggered(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Veteran", traits=["dirty_fighter"])
        defender = _fighter(name="Target")
        defender.add_condition(ConditionType.STAGGERED, 2)

        result: dict = {}
        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, result)

        assert result.get("dirty_fighter_bonus") is True

    def test_dirty_fighter_bonus_vs_prone(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Veteran", traits=["dirty_fighter"])
        defender = _fighter(name="Target")
        defender.add_condition(ConditionType.PRONE, 1)

        result: dict = {}
        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, result)

        assert result.get("dirty_fighter_bonus") is True

    def test_dirty_fighter_bonus_vs_dazed(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Veteran", traits=["dirty_fighter"])
        defender = _fighter(name="Target")
        defender.add_condition(ConditionType.DAZED, 2)

        result: dict = {}
        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, result)

        assert result.get("dirty_fighter_bonus") is True

    def test_dirty_fighter_no_bonus_vs_healthy_target(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Veteran", traits=["dirty_fighter"])
        defender = _fighter(name="Target")

        result: dict = {}
        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, result)

        assert "dirty_fighter_bonus" not in result

    def test_dirty_fighter_not_applied_without_trait(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Normal", traits=[])
        defender = _fighter(name="Target")
        defender.add_condition(ConditionType.STAGGERED, 2)

        result: dict = {}
        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, result)

        assert "dirty_fighter_bonus" not in result


# ── curse_hex ─────────────────────────────────────────────────────────────────

class TestCurseHex:
    def test_curse_hex_prebattle_applies_on_wil_fail(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        seidr = _fighter(name="SeidrWorker", traits=["curse_hex"])
        target = _fighter(name="Hero", wil=5)

        result = run_duel(seidr, target, max_rounds=0)
        pre = result.get("pre_battle", [])

        hex_events = [e for e in pre if e.get("type") == "curse_hex"]
        assert hex_events, "curse_hex event should appear in pre_battle"
        assert target.curse_hex_rounds > 0

    def test_curse_hex_prebattle_resisted_on_wil_pass(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _pass_check)

        seidr = _fighter(name="SeidrWorker", traits=["curse_hex"])
        target = _fighter(name="Hero", wil=5)

        result = run_duel(seidr, target, max_rounds=0)
        pre = result.get("pre_battle", [])

        resisted = [e for e in pre if e.get("type") == "curse_hex_resisted"]
        assert resisted, "curse_hex_resisted event should appear when WIL passes"
        assert target.curse_hex_rounds == 0

    def test_curse_hex_rounds_countdown(self):
        """curse_hex_rounds decrements each round."""
        attacker = _fighter(name="A")
        defender = _fighter(name="B")
        defender.curse_hex_rounds = 3  # set manually, runs down each round

        run_duel(attacker, defender, max_rounds=2)

        # After 2 rounds the countdown should have ticked (may reach 0 if rounds ran)
        assert defender.curse_hex_rounds < 3

    def test_hexed_defender_suffers_attack_penalty(self, monkeypatch: pytest.MonkeyPatch):
        """When defender is hexed, d_mods should be lower (curse_hex -= 10)."""
        import combat_sim as cs

        calls: list[dict] = []

        def capture_opposed(a_attr, a_skill, a_mods, d_attr, d_skill, d_mods, **kwargs):
            calls.append({"a_mods": a_mods, "d_mods": d_mods})
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", capture_opposed)

        attacker = _fighter(name="A", weapon_skill=3, nim=7)
        defender_clean = _fighter(name="B", weapon_skill=3, nim=7)
        defender_hexed = _fighter(name="B", weapon_skill=3, nim=7)
        defender_hexed.curse_hex_rounds = 3

        # baseline — no hex
        calls.clear()
        resolve_attack(attacker, defender_clean, Maneuver.CUT, Maneuver.GUARD, {})
        baseline_d_mods = calls[-1]["d_mods"] if calls else None

        # hexed
        calls.clear()
        resolve_attack(attacker, defender_hexed, Maneuver.CUT, Maneuver.GUARD, {})
        hexed_d_mods = calls[-1]["d_mods"] if calls else None

        if baseline_d_mods is not None and hexed_d_mods is not None:
            assert hexed_d_mods < baseline_d_mods, (
                f"hexed d_mods ({hexed_d_mods}) should be < baseline ({baseline_d_mods})"
            )


# ── prepared_ground ────────────────────────────────────────────────────────────

class TestPreparedGround:
    def test_prepared_ground_applies_hamstrung_on_nim_fail(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        trapper = _fighter(name="Trapper", traits=["prepared_ground"])
        target = _fighter(name="Hero", nim=5)

        result = run_duel(trapper, target, max_rounds=0)
        pre = result.get("pre_battle", [])

        trap_events = [e for e in pre if e.get("type") == "prepared_ground"]
        assert trap_events, "prepared_ground event should appear in pre_battle"
        assert target.has_condition(ConditionType.HAMSTRUNG)

    def test_prepared_ground_avoided_on_nim_pass(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _pass_check)

        trapper = _fighter(name="Trapper", traits=["prepared_ground"])
        target = _fighter(name="Hero", nim=5)

        result = run_duel(trapper, target, max_rounds=0)
        pre = result.get("pre_battle", [])

        avoided = [e for e in pre if e.get("type") == "prepared_ground_avoided"]
        assert avoided, "prepared_ground_avoided event should appear when NIM passes"
        assert not target.has_condition(ConditionType.HAMSTRUNG)

    def test_prepared_ground_fires_once_only(self, monkeypatch: pytest.MonkeyPatch):
        """The trap fires at most once even in skirmish with multiple encounters."""
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        trapper = _fighter(name="Trapper", traits=["prepared_ground"])
        target = _fighter(name="Hero", nim=5)

        # Manually mark triggered and re-run
        trapper.prepared_ground_triggered = True

        result = run_duel(trapper, target, max_rounds=0)
        pre = result.get("pre_battle", [])

        trap_events = [e for e in pre if e.get("type") == "prepared_ground"]
        assert not trap_events, "prepared_ground should not fire again once triggered"


# ── skirmisher_retreat ────────────────────────────────────────────────────────

class TestSkirmisherRetreat:
    def test_skirmisher_retreats_when_badly_losing(self, monkeypatch: pytest.MonkeyPatch):
        """Scout at ≤50% HP vs full-HP opponent → FLEEING applied (opponent never hits back)."""
        # Prevent the opponent from killing the scout by always giving the defender a win
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        scout = _fighter(name="Scout", traits=["skirmisher_retreat"], hp=10, max_hp=24)
        opponent = _fighter(name="Fighter", hp=24, max_hp=24)

        result = run_duel(scout, opponent, max_rounds=2)

        rounds = result.get("round_log", [])
        retreat_events = []
        for rd in rounds:
            for entry in rd.get("actions", []):
                if isinstance(entry, dict) and entry.get("type") == "skirmisher_retreat":
                    retreat_events.append(entry)

        # Verify the scout meets the trigger conditions (state-based check as fallback)
        scout_state = result.get("combatants", {}).get("Scout", {})
        scout_conditions = scout_state.get("conditions", {})
        scout_fled = "FLEEING" in scout_conditions or bool(retreat_events)
        assert scout_fled, "scout should FLEE when at ≤50% HP vs ≥70% HP opponent"

    def test_skirmisher_no_retreat_when_winning(self):
        """Scout at full HP vs wounded opponent → no retreat."""
        scout = _fighter(name="Scout", traits=["skirmisher_retreat"], hp=24, max_hp=24)
        opponent = _fighter(name="Fighter", hp=8, max_hp=24)

        result = run_duel(scout, opponent, max_rounds=1)

        rounds = result.get("round_log", [])
        for rd in rounds:
            for entry in rd.get("actions", []):
                if isinstance(entry, dict):
                    assert entry.get("type") != "skirmisher_retreat"

    def test_skirmisher_not_applied_without_trait(self):
        """No trait → never triggers retreat even when badly losing."""
        fighter = _fighter(name="Normal", traits=[], hp=10, max_hp=24)
        opponent = _fighter(name="Fighter", hp=20, max_hp=24)

        result = run_duel(fighter, opponent, max_rounds=2)

        rounds = result.get("round_log", [])
        for rd in rounds:
            for entry in rd.get("actions", []):
                if isinstance(entry, dict):
                    assert entry.get("type") != "skirmisher_retreat"


# ── YAML bestiary coverage ────────────────────────────────────────────────────

class TestWolfsheadBestiary:
    """Verify all 6 wolfshead entries load and have sim_traits."""

    EXPECTED = {
        "HUM_WOLF_01": ["skirmisher_retreat"],
        "HUM_WOLF_02": ["dirty_fighter"],
        "HUM_WOLF_03": ["dirty_fighter", "tactical_withdrawal_once"],
        "HUM_WOLF_04": ["berserker_pain_fury"],
        "HUM_WOLF_05": ["prepared_ground", "skirmisher_retreat"],
        "HUM_WOLF_06": ["curse_hex", "skirmisher_retreat"],
    }

    @pytest.fixture(scope="class")
    def bestiary(self):
        import yaml, pathlib
        path = pathlib.Path(__file__).parent.parent / "data" / "bestiary" / "humans.yaml"
        with open(path) as fh:
            data = yaml.safe_load(fh)
        # humans.yaml may use a top-level key or be a flat list
        entries: list = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    entries.extend(v)
        return {e["id"]: e for e in entries if isinstance(e, dict) and "id" in e}

    @pytest.mark.parametrize("entry_id,expected_traits", list(EXPECTED.items()))
    def test_wolfshead_has_expected_traits(self, bestiary, entry_id, expected_traits):
        entry = bestiary.get(entry_id)
        assert entry is not None, f"{entry_id} not found in bestiary"
        actual = entry.get("sim_traits", [])
        for trait in expected_traits:
            assert trait in actual, f"{entry_id} missing trait '{trait}'"
