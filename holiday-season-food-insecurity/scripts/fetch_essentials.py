"""CPI for essential household costs, October 2022 vs October 2026 (BLS public
API v1, not seasonally adjusted, US city average). Compare with pay at the
low end (fetch_low_end.py: 10th percentile full-time pay +13.2%).

Run from the repo root: python -I projects/holiday-season-food-insecurity/scripts/fetch_essentials.py
"""
import json
import urllib.request

SERIES = {
    "CUUR0000SA0": "All items",
    "CUUR0000SAH1": "Shelter",
    "CUUR0000SEHA": "Rent of primary residence",
    "CUUR0000SEHF01": "Electricity",
    "CUUR0000SEHF02": "Utility (piped) gas",
    "CUUR0000SEHG": "Water, sewer and trash",
    "CUUR0000SAF11": "Food at home",
    "CUUR0000SETE": "Motor vehicle insurance",
    "CUUR0000SETB01": "Gasoline (all types)",
    "CUUR0000SETG": "Public transportation",
    "CUUR0000SEME": "Health insurance",
    "CUUR0000SAM2": "Medical care services",
    "CUUR0000SEMF01": "Prescription drugs",
    "CUUR0000SEEB03": "Day care and preschool",
    "CUUR0000SEED": "Telephone services",
    "CUUR0000SEEE03": "Internet services",
}


def main():
    body = json.dumps({"seriesid": list(SERIES), "startyear": "2022", "endyear": "2026"}).encode()
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v1/timeseries/data/",
        data=body,
        headers={"Content-type": "application/json", "User-Agent": "content-engine-research-bot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if res.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS API: {res.get('status')} {res.get('message')}")
    rows = []
    for s in res["Results"]["series"]:
        v = {(d["year"], d["period"]): float(d["value"]) for d in s["data"] if d["value"] not in ("-", "")}
        a, b = v.get(("2022", "M10")), v.get(("2026", "M10"))
        if a and b:
            rows.append((100 * (b / a - 1), SERIES[s["seriesID"]], s["seriesID"]))
        else:
            print(f"{SERIES[s['seriesID']]}: missing Oct 2022 or Oct 2026")
    print("Oct 2022 -> Oct 2026")
    for pct, name, sid in sorted(rows, reverse=True):
        print(f"  {name:28s} {pct:+6.1f}%   {sid}")
    print("  (Lowest-paid 10% of full-time workers, Q3 to Q3: +13.2%)")


if __name__ == "__main__":
    main()
