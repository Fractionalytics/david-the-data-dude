"""AFBF classic Thanksgiving dinner for 10, in the year's dollars and in October 2026
dollars (deflated by CPI-U all items, US city average, NSA, October of each year;
AFBF's volunteer shoppers price items in late October / early November).

Prices: AFBF releases (fb.org). 2022, 2025 and 2026 read on fb.org's releases;
2019-2021, 2023 and 2024 from fb.org pages via search summaries (see docs/the-case.md).

Writes data/dinner_real.csv. Run from the repo root:
python -I projects/thanksgiving-food-insecurity/scripts/dinner_real.py
"""
import csv
import json
import pathlib
import urllib.request

AFBF = {2019: 48.91, 2020: 46.90, 2021: 53.31, 2022: 64.05, 2023: 61.17, 2024: 58.08, 2025: 55.18, 2026: 58.63}
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "dinner_real.csv"


def cpi_october():
    body = json.dumps({"seriesid": ["CUUR0000SA0"], "startyear": "2019", "endyear": "2026"}).encode()
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v1/timeseries/data/",
        data=body,
        headers={"Content-type": "application/json", "User-Agent": "content-engine-research-bot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    data = res["Results"]["series"][0]["data"]
    v = {(int(d["year"]), d["period"]): float(d["value"]) for d in data if d["value"] not in ("-", "")}
    out = {yr: v[(yr, "M10")] for yr in AFBF if (yr, "M10") in v}
    # BLS never published October 2025 (the federal shutdown). Use the September-November average.
    if 2025 not in out:
        out[2025] = (v[(2025, "M09")] + v[(2025, "M11")]) / 2
    return out


def main():
    cpi = cpi_october()
    base = cpi[2026]
    rows = []
    for yr, p in AFBF.items():
        real = p * base / cpi[yr]
        rows.append((yr, p, cpi[yr], round(real, 2)))
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "afbf_nominal", "cpi_oct", "afbf_oct2026_dollars"])
        w.writerows(rows)
    print("year  nominal  Oct-2026 dollars")
    for yr, p, _, real in rows:
        print(f"{yr}  ${p:6.2f}   ${real:6.2f}")
    r = {yr: real for yr, _, _, real in rows}
    print(f"2022 -> 2026: nominal {100 * (AFBF[2026] / AFBF[2022] - 1):+.1f}%, after inflation {100 * (r[2026] / r[2022] - 1):+.1f}%")
    print(f"2019 -> 2026: nominal {100 * (AFBF[2026] / AFBF[2019] - 1):+.1f}%, after inflation {100 * (r[2026] / r[2019] - 1):+.1f}%")


if __name__ == "__main__":
    main()
