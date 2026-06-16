# Baseline Report

Date: 2026-06-16
Branch: `codex/command-property-dashboard`
HEAD: `9897beffe993600c906052895a099cf73014c3a8`

## Scope

Establish current baseline behavior of the cloned SHR extractor app without changing product behavior.

## Project shape

- Flask entrypoint: `app.py`
- Parser and export helpers: `extract_shr.py`
- Templates: `templates/index.html`, `templates/results.html`
- Dependencies: `requirements.txt`
- Existing automated tests: none found in the clone at the time of verification

## Commands run

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
rg --files
python3 -c "import flask, pypdf, pdfplumber, cryptography; print('deps_ok')"
python3 -c "from extract_shr import parse_shr_pdf, aggregate_records, to_csv, to_csv_aggregated; print('parser_import_ok')"
python3 -c "from app import app; client = app.test_client(); html = client.get('/').get_data(as_text=True); print('status', client.get('/').status_code); print('has_title', 'SHR Extractor' in html); print('has_submit', 'Extract Property Data' in html); print('has_form', 'enctype=\"multipart/form-data\"' in html)"
python3 -c "from app import app; client = app.test_client(); \
for path in ['/download/csv','/download/csv/full','/download/json']: \
    r = client.get(path); print(path, r.status_code, r.get_data(as_text=True).strip())"
python3 app.py
python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5001/').status)"
rg -n "csv|json|send_file|render_template|parse_shr_pdf|aggregate"
```

## Observed baseline behavior

- Dependency imports succeeded using the current Python environment.
- Parser imports succeeded:
  - `parse_shr_pdf`
  - `aggregate_records`
  - `to_csv`
  - `to_csv_aggregated`
- Flask app booted successfully in debug mode on `http://127.0.0.1:5001`.
- Upload page rendered successfully:
  - test client returned `200`
  - page contains `SHR Extractor`
  - page contains `Extract Property Data`
  - page contains a multipart upload form
- A live localhost request to `http://127.0.0.1:5001/` returned `200`.

## Export paths represented in the codebase

- Aggregated CSV route: `/download/csv`
- Full per-serial CSV route: `/download/csv/full`
- JSON route: `/download/json`
- Results template exposes all three download actions.

## Guard behavior without uploaded data

Before any PDF upload, all export routes return `400` with:

`No data. Upload a PDF first.`

This applies to:

- `/download/csv`
- `/download/csv/full`
- `/download/json`

## Notes

- No automated test suite exists yet, so baseline verification is currently smoke-test based.
- Runtime emitted a `CryptographyDeprecationWarning` from `pypdf` referencing `ARC4`; this did not block imports or app boot.
