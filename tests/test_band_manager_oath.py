import yaml

import band_manager


def _write_state(path, count=0, flag=False):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "band": {
                    "name": "Voss's Black Axes",
                    "oath_break_count": count,
                    "oath_breaker": flag,
                    "history": [],
                },
                "members": [],
            },
            f,
            sort_keys=False,
        )



def test_oath_break_flags_after_three(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file)

    band_manager.cmd_oath_break(state_path=str(state_file))
    band_manager.cmd_oath_break(state_path=str(state_file))
    result = band_manager.cmd_oath_break(state_path=str(state_file))

    assert result["oath_break_count"] == 3
    assert result["oath_breaker"] is True



def test_oath_clear_requires_reputation_then_clears(tmp_path):
    state_file = tmp_path / "band_state.yaml"
    _write_state(state_file, count=3, flag=True)

    denied = band_manager.cmd_oath_clear(witness_rep=1, state_path=str(state_file))
    allowed = band_manager.cmd_oath_clear(witness_rep=3, state_path=str(state_file))

    assert denied["cleared"] is False
    assert allowed["cleared"] is True
    assert allowed["oath_break_count"] == 3
