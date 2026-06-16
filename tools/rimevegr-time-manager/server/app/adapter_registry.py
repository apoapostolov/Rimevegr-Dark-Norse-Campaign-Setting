from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import random
from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from typing import Any

from .models import (
    AdapterDescriptor,
    AdapterPreviewResponse,
    AdapterPreviewResult,
    TimelineCursor,
)
from .state_paths import DATA_DIR, SCRIPTS_DIR


def _load_script_module(module_name: str, path: Path) -> ModuleType:
    scripts_dir = str(path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sum_union_treasury(view_state: dict[str, Any]) -> int:
    unions = view_state.get("unions", [])
    if isinstance(unions, dict):
        iterable = unions.values()
    elif isinstance(unions, list):
        iterable = unions
    else:
        iterable = []
    return sum(
        int(union.get("treasury_silver", 0))
        for union in iterable
        if isinstance(union, dict)
    )


class RandomJournal:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)
        self.draws: list[dict[str, Any]] = []

    def _caller_name(self) -> str:
        for frame_info in inspect.stack()[2:8]:
            filename = str(frame_info.filename)
            if filename.endswith("village_politics.py"):
                return frame_info.function
        return "unknown"

    def randint(self, a: int, b: int) -> int:
        value = self._rng.randint(a, b)
        self.draws.append(
            {
                "fn": "randint",
                "args": [a, b],
                "value": value,
                "caller": self._caller_name(),
            }
        )
        return value

    def choice(self, seq: list[Any]) -> Any:
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
        index = self._rng.randrange(len(seq))
        value = seq[index]
        self.draws.append(
            {
                "fn": "choice",
                "size": len(seq),
                "index": index,
                "value_repr": repr(value)[:200],
                "caller": self._caller_name(),
            }
        )
        return value


@contextmanager
def _patched_module_random(module: ModuleType, seed: int | None):
    if seed is None:
        yield None
        return
    journal = RandomJournal(seed)
    original_random = module.random
    module.random = journal
    try:
        yield journal
    finally:
        module.random = original_random


class TimeSimulationAdapter(ABC):
    def __init__(self, descriptor: AdapterDescriptor) -> None:
        self.descriptor = descriptor

    def supports(self, unit: str) -> bool:
        return unit in self.descriptor.granularities

    @abstractmethod
    def preview(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> AdapterPreviewResult:
        raise NotImplementedError

    def replay_probe(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> dict[str, Any] | None:
        if not self.descriptor.deterministic or not self.supports(unit):
            return None
        preview = self.preview(cursor, unit, amount, seed=seed)
        if not preview.supported:
            return None
        return {
            "key": preview.key,
            "summary": preview.summary,
            "metrics": dict(preview.metrics),
            "affected_entities": list(preview.affected_entities),
            "warnings": list(preview.warnings),
        }


class SettlementSimulationAdapter(TimeSimulationAdapter):
    def __init__(self) -> None:
        super().__init__(
            AdapterDescriptor(
                key="settlement_stack",
                label="Settlement Simulation Stack",
                domains=[
                    "economy",
                    "demographics",
                    "politics",
                    "wolfshead",
                    "routes",
                    "construction",
                    "contract_market",
                    "mine_production",
                ],
                granularities=["week", "season"],
                write_targets=[
                    "writing/norse_grit/data/political_state.yaml",
                    "writing/norse_grit/data/economy/settlement_economies.yaml",
                    "writing/norse_grit/data/geography/routes.yaml",
                    "writing/norse_grit/data/contracts/*.yaml",
                ],
                deterministic=True,
                implementation_status="active",
                notes=(
                    "Uses the existing village_politics simulation stack in preview "
                    "mode on copied state with tool-level random journaling."
                ),
            )
        )
        self._module: ModuleType | None = None

    def _vp(self) -> ModuleType:
        if self._module is None:
            self._module = _load_script_module(
                "rimevegr_village_politics",
                SCRIPTS_DIR / "village_politics.py",
            )
        return self._module

    def preview(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> AdapterPreviewResult:
        if not self.supports(unit):
            return AdapterPreviewResult(
                key=self.descriptor.key,
                label=self.descriptor.label,
                domains=self.descriptor.domains,
                status="skipped",
                supported=False,
                write_targets=self.descriptor.write_targets,
                summary=(
                    f"{unit} steps are not yet wired into the settlement "
                    "simulation stack."
                ),
                warnings=["Use week or season for settlement simulation previews."],
            )

        vp = self._vp()
        state = deepcopy(vp.load_state())
        before_view = vp.build_runtime_view_state(deepcopy(state))

        if unit == "week":
            reports: list[dict[str, Any]] = []
            draw_count = 0
            with _patched_module_random(vp, seed) as journal:
                for _ in range(amount):
                    reports.extend(vp.tick_week(state))
                if journal is not None:
                    draw_count = len(journal.draws)

            after_view = vp.build_runtime_view_state(state)
            economies = after_view.get("economies", {})
            union_before = _sum_union_treasury(before_view)
            union_after = _sum_union_treasury(after_view)
            affected = [
                name
                for name, econ in economies.items()
                if (econ.get("unmet_imports") or {})
                or econ.get("route_disruption_flags")
                or float(econ.get("outlaw_pressure", 0) or 0) > 0
            ][:8]
            return AdapterPreviewResult(
                key=self.descriptor.key,
                label=self.descriptor.label,
                domains=self.descriptor.domains,
                status="previewed",
                supported=True,
                write_targets=self.descriptor.write_targets,
                summary=(
                    f"Previewed {amount} weekly settlement stack step(s) across "
                    f"{len(reports)} settlement reports."
                ),
                metrics={
                    "weeks": amount,
                    "seed": seed or 0,
                    "random_draws": draw_count,
                    "settlement_reports": len(reports),
                    "settlements_with_shortages": sum(
                        1 for econ in economies.values() if (econ.get("unmet_imports") or {})
                    ),
                    "settlements_with_route_pressure": sum(
                        1 for econ in economies.values() if econ.get("route_disruption_flags")
                    ),
                    "settlements_with_outlaw_pressure": sum(
                        1
                        for econ in economies.values()
                        if float(econ.get("outlaw_pressure", 0) or 0) > 0
                    ),
                    "union_treasury_delta_silver": union_after - union_before,
                },
                affected_entities=affected,
                warnings=[],
            )

        season_summaries: list[dict[str, Any]] = []
        draw_count = 0
        with _patched_module_random(vp, seed) as journal:
            for _ in range(amount):
                season_summaries.append(vp.tick_season(state))
            if journal is not None:
                draw_count = len(journal.draws)

        after_view = vp.build_runtime_view_state(state)
        economies = after_view.get("economies", {})
        before_population = sum(
            int(econ.get("population", 0) or 0)
            for econ in before_view.get("economies", {}).values()
        )
        after_population = sum(
            int(econ.get("population", 0) or 0) for econ in economies.values()
        )
        affected = [
            name
            for name, econ in economies.items()
            if econ.get("shortage_flags") or econ.get("route_disruption_flags")
        ][:8]
        return AdapterPreviewResult(
            key=self.descriptor.key,
            label=self.descriptor.label,
            domains=self.descriptor.domains,
            status="previewed",
            supported=True,
            write_targets=self.descriptor.write_targets,
            summary=f"Previewed {amount} seasonal settlement stack step(s).",
            metrics={
                "seasons": amount,
                "seed": seed or 0,
                "random_draws": draw_count,
                "season_runs": len(season_summaries),
                "population_delta": after_population - before_population,
                "settlements_with_shortage_flags": sum(
                    1 for econ in economies.values() if econ.get("shortage_flags")
                ),
            },
            affected_entities=affected,
            warnings=[],
        )

    def replay_probe(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> dict[str, Any] | None:
        if not self.supports(unit) or seed is None:
            return None

        vp = self._vp()
        state = deepcopy(vp.load_state())
        with _patched_module_random(vp, seed) as journal:
            if unit == "week":
                for _ in range(amount):
                    vp.tick_week(state)
            else:
                for _ in range(amount):
                    vp.tick_season(state)
            draw_journal = list(journal.draws if journal is not None else [])

        sample_draws = draw_journal[:24]
        return {
            "key": self.descriptor.key,
            "summary": f"Replay journal for {amount} {unit} settlement-stack step(s).",
            "metrics": {
                "steps": amount,
                "seed": seed,
                "random_draws": len(draw_journal),
            },
            "affected_entities": [],
            "warnings": [],
            "draw_journal": {
                "sample": sample_draws,
                "sample_size": len(sample_draws),
                "total_draws": len(draw_journal),
            },
        }


class AnimalBreedingAdapter(TimeSimulationAdapter):
    def __init__(self) -> None:
        super().__init__(
            AdapterDescriptor(
                key="animal_breeding",
                label="Horse Herd And Kennel Seasons",
                domains=["horse_herds", "dog_kennels"],
                granularities=["season"],
                write_targets=[
                    "writing/norse_grit/data/horse_herds.yaml",
                    "writing/norse_grit/data/dog_kennels.yaml",
                ],
                deterministic=True,
                implementation_status="active",
                notes=(
                    "Runs seasonal herd and kennel previews against temporary file copies."
                ),
            )
        )
        self._horse_module: ModuleType | None = None
        self._dog_module: ModuleType | None = None

    def _horse(self) -> ModuleType:
        if self._horse_module is None:
            self._horse_module = _load_script_module(
                "rimevegr_horse_breeding",
                SCRIPTS_DIR / "horse_breeding.py",
            )
        return self._horse_module

    def _dog(self) -> ModuleType:
        if self._dog_module is None:
            self._dog_module = _load_script_module(
                "rimevegr_dog_breeding",
                SCRIPTS_DIR / "dog_breeding.py",
            )
        return self._dog_module

    @staticmethod
    def _season_id(cursor: TimelineCursor, offset: int) -> str:
        season_index = ((cursor.day_of_year - 1) // 90) + 1 + offset
        year = cursor.year
        while season_index > 4:
            season_index -= 4
            year += 1
        return f"Y{year}-S{season_index}"

    def replay_probe(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> dict[str, Any] | None:
        if not self.supports(unit):
            return None

        horse = self._horse()
        dog = self._dog()
        herd_payload = horse.load_herds()
        kennel_payload = dog.load_kennels()
        seed_base = seed or 0

        scheduled_horse_pairs: list[dict[str, Any]] = []
        scheduled_dog_pairs: list[dict[str, Any]] = []

        for season_offset in range(amount):
            season_id = self._season_id(cursor, season_offset)
            for herd_index, herd in enumerate(herd_payload.get("horse_herds", [])):
                herd_id = herd.get("herd_id")
                for pair_index, pair in enumerate(herd.get("breeding_pairs", [])):
                    if pair.get("target_season") != season_id:
                        continue
                    scheduled_horse_pairs.append(
                        {
                            "season_id": season_id,
                            "herd_id": herd_id,
                            "dam": pair.get("dam"),
                            "sire": pair.get("sire"),
                            "draw_seed": seed_base
                            + 1_000
                            + season_offset * 100
                            + herd_index
                            + pair_index,
                        }
                    )
            for kennel_index, kennel in enumerate(kennel_payload.get("dog_kennels", [])):
                kennel_id = kennel.get("kennel_id")
                for pair_index, pair in enumerate(kennel.get("breeding_pairs", [])):
                    if pair.get("target_season") != season_id:
                        continue
                    scheduled_dog_pairs.append(
                        {
                            "season_id": season_id,
                            "kennel_id": kennel_id,
                            "dam": pair.get("dam"),
                            "sire": pair.get("sire"),
                            "draw_seed": seed_base
                            + 2_000
                            + season_offset * 100
                            + kennel_index
                            + pair_index,
                        }
                    )

        return {
            "key": self.descriptor.key,
            "summary": f"Replay journal for {amount} seasonal animal-breeding step(s).",
            "metrics": {
                "seasons": amount,
                "seed": seed_base,
                "horse_pair_draws": len(scheduled_horse_pairs),
                "dog_pair_draws": len(scheduled_dog_pairs),
            },
            "affected_entities": [
                *(item["herd_id"] for item in scheduled_horse_pairs[:4] if item.get("herd_id")),
                *(item["kennel_id"] for item in scheduled_dog_pairs[:4] if item.get("kennel_id")),
            ],
            "warnings": [],
            "draw_journal": {
                "horse_pairs": scheduled_horse_pairs,
                "dog_pairs": scheduled_dog_pairs,
            },
        }

    def preview(
        self,
        cursor: TimelineCursor,
        unit: str,
        amount: int,
        seed: int | None = None,
    ) -> AdapterPreviewResult:
        if not self.supports(unit):
            return AdapterPreviewResult(
                key=self.descriptor.key,
                label=self.descriptor.label,
                domains=self.descriptor.domains,
                status="skipped",
                supported=False,
                write_targets=self.descriptor.write_targets,
                summary="Animal breeding advances only on seasonal boundaries.",
                warnings=["Use season steps to preview herds and kennels."],
            )

        horse = self._horse()
        dog = self._dog()
        herd_payload = horse.load_herds()
        kennel_payload = dog.load_kennels()
        herd_ids = [item.get("herd_id") for item in herd_payload.get("horse_herds", [])]
        kennel_ids = [item.get("kennel_id") for item in kennel_payload.get("dog_kennels", [])]

        horse_births = 0
        dog_births = 0
        seed_base = seed or 0
        with tempfile.TemporaryDirectory(prefix="rimevegr_animals_") as tmp:
            tmpdir = Path(tmp)
            herd_file = tmpdir / "horse_herds.yaml"
            kennel_file = tmpdir / "dog_kennels.yaml"
            herd_file.write_text(
                (DATA_DIR / "horse_herds.yaml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            kennel_file.write_text(
                (DATA_DIR / "dog_kennels.yaml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            for season_offset in range(amount):
                season_id = self._season_id(cursor, season_offset)
                for index, herd_id in enumerate(filter(None, herd_ids)):
                    result = horse.tick_herd_season(
                        herd_id,
                        herd_file=herd_file,
                        season_id=season_id,
                        seed=seed_base + 1_000 + season_offset * 100 + index,
                    )
                    horse_births += int(result.get("foals_born", 0))
                for index, kennel_id in enumerate(filter(None, kennel_ids)):
                    result = dog.tick_kennel_season(
                        kennel_id,
                        kennel_file=kennel_file,
                        season_id=season_id,
                        seed=seed_base + 2_000 + season_offset * 100 + index,
                    )
                    dog_births += int(result.get("pups_born", 0))

        return AdapterPreviewResult(
            key=self.descriptor.key,
            label=self.descriptor.label,
            domains=self.descriptor.domains,
            status="previewed",
            supported=True,
            write_targets=self.descriptor.write_targets,
            summary=(
                f"Previewed {amount} seasonal breeding step(s) on temporary herd "
                "and kennel copies."
            ),
            metrics={
                "seasons": amount,
                "seed": seed or 0,
                "herds_processed": len(herd_ids),
                "kennels_processed": len(kennel_ids),
                "foals_born": horse_births,
                "pups_born": dog_births,
            },
            affected_entities=[*filter(None, herd_ids[:4]), *filter(None, kennel_ids[:4])],
            warnings=[],
        )


def get_adapter_registry() -> list[TimeSimulationAdapter]:
    return [SettlementSimulationAdapter(), AnimalBreedingAdapter()]


def built_in_adapters() -> list[AdapterDescriptor]:
    return [adapter.descriptor for adapter in get_adapter_registry()]


def preview_adapters(
    cursor: TimelineCursor,
    unit: str,
    amount: int,
    adapter_seeds: dict[str, int] | None = None,
) -> AdapterPreviewResponse:
    adapter_seeds = adapter_seeds or {}
    return AdapterPreviewResponse(
        cursor=cursor,
        unit=unit,
        amount=amount,
        adapters=[
            adapter.preview(
                cursor,
                unit,
                amount,
                seed=adapter_seeds.get(adapter.descriptor.key),
            )
            for adapter in get_adapter_registry()
        ],
    )


def build_replay_probe_payloads(
    cursor: TimelineCursor,
    unit: str,
    amount: int,
    adapter_seeds: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    adapter_seeds = adapter_seeds or {}
    payloads: list[dict[str, Any]] = []
    for adapter in get_adapter_registry():
        probe = adapter.replay_probe(
            cursor,
            unit,
            amount,
            seed=adapter_seeds.get(adapter.descriptor.key),
        )
        if probe is not None:
            payloads.append(probe)
    return payloads
