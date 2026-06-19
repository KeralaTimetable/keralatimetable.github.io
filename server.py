"""
server.py
---------
FastAPI REST API exposing KTU paper search + branded download.
This is the layer you call from your website frontend OR from another AI / agent.
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
    allow_origins=["*"],          
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- branding config ----
BRAND_TEXT = os.getenv("BRAND_TEXT", "Downloaded from Keralatimetable.in")
LOGO_PATH  = os.getenv("BRAND_LOGO_PATH", "keralattlogo.png")     
LOGO_BYTES = open(LOGO_PATH, "rb").read() if LOGO_PATH and os.path.exists(LOGO_PATH) else None
ADMIN_KEY  = os.getenv("ADMIN_KEY", "change-me")


class DownloadReq(BaseModel):
    handles: list[str]          
    watermark: bool = True


@app.get("/search")
def search(q: str = Query(..., min_length=2), year: int | None = None, limit: int = 50):
    """Search papers by course code or keyword with exact-match priority & deduplication."""
    
    # 1. Fetch extra results so our exact matches aren't buried under partial matches
    raw_results = repo.search(q, year=year, limit=limit + 100)
    
    q_clean = q.upper().replace(" ", "")
    exact_matches = []
    
    for r in raw_results:
        cc = r.get("course_code") or ""
        if cc.upper().replace(" ", "") == q_clean:
            exact_matches.append(r)
            
    # 2. Smart Filter: If we found exact course code matches, ONLY show those.
    # Otherwise, fall back to normal search (for keyword searches like "Physics")
    if exact_matches:
        filtered_results = exact_matches
    else:
        filtered_results = raw_results

    # 3. Deduplicate: Remove identical entries if KTU uploaded the same file twice
    unique_results = []
    seen_handles = set()
    for r in filtered_results:
        handle = r.get("handle")
        if handle not in seen_handles:
            seen_handles.add(handle)
            unique_results.append(r)

    # 4. Apply the final limit
    final_results = unique_results[:limit]

    return {"query": q, "year": year, "count": len(final_results), "results": final_results}


@app.get("/paper/{prefix}/{num}")
def paper(prefix: str, num: str):
    """Get one paper's details + resolve its direct PDF url."""
    handle = f"{prefix}/{num}"
    rows = repo.search(handle, limit=1)            
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
