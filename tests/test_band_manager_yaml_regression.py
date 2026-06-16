from pathlib import Path

import band_manager


def test_load_band_reads_wrapped_yaml_state():
    band_path = Path(__file__).resolve().parents[1] / "data" / "band_state.yaml"
    data = band_manager.load_band(str(band_path))

    assert isinstance(data, dict)
    assert "members" in data
    assert "name" in data
    assert isinstance(data["members"], list)
