"""
ktu_repo.py
-----------
Search KTU question papers and fetch paper details (course code, exam session
like "December 2025", PDF URL) directly from the source DSpace repository.

Source of truth: the public DSpace digital library used by KTUSPOT-style sites
(Jyothi Engineering College repository). We harvest it ONCE via OAI-PMH into a
local SQLite index, then search instantly offline. Re-run harvest() periodically
(e.g. daily cron) to pick up newly uploaded papers.

This is the same idea behind the "search_cache" you saw on ktuspot.in:
harvest -> index -> serve fast.
"""

from __future__ import annotations
import re
import sqlite3
import time
import html
from dataclasses import dataclass, asdict
from typing import Optional
from xml.etree import ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ----------------------------------------------------------------------------- config
REPO_HOST   = "http://202.88.225.92"           # DSpace host (change if it moves)
XMLUI       = f"{REPO_HOST}/xmlui"
OAI_URL     = f"{REPO_HOST}/oai/request"
DB_PATH     = "ktu_index.db"
USER_AGENT  = "Mozilla/5.0 (compatible; KTUPaperBot/1.0)"

# ----------------------------------------------------------------------------- http session with retries
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(total=5, backoff_factor=1.5,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"])
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

SESSION = make_session()

# ----------------------------------------------------------------------------- parsing helpers
MONTHS = ("JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|"
          "SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER")
_SESSION_RE = re.compile(rf'\b({MONTHS})\b[\s,./-]*([0-9]{{4}})', re.I)
_COURSE_RE  = re.compile(r'\b([A-Z]{2,6})\s*0?\s*([0-9]{3}[A-Z]?)\b')  # supports 2019 (MAT101) & 2024 (GAMAT101) schemes

def parse_session(title: str):
    """Return (month, year, 'Month Year') extracted from the paper title."""
    m = _SESSION_RE.search(title or "")
    if not m:
        return None, None, None
    month = m.group(1).title()
    year = int(m.group(2))
    return month, year, f"{month} {year}"

def parse_course_code(title: str) -> Optional[str]:
    """Return a normalised course code like 'MAT101' / 'CST201' if present."""
    m = _COURSE_RE.search((title or "").upper())
    return (m.group(1) + m.group(2)) if m else None

# ----------------------------------------------------------------------------- data model
@dataclass
class Paper:
    handle: str            # e.g. "1/8891"
    title: str
    course_code: Optional[str]
    exam_month: Optional[str]
    exam_year: Optional[int]
    exam_session: Optional[str]   # "December 2025"
    item_url: str          # human page
    pdf_url: Optional[str] # direct bitstream (resolved lazily)

    def to_dict(self):
        return asdict(self)

# ----------------------------------------------------------------------------- DB
def _connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS papers(
        handle TEXT PRIMARY KEY,
        title TEXT,
        course_code TEXT,
        exam_month TEXT,
        exam_year INTEGER,
        exam_session TEXT,
        item_url TEXT,
        pdf_url TEXT
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_course ON papers(course_code)")
    con.commit()
    return con

# ----------------------------------------------------------------------------- harvest (OAI-PMH)
_OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/",
           "dc":  "http://purl.org/dc/elements/1.1/",
           "od":  "http://www.openarchives.org/OAI/2.0/oai_dc/"}

def harvest(max_pages: int | None = None, sleep: float = 0.5) -> int:
    """Harvest all records via OAI-PMH into the local SQLite index.
    Returns number of records stored. Safe to re-run (upserts)."""
    con = _connect()
    url = f"{OAI_URL}?verb=ListRecords&metadataPrefix=oai_dc"
    stored, pages = 0, 0
    while url:
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        for rec in root.findall(".//oai:record", _OAI_NS):
            oai_id = rec.findtext(".//oai:identifier", default="", namespaces=_OAI_NS)
            # oai:localhost:1/8891  ->  handle "1/8891"
            handle = oai_id.split(":")[-1] if oai_id else ""
            dc = rec.find(".//od:dc", _OAI_NS)
            if not handle or dc is None:
                continue
            title = (dc.findtext("dc:title", default="", namespaces=_OAI_NS) or "").strip()
            if not title:
                continue
            month, year, sess = parse_session(title)
            p = Paper(handle=handle, title=title,
                      course_code=parse_course_code(title),
                      exam_month=month, exam_year=year, exam_session=sess,
                      item_url=f"{XMLUI}/handle/{handle}", pdf_url=None)
            con.execute("""INSERT INTO papers
                (handle,title,course_code,exam_month,exam_year,exam_session,item_url,pdf_url)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(handle) DO UPDATE SET
                title=excluded.title, course_code=excluded.course_code,
                exam_month=excluded.exam_month, exam_year=excluded.exam_year,
                exam_session=excluded.exam_session, item_url=excluded.item_url""",
                (p.handle, p.title, p.course_code, p.exam_month, p.exam_year,
                 p.exam_session, p.item_url, None))
            stored += 1
        con.commit()
        pages += 1
        # follow resumptionToken for next page
        token_el = root.find(".//oai:resumptionToken", _OAI_NS)
        token = token_el.text if token_el is not None else None
        if token and (max_pages is None or pages < max_pages):
            url = f"{OAI_URL}?verb=ListRecords&resumptionToken={token}"
            time.sleep(sleep)
        else:
            url = None
    con.close()
    return stored

# ----------------------------------------------------------------------------- search
def search(query: str, year: int | None = None, limit: int = 50,
           dedupe: bool = True) -> list[dict]:
    """Search the local index by course code or any keyword in the title.
    Optionally filter by exam year. Newest papers first.

    dedupe=True collapses duplicate uploads of the same paper
    (same course_code + exam_session) that exist in the repository,
    keeping the first handle. Set dedupe=False to see every raw item.
    """
    con = _connect()
    q = f"%{query.strip()}%"
    sql = ("SELECT handle,title,course_code,exam_month,exam_year,exam_session,"
           "item_url,pdf_url FROM papers "
           "WHERE (course_code LIKE ? OR title LIKE ?)")
    args = [q, q]
    if year:
        sql += " AND exam_year = ?"
        args.append(year)
    sql += " ORDER BY exam_year DESC, title"
    rows = con.execute(sql, args).fetchall()
    con.close()
    cols = ["handle","title","course_code","exam_month","exam_year",
            "exam_session","item_url","pdf_url"]
    results = [dict(zip(cols, r)) for r in rows]

    if dedupe:
        seen, unique = set(), []
        for r in results:
            # key on course_code+session when known, else fall back to title
            key = (r["course_code"], r["exam_session"]) if r["course_code"] and r["exam_session"] else (r["title"],)
            if key in seen:
                continue
            seen.add(key)
            unique.append(r)
        results = unique

    return results[:limit]

# ----------------------------------------------------------------------------- resolve PDF url (lazy)
def resolve_pdf_url(handle: str) -> Optional[str]:
    """Fetch the item page and extract the real PDF bitstream URL. Cached in DB."""
    con = _connect()
    cached = con.execute("SELECT pdf_url FROM papers WHERE handle=?", (handle,)).fetchone()
    if cached and cached[0]:
        con.close()
        return cached[0]
    r = SESSION.get(f"{XMLUI}/handle/{handle}", timeout=60)
    links = re.findall(r'(/xmlui/bitstream/handle/[^"\']+?\?sequence=\d+)', r.text)
    pdf_url = None
    for l in links:
        if l.lower().split("?")[0].endswith(".pdf"):
            pdf_url = REPO_HOST + html.unescape(l)
            break
    if not pdf_url and links:                      # fall back to first bitstream
        pdf_url = REPO_HOST + html.unescape(links[0])
    if pdf_url:
        con.execute("UPDATE papers SET pdf_url=? WHERE handle=?", (pdf_url, handle))
        con.commit()
    con.close()
    return pdf_url

# ----------------------------------------------------------------------------- download (server-side proxy)
def download_pdf(pdf_url: str) -> bytes:
    """Download raw PDF bytes server-side (bypasses browser CORS / http issues)."""
    r = SESSION.get(pdf_url, timeout=120)
    r.raise_for_status()
    return r.content


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) > 1 and sys.argv[1] == "harvest":
        print("Harvesting OAI-PMH... (this takes a few minutes the first time)")
        n = harvest()
        print(f"Stored/updated {n} records into {DB_PATH}")
    else:
        q = sys.argv[1] if len(sys.argv) > 1 else "MAT101"
        results = search(q, limit=10)
        print(json.dumps(results, indent=2, ensure_ascii=False))
