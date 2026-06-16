from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapter_registry import (
    build_replay_probe_payloads,
    built_in_adapters,
    preview_adapters,
)
from app.deterministic import build_replay_signature, build_seed_journal
from app.time_engine import _build_replay_probes, current_cursor


def test_built_in_adapters_expose_active_domains() -> None:
    adapters = built_in_adapters()
    keys = {adapter.key for adapter in adapters}
    assert "settlement_stack" in keys
    assert "animal_breeding" in keys
    assert any("economy" in adapter.domains for adapter in adapters)
    settlement = next(adapter for adapter in adapters if adapter.key == "settlement_stack")
    assert settlement.deterministic is True


def test_preview_adapters_returns_weekly_preview() -> None:
    preview = preview_adapters(current_cursor(), unit="week", amount=1)
    assert preview.unit == "week"
    assert preview.adapters
    settlement = next(item for item in preview.adapters if item.key == "settlement_stack")
    assert settlement.supported is True
    assert settlement.status == "previewed"


def test_preview_adapters_skips_animals_on_week() -> None:
    preview = preview_adapters(current_cursor(), unit="week", amount=1)
    animals = next(item for item in preview.adapters if item.key == "animal_breeding")
    assert animals.supported is False
    assert animals.status == "skipped"


def test_seed_journal_is_stable_for_same_request() -> None:
    cursor = current_cursor()
    journal_a = build_seed_journal(
        cursor,
        unit="week",
        amount=1,
        transaction_id="txn_same",
        adapter_keys=["settlement_stack", "animal_breeding"],
    )
    journal_b = build_seed_journal(
        cursor,
        unit="week",
        amount=1,
        transaction_id="txn_same",
        adapter_keys=["settlement_stack", "animal_breeding"],
    )
    assert journal_a == journal_b


def test_deterministic_replay_probes_are_stable() -> None:
    cursor = current_cursor()
    probes_a = _build_replay_probes(
        cursor,
        unit="week",
        amount=1,
        adapter_seeds={"animal_breeding": 12345, "settlement_stack": 777},
    )
    probes_b = _build_replay_probes(
        cursor,
        unit="week",
        amount=1,
        adapter_seeds={"animal_breeding": 12345, "settlement_stack": 777},
    )
    assert probes_a == probes_b
    assert probes_a
    for probe in probes_a:
        assert probe["signature"] == build_replay_signature(probe["payload"])


def test_replay_probe_payloads_include_draw_journal_for_animals() -> None:
    cursor = current_cursor()
    payloads = build_replay_probe_payloads(
        cursor,
        unit="season",
        amount=1,
        adapter_seeds={"animal_breeding": 12345},
    )
    animal = next(item for item in payloads if item["key"] == "animal_breeding")
    assert "draw_journal" in animal
    assert "horse_pairs" in animal["draw_journal"]


def test_replay_probe_payloads_include_draw_journal_for_settlement_stack() -> None:
    cursor = current_cursor()
    payloads = build_replay_probe_payloads(
        cursor,
        unit="week",
        amount=1,
        adapter_seeds={"settlement_stack": 777},
    )
    settlement = next(item for item in payloads if item["key"] == "settlement_stack")
    assert "draw_journal" in settlement
    assert settlement["draw_journal"]["total_draws"] >= settlement["draw_journal"]["sample_size"]


def test_seasonal_settlement_stack_draw_journal_has_random_calls() -> None:
    cursor = current_cursor()
    payloads = build_replay_probe_payloads(
        cursor,
        unit="season",
        amount=1,
        adapter_seeds={"settlement_stack": 777},
    )
    settlement = next(item for item in payloads if item["key"] == "settlement_stack")
    assert settlement["draw_journal"]["total_draws"] > 0
    sample = settlement["draw_journal"]["sample"]
    assert sample
    assert "caller" in sample[0]
