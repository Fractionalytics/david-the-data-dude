"""Download the NY Fed Household Debt and Credit data workbook (Q3 2026) into
data/raw/nyfed/. Used by docs/research/federal-surveys.md.

Run: python -I scripts/fetch_nyfed.py
"""
import pathlib
import sys
import urllib.error
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "nyfed"
UA = "content-engine-research-bot/1.0 (research bot; data journalism; low-volume downloads)"
FILES = {
    "HHD_C_Report_2026Q3.xlsx":
        "https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/HHD_C_Report_2026Q3.xlsx",
    "LSE_2026_scally-hhdc2026q3.xlsx":
        "https://libertystreeteconomics.newyorkfed.org/wp-content/uploads/sites/2/2026/11/LSE_2026_scally-hhdc2026q3.xlsx",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        dest = OUT / name
        if dest.exists():
            print("have", name)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                dest.write_bytes(r.read())
                print(r.status, name, url)
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, url, file=sys.stderr)


if __name__ == "__main__":
    main()
