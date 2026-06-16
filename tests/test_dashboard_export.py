import re

from dashboard_export import render_dashboard_html


def test_render_dashboard_html_embeds_bootstrap_payload_and_warning():
    html = render_dashboard_html(
        [
            {
                "record_key": "serial:SN-001",
                "serial_number": "SN-001",
                "notes": "Check cage inventory",
                "labels": ["priority"],
            }
        ],
        {"generated_at": "2026-06-16T00:00:00Z"},
    )

    assert "<!DOCTYPE html>" in html
    assert "Privacy warning" in html
    assert "embedded property book data" in html
    assert "window.__DASHBOARD_DATA__" in html
    assert '"serial_number": "SN-001"' in html
    assert '"generated_at": "2026-06-16T00:00:00Z"' in html


def test_render_dashboard_html_exposes_offline_control_hooks():
    html = render_dashboard_html([], {"generated_at": "2026-06-16T00:00:00Z"})

    assert "Save Dashboard HTML" in html
    assert "Export JSON Backup" in html
    assert "Import JSON Backup" in html
    assert "Export Inventory CSV" in html
    assert "Export Discrepancy CSV" in html
    assert "function saveDashboardHtml()" in html
    assert "function exportJsonBackup()" in html
    assert "function importJsonBackup(event)" in html
    assert 'data-field="assignee"' in html
    assert 'data-field="notes"' in html


def test_render_dashboard_html_has_no_external_asset_links():
    html = render_dashboard_html([], {"generated_at": "2026-06-16T00:00:00Z"})

    assert '<link rel="' not in html
    assert "src=\"http" not in html
    assert "href=\"http" not in html
    assert "https://" not in html
    assert "http://" not in html
    assert "fetch(" not in html
    assert "XMLHttpRequest" not in html


def test_render_dashboard_html_escapes_embedded_script_termination():
    html = render_dashboard_html(
        [{"record_key": "serial:SN-009", "notes": "</script><script>alert(1)</script>"}],
        {"generated_at": "2026-06-16T00:00:00Z"},
    )

    bootstrap_match = re.search(
        r'<script id="shr-dashboard-bootstrap" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )

    assert bootstrap_match is not None
    assert "</script><script>alert(1)</script>" not in bootstrap_match.group(1)
    assert "<\\/script><script>alert(1)<\\/script>" in bootstrap_match.group(1)


def test_render_dashboard_html_includes_accessibility_and_offline_hardening_hooks():
    html = render_dashboard_html(
        [{"record_key": "serial:SN-001", "serial_number": "SN-001", "labels": []}],
        {"generated_at": "2026-06-16T00:00:00Z"},
    )

    assert "Skip to main dashboard content" in html
    assert "prefers-reduced-motion: reduce" in html
    assert "aria-live=\"polite\"" in html
    assert "Offline-safe" in html
    assert "No network dependencies" in html
    assert "Status is labeled in text, not just color" in html
