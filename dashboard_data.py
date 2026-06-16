from __future__ import annotations

from copy import deepcopy
from typing import Any

from dashboard_records import normalize_extractor_records
from merge_inventory import merge_inventory_records


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compatibility facade for earlier dashboard_data contract tests."""
    normalized = normalize_extractor_records(records)
    return [_with_legacy_contract(record) for record in normalized]


def merge_records(
    previous_records: list[dict[str, Any]],
    latest_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = merge_inventory_records(previous_records, latest_records)
    return [_with_legacy_contract(record) for record in merged]


def _with_legacy_contract(record: dict[str, Any]) -> dict[str, Any]:
    compatible = deepcopy(record)
    record_key = compatible.get("record_key") or compatible.get("record_id") or _record_key_for(compatible)
    compatible.setdefault("record_key", record_key)
    compatible["record_id"] = _legacy_record_id(record_key)
    compatible["merge_confidence"] = _legacy_merge_confidence(compatible.get("merge_confidence"))
    return compatible


def _record_key_for(record: dict[str, Any]) -> str:
    serial_number = (record.get("serial_number") or "").strip()
    if serial_number:
        return f"serial:{serial_number}"
    return "fallback:" + ":".join(
        [
            (record.get("lin") or "unknown-lin").strip(),
            (record.get("nsn") or "unknown-nsn").strip(),
            (record.get("nsn_description") or "unknown-description").strip(),
        ]
    )


def _legacy_record_id(record_key: str) -> str:
    if record_key.startswith("serial:"):
        return "sn:" + record_key.removeprefix("serial:")
    return record_key


def _legacy_merge_confidence(value: Any) -> str:
    if value in {"serial", "serial_number", "high"}:
        return "high"
    if value in {"fallback", "low"}:
        return "low"
    return str(value or "low")
