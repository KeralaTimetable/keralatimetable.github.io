"""
server.py
---------
FastAPI REST API exposing KTU paper search + branded download + live status pinging.
This is the layer you call from your website frontend OR from another AI / agent.
"""

from __future__ import annotations
import io
import os
import time  # <--- Added for tracking response latency in the status check
import httpx 

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

# ---- Hugging Face Vault URL ----
DATASET_RAW_URL = "https://huggingface.co/datasets/KeralaTimetable/ktu-pyq-archive/resolve/main"

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


@app.get("/live-ping")
async def live_ping(url: str):
    """
    🆕 Bypasses browser CORS restrictions to run an completely transparent backend ping test to KTU.
    Accurately isolates genuine 502/504 errors and SSL handshake blockages.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    start_time = time.time()
    try:
        # Using a strict 6-second max response time for live validation
        async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
            response = await client.get(url, headers=headers)
            ping_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code < 400:
                return {"status": "Online", "ping": ping_ms, "detail": "Operational"}
            else:
                return {"status": "Offline", "ping": "Error", "detail": f"HTTP {response.status_code}"}
                
    except httpx.ConnectTimeout:
        return {"status": "Offline", "ping": "Timeout", "detail": "Connection Timeout"}
    except httpx.ConnectError as e:
        # Check if the connection dropped cleanly due to local SSL verification crashes
        if "SSL" in str(e) or "certificate" in str(e):
            return {"status": "SSL Issue", "ping": "Blocked", "detail": "SSL Error"}
        return {"status": "Offline", "ping": "Error", "detail": "Network Error"}
    except Exception:
        return {"status": "Offline", "ping": "Error", "detail": "Down"}


@app.post("/download")
async def download(req: DownloadReq):
    """Download from Hugging Face + (optionally) merge + watermark the requested papers."""
    if not req.handles:
        raise HTTPException(400, "no handles provided")
    
    pdfs: list[bytes] = []
    
    # follow_redirects=True allows httpx to follow Hugging Face CDN routing
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for h in req.handles:
            # Convert JEC '1/9757' into Hugging Face '1_9757.pdf'
            safe_filename = f"{h.replace('/', '_')}.pdf"
            file_url = f"{DATASET_RAW_URL}/{safe_filename}"
            
            response = await client.get(file_url)
            if response.status_code != 200:
                print(f"FAILED: {file_url} returned status {response.status_code}")
                raise HTTPException(404, f"no PDF for handle {h} in cloud archive")
            
            pdfs.append(response.content)

    # Your custom watermark.py processes the bytes here
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
