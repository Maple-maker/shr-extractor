"""
extract_shr.py — Sub Hand Receipt XFA PDF extractor

Army SHR PDFs are XFA dynamic forms. The actual property data lives as structured
XML in the PDF binary — no OCR needed. This module pulls that XML and returns
flat records ready for CSV/JSON export.

Usage:
    python3 extract_shr.py path/to/SHR.pdf
"""

import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any

from pypdf import PdfReader


# XFA namespaces we need to strip for clean tag matching
_NS_RE = re.compile(r'\{[^}]+\}')


def _tag(element) -> str:
    """Return local tag name without namespace."""
    return _NS_RE.sub('', element.tag)


def _text(element) -> str:
    """Return stripped text content of an element, or empty string."""
    return (element.text or '').strip()


def _extract_datasets_xml(pdf_path: str) -> str:
    """
    Pull the xfa:datasets XML chunk out of an XFA PDF.

    The XFA array is a flat list of alternating [name, stream] pairs.
    We find the 'datasets' stream which contains the actual form data.
    """
    reader = PdfReader(pdf_path)
    root = reader.trailer['/Root'].get_object()
    acroform = root['/AcroForm'].get_object()
    xfa_array = acroform['/XFA'].get_object()

    items = list(xfa_array)
    for i in range(0, len(items) - 1, 2):
        try:
            val = items[i + 1].get_object()
            if not hasattr(val, 'get_data'):
                continue
            raw = val.get_data()
            if b'xfa:datasets' in raw:
                return raw.decode('utf-8', errors='replace')
        except Exception:
            continue

    raise ValueError("No xfa:datasets block found in this PDF — is it a valid SHR?")


def parse_shr_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """
    Extract equipment records from a Sub Hand Receipt PDF.

    Returns a list of flat dicts, one per serialized item:
        {
            unit, date, lin, mpo_description,
            nsn, nsn_description, oh_qty, serial_number
        }
    """
    xml_str = _extract_datasets_xml(pdf_path)
    root = ET.fromstring(xml_str)

    # Navigate: xfa:datasets > xfa:data > data
    # We strip namespaces so we can find by local tag
    def find_tag(node, tag):
        for child in node:
            if _tag(child) == tag:
                return child
        return None

    def findall_tag(node, tag):
        return [child for child in node if _tag(child) == tag]

    # Top-level metadata
    xfa_data = find_tag(root, 'data')  # xfa:data
    data = find_tag(xfa_data, 'data')  # inner <data>

    unit = _text(find_tag(data, 'IM_UNIT_DESC')) if find_tag(data, 'IM_UNIT_DESC') is not None else ''
    date = _text(find_tag(data, 'DATE')) if find_tag(data, 'DATE') is not None else ''

    records = []

    # Each IM_RECEIPT > DATA block is one MPO (line item group)
    im_receipt = find_tag(data, 'IM_RECEIPT')
    if im_receipt is None:
        return records

    for mpo_block in findall_tag(im_receipt, 'DATA'):
        mpo_descr_el = find_tag(mpo_block, 'MPO_DESCR')
        mpo_descr = _text(mpo_descr_el) if mpo_descr_el is not None else ''
        # LIN = first 6 alphanumeric characters of MPO_DESCR
        lin = re.sub(r'[^A-Z0-9]', '', mpo_descr.upper())[:6]

        rcpt_detail = find_tag(mpo_block, 'RCPT_DETAIL')
        if rcpt_detail is None:
            continue

        for item_block in findall_tag(rcpt_detail, 'DATA'):
            nsn_el = find_tag(item_block, 'NSN')
            maktx_el = find_tag(item_block, 'MAKTX')
            labst_el = find_tag(item_block, 'LABST')
            id_num_el = find_tag(item_block, 'ID_NUM')

            nsn = _text(nsn_el) if nsn_el is not None else ''
            nsn_description = _text(maktx_el) if maktx_el is not None else ''
            oh_qty = _text(labst_el) if labst_el is not None else '0'
            primary_sn = _text(id_num_el) if id_num_el is not None else ''

            # Collect all serial numbers (SERNR block can have SERNR1/2/3)
            serials = set()
            if primary_sn:
                serials.add(primary_sn)

            sernr_block = find_tag(item_block, 'SERNR')
            if sernr_block is not None:
                for sernr_data in findall_tag(sernr_block, 'DATA'):
                    for key in ('SERNR1', 'SERNR2', 'SERNR3'):
                        el = find_tag(sernr_data, key)
                        if el is not None and _text(el):
                            serials.add(_text(el))

            if not serials:
                serials.add('')

            for sn in sorted(serials):
                records.append({
                    'unit': unit,
                    'date': date,
                    'lin': lin,
                    'mpo_description': mpo_descr,
                    'nsn': nsn,
                    'nsn_description': nsn_description,
                    'oh_qty': oh_qty,
                    'serial_number': sn,
                })

    return records


def to_csv(records: list[dict]) -> str:
    """Convert records list to CSV string."""
    if not records:
        return ''
    buf = io.StringIO()
    fieldnames = ['lin', 'mpo_description', 'nsn', 'nsn_description', 'oh_qty', 'serial_number', 'unit', 'date']
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 extract_shr.py path/to/SHR.pdf")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Extracting: {path}")
    records = parse_shr_pdf(path)
    print(f"Found {len(records)} records\n")

    # Print first 5 as preview
    for r in records[:5]:
        print(f"  LIN: {r['lin']}  NSN: {r['nsn']}  SN: {r['serial_number']}  DESC: {r['nsn_description']}")

    # Write CSV output
    out_path = path.replace('.pdf', '_extracted.csv')
    with open(out_path, 'w') as f:
        f.write(to_csv(records))
    print(f"\nCSV saved: {out_path}")
