from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import DataDocumentSummary, DataPreviewResponse, ValidationIssue
from .state_paths import DATA_DIR, STATE_DIR

try:
    from ruamel.yaml import YAML
except Exception:  # pragma: no cover - fallback when dependency is not installed
    YAML = None


MANIFEST_PATH = STATE_DIR / "manifest.json"


@dataclass
class LoadedDocument:
    path: Path
    data: dict[str, Any] | list[Any] | None
    sha256: str
    parse_mode: str


TRACKED_YAML_FILES = [
    DATA_DIR / "settlements.yaml",
    DATA_DIR / "political_state.yaml",
    DATA_DIR / "horse_herds.yaml",
    DATA_DIR / "dog_kennels.yaml",
    DATA_DIR / "wolfshead_bands.yaml",
    DATA_DIR / "economy" / "settlement_economies.yaml",
    DATA_DIR / "geography" / "routes.yaml",
]


def _yaml_loader():
    if YAML is None:
        return None
    yaml_rt = YAML(typ="rt")
    yaml_rt.preserve_quotes = True
    yaml_rt.width = 120
    return yaml_rt


def ensure_state_layout() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("snapshots", "transactions", "exports", "locks"):
        (STATE_DIR / name).mkdir(parents=True, exist_ok=True)


def _iter_yaml_files() -> list[Path]:
    files = [path for path in TRACKED_YAML_FILES if path.exists()]
    contracts_dir = DATA_DIR / "contracts"
    if contracts_dir.exists():
        files.extend(sorted(contracts_dir.glob("*.yaml")))
    return sorted(files)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_yaml_document(path: Path) -> LoadedDocument:
    raw = path.read_bytes()
    sha256 = _sha256_bytes(raw)
    text = raw.decode("utf-8")
    yaml_rt = _yaml_loader()
    if yaml_rt is not None:
        data = yaml_rt.load(text)
        return LoadedDocument(path=path, data=data, sha256=sha256, parse_mode="ruamel-rt")
    return LoadedDocument(path=path, data=yaml.safe_load(text), sha256=sha256, parse_mode="pyyaml-safe")


def dump_yaml_document(data: Any) -> str:
    yaml_rt = _yaml_loader()
    if yaml_rt is not None:
        from io import StringIO

        stream = StringIO()
        yaml_rt.dump(data, stream)
        return stream.getvalue()
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)


def _collect_settlement_names(documents: list[LoadedDocument]) -> set[str]:
    names: set[str] = set()
    for document in documents:
        if document.path.name == "settlements.yaml" and isinstance(document.data, dict):
            for settlement in document.data.get("settlements", []):
                name = settlement.get("name")
                if name:
                    names.add(str(name))
    return names


def _collect_contract_ids(documents: list[LoadedDocument]) -> set[str]:
    ids: set[str] = set()
    for document in documents:
        if document.path.parent.name == "contracts" and isinstance(document.data, dict):
            for contract in document.data.get("contracts", []):
                contract_id = contract.get("id")
                if contract_id:
                    ids.add(str(contract_id))
    return ids


def _top_level_keys(data: Any) -> list[str]:
    if isinstance(data, dict):
        return [str(key) for key in data.keys()]
    return []


def _count_settlement_refs(data: Any) -> int:
    if isinstance(data, dict):
        total = 0
        for key, value in data.items():
            if key in {"settlement", "seat", "location"} and isinstance(value, str):
                total += 1
            total += _count_settlement_refs(value)
        return total
    if isinstance(data, list):
        return sum(_count_settlement_refs(item) for item in data)
    return 0


def _count_contract_refs(data: Any) -> int:
    if isinstance(data, dict):
        total = 0
        for key, value in data.items():
            if key in {"id", "contracts", "available_contract_ids"}:
                if isinstance(value, str):
                    total += 1
                elif isinstance(value, list):
                    total += len([item for item in value if isinstance(item, str)])
            total += _count_contract_refs(value)
        return total
    if isinstance(data, list):
        return sum(_count_contract_refs(item) for item in data)
    return 0


def validate_documents(documents: list[LoadedDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    settlement_names = _collect_settlement_names(documents)
    contract_ids = _collect_contract_ids(documents)

    for document in documents:
        data = document.data
        if data is None:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="empty_document",
                    message="YAML document parsed to null.",
                    path=str(document.path),
                )
            )
            continue

        if document.path.name == "political_state.yaml" and isinstance(data, dict):
            for bucket_name in ("economies", "demographics"):
                bucket = data.get(bucket_name, {})
                if isinstance(bucket, dict):
                    for settlement_name in bucket.keys():
                        if settlement_name not in settlement_names:
                            issues.append(
                                ValidationIssue(
                                    severity="error",
                                    code="unknown_settlement_ref",
                                    message=f"{bucket_name} references unknown settlement '{settlement_name}'.",
                                    path=str(document.path),
                                )
                            )
            for union in data.get("unions", []):
                seat = union.get("seat")
                if seat and seat not in settlement_names:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="unknown_union_seat",
                            message=f"Union seat '{seat}' is not present in settlements.yaml.",
                            path=str(document.path),
                        )
                    )
                for member in union.get("members", []):
                    settlement = member.get("settlement")
                    if settlement and settlement not in settlement_names:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                code="unknown_union_member",
                                message=f"Union member settlement '{settlement}' is not present in settlements.yaml.",
                                path=str(document.path),
                            )
                        )

        if document.path.parent.name == "contracts" and isinstance(data, dict):
            for contract in data.get("contracts", []):
                settlement = contract.get("settlement")
                if settlement and settlement not in settlement_names:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="unknown_contract_settlement",
                            message=f"Contract references unknown settlement '{settlement}'.",
                            path=str(document.path),
                        )
                    )
                consequences = contract.get("consequences", {})
                success = consequences.get("success", {}) if isinstance(consequences, dict) else {}
                unlocks = success.get("unlocks") or []
                for unlock_id in unlocks if isinstance(unlocks, list) else []:
                    if unlock_id not in contract_ids:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                code="unknown_contract_unlock",
                                message=f"Contract unlock target '{unlock_id}' was not found in the authored contract pool.",
                                path=str(document.path),
                            )
                        )

    return issues


def build_preview() -> DataPreviewResponse:
    ensure_state_layout()
    documents = [load_yaml_document(path) for path in _iter_yaml_files()]
    issues = validate_documents(documents)
    summaries = [
        DataDocumentSummary(
            path=str(document.path.relative_to(DATA_DIR.parent)),
            sha256=document.sha256,
            top_level_keys=_top_level_keys(document.data),
            settlement_refs=_count_settlement_refs(document.data),
            contract_refs=_count_contract_refs(document.data),
            parse_mode=document.parse_mode,
        )
        for document in documents
    ]

    manifest_payload = {
        "tool": "RIMEVEGR-TIME-MANAGER",
        "tracked_documents": [
            {"path": summary.path, "sha256": summary.sha256, "parse_mode": summary.parse_mode}
            for summary in summaries
        ],
        "issue_count": len(issues),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return DataPreviewResponse(
        document_count=len(summaries),
        documents=summaries,
        issues=issues,
        manifest_path=str(MANIFEST_PATH),
    )
