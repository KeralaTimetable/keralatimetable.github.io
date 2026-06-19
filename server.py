"""
server.py
---------
FastAPI REST API exposing KTU paper search + branded download.
This is the layer you call from your website frontend OR from another AI / agent.

Endpoints (mirrors what ktuspot.in does internally):
  GET  /search?q=MAT101&year=2025      -> list of papers with details
  POST /download   {handles:[...]}     -> merged + watermarked PDF (binary)
  GET  /paper/{handle}                 -> single paper detail + resolved pdf url
  POST /admin/harvest                  -> re-harvest index (protect this!)

Run:  uvicorn server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations
import io
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ktu_repo as repo
import watermark as wm

app = FastAPI(title="KTU Papers API", version="1.0")

# allow your website's domain to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # <-- replace with your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- branding config (set these to your own) ----
BRAND_TEXT = os.getenv("BRAND_TEXT", "Downloaded from Keralatimetable.in")
LOGO_PATH  = os.getenv("BRAND_LOGO_PATH", "keralattlogo.png")     # path to your logo .png
LOGO_BYTES = open(LOGO_PATH, "rb").read() if LOGO_PATH and os.path.exists(LOGO_PATH) else None
ADMIN_KEY  = os.getenv("ADMIN_KEY", "change-me")


class DownloadReq(BaseModel):
    handles: list[str]          # e.g. ["1/8891", "1/9281"]
    watermark: bool = True


@app.get("/search")
def search(q: str = Query(..., min_length=2), year: int | None = None, limit: int = 50):
    """Search papers by course code or keyword; optional exam-year filter."""
    results = repo.search(q, year=year, limit=limit)
    return {"query": q, "year": year, "count": len(results), "results": results}


@app.get("/paper/{prefix}/{num}")
def paper(prefix: str, num: str):
    """Get one paper's details + resolve its direct PDF url."""
    handle = f"{prefix}/{num}"
    rows = repo.search(handle, limit=1)            # not ideal; do a direct lookup
    pdf_url = repo.resolve_pdf_url(handle)
    if not pdf_url:
        raise HTTPException(404, "paper not found or no PDF")
    return {"handle": handle, "pdf_url": pdf_url}


@app.post("/download")
def download(req: DownloadReq):
    """Download + (optionally) merge + watermark the requested papers."""
    if not req.handles:
        raise HTTPException(400, "no handles provided")
    pdfs: list[bytes] = []
    for h in req.handles:
        url = repo.resolve_pdf_url(h)
        if not url:
            raise HTTPException(404, f"no PDF for handle {h}")
        pdfs.append(repo.download_pdf(url))

    if req.watermark:
        out = wm.brand_papers(pdfs, logo_bytes=LOGO_BYTES, text=BRAND_TEXT)
    else:
        out = wm.merge_pdfs(pdfs) if len(pdfs) > 1 else pdfs[0]

    fname = "ktu_papers.pdf"
    return StreamingResponse(io.BytesIO(out), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.post("/admin/harvest")
def admin_harvest(key: str):
    """Re-harvest the repository index. Protect with ADMIN_KEY env var."""
    if key != ADMIN_KEY:
        raise HTTPException(403, "forbidden")
    n = repo.harvest()
    return {"stored": n}

