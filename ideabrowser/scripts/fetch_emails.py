"""Download every Ideabrowser email from David's personal Gmail as raw .eml files.

Read-only: only Gmail messages.list and messages.get are called. Nothing is sent,
labeled, archived or deleted. Auth reuses the gworkspace-personal MCP server's
saved token; the refreshed access token is kept in memory and never written back.

Output (private; never published):
  data/raw/emails/<YYYY-MM-DD>_<message id>.eml
  data/raw/manifest.csv   one row per message: id, date (UTC), subject

Rerunnable: messages already on disk are skipped.

Usage: python projects/ideabrowser/scripts/fetch_emails.py
"""
import base64
import csv
import email
import email.header
import email.utils
from datetime import timezone
import json
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

QUERY = "from:notifications@mail.ideabrowser.com"
PROFILE = Path.home() / ".config/google-workspace-mcp/profiles/personal"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT = RAW / "emails"


def gmail():
    client = json.loads((PROFILE / "credentials.json").read_text())
    client = client.get("installed") or client.get("web") or client
    tokens = json.loads((PROFILE / "tokens.json").read_text())
    creds = Credentials(
        token=None,
        refresh_token=tokens["refresh_token"],
        token_uri=client["token_uri"],
        client_id=client["client_id"],
        client_secret=client["client_secret"],
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def list_ids(svc):
    ids, page = [], None
    while True:
        resp = svc.users().messages().list(
            userId="me", q=QUERY, maxResults=500, pageToken=page
        ).execute()
        ids += [m["id"] for m in resp.get("messages", [])]
        page = resp.get("nextPageToken")
        if not page:
            return ids


def fetch_raw(svc, mid):
    # Gmail caps query cost per user per minute; pace requests and wait out a 403.
    while True:
        try:
            time.sleep(0.3)
            return svc.users().messages().get(userId="me", id=mid, format="raw").execute()
        except HttpError as e:
            if e.resp.status not in (403, 429) or "rateLimitExceeded" not in str(e):
                raise
            print("  rate limited; waiting 60s")
            time.sleep(60)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svc = gmail()
    ids = list_ids(svc)
    print(f"{len(ids)} messages match {QUERY!r}")

    have = {p.stem.split("_", 1)[1]: p for p in OUT.glob("*.eml")}
    for i, mid in enumerate(ids, 1):
        if mid in have:
            continue
        msg = fetch_raw(svc, mid)
        raw = base64.urlsafe_b64decode(msg["raw"])
        dt = email.utils.parsedate_to_datetime(email.message_from_bytes(raw)["Date"])
        path = OUT / f"{dt.astimezone(timezone.utc):%Y-%m-%d}_{mid}.eml"
        path.write_bytes(raw)
        have[mid] = path
        if i % 50 == 0:
            print(f"  {i}/{len(ids)}")

    rows = []
    for mid, path in have.items():
        m = email.message_from_bytes(path.read_bytes())
        dt = email.utils.parsedate_to_datetime(m["Date"]).astimezone(timezone.utc)
        subject = str(email.header.make_header(email.header.decode_header(m["Subject"] or "")))
        rows.append((mid, dt.isoformat(), subject))
    rows.sort(key=lambda r: r[1])
    with open(RAW / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "date_utc", "subject"])
        w.writerows(rows)
    print(f"{len(rows)} emails on disk, {rows[0][1][:10]} to {rows[-1][1][:10]}")


if __name__ == "__main__":
    main()
