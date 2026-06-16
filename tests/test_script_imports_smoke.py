"""Smoke tests to ensure every script module imports successfully.

These are intentionally lightweight guardrails for modules that currently
lack dedicated test files.
"""

from __future__ import annotations

import importlib

import pytest


UNMATCHED_SCRIPT_MODULES = [
    "band_manager",
    "barrow_generator",
    "bestiary",
    "calendar_sim",
    "combat_ai",
    "combat_model",
    "combat_sim",
    "combat_types",
    "contract_manager",
    "contracts",
    "event_manager",
    "hidden_info",
    "npc_manager",
    "trauma",
    "travel",
    "village_politics",
    "wounds",
]


@pytest.mark.parametrize("module_name", UNMATCHED_SCRIPT_MODULES)
def test_module_imports(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None
    assert hasattr(module, "__file__")
