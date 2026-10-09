"""Parse the raw Ideabrowser emails into two tables.

Reads data/raw/emails/*.eml (from fetch_emails.py). Writes, private:
  data/processed/emails.csv  one row per email
  data/processed/ideas.csv   one row per idea linked in an email (featured + "more ideas")

The newsletter's template changed twice, so emails are tagged by era:
  1  2025-07-29 .. 2026-01-25  structured idea, "More ideas released today" with titles
  2  2026-01-26 .. 2026-07-27  "Also released today" (links only), market-insight sections
  3  2026-07-28 ..             chatty newsletter, "IDEA OF THE DAY" section
Ideas are identified by their ideabrowser.com/idea/<slug> link, which is stable across eras.

Usage: python projects/ideabrowser/scripts/build_table.py
"""
import csv
import email
import re
from collections import Counter
from datetime import date, timezone
from email import policy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data"
RAW = ROOT / "raw" / "emails"
OUT = ROOT / "processed"

ERA2, ERA3 = date(2026, 1, 26), date(2026, 7, 28)
INVISIBLE = re.compile(r"[​-‏͏﻿­⁠ ]+")
IDEA_URL = re.compile(r"https?://(?:www\.)?ideabrowser\.com/idea/([a-z0-9-]+)")
URL = re.compile(r"https?://\S+")
MONEY_TAG = re.compile(r"\((\$[^()]*)\)\s*$")
EXTRA_SECTION = re.compile(r"More ideas released today|Also released today", re.I)
SECTION_END = re.compile(r"^(-{10,}|━{10,}|View this idea|View [Ff]ull [Ii]dea|HIDDEN NICHE)", re.M)


def plain_text(msg):
    part = msg.get_body(("plain",))
    text = part.get_content().replace("\r\n", "\n")
    return INVISIBLE.sub(" ", text)


def era_of(d):
    return 1 if d < ERA2 else 2 if d < ERA3 else 3


def lines(text):
    return [l.strip() for l in text.splitlines() if l.strip()]


def featured_title(era, subject, text):
    ls = lines(URL.sub("", text))
    if era == 1:
        # Title is the first line that isn't the date, a heading, or a (wrapped) preheader.
        joined = "\n".join(ls)
        m = re.search(r"Idea of the Day: \w+ \d{1,2}, 20\d\d\n(.+?)\n", joined)
        if m:  # era-1 variant: preheader, then "Idea of the Day: <date>", then UPPERCASE title
            title = m.group(1)
            nxt = joined[m.end():].split("\n", 1)[0]
            if title.isupper() and nxt.isupper():  # title wrapped onto a second line
                title += " " + nxt
            return title
        for l in ls:
            if not re.fullmatch(r"\w+ \d{1,2}, 20\d\d", l):
                return l
    if era == 2:
        for i, l in enumerate(ls):
            m = re.match(r"📌\s*TODAY'S IDEA:\s*(.+)", l)
            if m:
                return m.group(1)
            if re.fullmatch(r"(📌\s*)?IDEA OF THE DAY|Idea of the Day", l) and i + 1 < len(ls):
                # From late May 2026 the heading is followed by the pitch paragraph, not a
                # title; the subject's short name is the only title the email carries.
                # A few June/July 2026 emails put the date there instead.
                if len(ls[i + 1].split()) > 20 or re.fullmatch(r"\w+ \d{1,2}, 20\d\d", ls[i + 1]):
                    return re.sub(r"^Idea of the Day:\s*", "", subject)
                return ls[i + 1]
    if era == 3:
        for i, l in enumerate(ls):
            if l == "IDEA OF THE DAY" and i + 1 < len(ls):
                return ls[i + 1]
    return ""


def extra_ideas(text):
    """(slug, title, money_tag) for ideas listed under 'More ideas' / 'Also released'."""
    m = EXTRA_SECTION.search(text)
    if not m:
        return []
    block = text[m.end():]
    end = SECTION_END.search(block)
    block = block[: end.start()] if end else block
    out = []
    for slug_m in IDEA_URL.finditer(block):
        line = URL.split(block[: slug_m.start()].rsplit("\n", 1)[-1])[-1]  # links can share a line
        title = re.sub(r"^[-•\s]+", "", line).rstrip(": ").strip()
        tag = MONEY_TAG.search(title)
        out.append((slug_m.group(1), MONEY_TAG.sub("", title).strip(), tag.group(1) if tag else ""))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    emails, ideas = [], []
    for path in sorted(RAW.glob("*.eml")):
        msg = email.message_from_bytes(path.read_bytes(), policy=policy.default)
        sent = email.utils.parsedate_to_datetime(msg["Date"]).astimezone(timezone.utc)
        era = era_of(sent.date())
        subject = str(msg["Subject"])
        text = plain_text(msg)
        extras = extra_ideas(text)
        extra_slugs = {s for s, _, _ in extras}

        slugs = IDEA_URL.findall(text)
        featured = Counter(s for s in slugs if s not in extra_slugs).most_common(1)
        featured_slug = featured[0][0] if featured else ""
        title = featured_title(era, subject, text) if featured_slug or era == 3 else ""
        tag = MONEY_TAG.search(title)
        title = MONEY_TAG.sub("", title).strip()

        body = re.sub(r"[ \t]+", " ", URL.sub("", text)).strip()
        mid = path.stem.split("_", 1)[1]
        emails.append({
            "id": mid,
            "date_utc": sent.isoformat(),
            "era": era,
            "subject": subject,
            "featured_slug": featured_slug,
            "featured_title": title,
            "featured_money_tag": tag.group(1) if tag else "",
            "n_extra_ideas": len(extras),
            "word_count": len(body.split()),
            "body_text": body,
        })
        if title:  # era 3 features an idea without an /idea/ link, so its slug is blank
            ideas.append({"email_id": mid, "date_utc": sent.isoformat(), "era": era, "role": "featured",
                          "slug": featured_slug, "title": title, "money_tag": tag.group(1) if tag else ""})
        for slug, t, mt in extras:
            ideas.append({"email_id": mid, "date_utc": sent.isoformat(), "era": era, "role": "extra",
                          "slug": slug, "title": t, "money_tag": mt})

    for name, rows in (("emails.csv", emails), ("ideas.csv", ideas)):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"{len(emails)} emails, {len(ideas)} idea mentions -> {OUT}")


if __name__ == "__main__":
    main()
