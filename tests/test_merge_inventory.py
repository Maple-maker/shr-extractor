import unittest

from merge_inventory import merge_inventory_records


def make_imported_record(serial_number, **overrides):
    record = {
        "unit": "A CO",
        "date": "2026-06-16",
        "lin": "R12345",
        "mpo_description": "RADIO SET",
        "nsn": "5820-01-000-0001",
        "nsn_description": "Radio",
        "oh_qty": "1",
        "serial_number": serial_number,
    }
    record.update(overrides)
    return record


def make_existing_record(serial_number, **overrides):
    record = make_imported_record(serial_number)
    record.update(
        {
            "assignee": "Sgt Smith",
            "sub_holder": "1st Platoon",
            "location_area": "Motor Pool",
            "location_building": "Bldg 1",
            "location_room": "Cage 2",
            "location_container": "Rack A",
            "location_notes": "Top shelf",
            "labels": ["sensitive", "dispatch-ready"],
            "discrepancy_status": "open",
            "notes": "Pending shortage annex",
            "last_reviewed_at": "2026-06-10",
            "updated_at": "2026-06-11T10:00:00Z",
            "is_new": False,
            "is_missing_from_latest": False,
            "merge_confidence": "serial",
        }
    )
    record.update(overrides)
    return record


class MergeInventoryRecordsTests(unittest.TestCase):
    def test_matching_serial_preserves_annotations_and_clears_missing_flag(self):
        existing = [
            make_existing_record(
                "SN-001",
                notes="Commander note",
                labels=["cyclic", "priority"],
                assignee="CPT Doe",
                location_area="Vault",
                is_missing_from_latest=True,
            )
        ]
        imported = [
            make_imported_record(
                "SN-001",
                date="2026-06-20",
                oh_qty="2",
                mpo_description="RADIO SET V2",
            )
        ]

        merged = merge_inventory_records(existing, imported)

        self.assertEqual(1, len(merged))
        record = merged[0]
        self.assertEqual("SN-001", record["serial_number"])
        self.assertEqual("Commander note", record["notes"])
        self.assertEqual(["cyclic", "priority"], record["labels"])
        self.assertEqual("CPT Doe", record["assignee"])
        self.assertEqual("Vault", record["location_area"])
        self.assertEqual("2026-06-20", record["date"])
        self.assertEqual("2", record["oh_qty"])
        self.assertFalse(record["is_new"])
        self.assertFalse(record["is_missing_from_latest"])
        self.assertEqual("serial", record["merge_confidence"])

    def test_unmatched_import_is_flagged_new_with_empty_annotations(self):
        merged = merge_inventory_records([], [make_imported_record("SN-NEW")])

        self.assertEqual(1, len(merged))
        record = merged[0]
        self.assertEqual("SN-NEW", record["serial_number"])
        self.assertTrue(record["is_new"])
        self.assertFalse(record["is_missing_from_latest"])
        self.assertEqual([], record["labels"])
        self.assertEqual("", record["notes"])
        self.assertEqual("", record["assignee"])
        self.assertEqual("serial", record["merge_confidence"])

    def test_existing_item_missing_from_latest_is_retained_and_flagged(self):
        existing = [make_existing_record("SN-MISSING", notes="Keep me")]

        merged = merge_inventory_records(existing, [])

        self.assertEqual(1, len(merged))
        record = merged[0]
        self.assertEqual("SN-MISSING", record["serial_number"])
        self.assertTrue(record["is_missing_from_latest"])
        self.assertFalse(record["is_new"])
        self.assertEqual("Keep me", record["notes"])

    def test_blank_serial_uses_conservative_fallback_match(self):
        existing = [
            make_existing_record(
                "",
                lin="W12345",
                nsn="1005-01-111-1111",
                nsn_description="Rifle",
                mpo_description="RIFLE",
                notes="Blank serial note",
            )
        ]
        imported = [
            make_imported_record(
                "",
                lin="W12345",
                nsn="1005-01-111-1111",
                nsn_description="Rifle",
                mpo_description="RIFLE",
                date="2026-06-21",
            )
        ]

        merged = merge_inventory_records(existing, imported)

        self.assertEqual(1, len(merged))
        record = merged[0]
        self.assertEqual("", record["serial_number"])
        self.assertEqual("Blank serial note", record["notes"])
        self.assertFalse(record["is_new"])
        self.assertFalse(record["is_missing_from_latest"])
        self.assertEqual("fallback", record["merge_confidence"])

    def test_blank_serial_different_fallback_key_does_not_merge(self):
        existing = [
            make_existing_record(
                "",
                lin="W12345",
                nsn="1005-01-111-1111",
                nsn_description="Rifle",
                mpo_description="RIFLE",
                notes="Old blank serial",
            )
        ]
        imported = [
            make_imported_record(
                "",
                lin="W12345",
                nsn="1005-01-111-1111",
                nsn_description="Rifle",
                mpo_description="RIFLE VARIANT",
            )
        ]

        merged = merge_inventory_records(existing, imported)

        self.assertEqual(2, len(merged))
        missing_record = next(record for record in merged if record["is_missing_from_latest"])
        new_record = next(record for record in merged if record["is_new"])
        self.assertEqual("Old blank serial", missing_record["notes"])
        self.assertEqual("", new_record["notes"])
        self.assertEqual("fallback", missing_record["merge_confidence"])
        self.assertEqual("fallback", new_record["merge_confidence"])


if __name__ == "__main__":
    unittest.main()
