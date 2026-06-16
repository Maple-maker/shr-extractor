from importlib import import_module

import pytest


def _require_module(module_name: str):
    try:
        return import_module(module_name)
    except ModuleNotFoundError as exc:
        pytest.fail(
            f"Expected module '{module_name}' to exist for dashboard work. "
            "Worker 4 added this as a contract test for a later implementation step."
        )


def test_normalization_contract():
    module = _require_module("dashboard_data")
    normalize_records = getattr(module, "normalize_records", None)
    assert callable(normalize_records), "dashboard_data.normalize_records must be implemented"

    records = [
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "AB1234",
            "mpo_description": "AB1234 Rifle Rack",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": "1",
            "serial_number": "SN-001",
        }
    ]

    normalized = normalize_records(records)

    assert len(normalized) == 1
    record = normalized[0]
    assert record["record_id"]
    assert record["unit"] == "B Co 1-66 AR"
    assert record["date"] == "2026-06-16"
    assert record["lin"] == "AB1234"
    assert record["mpo_description"] == "AB1234 Rifle Rack"
    assert record["nsn"] == "1005-01-234-5678"
    assert record["nsn_description"] == "RIFLE 5.56MM"
    assert record["oh_qty"] == "1"
    assert record["serial_number"] == "SN-001"
    assert record["assignee"] == ""
    assert record["sub_holder"] == ""
    assert record["location_area"] == ""
    assert record["location_building"] == ""
    assert record["location_room"] == ""
    assert record["location_container"] == ""
    assert record["location_notes"] == ""
    assert record["labels"] == []
    assert record["discrepancy_status"] == ""
    assert record["notes"] == ""
    assert record["last_reviewed_at"] == ""
    assert record["updated_at"] == ""
    assert record["is_new"] is False
    assert record["is_missing_from_latest"] is False
    assert record["merge_confidence"] == "high"


def test_merge_contract():
    module = _require_module("dashboard_data")
    merge_records = getattr(module, "merge_records", None)
    assert callable(merge_records), "dashboard_data.merge_records must be implemented"

    previous = [
        {
            "record_id": "sn:SN-001",
            "serial_number": "SN-001",
            "assignee": "CPT Smith",
            "notes": "Sight cracked",
            "labels": ["priority"],
            "is_new": False,
            "is_missing_from_latest": False,
            "merge_confidence": "high",
        }
    ]
    latest = [
        {
            "record_id": "sn:SN-001",
            "serial_number": "SN-001",
            "assignee": "",
            "notes": "",
            "labels": [],
            "is_new": False,
            "is_missing_from_latest": False,
            "merge_confidence": "high",
        },
        {
            "record_id": "sn:SN-002",
            "serial_number": "SN-002",
            "assignee": "",
            "notes": "",
            "labels": [],
            "is_new": False,
            "is_missing_from_latest": False,
            "merge_confidence": "high",
        },
    ]

    merged = merge_records(previous, latest)

    assert merged[0]["assignee"] == "CPT Smith"
    assert merged[0]["notes"] == "Sight cracked"
    assert merged[0]["labels"] == ["priority"]
    assert merged[1]["is_new"] is True


def test_export_contract():
    module = _require_module("dashboard_export")
    render_dashboard_html = getattr(module, "render_dashboard_html", None)
    assert callable(render_dashboard_html), "dashboard_export.render_dashboard_html must be implemented"

    html = render_dashboard_html(
        [{"record_id": "sn:SN-001", "serial_number": "SN-001", "labels": []}],
        {"generated_at": "2026-06-16T00:00:00Z"},
    )

    assert "<!DOCTYPE html>" in html
    assert "SN-001" in html
    assert "generated_at" in html
