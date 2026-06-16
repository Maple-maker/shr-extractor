from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Template


_TEMPLATE_PATH = Path(__file__).with_name("templates").joinpath("dashboard_export.html")


def render_dashboard_html(
    records: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> str:
    template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    payload = {
        "records": records,
        "metadata": _build_metadata(metadata, len(records)),
    }
    return template.render(
        bootstrap_json=_json_for_html(payload),
        generated_at=payload["metadata"]["generated_at"],
        record_count=len(records),
        title=payload["metadata"]["app_name"],
    )


def _build_metadata(metadata: dict[str, Any] | None, record_count: int) -> dict[str, Any]:
    merged = dict(metadata or {})
    merged.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    merged.setdefault("record_count", record_count)
    merged.setdefault("app_name", "SHR Command Dashboard")
    merged.setdefault("offline_mode", True)
    return merged


def _json_for_html(payload: dict[str, Any]) -> str:
    # Avoid closing the script tag if user-entered notes contain HTML-like text.
    return json.dumps(payload, indent=2, sort_keys=True).replace("</", "<\\/")
