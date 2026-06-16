from pathlib import Path

import yaml

import session_lifecycle as sl


def _write_yaml(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)


def test_cmd_end_dry_run_does_not_mutate_files(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    band_file = data_dir / "band_state.yaml"
    backups_dir = tmp_path / "backups"

    _write_yaml(
        band_file,
        {
            "band": {
                "day_of_year": 10,
                "treasury_silver": 21,
                "notes": [],
                "history": [],
            },
            "members": [],
        },
    )

    monkeypatch.setattr(sl, "DATA", data_dir)
    monkeypatch.setattr(sl, "BAND_FILE", band_file)
    monkeypatch.setattr(sl, "BACKUPS", backups_dir)
    monkeypatch.setattr(sl, "ROOT", tmp_path)

    result = sl.cmd_end(
        chapter=1,
        day_advance=7,
        treasury_delta=5,
        food_delta=-2,
        contract_status=None,
        note="dry run",
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["day_of_year"] == 17
    assert result["treasury_silver"] == 26

    with open(band_file, "r", encoding="utf-8") as f:
        persisted = yaml.safe_load(f)
    assert persisted["band"]["day_of_year"] == 10
    assert persisted["band"]["treasury_silver"] == 21
    assert not backups_dir.exists()
