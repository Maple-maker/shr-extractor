# Testing

Run the regression suite from the project root:

```bash
pytest
```

Run only the current extractor regression coverage:

```bash
pytest tests/test_extract_shr.py
```

Run the future-work contract tests:

```bash
pytest tests/test_dashboard_contracts.py
```

Notes:
- `tests/test_extract_shr.py` should pass once dependencies are installed.
- `tests/test_dashboard_contracts.py` now verifies the compatibility facade for normalization, merge, and dashboard export contracts.
- `tests/test_app_dashboard_export.py` covers the Flask dashboard download route and offline export controls.
