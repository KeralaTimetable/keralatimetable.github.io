"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
and safely remove existing third-party watermarks:
1) Ktunotes.live (multi-image pages: 1 camera photo + 1 overlay logo) -> deletes the overlay logo.
2) Ktuspecial.in (either multi-image OR flattened single-image white scans) ->
   - NEVER deletes a page's sole image (eliminates blank white pages 100%).
   - If 2+ images exist on a page, deletes the repeated/transparent watermark layer and keeps the scan.
   - If only 1 flattened image exists on a page, cleans the faint center watermark tint and overlays
     the cleaned center region cleanly as a standard PNG without touching the original XObject filter.
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
    Safely inspects an image XObject:
    - Computes a SHA1 hash of pixel samples so identical watermark logos with DIFFERENT
      xref IDs on each page still match 100%.
    - Detects `/SMask`, `/Mask`, or inline alpha transparency.
    """
    info = {
        "xref": xref,
        "sha1": "",
        "dims": (0, 0),
        "pixel_area": 0,
        "has_transparency": False,
    }
    try:
        smask_val = doc.xref_get_key(xref, "SMask")
        if smask_val and smask_val[0] == "xref":
            info["has_transparency"] = True

        mask_val = doc.xref_get_key(xref, "Mask")
        if mask_val and mask_val[0] != "null":
            info["has_transparency"] = True

        pix = fitz.Pixmap(doc, xref)
        info["dims"] = (pix.width, pix.height)
        info["pixel_area"] = pix.width * pix.height
        if pix.alpha:
            info["has_transparency"] = True

        samples = pix.samples
        h_slice = samples[:: max(1, len(samples) // 2048)]
        info["sha1"] = hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.n}:".encode() + bytes(h_slice)
        ).hexdigest()
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


def _clean_baked_watermark_on_single_image_page(page: fitz.Page) -> bool:
    """
    When a page has ONLY 1 flattened scan image (like Ktuspecial.in's GAMAT301 where the
    faint pastel-blue/gray graduation cap + 'KTU SPECIAL' logo is baked into the scan itself):
    - We NEVER delete or overwrite the raw XObject stream (so the page can NEVER turn black or blank!).
    - Instead, we render ONLY the center watermark box of the page at 150 DPI, check if the page
      has a clean white background (median >= 245, skipping gray camera photos like ktunotes.live),
      bleach ONLY the faint watermark pixels (luminance 202..249) to pure white (255) while keeping
      all dark handwriting pixels (< 195) 100% intact, and stamp that cleaned center patch back!
    """
    try:
        r = page.rect
        # Center box where the Ktuspecial.in / Ktunotes logo sits (middle 68% width x 58% height)
        center_box = fitz.Rect(
            r.x0 + r.width * 0.16,
            r.y0 + r.height * 0.20,
            r.x0 + r.width * 0.84,
            r.y0 + r.height * 0.78,
        )

        # Render the center box at 160 DPI (fast & sharp)
        pix = page.get_pixmap(clip=center_box, dpi=160, alpha=False)
        if pix.width < 100 or pix.height < 100:
            return False

        w, h, n = pix.width, pix.height, pix.n
        samples = bytearray(pix.samples)

        # 1) Check background brightness of this center box:
        # Must be a white-background scan (60th percentile luminance >= 245).
        # Gray phone-camera photos (like ktunotes.live) have background ~180..225 and return False immediately!
        lums = []
        step = max(1, (w * h) // 1024) * n
        for i in range(0, len(samples) - n + 1, step):
            lum = (samples[i] * 299 + samples[i + 1] * 587 + samples[i + 2] * 114) // 1000
            lums.append(lum)
        lums.sort()
        if not lums or lums[int(len(lums) * 0.60)] < 245:
            return False

        # 2) Whiten ONLY faint watermark pixels (luminance 200..249) inside the center box
        # Handwriting ink on ktuspecial.in is dark black/gray (< 185) and stays 100% untouched!
        min_wm_lum = 200
        max_wm_lum = 249
        changed_pixels = 0

        for i in range(0, len(samples) - 2, 3):
            r_c, g_c, b_c = samples[i], samples[i + 1], samples[i + 2]
            lum = (r_c * 299 + g_c * 587 + b_c * 114) // 1000
            if min_wm_lum <= lum <= max_wm_lum:
                samples[i] = 255
                samples[i + 1] = 255
                samples[i + 2] = 255
                changed_pixels += 1

        # Only overlay the cleaned patch if there was actually a faint watermark in the center
        total_px = w * h
        if changed_pixels < total_px * 0.005:
            return False

        cleaned_patch = fitz.Pixmap(fitz.csRGB, w, h, bytes(samples), 0)
        page.insert_image(center_box, stream=cleaned_patch.tobytes("png"), overlay=True)
        return True
    except Exception:
        return False


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    Removes existing text watermarks, hyperlink watermarks, repeated/transparent overlay
    logo images (on multi-image pages), and faint baked-in center watermarks (on single-image
    white-background scans).
    GUARANTEE: Never deletes the sole image on a page -> ZERO blank pages ever!
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
    # PASS 1: Catalog all images on every page & count cross-page repeats
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

    # Any image whose xref OR SHA1 pixel hash appears on >= 2 pages is a REPEATED WATERMARK
    repeated_watermark_xrefs: set[int] = set()
    if num_pages >= 2:
        for x, meta in xref_meta_cache.items():
            h = meta["sha1"]
            if xref_page_count[x] >= 2 or (h and hash_page_count[h] >= 2):
                repeated_watermark_xrefs.add(x)

    # ------------------------------------------------------------------
    # PASS 2: Page-by-page safe watermark removal
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        r = page.rect
        page_area = max(1.0, r.width * r.height)
        ordered_xrefs = page_img_xrefs.get(p_idx, [])
        bbox_map = page_bbox_by_xref.get(p_idx, {})

        # ==================================================================
        # CASE A: Page has 2 or more images (e.g. Ktunotes.live or layered PDF)
        # Keep the unique background scan image and delete the overlay/repeated logo!
        # ==================================================================
        if len(ordered_xrefs) >= 2:
            protected_on_this_page: set[int] = set()
            scan_candidates: list[tuple[int, float, int, int]] = []

            for x in ordered_xrefs:
                meta = xref_meta_cache[x]
                is_unique_to_page = x not in repeated_watermark_xrefs
                is_opaque = not meta["has_transparency"]
                rects = bbox_map.get(x) or page.get_image_rects(x)
                max_ratio = max(((ir.width * ir.height) / page_area for ir in rects), default=0.0)
                # Sort priority: (1) unique to this page & opaque, (2) largest area, (3) highest pixel count
                priority = (1 if (is_unique_to_page and is_opaque) else 0)
                scan_candidates.append((priority, max_ratio, meta["pixel_area"], x))

            scan_candidates.sort(reverse=True)
            protected_on_this_page.add(scan_candidates[0][3])

            xrefs_to_delete: set[int] = set()
            for x in ordered_xrefs:
                if x in protected_on_this_page:
                    continue
                meta = xref_meta_cache[x]
                if x in repeated_watermark_xrefs or meta["has_transparency"] or len(ordered_xrefs) >= 2:
                    xrefs_to_delete.add(x)

            for x in xrefs_to_delete:
                _nuke_image_xref(doc, page, x)
                removed_image_count += 1

        # ==================================================================
        # CASE B: Page has ONLY 1 single image (e.g. flattened Ktuspecial.in scan)
        # NEVER delete the sole image! Instead, clean the faint baked-in center watermark.
        # ==================================================================
        elif len(ordered_xrefs) == 1:
            if _clean_baked_watermark_on_single_image_page(page):
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
