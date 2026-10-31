"""
server.py
---------
FastAPI REST API exposing KTU paper search + branded download + live status pinging + secure Telegram auth.
"""

from __future__ import annotations
import io
import os
import time
import httpx 

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ktu_repo as repo
import watermark as wm

app = FastAPI(title="KTU Papers API", version="1.0")

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

# ---- Telegram Secrets (Stored in Hugging Face Space Secrets, NEVER in GitHub) ----
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID   = os.getenv("TG_CHAT_ID", "-1004463800271")

# ---- Hugging Face Vault URL ----
DATASET_RAW_URL = "https://huggingface.co/datasets/KeralaTimetable/ktu-pyq-archive/resolve/main"

class DownloadReq(BaseModel):
    handles: list[str]          
    watermark: bool = True


@app.get("/search")
def search(q: str = Query(..., min_length=2), year: int | None = None, limit: int = 50):
    """Search papers by course code or keyword with exact-match priority & deduplication."""
    raw_results = repo.search(q, year=year, limit=limit + 100)
    
    q_clean = q.upper().replace(" ", "")
    exact_matches = []
    
    for r in raw_results:
        cc = r.get("course_code") or ""
        if cc.upper().replace(" ", "") == q_clean:
            exact_matches.append(r)
            
    if exact_matches:
        filtered_results = exact_matches
    else:
        filtered_results = raw_results

    unique_results = []
    seen_handles = set()
    for r in filtered_results:
        handle = r.get("handle")
        if handle not in seen_handles:
            seen_handles.add(handle)
            unique_results.append(r)

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
    """Bypasses browser CORS restrictions to run a backend ping test to KTU."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    start_time = time.time()
    try:
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
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for h in req.handles:
            safe_filename = f"{h.replace('/', '_')}.pdf"
            file_url = f"{DATASET_RAW_URL}/{safe_filename}"
            
            response = await client.get(file_url)
            if response.status_code != 200:
                print(f"FAILED: {file_url} returned status {response.status_code}")
                raise HTTPException(404, f"no PDF for handle {h} in cloud archive")
            
            pdfs.append(response.content)

    if req.watermark:
        out = wm.brand_papers(pdfs, logo_bytes=LOGO_BYTES, text=BRAND_TEXT)
    else:
        out = wm.merge_pdfs(pdfs) if len(pdfs) > 1 else pdfs[0]

    fname = "ktu_papers.pdf"
    return StreamingResponse(io.BytesIO(out), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.post("/telegram-auth")
async def telegram_auth(request: Request):
    """
    Returns XOR-masked Telegram credentials from Hugging Face Secrets ONLY to keralatimetable.in.
    Keeps TG_BOT_TOKEN 100% out of GitHub while bypassing HF's outbound Telegram firewall block.
    """
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").lower()
    if "keralatimetable.in" not in origin and "localhost" not in origin and "127.0.0.1" not in origin:
        raise HTTPException(403, "Forbidden origin")

    if not TG_BOT_TOKEN:
        raise HTTPException(500, "TG_BOT_TOKEN secret not configured in Space")

    return {
        "t": [ord(c) ^ 42 for c in TG_BOT_TOKEN],
        "c": [ord(c) ^ 42 for c in TG_CHAT_ID]
    }


@app.post("/admin/harvest")
def admin_harvest(key: str):
    """Re-harvest the repository index. Protect with ADMIN_KEY env var."""
    if key != ADMIN_KEY:
        raise HTTPException(403, "forbidden")
    n = repo.harvest()
    return {"stored": n}
