"""
hkf_ltr_excel_handle.py  (v2 - xu ly file xlsx "ban")
-----------------------------------------------------
File xlsx tu portal HKF co alignment khong hop le (vd horizontal="right middle")
khien openpyxl / NPOI / ClosedXML deu chet khi doc stylesheet.

Cach xu ly: doc truc tiep cac XML ben trong file xlsx (file zip), KHONG qua stylesheet.
- Lay sharedStrings.xml (bang chuoi chung)
- Lay sheet "장기신규" (tim qua workbook.xml + rels), doc cell theo dong
=> Khong dung openpyxl de load style nua, nen khong dinh loi alignment.

Ghi ra CSV (nguyen bang, KHONG loc). Phan loc "세납" giu nguyen o Invoke Code UiPath.

Goi: python hkf_ltr_excel_handle.py "<input_xlsx>|<output_csv>"
Chi dung thu vien chuan cua Python (zipfile, xml) -> khong can pandas/openpyxl.
"""

import sys
import csv
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
SHEET_NAME = "장기신규"


def col_to_index(cell_ref):
    """VD 'B5' -> 1 (0-based cot). Bo phan so, chi lay chu."""
    letters = ""
    for ch in cell_ref:
        if ch.isalpha():
            letters += ch
        else:
            break
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    parts = arg.split("|")
    if len(parts) < 2:
        raise ValueError("Can: <input_xlsx>|<output_csv>. Nhan: " + arg)
    input_file = parts[0].strip()
    output_csv = parts[1].strip()

    with zipfile.ZipFile(input_file) as z:
        # 1) shared strings
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                # gom toan bo text (co the nam trong nhieu <t> neu la rich text)
                texts = [t.text or "" for t in si.iter("{%s}t" % NS["m"])]
                shared.append("".join(texts))

        # 2) tim r:id cua sheet "장기신규" trong workbook.xml
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        target_rid = None
        first_rid = None
        for sh in wb.find("m:sheets", NS).findall("m:sheet", NS):
            rid = sh.get("{%s}id" % NS["r"])
            if first_rid is None:
                first_rid = rid
            if sh.get("name") == SHEET_NAME:
                target_rid = rid
        if target_rid is None:
            target_rid = first_rid  # khong thay ten -> lay sheet dau

        # 3) map r:id -> duong dan sheet qua workbook.xml.rels
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_path = {}
        for rel in rels:
            rid_to_path[rel.get("Id")] = rel.get("Target")
        sheet_target = rid_to_path[target_rid]
        # Target thuong la dang "worksheets/sheet1.xml" (tuong doi voi thu muc xl/)
        # hoac "/xl/worksheets/sheet1.xml" (tuyet doi). Chuan hoa ve "xl/worksheets/..."
        sheet_target = sheet_target.lstrip("/")
        if not sheet_target.startswith("xl/"):
            sheet_target = "xl/" + sheet_target

        # 4) doc sheet
        sheet = ET.fromstring(z.read(sheet_target))
        rows_out = []
        sheet_data = sheet.find("m:sheetData", NS)
        for row in sheet_data.findall("m:row", NS):
            cells = {}
            max_c = -1
            for c in row.findall("m:c", NS):
                ref = c.get("r", "")
                ci = col_to_index(ref) if ref else 0
                t = c.get("t")  # type
                v = c.find("m:v", NS)
                text = ""
                if t == "s":  # shared string
                    if v is not None and v.text is not None:
                        text = shared[int(v.text)]
                elif t == "inlineStr":
                    is_el = c.find("m:is", NS)
                    if is_el is not None:
                        text = "".join(tt.text or "" for tt in is_el.iter("{%s}t" % NS["m"]))
                else:
                    if v is not None and v.text is not None:
                        text = v.text
                cells[ci] = text
                if ci > max_c:
                    max_c = ci
            row_list = [cells.get(i, "") for i in range(max_c + 1)]
            rows_out.append(row_list)

    # 5) ghi CSV (nguyen bang, co header la dong dau)
    # Chuan hoa so cot cho deu theo dong dai nhat
    width = max((len(r) for r in rows_out), default=0)
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        for r in rows_out:
            if len(r) < width:
                r = r + [""] * (width - len(r))
            w.writerow(r)

    print("ROWS=" + str(len(rows_out)))


if __name__ == "__main__":
    main()