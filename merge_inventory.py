from __future__ import annotations

from copy import deepcopy


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

ANNOTATION_FIELDS = tuple(ANNOTATION_DEFAULTS.keys())


def merge_inventory_records(existing_records: list[dict], imported_records: list[dict]) -> list[dict]:
    serial_matches = {
        _normalized_serial(record["serial_number"]): record
        for record in existing_records
        if _normalized_serial(record.get("serial_number"))
    }
    fallback_matches = {
        _fallback_key(record): record
        for record in existing_records
        if not _normalized_serial(record.get("serial_number")) and _fallback_key(record)
    }
    matched_existing_ids: set[int] = set()
    merged_records: list[dict] = []

    for imported in imported_records:
        serial_number = _normalized_serial(imported.get("serial_number"))
        if serial_number and serial_number in serial_matches:
            existing = serial_matches[serial_number]
            matched_existing_ids.add(id(existing))
            merged_records.append(_merge_matched_record(existing, imported, "serial"))
            continue

        fallback_key = _fallback_key(imported)
        if not serial_number and fallback_key and fallback_key in fallback_matches:
            existing = fallback_matches[fallback_key]
            matched_existing_ids.add(id(existing))
            merged_records.append(_merge_matched_record(existing, imported, "fallback"))
            continue

        merged_records.append(_build_new_record(imported))

    for existing in existing_records:
        if id(existing) in matched_existing_ids:
            continue
        merged_records.append(_build_missing_record(existing))

    return merged_records


def _merge_matched_record(existing: dict, imported: dict, merge_confidence: str) -> dict:
    merged = deepcopy(imported)
    _apply_annotation_defaults(merged)
    for field in ANNOTATION_FIELDS:
        merged[field] = deepcopy(existing.get(field, ANNOTATION_DEFAULTS[field]))
    merged["is_new"] = False
    merged["is_missing_from_latest"] = False
    merged["merge_confidence"] = merge_confidence
    return merged


def _build_new_record(imported: dict) -> dict:
    record = deepcopy(imported)
    _apply_annotation_defaults(record)
    record["is_new"] = True
    record["is_missing_from_latest"] = False
    record["merge_confidence"] = "serial" if _normalized_serial(record.get("serial_number")) else "fallback"
    return record


def _build_missing_record(existing: dict) -> dict:
    record = deepcopy(existing)
    _apply_annotation_defaults(record)
    record["is_new"] = False
    record["is_missing_from_latest"] = True
    record["merge_confidence"] = "serial" if _normalized_serial(record.get("serial_number")) else "fallback"
    return record


def _apply_annotation_defaults(record: dict) -> None:
    for field, default in ANNOTATION_DEFAULTS.items():
        if field not in record:
            record[field] = deepcopy(default)


def _normalized_serial(serial_number: str | None) -> str:
    return (serial_number or "").strip()


def _fallback_key(record: dict) -> tuple[str, str, str, str]:
    return (
        (record.get("lin") or "").strip(),
        (record.get("nsn") or "").strip(),
        (record.get("nsn_description") or "").strip(),
        (record.get("mpo_description") or "").strip(),
    )
