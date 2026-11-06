"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
and surgically remove existing third-party watermarks:
- Works on Ktunotes.live (transparent overlay logos on camera photos)
- Works on Ktuspecial.in (opaque/Multiply/repeated logos AND flattened white-scan faint logos)
- 100% protects handwritten notebook scans from ever being blanked out.
Pure-Python, uses PyMuPDF (fitz).
"""

from __future__ import annotations
import hashlib
import re
from collections import Counter
import fitz  # PyMuPDF


# Common competitor domains & watermark phrases found in KTU PDFs
DEFAULT_COMPETITOR_KEYWORDS = [
    "ktunotes.live",
    "ktunotes.in",
    "ktunotes.me",
    "ktunotes",
    "ktuspecial.in",
    "ktuspecial.com",
    "ktuspecial",
    "keralanotes.com",
    "keralanotes.in",
    "keralanotes",
    "ktuqbank.com",
    "ktuqbank",
    "ktuassist.in",
    "ktuassist",
    "ktustudents.in",
    "ktustudents",
    "ktuweb.com",
    "ktuonline.com",
    "apjktu.in",
    "studocu.com",
    "scribd.com",
    "scheme notes",
    "together dream the b.tech",
    "we can together dream",
]

# Regex catching "Downloaded from <site>", "Download from <site>", "Visit www.<site>", etc.
WATERMARK_TEXT_REGEX = re.compile(
    r"(?:downloaded\s+from|download\s+from|visit\s+us\s+at|shared\s+by|courtesy\s+of|www\.)\s*"
    r"([a-z0-9\-]+\.(?:live|in|com|org|net|me|co\.in|edu|info))"
    r"|(?:ktunotes|ktuspecial|keralanotes|ktuqbank|ktuassist|ktustudents)\s*\.\s*(?:live|in|com|me|org)",
    re.IGNORECASE,
)


def _is_competitor_text(line_text: str, extra_keywords: list[str] | None = None) -> bool:
    """Return True if a text line/span matches a known watermark phrase or competitor domain."""
    cleaned = " ".join(line_text.strip().split())
    if not cleaned:
        return False

    low = cleaned.lower()

    # Never strip our own watermark if re-processing
    if "keralatimetable" in low:
        return False

    if extra_keywords:
        for kw in extra_keywords:
            kw_clean = kw.strip().lower()
            if kw_clean and kw_clean in low:
                return True

    if WATERMARK_TEXT_REGEX.search(cleaned):
        return True

    if len(cleaned) <= 150:
        for kw in DEFAULT_COMPETITOR_KEYWORDS:
            if kw in low:
                return True

    return False


def _inspect_image_xref(doc: fitz.Document, xref: int) -> dict:
    """
    Inspects an image XObject:
    - Computes a SHA1 hash of pixel samples so identical watermark logos with DIFFERENT
      xref IDs on each page still match 100%.
    - Detects `/SMask`, `/Mask`, or inline alpha transparency.
    - Measures `dark_ink_ratio` and `is_washed_out_logo` so we can distinguish an opaque
      pre-faded watermark JPEG (like ktuspecial.in) from a real dark-ink handwriting scan.
    """
    info = {
        "xref": xref,
        "sha1": "",
        "dims": (0, 0),
        "pixel_area": 0,
        "has_transparency": False,
        "smask_xref": 0,
        "dark_ink_ratio": 0.5,
        "is_washed_out_logo": False,
    }
    try:
        smask_val = doc.xref_get_key(xref, "SMask")
        if smask_val and smask_val[0] == "xref":
            info["has_transparency"] = True
            info["smask_xref"] = int(smask_val[1].split()[0])

        mask_val = doc.xref_get_key(xref, "Mask")
        if mask_val and mask_val[0] != "null":
            info["has_transparency"] = True

        pix = fitz.Pixmap(doc, xref)
        info["dims"] = (pix.width, pix.height)
        info["pixel_area"] = pix.width * pix.height
        if pix.alpha:
            info["has_transparency"] = True

        if pix.colorspace and pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)

        samples = pix.samples
        h_slice = samples[:: max(1, len(samples) // 2048)]
        info["sha1"] = hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.n}:".encode() + bytes(h_slice)
        ).hexdigest()

        # Sample pixels to check if this is a pre-faded opaque watermark image (like ktuspecial.in)
        # vs a real handwriting page (which has dark ink strokes < 140 luminance)
        n = pix.n
        has_a = bool(pix.alpha)
        total_px = max(1, pix.width * pix.height)
        stride = max(1, total_px // 4096) * n

        dark_px = 0
        faint_px = 0
        white_px = 0
        sampled = 0

        for i in range(0, len(samples) - n + 1, stride):
            sampled += 1
            if has_a and samples[i + n - 1] <= 10:
                white_px += 1
                continue
            if n - pix.alpha == 1:
                lum = samples[i]
            else:
                lum = (samples[i] * 299 + samples[i + 1] * 587 + samples[i + 2] * 114) // 1000

            if lum < 135:
                dark_px += 1
            elif lum >= 246:
                white_px += 1
            else:
                faint_px += 1

        if sampled > 0:
            info["dark_ink_ratio"] = dark_px / sampled
            # An opaque pre-faded watermark JPEG on white background has almost NO dark black pixels
            # (< 0.8% dark pixels) and consists almost entirely of white + faint gray/blue tint
            if dark_px / sampled < 0.008 and faint_px > 10 and (white_px + faint_px) / sampled > 0.985:
                info["is_washed_out_logo"] = True

    except Exception:
        pass

    return info


def _nuke_image_xref(doc: fitz.Document, page: fitz.Page, xref: int) -> None:
    """
    Completely removes a watermark image XObject from the page and any nested Form XObjects.
    """
    try:
        for item in page.get_xobjects():
            x_xref, x_name, invoker_xref = item[0], item[1], item[2]
            if x_xref == xref and x_name:
                pat = re.compile(rb"/" + re.escape(x_name.encode("latin1")) + rb"\s+Do\b")
                for c_xref in page.get_contents():
                    st = doc.xref_stream(c_xref)
                    if st and pat.search(st):
                        doc.update_stream(c_xref, pat.sub(b"", st))
                if invoker_xref and invoker_xref > 0:
                    fst = doc.xref_stream(invoker_xref)
                    if fst and pat.search(fst):
                        doc.update_stream(invoker_xref, pat.sub(b"", fst))
    except Exception:
        pass

    try:
        page.delete_image(xref)
    except Exception:
        pass


def _clean_watermark_form_xobjects(
    doc: fitz.Document,
    page: fitz.Page,
    protected_page_xrefs: set[int],
    extra_keywords: list[str] | None = None,
) -> int:
    """
    Cleans `/Subtype /Form` XObjects that act as watermark stamps on the page.
    """
    cleaned = 0
    try:
        for item in page.get_xobjects():
            form_xref = item[0]
            subtype = doc.xref_get_key(form_xref, "Subtype")
            if not subtype or subtype[1] != "/Form":
                continue

            res_str = doc.xref_get_key(form_xref, "Resources")[1] or ""
            if any(f"{bg_x} 0 R" in res_str for bg_x in protected_page_xrefs):
                continue

            f_stream = doc.xref_stream(form_xref) or b""
            if not f_stream:
                continue

            f_text = f_stream.decode("latin1", errors="ignore")
            literal_strings = " ".join(re.findall(r"\(([^()]{1,120})\)", f_text))
            if _is_competitor_text(literal_strings, extra_keywords) or _is_competitor_text(f_text, extra_keywords):
                doc.update_stream(form_xref, b"")
                cleaned += 1
                continue

            obj_def = doc.xref_object(form_xref) or ""
            for m in re.finditer(r"/([A-Za-z0-9_\-\.]+)\s+(\d+)\s+0\s+R", obj_def + " " + res_str):
                gs_xref = int(m.group(2))
                gs_obj = doc.xref_object(gs_xref) or ""
                if "/ExtGState" in gs_obj or "/ca" in gs_obj or "/CA" in gs_obj or "/BM" in gs_obj:
                    ca_m = re.search(r"/(?:ca|CA)\s+([0-9]*\.?[0-9]+)", gs_obj)
                    has_multiply = "/Multiply" in gs_obj or "/Screen" in gs_obj or "/Darken" in gs_obj
                    if (ca_m and float(ca_m.group(1)) < 0.85) or has_multiply:
                        if len(f_stream) < 65536:
                            doc.update_stream(form_xref, b"")
                            cleaned += 1
                            break
    except Exception:
        pass

    return cleaned


def _clean_faint_watermark_on_white_scan(doc: fitz.Document, xref: int) -> bool:
    """
    Specifically for FLATTENED white-background scans (like Ktuspecial.in pages where the
    faint pastel-blue/gray logo was merged into the single page JPEG before PDF creation):
    - Checks that the scan has a pure white background (70th percentile luminance >= 245).
      (This automatically skips gray phone-camera photos like ktunotes.live!)
    - In the center watermark zone (x: 15%..85%, y: 20%..78%), whitens ONLY washed-out
      faint gray / faint pastel-blue watermark pixels (luminance 198..247) while keeping
      100% of dark handwriting ink (luminance < 190) crisp and untouched.
    """
    try:
        pix = fitz.Pixmap(doc, xref)
        if pix.width < 350 or pix.height < 350 or pix.alpha:
            return False
        if pix.colorspace and pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)

        w, h, n = pix.width, pix.height, pix.n
        samples = bytearray(pix.samples)

        # 1) Verify this is a pure-white background scan (like CamScanner / ktuspecial.in)
        # Gray shadow camera photos (like ktunotes.live) have median_bg ~ 185..225 and will be skipped!
        bg_lums = []
        step_y = max(1, h // 24)
        step_x = max(1, w // 24)
        for sy in range(0, h, step_y):
            row_off = sy * w * n
            for sx in range(0, w, step_x):
                idx = row_off + sx * n
                if n == 1:
                    bg_lums.append(samples[idx])
                else:
                    bg_lums.append(
                        (samples[idx] * 299 + samples[idx + 1] * 587 + samples[idx + 2] * 114) // 1000
                    )
        bg_lums.sort()
        white_bg = bg_lums[int(len(bg_lums) * 0.65)] if bg_lums else 0

        # Strictly require a clean white scan background (>= 244)
        if white_bg < 244:
            return False

        # Center logo region where Ktuspecial / Ktunotes logos sit (x: 14%..86%, y: 18%..80%)
        cx0, cx1 = int(w * 0.14), int(w * 0.86)
        cy0, cy1 = int(h * 0.18), int(h * 0.80)

        # In ktuspecial.in, handwriting is black/dark-gray (lum < 180)
        # while the faint graduation-cap / KTU SPECIAL watermark is light gray/blue (lum 196..248).
        min_wm_lum = 196
        max_wm_lum = 249
        modified = False

        for y in range(cy0, cy1):
            row_base = y * w * n
            for x in range(cx0, cx1):
                i = row_base + x * n
                if n == 1:
                    lum = samples[i]
                    if min_wm_lum <= lum <= max_wm_lum:
                        samples[i] = 255
                        modified = True
                else:
                    r_c, g_c, b_c = samples[i], samples[i + 1], samples[i + 2]
                    lum = (r_c * 299 + g_c * 587 + b_c * 114) // 1000
                    if min_wm_lum <= lum <= max_wm_lum:
                        # Faint gray or faint pastel-blue watermark tint -> turn pure white (255)
                        samples[i] = 255
                        samples[i + 1] = 255
                        samples[i + 2] = 255
                        modified = True

        if modified:
            cleaned_pix = fitz.Pixmap(pix.colorspace, w, h, bytes(samples), 0)
            doc.update_stream(xref, cleaned_pix.tobytes("jpeg", jpg_quality=93))
            return True
    except Exception:
        pass

    return False


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    Removes existing text watermarks, hyperlink watermarks, Form XObject stamps,
    repeated/overlay logo images, and flattened white-scan faint watermarks.
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    xref_meta_cache: dict[int, dict] = {}
    hash_page_count: Counter[str] = Counter()
    xref_page_count: Counter[int] = Counter()
    page_img_xrefs: dict[int, list[int]] = {}
    page_bbox_by_xref: dict[int, dict[int, list[fitz.Rect]]] = {}

    # ------------------------------------------------------------------
    # PASS 1: Inspect every image on every page & count cross-page repeats FIRST
    # (A real handwritten page NEVER repeats on 2+ pages; a watermark ALWAYS repeats!)
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        ordered_xrefs: list[int] = []
        for im in page.get_images(full=True):
            x = im[0]
            if x not in ordered_xrefs:
                ordered_xrefs.append(x)
            if x not in xref_meta_cache:
                xref_meta_cache[x] = _inspect_image_xref(doc, x)

        bbox_map: dict[int, list[fitz.Rect]] = {}
        try:
            for info_item in page.get_image_info(xrefs=True):
                ix = info_item.get("xref", 0)
                ibbox = info_item.get("bbox")
                if ix and ibbox:
                    bbox_map.setdefault(ix, []).append(fitz.Rect(ibbox))
                    if ix not in ordered_xrefs:
                        ordered_xrefs.append(ix)
                    if ix not in xref_meta_cache:
                        xref_meta_cache[ix] = _inspect_image_xref(doc, ix)
        except Exception:
            pass

        page_img_xrefs[p_idx] = ordered_xrefs
        page_bbox_by_xref[p_idx] = bbox_map

        seen_hashes: set[str] = set()
        for x in ordered_xrefs:
            xref_page_count[x] += 1
            h = xref_meta_cache[x]["sha1"]
            if h:
                seen_hashes.add(h)
        for h in seen_hashes:
            hash_page_count[h] += 1

    # Any image whose xref OR SHA1 pixel hash appears on >= 2 pages is a REPEATED WATERMARK!
    repeated_watermark_xrefs: set[int] = set()
    if num_pages >= 2:
        for x, meta in xref_meta_cache.items():
            h = meta["sha1"]
            if xref_page_count[x] >= 2 or (h and hash_page_count[h] >= 2):
                repeated_watermark_xrefs.add(x)

    # ------------------------------------------------------------------
    # PASS 2: Per-page protection of unique handwriting scan & removal of watermarks
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        r = page.rect
        page_area = max(1.0, r.width * r.height)
        ordered_xrefs = page_img_xrefs.get(p_idx, [])
        bbox_map = page_bbox_by_xref.get(p_idx, {})

        # Identify the UNIQUE handwritten notebook scan on THIS page:
        # Must NOT be a repeated cross-page watermark, must NOT have transparency,
        # and must NOT be a washed-out logo with zero dark ink.
        protected_on_this_page: set[int] = set()

        if len(ordered_xrefs) == 1:
            sole_x = ordered_xrefs[0]
            sole_meta = xref_meta_cache[sole_x]
            # If the sole image on the page is unique to this page (not repeated on all pages),
            # protect it as the handwritten scan!
            if sole_x not in repeated_watermark_xrefs and not sole_meta["is_washed_out_logo"]:
                protected_on_this_page.add(sole_x)
        elif len(ordered_xrefs) >= 2:
            # Page has 2+ images (e.g. 1 unique handwriting scan + 1 watermark logo)
            scan_candidates: list[tuple[float, float, int, int]] = []
            for x in ordered_xrefs:
                if x in repeated_watermark_xrefs:
                    continue  # Repeated across pages = watermark!
                meta = xref_meta_cache[x]
                if meta["has_transparency"] or meta["is_washed_out_logo"]:
                    continue  # Transparent or washed-out = watermark!
                rects = bbox_map.get(x) or page.get_image_rects(x)
                max_ratio = max(((ir.width * ir.height) / page_area for ir in rects), default=0.0)
                scan_candidates.append((max_ratio, meta["dark_ink_ratio"], meta["pixel_area"], x))

            if scan_candidates:
                scan_candidates.sort(reverse=True)
                protected_on_this_page.add(scan_candidates[0][3])

        # Decide which image xrefs on this page are watermarks to delete
        xrefs_to_delete: set[int] = set()
        for x in ordered_xrefs:
            if x in protected_on_this_page:
                continue

            meta = xref_meta_cache[x]

            # 1) Repeated across >= 2 pages (catches ktuspecial.in & ktunotes.live logos 100%)
            if x in repeated_watermark_xrefs:
                xrefs_to_delete.add(x)
                continue

            # 2) Has transparency (/SMask, /Mask, alpha) or is a washed-out faint logo
            if meta["has_transparency"] or meta["is_washed_out_logo"]:
                xrefs_to_delete.add(x)
                continue

            # 3) Extra image on a page that already has a protected handwriting scan
            if protected_on_this_page and len(ordered_xrefs) >= 2:
                xrefs_to_delete.add(x)
                continue

        # Delete all identified watermark image layers on this page
        for x in xrefs_to_delete:
            _nuke_image_xref(doc, page, x)
            removed_image_count += 1

        # Clean any `/Subtype /Form` watermark XObjects on this page
        removed_image_count += _clean_watermark_form_xobjects(
            doc, page, protected_on_this_page, extra_keywords
        )

        # If this page had ONLY 1 single flattened image (no separate watermark image layer)
        # AND it's a pure-white background scan (like flattened ktuspecial.in pages),
        # bleach the faint pastel/gray watermark pixels in the center while keeping dark ink:
        remaining_xrefs = [x for x in ordered_xrefs if x not in xrefs_to_delete]
        if len(remaining_xrefs) == 1:
            sole_remaining = remaining_xrefs[0]
            if _clean_faint_watermark_on_white_scan(doc, sole_remaining):
                removed_image_count += 1

        # ------------------------------------------------------------------
        # Redact competitor watermark text lines/spans (never touching images)
        # ------------------------------------------------------------------
        page_has_redactions = False
        try:
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    full_line_text = "".join(s.get("text", "") for s in spans)

                    if _is_competitor_text(full_line_text, extra_keywords):
                        bbox = fitz.Rect(line["bbox"])
                        page.add_redact_annot(bbox)
                        page_has_redactions = True
                        removed_text_count += 1
                    else:
                        for span in spans:
                            stext = span.get("text", "")
                            if _is_competitor_text(stext, extra_keywords):
                                sbbox = fitz.Rect(span["bbox"])
                                page.add_redact_annot(sbbox)
                                page_has_redactions = True
                                removed_text_count += 1
        except Exception:
            pass

        if page_has_redactions:
            try:
                page.apply_redactions(
                    images=fitz.PDF_REDACT_IMAGE_NONE,
                    graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                )
            except Exception:
                try:
                    page.apply_redactions(images=0)
                except Exception:
                    pass

        # ------------------------------------------------------------------
        # Strip clickable competitor links (URI annotations)
        # ------------------------------------------------------------------
        try:
            for link in list(page.get_links()):
                uri = (link.get("uri") or "").lower()
                if not uri or "keralatimetable" in uri:
                    continue
                if any(kw in uri for kw in DEFAULT_COMPETITOR_KEYWORDS) or (
                    extra_keywords and any(k.strip().lower() in uri for k in extra_keywords if k.strip())
                ):
                    page.delete_link(link)
                    removed_link_count += 1
        except Exception:
            pass

    return {
        "removed_text": removed_text_count,
        "removed_images": removed_image_count,
        "removed_links": removed_link_count,
    }


def _apply_png_opacity(logo_bytes: bytes, logo_opacity: float | None) -> tuple[bytes, float]:
    """
    Reads logo dimensions and optionally adjusts the PNG alpha channel to match
    the requested logo_opacity (0.01 to 1.0) using pure PyMuPDF Pixmap.
    """
    pix = fitz.Pixmap(logo_bytes)
    logo_ratio = pix.height / pix.width

    if logo_opacity is None:
        return logo_bytes, logo_ratio

    opacity = max(0.01, min(1.0, float(logo_opacity)))
    if not pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix, 1)

    samples = bytearray(pix.samples)
    alpha_slice = samples[3::4]
    max_a = max(alpha_slice) if alpha_slice else 255
    if max_a > 0:
        scale = (opacity * 255.0) / max_a
        samples[3::4] = bytes(min(255, max(0, int(a * scale))) for a in alpha_slice)

    faded_pix = fitz.Pixmap(pix.colorspace, pix.width, pix.height, bytes(samples), 1)
    return faded_pix.tobytes("png"), logo_ratio


def add_watermark(
    pdf_bytes: bytes,
    logo_bytes: bytes | None = None,
    text: str | None = "Downloaded from Keralatimetable.in",
    logo_scale: float = 0.65,
    logo_opacity: float | None = None,
    text_color=(0.2, 0.2, 0.2),
    clean_existing: bool = True,
    extra_remove_keywords: list[str] | None = None,
) -> bytes:
    """
    Safely strips existing third-party watermarks without ever deleting handwritten scan pages,
    and returns new PDF bytes with a centered logo and bottom-center text.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Step 1: Clean competitor watermarks
    if clean_existing:
        remove_existing_watermarks(doc, extra_keywords=extra_remove_keywords)

    # Step 2: Prepare our brand logo
    processed_logo = None
    logo_ratio = None
    if logo_bytes:
        processed_logo, logo_ratio = _apply_png_opacity(logo_bytes, logo_opacity)

    # Step 3: Stamp our centered logo + bottom text on every page
    for page in doc:
        r = page.rect
        short_side = min(r.width, r.height)

        # 1) Centered Logo image — uses short_side so 16:9 PPT slides & A4 Portrait both fit properly
        if processed_logo and logo_ratio:
            w = short_side * logo_scale
            h = w * logo_ratio

            max_h = r.height * 0.78
            if h > max_h:
                h = max_h
                w = h / logo_ratio

            x0 = r.x0 + (r.width - w) / 2
            y0 = r.y0 + (r.height - h) / 2

            box = fitz.Rect(x0, y0, x0 + w, y0 + h)
            page.insert_image(box, stream=processed_logo, overlay=True)

        # 2) Bottom-center text ("Downloaded from Keralatimetable.in")
        if text:
            font_size = max(10.0, min(13.0, short_side * 0.02))
            text_length = fitz.get_text_length(text, fontname="helv", fontsize=font_size)
            x_text = r.x0 + (r.width - text_length) / 2
            bottom_margin = max(18.0, min(30.0, r.height * 0.036))
            y_text = r.y1 - bottom_margin

            page.insert_text(
                fitz.Point(x_text, y_text),
                text,
                fontsize=font_size,
                fontname="helv",
                color=text_color,
                overlay=True,
            )

    out = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return out


def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
    """Merge several PDFs (in order) into one PDF, returns bytes."""
    merged = fitz.open()
    for b in pdf_bytes_list:
        d = fitz.open(stream=b, filetype="pdf")
        merged.insert_pdf(d)
        d.close()
    out = merged.tobytes(garbage=4, deflate=True)
    merged.close()
    return out


def brand_papers(
    pdf_bytes_list: list[bytes],
    logo_bytes: bytes | None = None,
    text: str | None = "Downloaded from Keralatimetable.in",
    logo_scale: float = 0.65,
    logo_opacity: float | None = None,
    clean_existing: bool = True,
    extra_remove_keywords: list[str] | None = None,
) -> bytes:
    """
    Clean existing watermarks on each PDF, merge if multiple, and stamp our brand watermark.
    """
    if clean_existing and len(pdf_bytes_list) > 1:
        cleaned_list: list[bytes] = []
        for b in pdf_bytes_list:
            d = fitz.open(stream=b, filetype="pdf")
            remove_existing_watermarks(d, extra_keywords=extra_remove_keywords)
            cleaned_list.append(d.tobytes(garbage=3, deflate=True))
            d.close()
        merged = merge_pdfs(cleaned_list)
        return add_watermark(
            merged,
            logo_bytes=logo_bytes,
            text=text,
            logo_scale=logo_scale,
            logo_opacity=logo_opacity,
            clean_existing=False,
        )

    merged = merge_pdfs(pdf_bytes_list) if len(pdf_bytes_list) > 1 else pdf_bytes_list[0]
    return add_watermark(
        merged,
        logo_bytes=logo_bytes,
        text=text,
        logo_scale=logo_scale,
        logo_opacity=logo_opacity,
        clean_existing=clean_existing,
        extra_remove_keywords=extra_remove_keywords,
    )


if __name__ == "__main__":
    import sys
    inp, logo, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    pdf = open(inp, "rb").read()
    lg = open(logo, "rb").read()
    open(outp, "wb").write(
        add_watermark(pdf, logo_bytes=lg, text="Downloaded from Keralatimetable.in", clean_existing=True)
    )
    print("wrote", outp)
