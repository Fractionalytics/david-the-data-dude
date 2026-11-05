"""Download the veteran source tables into data/raw/. Rerunning skips files already there.

VA tables come from data.va.gov (VetPop2023, CC0). ACS tables come from the Census
table-based summary files, which don't need an API key.
"""
from pathlib import Path
import urllib.request

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
UA = "content-engine-research-bot/1.0 (data journalism project)"

VA = {
    "vetpop_national_1L": "wubk-nag4",
    "vetpop_period_2L": "weu6-zpb9",
    "vetpop_branch_4L": "k9dc-9an8",
    "vetpop_rank_5L": "3bpv-5eec",
    "vetpop_state_6L": "f43c-vb9n",
    "vetpop_state_period_7L": "6kr5-skza",
    "vetpop_county_9L": "jrjd-qghv",
    "vetpop_national_race_3L": "8zhc-knsi",
    "vetpop_estimates_2000_2023": "6xz6-j7yi",
}
ACS = "https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-{}.dat"
ACS_TABLES = ["b21002", "b21100"]  # b21001 returned the server's "Request Rejected" page; adult shares come from PUMS
PDFS = {
    "nsv2010_final_report.pdf": "https://www.va.gov/vetdata/docs/SurveysAndStudies/NVSSurveyFinalWeightedReport.pdf",
    "nsv2010_appendix_d.pdf": "https://www.va.gov/vetdata/docs/SurveysAndStudies/AppendixDDetailedDataTables.pdf",
    "pew_2019_veterans.pdf": "https://www.pewresearch.org/social-trends/wp-content/uploads/sites/3/2019/09/PSDT.10.09.19_veteransexperiences_full.report.pdf",
    "va_mortality_usvets_2015.pdf": "https://webharvest.gov/congress115th/20181203180213/https://www.va.gov/vetdata/docs/SpecialReports/Mortality_study_USVETS_2015_1980_2014.pdf",
    "abr_2025_intro_appendix.pdf": "https://www.benefits.va.gov/REPORTS/abr/docs/2025-introduction-appendix.pdf",
    "abr_2025_compensation.pdf": "https://www.benefits.va.gov/REPORTS/abr/docs/2025-compensation.pdf",
    "abr_2025_pension.pdf": "https://www.benefits.va.gov/REPORTS/abr/docs/2025-pension-fiduciary.pdf",
    "abr_2025_education.pdf": "https://www.benefits.va.gov/REPORTS/abr/docs/2025-education.pdf",
    "bls_vet_2026_release.htm": "https://www.bls.gov/news.release/archives/vet_04282026.htm",
}


def get(url, name):
    dest = RAW / name
    if dest.exists():
        return
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            dest.write_bytes(r.read())
        print(f"ok   {name} ({dest.stat().st_size:,} bytes)")
    except Exception as e:
        print(f"FAIL {name}: {e}")


(RAW / "cache").mkdir(parents=True, exist_ok=True)  # cache/ is gitignored: the county and PUMS files are too big to commit
for name, view in VA.items():
    folder = "cache/" if name == "vetpop_county_9L" else ""
    get(f"https://www.data.va.gov/api/views/{view}/rows.csv?accessType=DOWNLOAD", f"{folder}{name}.csv")
for t in ACS_TABLES:
    get(ACS.format(t), f"acs2024_{t}.dat")
get("https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pus.zip", "cache/acs2024_pums_csv_pus.zip")
for name, url in PDFS.items():
    get(url, name)
