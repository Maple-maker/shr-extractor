from dashboard_records import normalize_extractor_records


def test_normalize_extractor_records_populates_dashboard_fields():
    records = [
        {
            "unit": "HHC 1-23 IN",
            "date": "2026-06-15",
            "lin": "A12345",
            "mpo_description": "RIFLE 5.56MM M4",
            "nsn": "1005-01-231-0973",
            "nsn_description": "CARBINE",
            "oh_qty": "2",
            "serial_number": "W1234567",
        }
    ]

    normalized = normalize_extractor_records(records)

    assert normalized == [
        {
            "record_key": "serial:W1234567",
            "unit": "HHC 1-23 IN",
            "date": "2026-06-15",
            "lin": "A12345",
            "mpo_description": "RIFLE 5.56MM M4",
            "nsn": "1005-01-231-0973",
            "nsn_description": "CARBINE",
            "oh_qty": "2",
            "serial_number": "W1234567",
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
            "is_new": False,
            "is_missing_from_latest": False,
            "merge_confidence": "serial_number",
        }
    ]


def test_normalize_extractor_records_uses_conservative_fallback_for_blank_serials():
    records = [
        {
            "unit": "B CO",
            "date": "2026-06-15",
            "lin": "B54321",
            "mpo_description": "NIGHT VISION DEVICE",
            "nsn": "5855-01-246-8275",
            "nsn_description": "AN/PVS-14",
            "oh_qty": "1",
            "serial_number": "   ",
        },
        {
            "unit": "B CO",
            "date": "2026-06-15",
            "lin": "B54321",
            "mpo_description": "NIGHT VISION DEVICE",
            "nsn": "5855-01-246-8275",
            "nsn_description": "AN/PVS-14",
            "oh_qty": "1",
            "serial_number": "",
        },
    ]

    normalized = normalize_extractor_records(records)

    assert [item["record_key"] for item in normalized] == [
        "fallback:B54321:5855-01-246-8275:AN/PVS-14:0",
        "fallback:B54321:5855-01-246-8275:AN/PVS-14:1",
    ]
    assert all(item["serial_number"] == "" for item in normalized)
    assert all(item["merge_confidence"] == "fallback" for item in normalized)
    assert all(item["is_new"] is False for item in normalized)
    assert all(item["is_missing_from_latest"] is False for item in normalized)


def test_normalize_extractor_records_trims_values_without_changing_extractor_shape():
    records = [
        {
            "unit": "  FSC  ",
            "date": " 2026-06-15 ",
            "lin": " C77777 ",
            "mpo_description": " TOOL KIT ",
            "nsn": " 5180-00-177-7033 ",
            "nsn_description": " GENERAL MECHANIC ",
            "oh_qty": " 4 ",
            "serial_number": " SN-42 ",
        }
    ]

    normalized = normalize_extractor_records(records)

    assert normalized[0]["unit"] == "FSC"
    assert normalized[0]["date"] == "2026-06-15"
    assert normalized[0]["lin"] == "C77777"
    assert normalized[0]["mpo_description"] == "TOOL KIT"
    assert normalized[0]["nsn"] == "5180-00-177-7033"
    assert normalized[0]["nsn_description"] == "GENERAL MECHANIC"
    assert normalized[0]["oh_qty"] == "4"
    assert normalized[0]["serial_number"] == "SN-42"
    assert normalized[0]["record_key"] == "serial:SN-42"
