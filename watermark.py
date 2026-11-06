"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
remove existing third-party watermarks (text, links & logo images like Ktunotes.live,
Ktuspecial.in, etc.), and merge multiple papers/notes into one branded file.
Pure-Python, uses PyMuPDF (fitz).
"""

from __future__ import annotations
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

    # Check custom user-supplied keywords first
    if extra_keywords:
        for kw in extra_keywords:
            kw_clean = kw.strip().lower()
            if kw_clean and kw_clean in low:
                return True

    # Check regex for "Downloaded from xyz.in / ktunotes.live / ktuspecial.in"
    if WATERMARK_TEXT_REGEX.search(cleaned):
        return True

    # Check known competitor domains/keywords (only on short watermark-like lines <= 120 chars
    # so legitimate paragraph references aren't accidentally wiped)
    if len(cleaned) <= 120:
        for kw in DEFAULT_COMPETITOR_KEYWORDS:
            if kw in low:
                return True

    return False


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    In-place removal of existing text watermarks, hyperlink watermarks, and
    centered/footer watermark logo images across a PyMuPDF Document.
    Carefully preserves full-page scanned note images and actual study content.
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    # ------------------------------------------------------------------
    # PASS 1: Identify repeated watermark XObject images across pages
    # ------------------------------------------------------------------
    xref_page_occurrences: Counter[int] = Counter()
    xref_geometry: dict[int, list[tuple[float, float, bool, bool]]] = {}

    for page in doc:
        r = page.rect
        page_area = max(1.0, r.width * r.height)
        page_center_x = r.x0 + r.width / 2.0
        page_center_y = r.y0 + r.height / 2.0

        seen_on_this_page: set[int] = set()
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            rects = page.get_image_rects(xref)
            if not rects:
                continue

            for ir in rects:
                img_area_ratio = (ir.width * ir.height) / page_area

                # NEVER delete a full-page scan (camscanner / handwritten notes page)
                if img_area_ratio > 0.72:
                    continue

                ir_cx = ir.x0 + ir.width / 2.0
                ir_cy = ir.y0 + ir.height / 2.0

                is_centered = (
                    abs(ir_cx - page_center_x) <= r.width * 0.18
                    and abs(ir_cy - page_center_y) <= r.height * 0.18
                )
                is_header_or_footer_banner = (
                    ir.y0 >= r.y1 - r.height * 0.12
                    or ir.y1 <= r.y0 + r.height * 0.10
                )

                xref_geometry.setdefault(xref, []).append(
                    (img_area_ratio, ir.height / max(1.0, r.height), is_centered, is_header_or_footer_banner)
                )
                seen_on_this_page.add(xref)

        for xref in seen_on_this_page:
            xref_page_occurrences[xref] += 1

    # Decide which image xrefs are watermarks
    watermark_xrefs: set[int] = set()
    for xref, count in xref_page_occurrences.items():
        geoms = xref_geometry.get(xref, [])
        if not geoms:
            continue

        avg_area = sum(g[0] for g in geoms) / len(geoms)
        any_centered = any(g[2] for g in geoms)
        any_edge_stamp = any(g[3] for g in geoms)

        # Case A: Multi-page PDF where the same logo/stamp XObject appears on >=2 pages
        # (and at least 40% of pages, or >=3 pages)
        if num_pages >= 2 and (count >= max(2, int(num_pages * 0.4)) or count >= 3):
            if avg_area <= 0.65 and (any_centered or any_edge_stamp):
                watermark_xrefs.add(xref)
                continue

        # Case B: Single-page (or non-shared XObject) centered watermark with alpha/smask
        if any_centered and 0.03 <= avg_area <= 0.58:
            try:
                img_dict = doc.extract_image(xref)
                smask = img_dict.get("smask", 0)
                if smask and smask > 0:
                    watermark_xrefs.add(xref)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # PASS 2: Strip watermark images, text spans, and links on each page
    # ------------------------------------------------------------------
    for page in doc:
        r = page.rect
        page_area = max(1.0, r.width * r.height)

        # 2A) Delete identified watermark images
        page_xrefs = {img[0] for img in page.get_images(full=True)}
        for xref in page_xrefs:
            should_delete = xref in watermark_xrefs

            # Also check if there is a small footer/header logo right next to competitor text
            if not should_delete:
                rects = page.get_image_rects(xref)
                for ir in rects:
                    area_ratio = (ir.width * ir.height) / page_area
                    if area_ratio > 0.72:
                        continue
                    # Small footer stamp at very bottom of page (< 8% height, in bottom 10% margin)
                    if ir.y0 >= r.y1 - r.height * 0.09 and (ir.height / r.height) <= 0.08 and area_ratio <= 0.12:
                        should_delete = True
                        break

            if should_delete:
                try:
                    page.delete_image(xref)
                    removed_image_count += 1
                except Exception:
                    pass

        # 2B) Redact competitor watermark text lines/spans (without touching underlying images)
        page_has_redactions = False
        try:
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if block.get("type") != 0:  # 0 = text block
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
                        # Check individual spans in case watermark shares a line bbox
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
                # CRITICAL: images=PDF_REDACT_IMAGE_NONE ensures scanned notes images are NEVER blanked out
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
        # Normalize against peak alpha so slider 1%..100% maps to true 1%..100% opacity
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
    Optionally strips existing third-party watermarks (Ktunotes.live, Ktuspecial.in, etc.)
    and returns new PDF bytes with a centered logo and bottom-center text.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Step 1: Clean competitor watermarks (text, links, and repeated/centered logos)
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
    Cleaning each PDF before merging ensures per-document repeated watermark detection is accurate.
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
            clean_existing=False,  # Already cleaned per document
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
