import unittest

import app as shr_app


class DashboardExportRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = shr_app.app.test_client()
        shr_app._last_records = []

    def tearDown(self):
        shr_app._last_records = []

    def test_dashboard_download_requires_prior_extraction(self):
        response = self.client.get("/download/dashboard")

        self.assertEqual(400, response.status_code)
        self.assertIn(b"No data. Upload a PDF first.", response.data)

    def test_dashboard_download_returns_self_contained_html_attachment(self):
        shr_app._last_records = [
            {
                "unit": "A CO",
                "date": "2026-06-16",
                "lin": "A12345",
                "mpo_description": "RIFLE 5.56MM M4",
                "nsn": "1005-01-231-0973",
                "nsn_description": "CARBINE",
                "oh_qty": "1",
                "serial_number": "SN-001",
            }
        ]

        response = self.client.get("/download/dashboard")

        self.assertEqual(200, response.status_code)
        self.assertEqual("text/html; charset=utf-8", response.content_type)
        self.assertIn("attachment; filename=shr_command_dashboard.html", response.headers["Content-Disposition"])
        body = response.get_data(as_text=True)
        self.assertIn("SHR Command Dashboard", body)
        self.assertIn('"record_key": "serial:SN-001"', body)
        self.assertIn('"serial_number": "SN-001"', body)
        self.assertIn("window.__DASHBOARD_DATA__", body)
        self.assertNotIn("https://", body)
        self.assertNotIn("http://", body)

    def test_dashboard_download_includes_local_persistence_and_export_controls(self):
        shr_app._last_records = [
            {
                "unit": "A CO",
                "date": "2026-06-16",
                "lin": "A12345",
                "mpo_description": "RIFLE 5.56MM M4",
                "nsn": "1005-01-231-0973",
                "nsn_description": "CARBINE",
                "oh_qty": "1",
                "serial_number": "SN-001",
            }
        ]

        response = self.client.get("/download/dashboard")

        self.assertEqual(200, response.status_code)
        body = response.get_data(as_text=True)
        self.assertIn("Save Dashboard HTML", body)
        self.assertIn("Export JSON Backup", body)
        self.assertIn("Import JSON Backup", body)
        self.assertIn("Export Inventory CSV", body)
        self.assertIn("Export Discrepancies CSV", body)
        self.assertIn("function saveDashboardHtml()", body)
        self.assertIn("function exportJsonBackup()", body)
        self.assertIn("function importJsonBackup(event)", body)
        self.assertIn("function exportInventoryCsv()", body)
        self.assertIn("function exportDiscrepancyCsv()", body)
        self.assertIn('data-field="assignee"', body)
        self.assertIn('data-field="notes"', body)


if __name__ == "__main__":
    unittest.main()
