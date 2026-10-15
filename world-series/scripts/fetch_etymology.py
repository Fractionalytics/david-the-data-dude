"""Fetch a Wiktionary etymology for every 2026 surname (and each half of a compound surname).

Wiktionary (en.wiktionary.org, CC BY-SA 4.0) via the MediaWiki API: 50 titles per request,
sequential, identified User-Agent (approved by David 2026-10-11). Raw wikitext is cached in
data/raw/cache/wiktionary.json; spellings with no page are retried without accents.

Extraction: from each language section whose page calls the word a surname, keep the
Etymology text and the surname definition lines, with templates flattened to plain words.
Sections in the language most likely for the player's birth country come first.

Output: data/processed/etymology.json  {surname: [{"language": ..., "text": ...}, ...]}
"""
import json
import re
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests

from names import compound_parts, is_compound, surname

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "wiktionary.json"
OUT = ROOT / "data" / "processed" / "etymology.json"
API = "https://en.wiktionary.org/w/api.php"
UA = {"User-Agent": "content-engine surname research (contact: dksmith01@gmail.com)"}
MAX_CHARS = 700  # per language section


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def fetch(titles):
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = [t for t in titles if t not in cache]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        r = requests.get(API, params={
            "action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
            "titles": "|".join(batch), "redirects": 1, "format": "json", "formatversion": 2,
        }, headers=UA, timeout=120)
        r.raise_for_status()
        q = r.json()["query"]
        alias = {n["to"]: n["from"] for k in ("normalized", "redirects") for n in q.get(k, [])}
        for t in batch:
            cache.setdefault(t, None)
        for page in q["pages"]:
            if "revisions" in page:
                title = page["title"]
                src = alias.get(title, title)
                src = alias.get(src, src)
                cache[src] = page["revisions"][0]["slots"]["main"]["content"]
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        time.sleep(1)
    return cache


ETY_TEMPLATES_DROP = {"rfe", "etystub", "tree", "root", "top2", "bottom", "multiple images", "wikipedia", "wp"}


def flatten_template(body):
    parts = body.split("|")
    name = parts[0].strip().lower()
    if name in ETY_TEMPLATES_DROP:
        return ""
    gloss = [p.split("=", 1)[1] for p in parts[1:] if re.match(r"\s*(t|gloss|tr)\s*=", p)]
    pos = [p for p in parts[1:] if "=" not in p]
    words = [p for p in pos if p and not re.fullmatch(r"[a-z]{2,3}(-[a-z]{2,4})*|:[a-z]+|[a-z]{2,3}-[a-z]+", p.strip())]
    out = " ".join(w.strip() for w in words if w.strip())
    if gloss:
        out += ' ("' + "; ".join(gloss) + '")'
    if name in ("surname",):
        out = "surname " + out
    return out


def clean(text):
    for _ in range(6):
        new = re.sub(r"\{\{([^{}]*)\}\}", lambda m: flatten_template(m.group(1)), text)
        if new == text:
            break
        text = new
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<ref.*?(</ref>|/>)", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>|'''?", "", text)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n+", " ", text)).strip()


COUNTRY_LANG = {
    "USA": ["English"], "Canada": ["English", "French"], "Australia": ["English"],
    "United Kingdom": ["English"], "Bahamas": ["English"], "Japan": ["Japanese"],
    "Republic of Korea": ["Korean"], "Taiwan": ["Chinese"], "Germany": ["German"],
    "Italy": ["Italian"], "Aruba": ["Dutch", "Papiamentu", "Spanish"],
    "Curacao": ["Dutch", "Papiamentu", "Spanish"], "Slovakia": ["Slovak"],
}


def extract(wikitext):
    """[(language, text)] for language sections that describe a surname."""
    out = []
    for m in re.finditer(r"(?m)^==([^=].*?)==\s*$", wikitext):
        start = m.end()
        nxt = re.search(r"(?m)^==[^=].*?==\s*$", wikitext[start:])
        sec = wikitext[start:start + nxt.start()] if nxt else wikitext[start:]
        if "surname" not in sec.lower():
            continue
        etys = re.findall(r"(?ms)^===+\s*Etymology[^=]*=+\s*$\n(.*?)(?=^===)", sec + "\n===")
        defs = [l for l in sec.splitlines() if l.startswith("#") and not l.startswith(("#:", "#*")) and "surname" in l.lower()]
        txt = clean(" ".join(e.strip() for e in etys))
        dtxt = clean(" ".join(d.lstrip("# ") for d in defs))
        body = (f"Etymology: {txt} " if txt else "") + (f"Definitions: {dtxt}" if dtxt else "")
        if body.strip():
            out.append((m.group(1).strip(), body.strip()[:MAX_CHARS]))
    return out


def order_for(sections, country):
    pref = COUNTRY_LANG.get(country, ["Spanish", "English"])
    rank = {l: i for i, l in enumerate(pref)}
    return sorted(sections, key=lambda s: rank.get(s[0], len(pref)))


def main():
    p = pd.read_csv(ROOT / "data" / "processed" / "players_2026.csv")
    p = p[p.has_war]
    names = sorted({surname(s) for s in p.use_last_name})
    parts = sorted({w for s in names if is_compound(s) for w in compound_parts(s)})
    wanted = sorted(set(names) | set(parts))
    cache = fetch(wanted)
    retry = sorted({strip_accents(t) for t in wanted if cache.get(t) is None} - set(cache))
    cache = fetch(wanted + retry)

    out = {}
    for t in wanted:
        text = cache.get(t) or cache.get(strip_accents(t))
        out[t] = [{"language": l, "text": x} for l, x in extract(text)] if text else []
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    found = sum(bool(v) for v in out.values())
    print(f"{len(wanted)} names ({len(parts)} compound parts); page found: "
          f"{sum(bool(cache.get(t) or cache.get(strip_accents(t))) for t in wanted)}; "
          f"surname etymology extracted: {found}")


if __name__ == "__main__":
    main()
