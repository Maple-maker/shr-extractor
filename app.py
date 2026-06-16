"""
app.py — SHR Extractor web interface

Upload a Sub Hand Receipt PDF, get back CSV + JSON of all property records.
"""

import io
import json
import os
import tempfile

from flask import Flask, jsonify, render_template, request, Response, session

from extract_shr import parse_shr_pdf, to_csv, to_csv_aggregated, aggregate_records

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shr-extractor-dev')

# Store last extraction in-process (single-user tool; no persistence needed)
_last_records = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    global _last_records

    if 'pdf' not in request.files or request.files['pdf'].filename == '':
        return render_template('index.html', error="No file selected.")

    f = request.files['pdf']
    if not f.filename.lower().endswith('.pdf'):
        return render_template('index.html', error="File must be a PDF.")

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name

    try:
        records = parse_shr_pdf(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        return render_template('index.html', error=f"Extraction failed: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    _last_records = records
    agg = aggregate_records(records)
    return render_template('results.html', records=agg, raw_count=len(records), count=len(agg))


@app.route('/download/csv')
def download_csv():
    if not _last_records:
        return "No data. Upload a PDF first.", 400
    csv_data = to_csv_aggregated(_last_records)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=shr_extract.csv'}
    )


@app.route('/download/csv/full')
def download_csv_full():
    if not _last_records:
        return "No data. Upload a PDF first.", 400
    csv_data = to_csv(_last_records)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=shr_extract_full.csv'}
    )


@app.route('/download/json')
def download_json():
    if not _last_records:
        return "No data. Upload a PDF first.", 400
    return Response(
        json.dumps(_last_records, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=shr_extract.json'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
