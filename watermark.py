"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
and surgically remove existing third-party watermarks (like the centered "KTU ktunotes.live
2024 SCHEME NOTES" overlay logo + bottom "Downloaded from KTUNOTES.LIVE" text)
while 100% protecting underlying phone-camera / handwritten notebook scans.
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

    if len(cleaned) <= 140:
        for kw in DEFAULT_COMPETITOR_KEYWORDS:
            if kw in low:
                return True

    return False


def _inspect_image_xref(doc: fitz.Document, xref: int) -> dict:
    """
    Inspects an image XObject:
    - Computes a pixel SHA1 hash so identical watermark logos with DIFFERENT xref IDs
      across pages still match 100%.
    - Detects whether the image has an /SMask (soft mask), inline alpha, or /Mask.
    """
    info = {
        "xref": xref,
        "sha1": "",
        "dims": (0, 0),
        "pixel_area": 0,
        "has_transparency": False,
        "smask_xref": 0,
    }
    try:
        # Check PDF dictionary keys for /SMask or /Mask
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

        samples = pix.samples
        h_slice = samples[:: max(1, len(samples) // 2048)]
        info["sha1"] = hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.n}:".encode() + bytes(h_slice)
        ).hexdigest()
    except Exception:
        pass

    return info


def _nuke_image_xref(doc: fitz.Document, page: fitz.Page, xref: int, smask_xref: int = 0) -> None:
    """
    Completely eradicates a watermark image XObject so it cannot render anywhere:
    1) Removes `/ImX Do` from page content streams and nested Form XObject streams.
    2) Calls `page.delete_image(xref)`.
    3) Replaces the image XObject stream (and its /SMask if any) with a 1x1 100%-transparent
       pixel as a failsafe in case a deeply nested Form XObject still invokes it.
    """
    # 1) Strip `/Name Do` from page contents and Form XObjects
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

    # 2) Standard PyMuPDF delete_image
    try:
        page.delete_image(xref)
    except Exception:
        pass


def _clean_watermark_form_xobjects(
    doc: fitz.Document,
    page: fitz.Page,
    protected_bg_xrefs: set[int],
    extra_keywords: list[str] | None = None,
) -> int:
    """
    Many watermark tools (including Ktunotes.live / Ktuspecial.in / PyMuPDF / ReportLab / iText)
    place the centered watermark inside a `/Subtype /Form` XObject overlaid on the page.
    This inspects all Form XObjects on the page and clears any Form XObject that:
    - Contains competitor text ("ktunotes", "scheme notes", "ktuspecial", etc.), OR
    - Uses a low-opacity ExtGState (/ca < 0.85) AND does NOT contain the protected notebook scan image.
    """
    cleaned = 0
    try:
        for item in page.get_xobjects():
            form_xref, form_name, invoker_xref = item[0], item[1], item[2]
            subtype = doc.xref_get_key(form_xref, "Subtype")
            if not subtype or subtype[1] != "/Form":
                continue

            # Never touch a Form XObject if it holds the protected background notebook image!
            res_str = (doc.xref_get_key(form_xref, "Resources")[1] or "")
            if any(f"{bg_x} 0 R" in res_str for bg_x in protected_bg_xrefs):
                continue

            f_stream = doc.xref_stream(form_xref) or b""
            if not f_stream:
                continue

            f_text = f_stream.decode("latin1", errors="ignore")

            # Check A: Does the Form stream contain competitor text strings?
            # Extract PDF literal strings (...) inside the Form stream
            literal_strings = " ".join(re.findall(r"\(([^()]{1,120})\)", f_text))
            if _is_competitor_text(literal_strings, extra_keywords) or _is_competitor_text(f_text, extra_keywords):
                doc.update_stream(form_xref, b"")
                cleaned += 1
                continue

            # Check B: Does this Form XObject use a low-opacity ExtGState (/ca < 0.8) typical of a watermark stamp?
            obj_def = doc.xref_object(form_xref) or ""
            has_low_op_gs = False
            for m in re.finditer(r"/([A-Za-z0-9_\-\.]+)\s+(\d+)\s+0\s+R", obj_def + " " + res_str):
                gs_xref = int(m.group(2))
                gs_obj = doc.xref_object(gs_xref) or ""
                if "/ExtGState" in gs_obj or "/ca" in gs_obj or "/CA" in gs_obj:
                    ca_m = re.search(r"/(?:ca|CA)\s+([0-9]*\.?[0-9]+)", gs_obj)
                    if ca_m and float(ca_m.group(1)) < 0.80:
                        has_low_op_gs = True
                        break

            if has_low_op_gs and len(f_stream) < 65536:
                doc.update_stream(form_xref, b"")
                cleaned += 1
    except Exception:
        pass

    return cleaned


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    Removes existing text watermarks, hyperlink watermarks, Form XObject stamps,
    and overlay logo images (like the centered "KTU ktunotes.live 2024 SCHEME NOTES" logo)
    while 100% protecting the underlying handwritten notebook scan on every page.
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    xref_meta_cache: dict[int, dict] = {}
    hash_page_count: Counter[str] = Counter()
    dims_page_count: Counter[tuple[int, int]] = Counter()
    xref_page_count: Counter[int] = Counter()

    # Per-page ordered list of image xrefs and protected background xrefs
    page_img_xrefs: dict[int, list[int]] = {}
    protected_notebook_xrefs: set[int] = set()

    # ------------------------------------------------------------------
    # PASS 1: Catalog all images on every page & lock the main notebook scan
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        r = page.rect
        page_area = max(1.0, r.width * r.height)

        # Collect all image xrefs on this page (including those inside Form XObjects!)
        raw_imgs = page.get_images(full=True)
        ordered_xrefs: list[int] = []
        for im in raw_imgs:
            x = im[0]
            if x not in ordered_xrefs:
                ordered_xrefs.append(x)
            if x not in xref_meta_cache:
                xref_meta_cache[x] = _inspect_image_xref(doc, x)

        # Also get rendered bounding boxes via get_image_info(xrefs=True)
        # (Works even when get_image_rects() returns [] for images inside Form XObjects!)
        bbox_by_xref: dict[int, list[fitz.Rect]] = {}
        try:
            for info_item in page.get_image_info(xrefs=True):
                ix = info_item.get("xref", 0)
                ibbox = info_item.get("bbox")
                if ix and ibbox:
                    bbox_by_xref.setdefault(ix, []).append(fitz.Rect(ibbox))
                    if ix not in ordered_xrefs:
                        ordered_xrefs.append(ix)
                    if ix not in xref_meta_cache:
                        xref_meta_cache[ix] = _inspect_image_xref(doc, ix)
        except Exception:
            pass

        page_img_xrefs[p_idx] = ordered_xrefs

        # Identify which image (if any) is the MAIN HANDWRITTEN NOTEBOOK SCAN on this page:
        # A notebook scan is an OPAQUE image (no /SMask or transparency) that covers the largest
        # area on the page (>= 45% of page area or highest pixel resolution on a scan page).
        opaque_candidates: list[tuple[float, int, int]] = []
        for x in ordered_xrefs:
            meta = xref_meta_cache[x]
            if meta["has_transparency"]:
                continue  # A transparent PNG/SMask image is an overlay, never a camera scan!
            rects = bbox_by_xref.get(x) or page.get_image_rects(x)
            max_ratio = max(((ir.width * ir.height) / page_area for ir in rects), default=0.0)
            opaque_candidates.append((max_ratio, meta["pixel_area"], x))

        if len(ordered_xrefs) == 1 and opaque_candidates:
            # Sole opaque image on the page -> 100% protected notebook scan
            protected_notebook_xrefs.add(opaque_candidates[0][2])
        elif opaque_candidates:
            # Multiple images on the page: lock the largest opaque image as the notebook scan
            # if it covers >= 40% of the page (or has > 250,000 pixels)
            opaque_candidates.sort(reverse=True)
            best_ratio, best_px, best_xref = opaque_candidates[0]
            if best_ratio >= 0.40 or best_px >= 250_000:
                protected_notebook_xrefs.add(best_xref)

        # Count cross-page repetitions for all NON-protected images
        seen_hashes: set[str] = set()
        seen_dims: set[tuple[int, int]] = set()
        for x in ordered_xrefs:
            if x in protected_notebook_xrefs:
                continue
            xref_page_count[x] += 1
            meta = xref_meta_cache[x]
            if meta["sha1"]:
                seen_hashes.add(meta["sha1"])
            if meta["dims"] != (0, 0):
                seen_dims.add(meta["dims"])

        for h in seen_hashes:
            hash_page_count[h] += 1
        for d in seen_dims:
            dims_page_count[d] += 1

    # ------------------------------------------------------------------
    # PASS 2: Delete watermark overlay images, Form XObjects, text & links
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        ordered_xrefs = page_img_xrefs.get(p_idx, [])
        has_protected_scan_on_page = any(x in protected_notebook_xrefs for x in ordered_xrefs)

        xrefs_to_delete: set[int] = set()

        for x in ordered_xrefs:
            # NEVER touch the protected handwritten notebook scan!
            if x in protected_notebook_xrefs:
                continue

            meta = xref_meta_cache[x]
            img_hash = meta["sha1"]
            dims = meta["dims"]

            # RULE 1: Any image with transparency (/SMask, /Mask, or alpha channel)
            # In KTU notes PDFs, centered logos like "KTU ktunotes.live 2024 SCHEME NOTES"
            # have transparency so the handwriting underneath shows through.
            if meta["has_transparency"]:
                xrefs_to_delete.add(x)
                continue

            # RULE 2: Same xref ID, same SHA1 image hash, or same pixel dimensions
            # repeats across >= 2 pages (and is NOT a protected notebook scan)
            if num_pages >= 2 and (
                xref_page_count[x] >= 2
                or hash_page_count.get(img_hash, 0) >= 2
                or (dims_page_count.get(dims, 0) >= max(2, int(num_pages * 0.35)))
            ):
                xrefs_to_delete.add(x)
                continue

            # RULE 3: This page is a handwritten notebook scan (has a protected full-page photo)
            # AND there is a 2nd extra image overlaid on the same page!
            if has_protected_scan_on_page and len(ordered_xrefs) >= 2:
                xrefs_to_delete.add(x)
                continue

        # Execute complete removal of all identified watermark image xrefs on this page
        for x in xrefs_to_delete:
            smask_x = xref_meta_cache.get(x, {}).get("smask_xref", 0)
            _nuke_image_xref(doc, page, x, smask_x)
            removed_image_count += 1

        # Clean any `/Subtype /Form` watermark XObjects on this page
        removed_image_count += _clean_watermark_form_xobjects(
            doc, page, protected_notebook_xrefs, extra_keywords
        )

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
                # CRITICAL: PDF_REDACT_IMAGE_NONE ensures underlying notebook photos are untouched
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
