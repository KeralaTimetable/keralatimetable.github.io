"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
aggressively remove existing third-party watermarks (text, links, low-opacity logos,
Form XObject stamps & faint background marks like Ktunotes.live, Ktuspecial.in, etc.),
and merge multiple papers/notes into one branded file.
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


def _analyze_image_faintness(doc: fitz.Document, xref: int) -> dict:
    """
    Inspects an image XObject (and its /SMask soft-mask if present) at pixel level
    to determine if it is a low-opacity / faded watermark logo vs real content/scan.
    """
    info = {
        "has_alpha": False,
        "mean_alpha": 255.0,
        "max_alpha": 255,
        "transparent_ratio": 0.0,
        "is_low_opacity_alpha": False,
        "is_washed_out_faint": False,
        "dark_ink_ratio": 1.0,
        "sha1": "",
        "dims": (0, 0),
    }

    try:
        raw_stream = doc.xref_stream(xref) or b""
        smask_val = doc.xref_get_key(xref, "SMask")
        smask_xref = 0
        if smask_val and smask_val[0] == "xref":
            smask_xref = int(smask_val[1].split()[0])

        # Inspect soft-mask (/SMask) directly if PDF uses separate alpha XObject
        if smask_xref > 0:
            info["has_alpha"] = True
            smask_pix = fitz.Pixmap(doc, smask_xref)
            s_bytes = smask_pix.samples
            if s_bytes:
                step = max(1, len(s_bytes) // 4096)
                sampled = s_bytes[::step]
                non_zero = [a for a in sampled if a > 3]
                info["transparent_ratio"] = 1.0 - (len(non_zero) / max(1, len(sampled)))
                if non_zero:
                    info["mean_alpha"] = sum(non_zero) / len(non_zero)
                    info["max_alpha"] = max(non_zero)
                else:
                    info["mean_alpha"] = 0.0
                    info["max_alpha"] = 0

                # Low opacity watermark if visible pixels have mean alpha < 175 (~68% opacity)
                # OR if it's mostly transparent overlay (>35% transparent pixels)
                if info["mean_alpha"] < 175 or info["max_alpha"] < 195:
                    info["is_low_opacity_alpha"] = True

        # Load base image Pixmap
        pix = fitz.Pixmap(doc, xref)
        info["dims"] = (pix.width, pix.height)

        # Convert CMYK or other colorspaces to RGB for pixel inspection
        if pix.colorspace and pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)

        samples = pix.samples
        # Hash a downsampled slice + dimensions so identical logos with different xrefs match
        h_slice = samples[:: max(1, len(samples) // 2048)]
        info["sha1"] = hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.alpha}:".encode() + bytes(h_slice)
        ).hexdigest()

        n = pix.n  # channels including alpha
        has_inline_alpha = bool(pix.alpha)
        if has_inline_alpha:
            info["has_alpha"] = True

        total_px = pix.width * pix.height
        stride = max(1, total_px // 4096) * n

        dark_pixels = 0
        faint_watermark_pixels = 0
        white_or_clear_pixels = 0
        alpha_non_zero_sum = 0
        alpha_non_zero_cnt = 0
        sampled_px = 0

        for idx in range(0, len(samples) - n + 1, stride):
            sampled_px += 1
            a = samples[idx + n - 1] if has_inline_alpha else 255

            if has_inline_alpha:
                if a <= 5:
                    white_or_clear_pixels += 1
                    continue
                alpha_non_zero_sum += a
                alpha_non_zero_cnt += 1

            if n - pix.alpha == 1:
                lum = samples[idx]
            else:
                r_c, g_c, b_c = samples[idx], samples[idx + 1], samples[idx + 2]
                lum = (r_c * 299 + g_c * 587 + b_c * 114) // 1000

            if lum >= 246:
                white_or_clear_pixels += 1
            elif lum < 145 and a > 160:
                dark_pixels += 1
            else:
                # Mid-light / pastel / washed-out gray/color pixel (typical pre-faded watermark)
                faint_watermark_pixels += 1

        if sampled_px > 0:
            info["dark_ink_ratio"] = dark_pixels / sampled_px
            if has_inline_alpha and not smask_xref:
                info["transparent_ratio"] = white_or_clear_pixels / sampled_px
                if alpha_non_zero_cnt > 0:
                    info["mean_alpha"] = alpha_non_zero_sum / alpha_non_zero_cnt
                    if info["mean_alpha"] < 175:
                        info["is_low_opacity_alpha"] = True

            # Pre-faded RGB watermark on white background:
            # Very few dark ink pixels (< 2.5%), mostly white/clear + faint gray/pastel pixels
            if (
                info["dark_ink_ratio"] < 0.025
                and faint_watermark_pixels > 0
                and (white_or_clear_pixels + faint_watermark_pixels) / sampled_px > 0.96
            ):
                info["is_washed_out_faint"] = True

    except Exception:
        pass

    return info


def _purge_image_names_from_streams(doc: fitz.Document, page: fitz.Page, target_xrefs: set[int]) -> int:
    """
    Removes `/ImX Do` operator invocations for target image xrefs from both the page's
    content streams and any nested `/Subtype /Form` XObjects referenced on the page.
    """
    removed = 0
    try:
        # 1) Map XObject names (e.g. /Im0, /Fm1) on the page and inside Form XObjects
        for item in page.get_xobjects():
            # item = (xref, name, invoker_xref, bbox)
            x_xref = item[0]
            x_name = item[1]
            if x_xref in target_xrefs and x_name:
                # Strip `/x_name Do` from all content streams of the page
                pattern = re.compile(rb"/" + re.escape(x_name.encode("latin1")) + rb"\s+Do\b")
                for c_xref in page.get_contents():
                    stream = doc.xref_stream(c_xref)
                    if stream and pattern.search(stream):
                        new_stream = pattern.sub(b"", stream)
                        doc.update_stream(c_xref, new_stream)
                        removed += 1

                # Also check if invoked inside a Form XObject
                invoker = item[2]
                if invoker and invoker > 0:
                    f_stream = doc.xref_stream(invoker)
                    if f_stream and pattern.search(f_stream):
                        doc.update_stream(invoker, pattern.sub(b"", f_stream))
                        removed += 1
    except Exception:
        pass

    # 2) Also check Form XObjects that exist solely as a single-image watermark stamp
    try:
        for item in page.get_xobjects():
            form_xref = item[0]
            form_name = item[1]
            subtype = doc.xref_get_key(form_xref, "Subtype")
            if subtype and subtype[1] == "/Form":
                f_stream = doc.xref_stream(form_xref) or b""
                # Check if this Form XObject contains competitor text or references a watermark image
                f_text = f_stream.decode("latin1", errors="ignore")
                if _is_competitor_text(f_text):
                    doc.update_stream(form_xref, b"")
                    removed += 1
                    continue

                # Check if Form's /Resources /XObject references any target_xrefs
                res = doc.xref_get_key(form_xref, "Resources")
                if res and any(f"{tx} 0 R" in res[1] for tx in target_xrefs):
                    # Blank out the watermark Form stream if it's small
                    if len(f_stream) < 4096:
                        doc.update_stream(form_xref, b"")
                        removed += 1
    except Exception:
        pass

    return removed


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    In-place removal of existing text watermarks, hyperlink watermarks, and
    low-opacity / repeated / centered / footer watermark logo images across a PyMuPDF Document.
    Carefully preserves full-page scanned note images and actual study diagrams.
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    # Cache pixel analysis per xref so we only inspect each image once
    xref_analysis_cache: dict[int, dict] = {}
    hash_page_occurrences: Counter[str] = Counter()
    xref_geometries: dict[int, list[dict]] = {}

    # ------------------------------------------------------------------
    # PASS 1: Inspect all images across pages (Position + Pixel Faintness + Hash)
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        r = page.rect
        page_area = max(1.0, r.width * r.height)
        page_cx = r.x0 + r.width / 2.0
        page_cy = r.y0 + r.height / 2.0

        seen_hashes_on_page: set[str] = set()

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref not in xref_analysis_cache:
                xref_analysis_cache[xref] = _analyze_image_faintness(doc, xref)
            faint_info = xref_analysis_cache[xref]

            rects = page.get_image_rects(xref)
            if not rects:
                continue

            for ir in rects:
                area_ratio = (ir.width * ir.height) / page_area
                ir_cx = ir.x0 + ir.width / 2.0
                ir_cy = ir.y0 + ir.height / 2.0

                # Centered check (generous tolerance for slightly off-center logos)
                is_centered = (
                    abs(ir_cx - page_cx) <= r.width * 0.24
                    and abs(ir_cy - page_cy) <= r.height * 0.24
                )
                # Header / Footer / Corner stamp check
                is_edge_stamp = (
                    ir.y0 >= r.y1 - r.height * 0.14
                    or ir.y1 <= r.y0 + r.height * 0.12
                )

                xref_geometries.setdefault(xref, []).append({
                    "page": p_idx,
                    "area_ratio": area_ratio,
                    "height_ratio": ir.height / max(1.0, r.height),
                    "is_centered": is_centered,
                    "is_edge_stamp": is_edge_stamp,
                })

            if faint_info["sha1"]:
                seen_hashes_on_page.add(faint_info["sha1"])

        for h in seen_hashes_on_page:
            hash_page_occurrences[h] += 1

    # ------------------------------------------------------------------
    # Decide which image xrefs are watermarks
    # ------------------------------------------------------------------
    watermark_xrefs: set[int] = set()

    for xref, geoms in xref_geometries.items():
        faint = xref_analysis_cache.get(xref, {})
        img_hash = faint.get("sha1", "")
        repeat_pages = hash_page_occurrences.get(img_hash, 1)

        avg_area = sum(g["area_ratio"] for g in geoms) / len(geoms)
        any_centered = any(g["is_centered"] for g in geoms)
        any_edge = any(g["is_edge_stamp"] for g in geoms)

        is_faint_or_low_alpha = (
            faint.get("is_low_opacity_alpha", False)
            or faint.get("is_washed_out_faint", False)
        )
        has_alpha = faint.get("has_alpha", False)
        transparent_ratio = faint.get("transparent_ratio", 0.0)
        dark_ink_ratio = faint.get("dark_ink_ratio", 1.0)

        # SAFETY GUARD: Never delete a real full-page scanned note image!
        # A real full-page scan covers > 70% of the page AND is opaque (not a transparent overlay)
        # AND contains real dark ink notes (dark_ink_ratio >= 0.015).
        if avg_area > 0.72:
            is_fullpage_watermark_overlay = (
                (has_alpha and transparent_ratio > 0.45 and is_faint_or_low_alpha)
                or (is_faint_or_low_alpha and dark_ink_ratio < 0.015)
            )
            if is_fullpage_watermark_overlay:
                watermark_xrefs.add(xref)
            continue

        # RULE 1: Any low-opacity / faded image in the center or header/footer of the page
        # (Works even on a 1-page PDF or when every page has a unique xref!)
        if is_faint_or_low_alpha and (any_centered or any_edge) and avg_area >= 0.004:
            watermark_xrefs.add(xref)
            continue

        # RULE 2: Centered overlay image with alpha transparency (e.g. PNG logo with transparent bg)
        # that sits in the middle of the page (size between 2% and 70% of page)
        if any_centered and has_alpha and transparent_ratio > 0.18 and 0.02 <= avg_area <= 0.70:
            watermark_xrefs.add(xref)
            continue

        # RULE 3: Image (by content SHA1 hash, even if xrefs differ) repeats across multiple pages
        if num_pages >= 2 and (repeat_pages >= max(2, int(num_pages * 0.35)) or repeat_pages >= 3):
            if any_centered or any_edge or is_faint_or_low_alpha or has_alpha:
                watermark_xrefs.add(xref)
                continue

        # RULE 4: Pre-faded / washed-out RGB image anywhere on the page with almost zero dark ink
        if faint.get("is_washed_out_faint", False) and avg_area >= 0.015:
            watermark_xrefs.add(xref)
            continue

    # ------------------------------------------------------------------
    # PASS 2: Delete watermark images, clean Form XObject streams, redact text & links
    # ------------------------------------------------------------------
    for page in doc:
        r = page.rect
        page_area = max(1.0, r.width * r.height)

        page_xrefs = {img[0] for img in page.get_images(full=True)}
        xrefs_to_remove_on_page: set[int] = set()

        for xref in page_xrefs:
            should_delete = xref in watermark_xrefs

            # Also catch small footer/header logo stamps near top/bottom margins
            if not should_delete:
                for ir in page.get_image_rects(xref):
                    area_ratio = (ir.width * ir.height) / page_area
                    if area_ratio > 0.72:
                        continue
                    if (
                        ir.y0 >= r.y1 - r.height * 0.10
                        and (ir.height / r.height) <= 0.09
                        and area_ratio <= 0.14
                    ):
                        should_delete = True
                        break

            if should_delete:
                xrefs_to_remove_on_page.add(xref)

        # 2A) Purge `/ImX Do` references inside page Contents and Form XObjects first,
        # then call page.delete_image(xref)
        if xrefs_to_remove_on_page:
            _purge_image_names_from_streams(doc, page, xrefs_to_remove_on_page)
            for xref in xrefs_to_remove_on_page:
                try:
                    page.delete_image(xref)
                    removed_image_count += 1
                except Exception:
                    pass

        # 2B) Redact competitor watermark text lines/spans (without touching underlying note images)
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

        # 2C) Strip clickable competitor links (URI annotations)
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
    Strips existing third-party watermarks (text, links, low-opacity centered/footer logos)
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
