"""Parse FDLE's Silver Alert "Success Stories" pages (2014-2022) into one row per story.

Input:  data/raw/recon/silver_success_<year>.html (fetched by recon5.py)
Output: data/interim/silver_success_stories.csv

Columns: year, month, county, age, sex, found_by, channel, text.
found_by / channel are keyword rules (channel "unspecified" = story just says "from the Silver Alert") over the story text; `text` is kept so every label can be checked.
The stories contain no names (age and sex only).
"""
from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / "data"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
HEAD = re.compile(rf"({MONTHS})\s+(20\d\d)\s*[—–-]+\s*([A-Za-z.' \-]+?)\s+(?:County|Parish)\b", re.I)
AGE_SEX = re.compile(r"(\d{2,3})[- ]year[- ]old (male|female|man|woman)", re.I)

# First match wins, so order matters: the subject finding themself beats "citizen", etc.
FOUND_BY = [
    ("self", r"recognized (himself|herself)|saw (his|her) (own )?(vehicle|information|name|photo)|subject of the alert (saw|heard|called)"),
    ("family", r"\b(family member|wife|husband|son|daughter|relative|grandson|granddaughter)\b.*(saw|recognized|located|found)"),
    ("citizen", r"\b(citizens?|workers?|nurse|hospital staff|motorist|driver|resident|witness|employee|clerk|attendant|passerby|truck driver|caller|good samaritan|bystander|member of the public)\b"),
    ("law_enforcement", r"\b(deputy|officer|trooper|law enforcement|sheriff|police|FHP|detective|agent|highway patrol|state patrol|license[- ]plate reader)\b"),
]
CHANNEL = [
    ("plate_reader", r"license[- ]plate reader|LPR|tag reader|plate reader"),
    ("highway_sign", r"dynamic message sign|DMS|highway sign|road sign|message board|overhead sign"),
    ("bolo_teletype", r"BOLO|be on the lookout|teletype|FCIC|NCIC"),
    ("media", r"\b(news|television|TV|radio|media|broadcast)\b"),
    ("social_media", r"facebook|twitter|social media"),
    ("text_email_alert", r"text alert|email alert|wireless emergency|cell ?phone alert|alert on (his|her) phone"),
    ("lottery", r"lottery"),
]


def classify(text, rules, default):
    for label, pattern in rules:
        if re.search(pattern, text, re.I):
            return label
    return default


rows = []
for year in range(2014, 2023):
    html = (ROOT / "raw" / "recon" / f"silver_success_{year}.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    end = text.find("Return to top")
    text = text[:end] if end > 0 else text
    heads = [m for m in HEAD.finditer(text) if m.group(2) == str(year)]
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)].strip()
        age_sex = AGE_SEX.search(body)
        sex = age_sex.group(2).lower() if age_sex else None
        rows.append({
            "year": year,
            "month": m.group(1).title(),
            "county": m.group(3).strip(),
            "age": int(age_sex.group(1)) if age_sex else None,
            "sex": {"man": "male", "woman": "female"}.get(sex, sex),
            "found_by": classify(body, FOUND_BY, "unclear"),
            "channel": classify(body, CHANNEL, "unspecified"),
            "text": body,
        })

df = pd.DataFrame(rows)
out = ROOT / "interim" / "silver_success_stories.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"{len(df)} stories -> {out}")
print(df.groupby("year").size().to_string())
print("\nfound_by:\n", df.found_by.value_counts().to_string())
print("\nchannel:\n", df.channel.value_counts().to_string())
print("\nmissing age/sex:", df.age.isna().sum(), df.sex.isna().sum())
