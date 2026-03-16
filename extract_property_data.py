#!/usr/bin/env python3
"""
Extract property assessment data from VGSI for all Peacock Farm properties.
Outputs: property_data.csv, property_data.xlsx (if openpyxl available)

Fields extracted:
  parcel_id, address, owner, year_built, style, grade, stories,
  living_area_sqft, land_value, improvement_value, total_value,
  last_sale_price, last_sale_date, last_sale_book_page,
  lot_area, valuation_year, vgsi_pid, vpc_location_id
"""

import json
import re
import csv
import ssl
import time
import urllib.request
from html.parser import HTMLParser

# ── Property list ─────────────────────────────────────────────────────────────
PROPERTIES = [
    ("2 Peacock Farm Rd", "8-82"), ("3 Peacock Farm Rd", "7-91C"),
    ("4 Peacock Farm Rd", "8-83"), ("6 Peacock Farm Rd", "8-84"),
    ("8 Peacock Farm Rd", "8-85"), ("9 Peacock Farm Rd", "8-94"),
    ("10 Peacock Farm Rd", "8-86"), ("12 Peacock Farm Rd", "8-87"),
    ("15 Peacock Farm Rd", "8-93"), ("17 Peacock Farm Rd", "7-89"),
    ("18 Peacock Farm Rd", "7-10"), ("19 Peacock Farm Rd", "7-88"),
    ("22 Peacock Farm Rd", "7-22"), ("23 Peacock Farm Rd", "7-87"),
    ("24 Peacock Farm Rd", "7-23"), ("25 Peacock Farm Rd", "7-86"),
    ("26 Peacock Farm Rd", "7-24"), ("27 Peacock Farm Rd", "7-85"),
    ("28 Peacock Farm Rd", "7-25"), ("29 Peacock Farm Rd", "7-84"),
    ("30 Peacock Farm Rd", "7-26"), ("31 Peacock Farm Rd", "7-83"),
    ("32 Peacock Farm Rd", "7-27"), ("33 Peacock Farm Rd", "7-82"),
    ("34 Peacock Farm Rd", "7-28"), ("35 Peacock Farm Rd", "7-81A"),
    ("37 Peacock Farm Rd", "7-80C"), ("38 Peacock Farm Rd", "7-29"),
    ("39 Peacock Farm Rd", "7-79A"), ("40 Peacock Farm Rd", "7-30"),
    ("41 Peacock Farm Rd", "7-78"), ("42 Peacock Farm Rd", "7-31"),
    ("43 Peacock Farm Rd", "7-76"), ("45 Peacock Farm Rd", "7-75"),
    ("46 Peacock Farm Rd", "7-37"), ("47 Peacock Farm Rd", "7-74"),
    ("48 Peacock Farm Rd", "7-38"), ("49 Peacock Farm Rd", "7-73"),
    ("50 Peacock Farm Rd", "7-39"), ("51 Peacock Farm Rd", "7-72"),
    ("52 Peacock Farm Rd", "7-40"), ("53 Peacock Farm Rd", "7-71"),
    ("1 Compton Cir", "7-36"), ("3 Compton Cir", "7-35"),
    ("4 Compton Cir", "7-32"), ("5 Compton Cir", "7-34"),
    ("6 Compton Cir", "7-33"), ("1 Mason St", "8-92"),
    ("2 Mason St", "8-88"), ("4 Mason St", "8-89"),
    ("5 Mason St", "8-91"), ("4 Trotting Horse Dr", "7-11"),
    ("6 Trotting Horse Dr", "7-12"), ("7 Trotting Horse Dr", "7-21"),
    ("8 Trotting Horse Dr", "7-13"), ("10 Trotting Horse Dr", "7-14"),
    ("11 Trotting Horse Dr", "7-20"), ("12 Trotting Horse Dr", "7-15"),
    ("14 Trotting Horse Dr", "7-16"), ("15 Trotting Horse Dr", "7-19"),
    ("16 Trotting Horse Dr", "7-17"), ("17 Trotting Horse Dr", "7-18"),
    ("4 Fessenden Way", "53-49"), ("5 Fessenden Way", "53-45"),
    ("6 Fessenden Way", "53-50"), ("7 Fessenden Way", "53-44"),
    ("9 Fessenden Way", "53-43"), ("10 Fessenden Way", "53-56"),
    ("11 Fessenden Way", "53-42"), ("12 Fessenden Way", "53-57"),
    ("2 Marshall Rd", "53-40"), ("3 Marshall Rd", "53-64A"),
    ("4 Marshall Rd", "53-41"), ("5 Marshall Rd", "53-63"),
    ("7 Marshall Rd", "53-62"), ("8 Marshall Rd", "53-58"),
    ("9 Marshall Rd", "53-61"), ("10 Marshall Rd", "53-59"),
    ("11 Marshall Rd", "53-60"), ("2 Rogers Rd", "53-51"),
    ("3 Rogers Rd", "53-55"), ("4 Rogers Rd", "53-52"),
    ("5 Rogers Rd", "53-54"), ("6 Rogers Rd", "53-53"),
    ("3 Rolfe Rd", "53-47"), ("4 Rolfe Rd", "54-102"),
    ("6 Rolfe Rd", "54-103"), ("7 Rolfe Rd", "53-48"),
    ("1 Rolfe Rd", "53-31"), ("8 Rolfe Rd", "54-104"),
    ("2 Angier Rd", "77-164"), ("3 Angier Rd", "77-163"),
    ("4 Angier Rd", "77-165"), ("5 Angier Rd", "77-162"),
    ("6 Angier Rd", "77-166"), ("7 Angier Rd", "77-161"),
    ("8 Angier Rd", "82-93"), ("10 Angier Rd", "82-92"),
    ("11 Angier Rd", "77-160"), ("2 Diamond Rd", "77-142"),
    ("3 Diamond Rd", "77-172"), ("5 Diamond Rd", "77-171"),
    ("7 Diamond Rd", "77-170"), ("8 Diamond Rd", "77-178"),
    ("9 Diamond Rd", "77-169"), ("10 Diamond Rd", "77-179"),
    ("11 Diamond Rd", "77-168"), ("12 Diamond Rd", "82-99"),
    ("15 Diamond Rd", "82-98"), ("16 Diamond Rd", "82-100"),
    ("17 Diamond Rd", "82-97"), ("18 Diamond Rd", "82-101A"),
    ("351 North Emerson Rd", "82-83B"), ("352 North Emerson Rd", "77-159"),
    ("353 North Emerson Rd", "82-91"), ("355 North Emerson Rd", "82-90"),
    ("357 North Emerson Rd", "82-89"), ("358 North Emerson Rd", "82-94"),
    ("359 North Emerson Rd", "82-88"), ("360 North Emerson Rd", "82-95"),
    ("361 North Emerson Rd", "82-87"), ("362 North Emerson Rd", "82-96"),
    ("363 North Emerson Rd", "82-86"), ("365 North Emerson Rd", "82-85"),
    ("2 White Ter", "77-173"), ("3 White Ter", "77-177"),
    ("4 White Ter", "77-174"), ("5 White Ter", "77-176"),
    ("7 White Ter", "77-175"), ("5 Grove St", "77-145"),
    ("11 Grove St", "77-144"), ("60 Burlington St", "77-91"),
    ("96 Burlington St", "77-146"), ("105 Burlington St", "77-38"),
    ("4 Rumford Rd", "46-16"), ("5 Rumford Rd", "46-18"),
    ("6 Rumford Rd", "46-17"), ("7 Rumford Rd", "54-123"),
    ("8 Rumford Rd", "54-128"), ("9 Rumford Rd", "54-122"),
    ("10 Rumford Rd", "54-129"), ("11 Rumford Rd", "54-121"),
    ("12 Rumford Rd", "54-130"), ("13 Rumford Rd", "54-120"),
    ("14 Rumford Rd", "54-131"), ("15 Rumford Rd", "54-119"),
    ("16 Rumford Rd", "54-132"), ("17 Rumford Rd", "54-118"),
    ("2 Rumford Rd", "46-15"), ("4 Turning Mill Rd", "82-32"),
    ("7 Turning Mill Rd", "82-79"), ("9 Turning Mill Rd", "82-78"),
    ("11 Turning Mill Rd", "82-77"), ("12 Turning Mill Rd", "82-45"),
    ("13 Turning Mill Rd", "82-76"), ("13A Turning Mill Rd", "82-53"),
    ("14 Turning Mill Rd", "82-46"), ("15 Turning Mill Rd", "82-52"),
    ("16 Turning Mill Rd", "82-47"), ("17 Turning Mill Rd", "82-51"),
    ("18 Turning Mill Rd", "82-48"), ("19 Turning Mill Rd", "82-50A"),
    ("20 Turning Mill Rd", "82-49"), ("21 Turning Mill Rd", "86-51A"),
    ("22 Turning Mill Rd", "86-52"), ("23 Turning Mill Rd", "86-50A"),
    ("24 Turning Mill Rd", "86-53"), ("25 Turning Mill Rd", "86-49A"),
    ("26 Turning Mill Rd", "86-54"), ("27 Turning Mill Rd", "86-48A"),
    ("28 Turning Mill Rd", "86-55"), ("29 Turning Mill Rd", "86-47"),
    ("30 Turning Mill Rd", "86-56"), ("31 Turning Mill Rd", "86-31"),
    ("32 Turning Mill Rd", "86-57"), ("34 Turning Mill Rd", "86-58"),
    ("36 Turning Mill Rd", "86-10"), ("38 Turning Mill Rd", "86-11"),
    ("39 Turning Mill Rd", "86-25"), ("40 Turning Mill Rd", "86-12"),
    ("41 Turning Mill Rd", "86-24"), ("45 Turning Mill Rd", "86-18A"),
    ("46 Turning Mill Rd", "86-16"), ("47 Turning Mill Rd", "89-31"),
    ("48 Turning Mill Rd", "86-17"), ("49 Turning Mill Rd", "89-30"),
    ("50 Turning Mill Rd", "89-33"), ("51 Turning Mill Rd", "89-29"),
    ("52 Turning Mill Rd", "89-34"), ("53 Turning Mill Rd", "89-28"),
    ("54 Turning Mill Rd", "89-35"), ("55 Turning Mill Rd", "89-27"),
    ("57 Turning Mill Rd", "89-26"), ("58 Turning Mill Rd", "89-37"),
    ("59 Turning Mill Rd", "89-25"), ("60 Turning Mill Rd", "89-38"),
    ("61 Turning Mill Rd", "89-24"), ("62 Turning Mill Rd", "89-39"),
    ("64 Turning Mill Rd", "89-40"), ("65 Turning Mill Rd", "89-23"),
    ("5 Dewey Rd", "89-14"), ("8 Dewey Rd", "89-41"),
    ("10 Dewey Rd", "89-42"), ("14 Dewey Rd", "89-43"),
    ("15 Dewey Rd", "89-46"), ("16 Dewey Rd", "89-44"),
    ("3 Gould Rd", "89-51"), ("4 Gould Rd", "89-12"),
    ("5 Gould Rd", "89-50"), ("7 Gould Rd", "89-49"),
    ("8 Gould Rd", "89-19"), ("9 Gould Rd", "89-48"),
    ("10 Gould Rd", "89-20"), ("2 Grimes Rd", "86-20A"),
    ("4 Grimes Rd", "86-21"), ("5 Grimes Rd", "86-22"),
    ("6 Mason St", "8-155"), ("7 Mason St", "8-153"),
    ("8 Mason St", "8-156"), ("9 Mason St", "8-154"),
    ("11 Mason St", "14-139"), ("15 Mason St", "14-140"),
    ("17 Mason St", "14-145"), ("18 Mason St", "14-138"),
    ("19 Mason St", "14-144"), ("20 Mason St", "14-137"),
    ("21 Mason St", "14-143A"), ("22 Mason St", "14-136"),
    ("23 Mason St", "14-149"), ("24 Mason St", "14-135"),
    ("25 Mason St", "14-148"), ("26 Mason St", "14-134B"),
    ("27 Mason St", "14-147"), ("28 Mason St", "14-133B"),
    ("29 Mason St", "14-146"), ("1 White Pine Ln", "14-129"),
    ("2 White Pine Ln", "8-157"), ("3 White Pine Ln", "14-130"),
    ("4 White Pine Ln", "8-158"), ("5 White Pine Ln", "14-131"),
    ("6 White Pine Ln", "8-159"), ("7 White Pine Ln", "14-132A"),
    ("8 White Pine Ln", "8-160"), ("9 White Pine Ln", "8-162A"),
    ("10 White Pine Ln", "8-161"), ("11 White Pine Ln", "8-163C"),
    ("12 White Pine Ln", "8-164"), ("13 White Pine Ln", "8-163B"),
    ("14 White Pine Ln", "8-165"), ("64 Pleasant St", "14-56C"),
]

SEARCH_URL = "https://gis.vgsi.com/lexingtonma/async.asmx/GetDataAddress"
PARCEL_URL = "https://gis.vgsi.com/lexingtonma/Parcel.aspx?pid={pid}"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


# ── HTML text extractor ───────────────────────────────────────────────────────
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self._current = ""
        self._in_tag = False

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th", "span", "label", "div"):
            self._in_tag = True
            self._current = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th", "span", "label", "div"):
            t = self._current.strip()
            if t:
                self.texts.append(t)
            self._in_tag = False

    def handle_data(self, data):
        if self._in_tag:
            self._current += data


def get_text_after(texts, label):
    """Return the value that follows a label in the flat text list."""
    for i, t in enumerate(texts):
        if t.strip().rstrip(":") == label and i + 1 < len(texts):
            return texts[i + 1].strip()
    return ""


def dollar_to_int(s):
    return int(re.sub(r"[^0-9]", "", s)) if s else None


def lookup_pid(address):
    search = address.upper()
    for suffix in [" RD", " ST", " DR", " WAY", " CIR", " LN", " TER"]:
        if search.endswith(suffix):
            search = search[: -len(suffix)]
            break
    payload = json.dumps({"inVal": search, "src": "i_address"}).encode()
    req = urllib.request.Request(
        SEARCH_URL,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as r:
        data = json.loads(r.read())
    results = data.get("d", [])
    return results[0]["id"] if results else None


def fetch_parcel(pid):
    req = urllib.request.Request(
        PARCEL_URL.format(pid=pid),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_parcel(html):
    ex = TextExtractor()
    ex.feed(html)
    texts = [t for t in ex.texts if t]

    def after(label):
        return get_text_after(texts, label)

    # Find valuation row: look for "2026" or year near Improvements/Land/Total
    land = improvement = total = valuation_year = None
    for i, t in enumerate(texts):
        if re.match(r"20\d\d", t) and i + 3 < len(texts):
            try:
                imp = dollar_to_int(texts[i + 1])
                lnd = dollar_to_int(texts[i + 2])
                tot = dollar_to_int(texts[i + 3])
                if imp and lnd and tot and tot == imp + lnd:
                    valuation_year = t
                    improvement = imp
                    land = lnd
                    total = tot
                    break
            except Exception:
                pass

    # Sale history — find first sale (most recent)
    sale_price = sale_date = sale_book = None
    for i, t in enumerate(texts):
        if re.match(r"\d{2}/\d{2}/\d{4}", t):
            # Look back for a dollar amount and forward for book/page
            for j in range(max(0, i - 5), i):
                m = re.match(r"\$[\d,]+", texts[j])
                if m:
                    sale_price = dollar_to_int(texts[j])
                    sale_date = t
                    # Look for book/page nearby
                    for k in range(i - 5, min(len(texts), i + 5)):
                        if re.match(r"\d{4,6}/\d{4}", texts[k]):
                            sale_book = texts[k]
                    break
            if sale_price:
                break

    return {
        "owner": after("Owner"),
        "year_built": after("Year Built:") or after("Year Built"),
        "style": after("Style:") or after("Style"),
        "grade": after("Grade:") or after("Grade"),
        "stories": after("Stories:") or after("Stories"),
        "living_area_sqft": re.sub(r"[^0-9]", "", after("Living Area:") or after("Living Area")) or None,
        "land_value": land,
        "improvement_value": improvement,
        "total_value": total,
        "valuation_year": valuation_year,
        "last_sale_price": sale_price,
        "last_sale_date": sale_date,
        "last_sale_book_page": sale_book,
    }


def main():
    # Load VPC location IDs
    try:
        with open("vpc_locations.json") as f:
            vpc = json.load(f)
    except FileNotFoundError:
        vpc = {}

    total = len(PROPERTIES)
    rows = []
    failed = []

    print(f"Extracting data for {total} properties...\n")

    for i, (addr, parcel) in enumerate(PROPERTIES, 1):
        try:
            pid = lookup_pid(addr)
            if not pid:
                raise ValueError("PID not found")
            html = fetch_parcel(pid)
            data = parse_parcel(html)
            row = {
                "parcel_id": parcel,
                "address": addr,
                "city": "Lexington",
                "state": "MA",
                "vgsi_pid": pid,
                "vpc_location_id": vpc.get(parcel, ""),
                "owner": data["owner"],
                "year_built": data["year_built"],
                "style": data["style"],
                "grade": data["grade"],
                "stories": data["stories"],
                "living_area_sqft": data["living_area_sqft"],
                "land_value": data["land_value"],
                "improvement_value": data["improvement_value"],
                "total_assessed_value": data["total_value"],
                "valuation_year": data["valuation_year"],
                "last_sale_price": data["last_sale_price"],
                "last_sale_date": data["last_sale_date"],
                "last_sale_book_page": data["last_sale_book_page"],
                "property_card_url": f"https://images.vgsi.com/cards/LexingtonMACards//{pid}.pdf",
                "permits_url": f"https://lexingtonma.viewpointcloud.com/locations/{vpc[parcel]}" if parcel in vpc else "",
            }
            rows.append(row)
            print(f"  [{i:3}/{total}] OK  {addr:35s} owner={data['owner'][:25]:25s} total=${data['total_value']:,}" if data['total_value'] else f"  [{i:3}/{total}] OK  {addr}")
        except Exception as e:
            print(f"  [{i:3}/{total}] ERR {addr} — {e}")
            failed.append((addr, parcel))
        time.sleep(0.2)

    # Write CSV
    if rows:
        fields = list(rows[0].keys())
        with open("property_data.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"\nCSV saved: property_data.csv ({len(rows)} rows)")

    # Write Excel if openpyxl available
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Peacock Farm Properties"
        ws.append(fields)
        for row in rows:
            ws.append([row[f] for f in fields])
        # Auto-width columns
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)
        wb.save("property_data.xlsx")
        print(f"Excel saved: property_data.xlsx")
    except ImportError:
        print("(openpyxl not installed — skipping Excel output)")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for a, p in failed:
            print(f"  {a} ({p})")


if __name__ == "__main__":
    main()
