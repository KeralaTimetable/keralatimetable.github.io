"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
safely remove existing third-party watermarks (text, links, overlay logo layers, AND
faint watermarks baked into flattened handwritten scans like Ktunotes.live / Ktuspecial.in)
WITHOUT ever deleting or blanking out handwritten note pages.
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

    if len(cleaned) <= 120:
        for kw in DEFAULT_COMPETITOR_KEYWORDS:
            if kw in low:
                return True

    return False


def _inspect_image_xref(doc: fitz.Document, xref: int) -> dict:
    """
    Lightweight, safe inspection of an image XObject:
    - Computes a perceptual/pixel SHA1 hash so identical watermark logos with DIFFERENT
      xref IDs on each page still match 100%.
    - Checks whether the image has a true transparency mask (/SMask or inline alpha).
    """
    info = {
        "sha1": "",
        "dims": (0, 0),
        "has_smask_or_alpha": False,
        "mean_alpha": 255.0,
        "transparent_ratio": 0.0,
    }
    try:
        smask_val = doc.xref_get_key(xref, "SMask")
        smask_xref = 0
        if smask_val and smask_val[0] == "xref":
            smask_xref = int(smask_val[1].split()[0])

        if smask_xref > 0:
            info["has_smask_or_alpha"] = True
            smask_pix = fitz.Pixmap(doc, smask_xref)
            s_bytes = smask_pix.samples
            if s_bytes:
                step = max(1, len(s_bytes) // 4096)
                sampled = s_bytes[::step]
                non_zero = [a for a in sampled if a > 4]
                info["transparent_ratio"] = 1.0 - (len(non_zero) / max(1, len(sampled)))
                if non_zero:
                    info["mean_alpha"] = sum(non_zero) / len(non_zero)
                else:
                    info["mean_alpha"] = 0.0

        pix = fitz.Pixmap(doc, xref)
        info["dims"] = (pix.width, pix.height)
        if pix.alpha:
            info["has_smask_or_alpha"] = True

        samples = pix.samples
        h_slice = samples[:: max(1, len(samples) // 2048)]
        info["sha1"] = hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.n}:".encode() + bytes(h_slice)
        ).hexdigest()

        if pix.alpha and not smask_xref and samples:
            alpha_vals = samples[pix.n - 1 :: pix.n * max(1, (pix.width * pix.height) // 4096)]
            if alpha_vals:
                non_zero = [a for a in alpha_vals if a > 4]
                info["transparent_ratio"] = 1.0 - (len(non_zero) / max(1, len(alpha_vals)))
                if non_zero:
                    info["mean_alpha"] = sum(non_zero) / len(non_zero)
    except Exception:
        pass

    return info


def _find_low_opacity_xobjects_in_page_streams(doc: fitz.Document, page: fitz.Page) -> set[int]:
    """
    Parses the page's content stream (and any Form XObjects) to find images or Forms
    drawn right after a low-opacity ExtGState (`/GSx gs` where `/ca < 0.85`).
    Many PDF watermarkers use opaque JPEG/PNGs + ExtGState opacity instead of /SMask!
    """
    low_op_xrefs: set[int] = set()
    try:
        # Collect all XObject name -> xref mappings on this page
        name_to_xref: dict[bytes, int] = {}
        for item in page.get_xobjects():
            # item = (xref, name, invoker_xref, bbox)
            if item[1]:
                name_to_xref[item[1].encode("latin1")] = item[0]

        if not name_to_xref:
            return low_op_xrefs

        # Inspect page and Form resources for ExtGState dictionaries with /ca < 0.85
        low_op_gs_names: set[bytes] = set()
        xrefs_to_check = [page.xref] + [item[0] for item in page.get_xobjects()]
        for obj_xref in xrefs_to_check:
            try:
                obj_str = doc.xref_object(obj_xref) or ""
                # Match /GSname << ... /ca 0.15 ... >> or indirect ref
                for m in re.finditer(r"/([A-Za-z0-9_\-\.]+)\s+(\d+)\s+0\s+R", obj_str):
                    gs_name, gs_xref = m.group(1), int(m.group(2))
                    gs_obj = doc.xref_object(gs_xref) or ""
                    ca_m = re.search(r"/ca\s+([0-9]*\.?[0-9]+)", gs_obj)
                    if ca_m and float(ca_m.group(1)) < 0.85:
                        low_op_gs_names.add(gs_name.encode("latin1"))
            except Exception:
                pass

        if not low_op_gs_names:
            return low_op_xrefs

        # Scan content streams for `/GSname gs ... /ImName Do`
        streams = [doc.xref_stream(c) or b"" for c in page.get_contents()]
        for item in page.get_xobjects():
            if doc.xref_get_key(item[0], "Subtype")[1] == "/Form":
                streams.append(doc.xref_stream(item[0]) or b"")

        for st in streams:
            for gs_name in low_op_gs_names:
                # Look for /GSname gs followed within 300 bytes by /XName Do
                pat = re.compile(
                    rb"/" + re.escape(gs_name) + rb"\s+gs\b[\s\S]{0,300}?/([A-Za-z0-9_\-\.]+)\s+Do\b"
                )
                for m in pat.finditer(st):
                    x_name = m.group(1)
                    if x_name in name_to_xref:
                        low_op_xrefs.add(name_to_xref[x_name])
    except Exception:
        pass

    return low_op_xrefs


def _purge_xobject_invocations(doc: fitz.Document, page: fitz.Page, target_xrefs: set[int]) -> None:
    """Removes `/ImX Do` calls for `target_xrefs` from page Contents and nested Form streams."""
    try:
        for item in page.get_xobjects():
            x_xref, x_name, invoker_xref = item[0], item[1], item[2]
            if x_xref in target_xrefs and x_name:
                pattern = re.compile(rb"/" + re.escape(x_name.encode("latin1")) + rb"\s+Do\b")
                for c_xref in page.get_contents():
                    stream = doc.xref_stream(c_xref)
                    if stream and pattern.search(stream):
                        doc.update_stream(c_xref, pattern.sub(b"", stream))
                if invoker_xref and invoker_xref > 0:
                    f_stream = doc.xref_stream(invoker_xref)
                    if f_stream and pattern.search(f_stream):
                        doc.update_stream(invoker_xref, pattern.sub(b"", f_stream))
    except Exception:
        pass


def _clean_baked_watermark_in_scan_region(doc: fitz.Document, xref: int) -> bool:
    """
    FOR FLATTENED HANDWRITTEN SCANS (where the watermark logo is baked into the single
    full-page scan image and there is NO separate watermark layer):
    - Only operates on the CENTER watermark zone (middle 65% width x 55% height) and
      BOTTOM footer strip (bottom 7% height).
    - Preserves 100% of dark/medium pen ink (blue, black, red, pencil strokes) and paper texture.
    - Only whitens ultra-faint, washed-out watermark pixels (luminance 208..246) that are
      lighter than the handwriting ink.
    """
    try:
        pix = fitz.Pixmap(doc, xref)
        # Only process standard RGB or Grayscale full-page scans of reasonable resolution
        if pix.width < 300 or pix.height < 300:
            return False
        if pix.alpha:
            return False
        if pix.colorspace and pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)

        w, h, n = pix.width, pix.height, pix.n
        samples = bytearray(pix.samples)

        # Sample overall page background brightness first
        # If the scan has a dark/gray/yellowed phone-camera background (median lum < 228),
        # DO NOT touch pixels at all so we never leave a white box on a gray camera photo!
        bg_samples = []
        step_y = max(1, h // 25)
        step_x = max(1, w // 25)
        for sy in range(0, h, step_y):
            row_off = sy * w * n
            for sx in range(0, w, step_x):
                idx = row_off + sx * n
                if n == 1:
                    bg_samples.append(samples[idx])
                else:
                    bg_samples.append(
                        (samples[idx] * 299 + samples[idx + 1] * 587 + samples[idx + 2] * 114) // 1000
                    )
        bg_samples.sort()
        median_bg = bg_samples[int(len(bg_samples) * 0.75)] if bg_samples else 255

        # Only bleach baked-in faint watermarks on clean white-background scans (CamScanner / digital)
        if median_bg < 236:
            return False

        # Define the two zones where competitor watermarks live:
        # Zone 1: Center logo box (x: 16%..84%, y: 24%..76%)
        cx0, cx1 = int(w * 0.16), int(w * 0.84)
        cy0, cy1 = int(h * 0.24), int(h * 0.76)

        # Zone 2: Bottom footer text strip (x: 15%..85%, y: 93%..99%)
        fy0, fy1 = int(h * 0.935), int(h * 0.992)

        # Faint watermark luminance band on a white (250-255) page:
        # Handwriting ink is darker (< 195) or saturated blue/red pen.
        # Faint 10%–22% opacity watermark sits in [206 .. median_bg - 3].
        low_lum = 206
        high_lum = max(215, median_bg - 3)
        rep_val = min(255, median_bg + 2)

        modified = False

        def _clean_band(y_start: int, y_end: int, x_start: int, x_end: int):
            nonlocal modified
            for y in range(y_start, y_end):
                row_base = y * w * n
                for x in range(x_start, x_end):
                    i = row_base + x * n
                    if n == 1:
                        v = samples[i]
                        if low_lum <= v <= high_lum:
                            samples[i] = rep_val
                            modified = True
                    else:
                        r_c, g_c, b_c = samples[i], samples[i + 1], samples[i + 2]
                        # Protect blue/red pen ink: if blue or red channel dominates strongly, keep it!
                        if (b_c - r_c > 28) or (r_c - b_c > 35):
                            continue
                        lum = (r_c * 299 + g_c * 587 + b_c * 114) // 1000
                        if low_lum <= lum <= high_lum:
                            samples[i] = rep_val
                            samples[i + 1] = rep_val
                            samples[i + 2] = rep_val
                            modified = True

        _clean_band(cy0, cy1, cx0, cx1)
        _clean_band(fy0, fy1, cx0, cx1)

        if modified:
            cleaned_pix = fitz.Pixmap(pix.colorspace, w, h, bytes(samples), 0)
            doc.update_stream(xref, cleaned_pix.tobytes("jpeg", jpg_quality=92))
            return True
    except Exception:
        pass

    return False


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    Safely removes existing text watermarks, hyperlink watermarks, and watermark logo images.
    GUARANTEE: Never deletes full-page handwritten note scans or sole content images on a page.
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    xref_info_cache: dict[int, dict] = {}
    hash_page_count: Counter[str] = Counter()
    dims_center_page_count: Counter[tuple[int, int]] = Counter()
    page_image_records: dict[int, list[dict]] = {}

    # ------------------------------------------------------------------
    # PASS 1: Catalog all images on every page
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        r = page.rect
        page_area = max(1.0, r.width * r.height)
        page_cx = r.x0 + r.width / 2.0
        page_cy = r.y0 + r.height / 2.0

        low_op_stream_xrefs = _find_low_opacity_xobjects_in_page_streams(doc, page)
        seen_hashes_this_page: set[str] = set()
        seen_center_dims_this_page: set[tuple[int, int]] = set()
        records: list[dict] = []

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref not in xref_info_cache:
                xref_info_cache[xref] = _inspect_image_xref(doc, xref)
            meta = xref_info_cache[xref]

            rects = page.get_image_rects(xref)
            if not rects:
                continue

            for ir in rects:
                area_ratio = (ir.width * ir.height) / page_area
                ir_cx = ir.x0 + ir.width / 2.0
                ir_cy = ir.y0 + ir.height / 2.0

                is_centered = (
                    abs(ir_cx - page_cx) <= r.width * 0.24
                    and abs(ir_cy - page_cy) <= r.height * 0.24
                )
                is_edge_stamp = (
                    ir.y0 >= r.y1 - r.height * 0.12
                    or ir.y1 <= r.y0 + r.height * 0.10
                )

                rec = {
                    "xref": xref,
                    "rect": ir,
                    "area_ratio": area_ratio,
                    "height_ratio": ir.height / max(1.0, r.height),
                    "is_centered": is_centered,
                    "is_edge_stamp": is_edge_stamp,
                    "is_low_op_gs": xref in low_op_stream_xrefs,
                    "meta": meta,
                }
                records.append(rec)

                # Only count non-full-page images (< 62% of page area) toward repeated watermark stats
                if area_ratio < 0.62:
                    if meta["sha1"]:
                        seen_hashes_this_page.add(meta["sha1"])
                    if (is_centered or is_edge_stamp) and meta["dims"] != (0, 0):
                        seen_center_dims_this_page.add(meta["dims"])

        page_image_records[p_idx] = records
        for h in seen_hashes_this_page:
            hash_page_count[h] += 1
        for d in seen_center_dims_this_page:
            dims_center_page_count[d] += 1

    # ------------------------------------------------------------------
    # PASS 2: Page-by-page safe watermark removal
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        records = page_image_records.get(p_idx, [])
        unique_xrefs_on_page = {rec["xref"] for rec in records}

        # Check if this page has substantial text content (digital notes vs scanned page)
        page_text_len = len((page.get_text("text") or "").strip())
        has_multiple_images = len(unique_xrefs_on_page) >= 2

        xrefs_to_delete: set[int] = set()

        for rec in records:
            xref = rec["xref"]
            area_ratio = rec["area_ratio"]
            meta = rec["meta"]
            img_hash = meta["sha1"]
            dims = meta["dims"]

            # ==================================================================
            # IRONCLAD HANDWRITTEN SCAN PROTECTION:
            # 1) Never delete any image covering >= 58% of the page unless it has a
            #    mostly-transparent alpha mask AND there is another image/text layer on the page.
            # 2) If a page has ONLY 1 image and almost no digital text (< 80 chars),
            #    that single image IS the scanned note page — NEVER delete it!
            # ==================================================================
            if not has_multiple_images and page_text_len < 80 and area_ratio > 0.25:
                continue

            if area_ratio >= 0.58:
                # Only allow deleting a large image if the page has multiple images AND
                # this one is a transparent overlay (has alpha mask with >45% transparency)
                if (
                    has_multiple_images
                    and meta["has_smask_or_alpha"]
                    and meta["transparent_ratio"] > 0.45
                    and meta["mean_alpha"] < 180
                ):
                    xrefs_to_delete.add(xref)
                continue

            # SAFE RULE A: Identical non-full-page image hash repeats across multiple pages
            repeat_by_hash = hash_page_count.get(img_hash, 0)
            if num_pages >= 2 and (
                repeat_by_hash >= max(2, int(num_pages * 0.35)) or repeat_by_hash >= 3
            ):
                if rec["is_centered"] or rec["is_edge_stamp"] or meta["has_smask_or_alpha"]:
                    xrefs_to_delete.add(xref)
                    continue

            # SAFE RULE B: Same exact pixel dimensions centered/footer on multiple pages
            # (catches watermarks re-encoded per page with slightly different JPEG compression)
            repeat_by_dims = dims_center_page_count.get(dims, 0)
            if num_pages >= 3 and (
                repeat_by_dims >= max(2, int(num_pages * 0.45)) or repeat_by_dims >= 3
            ):
                if (rec["is_centered"] or rec["is_edge_stamp"]) and area_ratio < 0.50:
                    xrefs_to_delete.add(xref)
                    continue

            # SAFE RULE C: Drawn with low-opacity ExtGState (/ca < 0.85) in content stream
            if rec["is_low_op_gs"] and (rec["is_centered"] or rec["is_edge_stamp"]):
                xrefs_to_delete.add(xref)
                continue

            # SAFE RULE D: Separate overlay logo with /SMask or Alpha channel sitting in center
            if (
                rec["is_centered"]
                and meta["has_smask_or_alpha"]
                and (meta["mean_alpha"] < 195 or meta["transparent_ratio"] > 0.25)
                and (has_multiple_images or page_text_len >= 80)
            ):
                xrefs_to_delete.add(xref)
                continue

            # SAFE RULE E: Small footer/header stamp at very top or bottom margin (< 8% height)
            if (
                rec["is_edge_stamp"]
                and rec["height_ratio"] <= 0.08
                and area_ratio <= 0.12
                and (has_multiple_images or page_text_len >= 40)
            ):
                xrefs_to_delete.add(xref)
                continue

        # Execute image layer deletion if watermark layers were found
        if xrefs_to_delete:
            _purge_xobject_invocations(doc, page, xrefs_to_delete)
            for xref in xrefs_to_delete:
                try:
                    page.delete_image(xref)
                    removed_image_count += 1
                except Exception:
                    pass
        else:
            # If NO separate watermark image layer existed on this page AND this page is a
            # single full-page scan (flattened handwritten notes), gently clean faint baked-in
            # watermark pixels in the center/footer without touching handwriting ink:
            if len(unique_xrefs_on_page) == 1 and records and records[0]["area_ratio"] >= 0.65:
                sole_xref = records[0]["xref"]
                if _clean_baked_watermark_in_scan_region(doc, sole_xref):
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
