"""
server.py
---------
FastAPI REST API exposing KTU paper search + branded download + PDF notes watermarker
+ live status pinging + secure Telegram, Gemini, Groq, OpenRouter & HF ZeroGPU Vision Brain relay.
"""

from __future__ import annotations
import base64
import io
import json
import os
import random
import time
import httpx

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ktu_repo as repo
import watermark as wm

app = FastAPI(title="KTU Papers API", version="1.4")

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

# ---- Telegram & AI Secrets (Stored in Hugging Face Space Secrets, NEVER in GitHub) ----
TG_BOT_TOKEN       = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID         = os.getenv("TG_CHAT_ID", "-1004463800271")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY       = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
HF_TOKEN           = os.getenv("HF_TOKEN", "")

# ---- Hugging Face URLs ----
DATASET_RAW_URL = "https://huggingface.co/datasets/KeralaTimetable/ktu-pyq-archive/resolve/main"

# Supports single or comma-separated Vision Brain Space URLs for load balancing
VISION_BRAIN_URLS_RAW = os.getenv(
    "VISION_BRAIN_URLS",
    "https://keralatimetable-ktu-vision-brain.hf.space/gradio_api/call/audit"
)


class DownloadReq(BaseModel):
    handles: list[str]
    watermark: bool = True


class WatermarkNotesReq(BaseModel):
    pdfs_b64: list[str]
    filename: str = "ktu_notes.pdf"


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


@app.post("/watermark-notes")
async def watermark_notes(req: WatermarkNotesReq):
    """
    Accepts uploaded PDF study notes or PPT slides (as base64) and stamps them using
    keralattlogo.png (LOGO_BYTES) and watermark.py (wm.brand_papers) on ktu-papers-api.
    """
    if not req.pdfs_b64:
        raise HTTPException(400, "No PDF files provided")

    pdfs: list[bytes] = []
    for b64_str in req.pdfs_b64:
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        pdfs.append(base64.b64decode(b64_str))

    out = wm.brand_papers(pdfs, logo_bytes=LOGO_BYTES, text=BRAND_TEXT)

    safe_name = (req.filename or "ktu_notes.pdf").replace('"', '')
    return StreamingResponse(
        io.BytesIO(out),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'}
    )


@app.post("/telegram-auth")
async def telegram_auth(request: Request):
    """
    Returns XOR-masked Telegram credentials from Hugging Face Secrets ONLY to keralatimetable.in.
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


@app.post("/gemini-auth")
async def gemini_auth(request: Request):
    """
    Returns XOR-masked Gemini, Groq, OpenRouter & HF API keys from Hugging Face Secrets ONLY to keralatimetable.in.
    Supports a single key or comma-separated multiple keys (key1,key2) for automatic load balancing.
    """
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").lower()
    if "keralatimetable.in" not in origin and "localhost" not in origin and "127.0.0.1" not in origin:
        raise HTTPException(403, "Forbidden origin")

    g_keys  = [k.strip() for k in GEMINI_API_KEY.split(",") if k.strip()]
    gr_keys = [k.strip() for k in GROQ_API_KEY.split(",") if k.strip()]
    or_keys = [k.strip() for k in OPENROUTER_API_KEY.split(",") if k.strip()]
    hf_keys = [k.strip() for k in HF_TOKEN.split(",") if k.strip()]

    if not g_keys and not gr_keys and not or_keys and not hf_keys:
        raise HTTPException(500, "No AI API keys configured in Space Secrets")

    c_gem = random.choice(g_keys) if g_keys else ""
    c_grq = random.choice(gr_keys) if gr_keys else ""
    c_ort = random.choice(or_keys) if or_keys else ""
    c_hft = random.choice(hf_keys) if hf_keys else ""

    return {
        "k": [ord(c) ^ 42 for c in c_gem],
        "g": [ord(c) ^ 42 for c in c_grq],
        "o": [ord(c) ^ 42 for c in c_ort],
        "h": [ord(c) ^ 42 for c in c_hft]
    }


@app.post("/vision-audit")
async def vision_audit(request: Request):
    """
    Authenticated Server Relay to KeralaTimetable/ktu-vision-brain (Qwen3-VL-8B on ZeroGPU).
    Rotates across comma-separated HF_TOKENs and VISION_BRAIN_URLS if multiple are provided.
    """
    payload = await request.json()
    payload_str = json.dumps(payload)

    hf_keys = [k.strip() for k in HF_TOKEN.split(",") if k.strip()]
    random.shuffle(hf_keys)
    token_candidates = hf_keys if hf_keys else [""]

    brain_urls = [u.strip() for u in VISION_BRAIN_URLS_RAW.split(",") if u.strip()]
    random.shuffle(brain_urls)

    client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")
    last_error = "Vision Brain relay failed"

    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        for api_url in brain_urls:
            for token in token_candidates:
                headers = {"Content-Type": "application/json"}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                elif client_ip:
                    headers["X-Forwarded-For"] = client_ip

                try:
                    # Step 1: Enqueue job on Gradio 5 (/gradio_api/call/audit)
                    init_res = await client.post(
                        api_url,
                        headers=headers,
                        json={"data": [payload_str]}
                    )
                    if init_res.status_code != 200:
                        last_error = f"Queue HTTP {init_res.status_code}: {init_res.text}"
                        continue

                    event_id = init_res.json().get("event_id")
                    if not event_id:
                        last_error = "Missing event_id from Vision Brain Space"
                        continue

                    # Step 2: Stream SSE result from /gradio_api/call/audit/{event_id}
                    stream_url = f"{api_url}/{event_id}"
                    sse_res = await client.get(stream_url, headers=headers)
                    if sse_res.status_code != 200:
                        last_error = f"Stream HTTP {sse_res.status_code}: {sse_res.text}"
                        continue

                    if "event: error" in sse_res.text:
                        last_error = f"ZeroGPU error/quota: {sse_res.text}"
                        continue

                    last_data_line = None
                    for line in sse_res.text.splitlines():
                        if line.startswith("data:"):
                            last_data_line = line[5:].strip()

                    if not last_data_line or last_data_line == "null":
                        last_error = "Empty stream from Vision Brain Space"
                        continue

                    parsed_arr = json.loads(last_data_line)
                    if isinstance(parsed_arr, list) and len(parsed_arr) > 0:
                        inner = parsed_arr[0]
                        if isinstance(inner, str):
                            return json.loads(inner)
                        return inner

                    return {"status": "ok", "results": parsed_arr}

                except Exception as e:
                    last_error = str(e)
                    continue

    raise HTTPException(503, f"Vision Brain busy or quota reached: {last_error}")


@app.post("/admin/harvest")
def admin_harvest(key: str):
    """Re-harvest the repository index. Protect with ADMIN_KEY env var."""
    if key != ADMIN_KEY:
        raise HTTPException(403, "forbidden")
    n = repo.harvest()
    return {"stored": n}
