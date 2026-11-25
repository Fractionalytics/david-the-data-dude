"""Low-end earnings vs prices: BLS usual weekly earnings of full-time workers
by percentile (CPS, quarterly), Q3 2022 vs Q3 2026, deflated by the CPI's
Q3 average; plus unemployment in October of each year.

Only full-time wage earners are covered. Part-time workers, the jobless and
retirees are not, and many SNAP households are among them.

Run from the repo root: python projects/thanksgiving-food-insecurity/scripts/fetch_low_end.py
"""
import json
import urllib.request

EARN = {
    "LEU0252911200": "Full-time weekly earnings, 10th percentile",
    "LEU0252911300": "Full-time weekly earnings, 25th percentile",
    "LEU0252881500": "Full-time weekly earnings, median",
    "LEU0252911500": "Full-time weekly earnings, 90th percentile",
}
UNEMP = {
    "LNS14000000": "Unemployment rate (%)",
    "LNS14000006": "Unemployment rate, Black (%)",
    "LNS13327709": "U-6 rate (%)",
    "LNS12032194": "Part-time for economic reasons (thousands)",
    "LNS13008636": "Unemployed 27+ weeks (thousands)",
    "LNS13025703": "Long-term unemployed share of unemployed (%)",
}
CPI = "CUUR0000SA0"


def fetch(ids):
    body = json.dumps({"seriesid": ids, "startyear": "2022", "endyear": "2026"}).encode()
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v1/timeseries/data/",
        data=body,
        headers={"Content-type": "application/json", "User-Agent": "content-engine-research-bot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if res.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS API: {res.get('status')} {res.get('message')}")
    # '-' marks months BLS never published (the October 2025 shutdown)
    return {
        s["seriesID"]: {(d["year"], d["period"]): float(d["value"]) for d in s["data"] if d["value"] not in ("-", "")}
        for s in res["Results"]["series"]
    }


def main():
    v = fetch([*EARN, *UNEMP, CPI])
    q3 = lambda y: sum(v[CPI][(y, m)] for m in ("M07", "M08", "M09")) / 3
    infl = q3("2026") / q3("2022") - 1
    print(f"CPI, Q3 2022 to Q3 2026: {100 * infl:+.1f}%")
    for sid, name in EARN.items():
        a, b = v[sid][("2022", "Q03")], v[sid][("2026", "Q03")]
        print(f"{name:45s} ${a:5.0f} -> ${b:5.0f}  nominal {100 * (b / a - 1):+5.1f}%  real {100 * (b / a / (1 + infl) - 1):+5.1f}%")
    for sid, name in UNEMP.items():
        a, b = v[sid][("2022", "M10")], v[sid][("2026", "M10")]
        print(f"{name:45s} Oct 2022 {a:>7}  Oct 2026 {b:>7}  change {b - a:+.1f}")


if __name__ == "__main__":
    main()
