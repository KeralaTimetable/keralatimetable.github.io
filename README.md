# KTU Papers — Search, Fetch & Watermark

Working code that reproduces how `ktuspot.in` finds KTU question papers, reads
their details (course code + exam session like *"December 2025"*), and serves
them watermarked. Plug it into your website or an AI/agent.

## How it works (3 stages)

1. **Harvest** — pull every paper's metadata from the source DSpace repository
   (`202.88.225.92`) via **OAI-PMH**, store it in a local SQLite index
   (`ktu_index.db`). Run once, then on a daily cron to pick up new uploads.
   This is the "search_cache" idea — harvest once, search instantly.
2. **Search** — query the local index by course code (`MAT101`) or keyword,
   optionally filtered by exam year. Returns title, course code, exam session
   ("December 2025"), item URL.
3. **Download + Watermark** — resolve the real PDF URL from the item handle,
   download server-side, merge (if multiple), stamp your **logo + diagonal text
   watermark** on every page, return the branded PDF.

## Files
| File | Purpose |
|------|---------|
| `ktu_repo.py`   | Harvest (OAI-PMH) + SQLite index + search + resolve PDF url + download |
| `watermark.py`  | `add_watermark()`, `merge_pdfs()`, `brand_papers()` (PyMuPDF) |
| `server.py`     | FastAPI REST API — call this from your website / AI |
| `requirements.txt` | dependencies |

## Setup
```bash
pip install -r requirements.txt

# 1) build the index (first time ~ a few minutes)
python ktu_repo.py harvest

# 2) quick CLI search
python ktu_repo.py MAT101
```

## Run the API
```bash
export BRAND_TEXT="YOURSITE.IN"
export BRAND_LOGO_PATH="/path/to/your_logo.png"   # optional
export ADMIN_KEY="some-secret"
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Endpoints
```
GET  /search?q=MAT101&year=2025
POST /download   body: {"handles": ["1/8891","1/9281"], "watermark": true}  -> PDF
POST /admin/harvest?key=some-secret    # rebuild index
```

## Use from your website (JS)
```js
const r = await fetch(`https://api.yoursite.in/search?q=${code}`);
const { results } = await r.json();
// results[i] = {handle, title, course_code, exam_session, item_url, ...}

// download branded PDF
const pdf = await fetch("https://api.yoursite.in/download", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ handles: ["1/8891"], watermark: true })
}).then(x => x.blob());
```

## Use from another AI / agent (tool spec)
Expose two tools to your LLM:
- `search_papers(query, year?)` → calls `GET /search`
- `get_branded_pdf(handles[])` → calls `POST /download`, returns a download URL

The LLM picks the right `handle`s from the search results, then requests the
branded PDF. The watermarking happens automatically server-side.

## Use the library directly (no server)
```python
import ktu_repo as repo, watermark as wm

repo.harvest()                          # once
hits = repo.search("MAT101", year=2024)
url  = repo.resolve_pdf_url(hits[0]["handle"])
pdf  = repo.download_pdf(url)
logo = open("logo.png","rb").read()
branded = wm.add_watermark(pdf, logo_bytes=logo, text="YOURSITE.IN")
open("out.pdf","wb").write(branded)
```

## Watermark options (`watermark.add_watermark`)
- `logo_bytes` — PNG of your logo (stamped top-right)
- `text` — faint diagonal repeating text (e.g. your domain)
- `logo_scale`, `logo_margin`, `text_opacity`, `text_color`, `angle`

## Notes / etiquette
- The source repository is a **public** KTU/college DSpace. Harvest politely
  (the code sleeps between OAI pages) and cache results — don't hammer it.
- Respect copyright/ownership; these are official university exam papers.
- The repo host (`REPO_HOST` in `ktu_repo.py`) may change — update it if so.
