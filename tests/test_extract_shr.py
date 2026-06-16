import xml.etree.ElementTree as ET

import pytest

from extract_shr import aggregate_records, parse_shr_pdf, to_csv, to_csv_aggregated, _parse_xfa_root


def test_parse_xfa_root_emits_one_record_per_unique_serial():
    root = ET.fromstring(
        """
        <xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">
          <xfa:data>
            <data>
              <IM_UNIT_DESC>B Co 1-66 AR</IM_UNIT_DESC>
              <DATE>2026-06-16</DATE>
              <IM_RECEIPT>
                <DATA>
                  <MPO_DESCR>AB1234 Rifle Rack</MPO_DESCR>
                  <RCPT_DETAIL>
                    <DATA>
                      <NSN>1005-01-234-5678</NSN>
                      <MAKTX>RIFLE 5.56MM</MAKTX>
                      <LABST>2</LABST>
                      <ID_NUM>SN-001</ID_NUM>
                      <SERNR>
                        <DATA>
                          <SERNR1>SN-001</SERNR1>
                          <SERNR2>SN-002</SERNR2>
                        </DATA>
                      </SERNR>
                    </DATA>
                  </RCPT_DETAIL>
                </DATA>
              </IM_RECEIPT>
            </data>
          </xfa:data>
        </xfa:datasets>
        """
    )

    records = _parse_xfa_root(root)

    assert records == [
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "AB1234",
            "mpo_description": "AB1234 Rifle Rack",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": "2",
            "serial_number": "SN-001",
        },
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "AB1234",
            "mpo_description": "AB1234 Rifle Rack",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": "2",
            "serial_number": "SN-002",
        },
    ]


def test_parse_xfa_root_uses_blank_serial_when_none_are_present():
    root = ET.fromstring(
        """
        <xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">
          <xfa:data>
            <data>
              <IM_UNIT_DESC>HHC</IM_UNIT_DESC>
              <DATE>2026-06-01</DATE>
              <IM_RECEIPT>
                <DATA>
                  <MPO_DESCR>CD5678 Tool Kit</MPO_DESCR>
                  <RCPT_DETAIL>
                    <DATA>
                      <NSN>5180-00-111-2222</NSN>
                      <MAKTX>TOOL KIT</MAKTX>
                      <LABST>1</LABST>
                    </DATA>
                  </RCPT_DETAIL>
                </DATA>
              </IM_RECEIPT>
            </data>
          </xfa:data>
        </xfa:datasets>
        """
    )

    records = _parse_xfa_root(root)

    assert len(records) == 1
    assert records[0]["serial_number"] == ""
    assert records[0]["lin"] == "CD5678"


@pytest.fixture
def sample_records():
    return [
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "AB1234",
            "mpo_description": "AB1234 Rifle Rack",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": "1",
            "serial_number": "SN-001",
        },
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "AB1234",
            "mpo_description": "AB1234 Rifle Rack",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": "1",
            "serial_number": "SN-002",
        },
        {
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
            "lin": "EF9012",
            "mpo_description": "EF9012 Radio",
            "nsn": "5820-01-111-2222",
            "nsn_description": "RADIO SET",
            "oh_qty": "1",
            "serial_number": "",
        },
    ]


def test_aggregate_records_groups_by_lin_and_nsn(sample_records):
    aggregated = aggregate_records(sample_records)

    assert aggregated == [
        {
            "lin": "AB1234",
            "nsn": "1005-01-234-5678",
            "nsn_description": "RIFLE 5.56MM",
            "oh_qty": 2,
            "serials": ["SN-001", "SN-002"],
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
        },
        {
            "lin": "EF9012",
            "nsn": "5820-01-111-2222",
            "nsn_description": "RADIO SET",
            "oh_qty": 1,
            "serials": [],
            "unit": "B Co 1-66 AR",
            "date": "2026-06-16",
        },
    ]


def test_to_csv_emits_current_per_serial_columns(sample_records):
    csv_output = to_csv(sample_records)

    assert "lin,mpo_description,nsn,nsn_description,oh_qty,serial_number,unit,date" in csv_output
    assert "AB1234 Rifle Rack" in csv_output
    assert "SN-002" in csv_output


def test_to_csv_aggregated_joins_serials_and_uses_grouped_qty(sample_records):
    csv_output = to_csv_aggregated(sample_records)

    assert "lin,nsn,nsn_description,oh_qty,serials,unit,date" in csv_output
    assert "SN-001, SN-002" in csv_output
    assert "AB1234,1005-01-234-5678,RIFLE 5.56MM,2" in csv_output


def test_parse_shr_pdf_falls_back_to_text_path(monkeypatch, sample_records):
    monkeypatch.setattr("extract_shr._extract_datasets_xml", lambda _: (_ for _ in ()).throw(ValueError("no_xfa")))
    monkeypatch.setattr("extract_shr._parse_text_pdf", lambda _: sample_records)

    parsed = parse_shr_pdf("dummy.pdf")

    assert parsed == sample_records


def test_parse_shr_pdf_raises_clear_error_when_no_strategy_can_extract(monkeypatch):
    monkeypatch.setattr("extract_shr._extract_datasets_xml", lambda _: (_ for _ in ()).throw(ValueError("no_xfa")))
    monkeypatch.setattr("extract_shr._parse_text_pdf", lambda _: [])

    with pytest.raises(ValueError, match="Could not extract any records from this PDF"):
        parse_shr_pdf("dummy.pdf")
