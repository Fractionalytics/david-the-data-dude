"""Pull CPI components and wages from the BLS public API (v1, no key) and
compare the latest month with the same month in 2022.

Writes data/cpi_wages.csv (all months) and prints the comparison.
Run from the repo root: python projects/holiday-season-food-insecurity/scripts/fetch_cpi.py
"""
import csv
import json
import pathlib
import urllib.request

SERIES = {
    "CUUR0000SA0": "CPI all items",
    "CUUR0000SAF11": "Food at home",
    "CUUR0000SAH1": "Shelter",
    "CUUR0000SEHA": "Rent of primary residence",
    "CUUR0000SEHF01": "Electricity",
    "CUUR0000SEHF02": "Utility (piped) gas",
    "CUUR0000SETE": "Motor vehicle insurance",
    "CUUR0000SAM": "Medical care",
    "CES0500000003": "Avg hourly earnings, all private",
    "CES0500000008": "Avg hourly earnings, production & nonsupervisory",
}

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "cpi_wages.csv"


def fetch():
    body = json.dumps({"seriesid": list(SERIES), "startyear": "2022", "endyear": "2026"}).encode()
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v1/timeseries/data/",
        data=body,
        headers={"Content-type": "application/json", "User-Agent": "content-engine-research-bot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    res = fetch()
    if res.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS API: {res.get('status')} {res.get('message')}")
    rows = []
    for s in res["Results"]["series"]:
        for d in s["data"]:
            if d["period"].startswith("M") and d["period"] != "M13" and d["value"] not in ("-", ""):
                rows.append((s["seriesID"], SERIES[s["seriesID"]], int(d["year"]), int(d["period"][1:]), float(d["value"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["series_id", "name", "year", "month", "value"])
        w.writerows(sorted(rows))

    by = {}
    for sid, name, y, m, v in rows:
        by.setdefault(sid, {})[(y, m)] = v
    # Latest month every series has
    common = set.intersection(*(set(v) for v in by.values()))
    ly, lm = max(k for k in common if k[0] == 2026)
    print(f"Latest common month: {ly}-{lm:02d}, compared with 2022-{lm:02d}")
    for sid, name in SERIES.items():
        a, b = by[sid].get((2022, lm)), by[sid].get((ly, lm))
        print(f"{name:52s} {a:9.3f} -> {b:9.3f}  {100 * (b / a - 1):+6.1f}%")


if __name__ == "__main__":
    main()
