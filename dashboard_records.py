from __future__ import annotations

from typing import Any


SOURCE_FIELDS = (
    "unit",
    "date",
    "lin",
    "mpo_description",
    "nsn",
    "nsn_description",
    "oh_qty",
    "serial_number",
)

ANNOTATION_DEFAULTS = {
    "assignee": "",
    "sub_holder": "",
    "location_area": "",
    "location_building": "",
    "location_room": "",
    "location_container": "",
    "location_notes": "",
    "labels": [],
    "discrepancy_status": "",
    "notes": "",
    "last_reviewed_at": "",
    "updated_at": "",
}

STATE_DEFAULTS = {
    "is_new": False,
    "is_missing_from_latest": False,
}


def normalize_extractor_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_records = []

    for index, record in enumerate(records):
        normalized = {field: _clean_text(record.get(field)) for field in SOURCE_FIELDS}
        serial_number = normalized["serial_number"]

        if serial_number:
            record_key = f"serial:{serial_number}"
            merge_confidence = "serial_number"
        else:
            record_key = _build_fallback_key(normalized, index)
            merge_confidence = "fallback"

        normalized_records.append(
            {
                "record_key": record_key,
                **normalized,
                **ANNOTATION_DEFAULTS,
                **STATE_DEFAULTS,
                "labels": [],
                "merge_confidence": merge_confidence,
            }
        )

    return normalized_records


def _build_fallback_key(record: dict[str, str], index: int) -> str:
    parts = (
        record["lin"] or "unknown-lin",
        record["nsn"] or "unknown-nsn",
        record["nsn_description"] or "unknown-description",
        str(index),
    )
    return "fallback:" + ":".join(parts)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
