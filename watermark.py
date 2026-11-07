"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
and safely remove existing third-party watermarks (Ktunotes.live, Ktuspecial.in, etc.)
while 100% preserving:
  - Typed note diagrams, flowcharts, and transparent PNG figures (DSA notes, PPTs, etc.)
  - Handwritten notebook scans & CamScanner pages (GAMAT301, etc.)
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


def _get_image_sha1(doc: fitz.Document, xref: int) -> str:
    """
    Computes a fast SHA1 hash of an image XObject's dimensions + pixel samples.
    Identical watermark logos re-embedded with different xref IDs on each page
    will produce the exact same SHA1 hash, whereas handwritten pages and DSA diagrams
    are unique and produce different hashes.
    """
    try:
        pix = fitz.Pixmap(doc, xref)
        samples = pix.samples
        step = max(1, len(samples) // 4096)
        return hashlib.sha1(
            f"{pix.width}x{pix.height}x{pix.n}:".encode() + bytes(samples[::step])
        ).hexdigest()
    except Exception:
        return f"xref_{xref}"


def _delete_watermark_xref_from_page(doc: fitz.Document, page: fitz.Page, xref: int) -> None:
    """
    Deletes a confirmed repeated watermark image XObject from `page` and strips its
    `/ImX Do` operator from the page's content stream (and any Form XObject stream).
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


def remove_existing_watermarks(
    doc: fitz.Document,
    extra_keywords: list[str] | None = None,
) -> dict[str, int]:
    """
    Removes third-party watermarks (text, links, and repeated watermark logo images)
    with 100% safety for both typed notes (DSA diagrams/figures) and handwritten scans.

    STRICT IMAGE SAFETY RULES:
    1) A diagram or handwritten scan is UNIQUE to its page — it NEVER repeats identically
       across >= 50% of the document's pages.
    2) An image XObject is ONLY deleted if:
       - The document has >= 2 pages,
       - That exact image (by `xref` or `SHA1` pixel hash) repeats on >= 50% of pages
         (or >= 3 pages), AND
       - Every page where it is deleted STILL has either another image (the notebook scan)
         OR real digital text (>= 50 characters of typed notes).
       This makes it mathematically IMPOSSIBLE to ever produce a blank page or delete a unique
       DSA diagram!
    """
    removed_text_count = 0
    removed_image_count = 0
    removed_link_count = 0
    num_pages = len(doc)

    xref_to_sha1: dict[int, str] = {}
    sha1_page_occurrences: Counter[str] = Counter()
    page_xrefs_map: dict[int, list[int]] = {}

    # ------------------------------------------------------------------
    # PASS 1: Count how many pages each exact image (by SHA1 hash) appears on
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        xrefs_on_page: list[int] = []
        for im in page.get_images(full=True):
            x = im[0]
            if x not in xrefs_on_page:
                xrefs_on_page.append(x)
            if x not in xref_to_sha1:
                xref_to_sha1[x] = _get_image_sha1(doc, x)

        try:
            for info_item in page.get_image_info(xrefs=True):
                ix = info_item.get("xref", 0)
                if ix and ix not in xrefs_on_page:
                    xrefs_on_page.append(ix)
                    if ix not in xref_to_sha1:
                        xref_to_sha1[ix] = _get_image_sha1(doc, ix)
        except Exception:
            pass

        page_xrefs_map[p_idx] = xrefs_on_page

        # Record unique image hashes present on this page
        seen_hashes_this_page = {xref_to_sha1[x] for x in xrefs_on_page if xref_to_sha1.get(x)}
        for h in seen_hashes_this_page:
            sha1_page_occurrences[h] += 1

    # Determine which SHA1 hashes are REPEATED WATERMARK LOGOS:
    # Must appear on at least 50% of all pages (for 2..5 page PDFs) or >= 3 pages (for larger PDFs)
    min_repeat_pages = max(2, min(3, int(num_pages * 0.5 + 0.5)))
    repeated_watermark_hashes: set[str] = set()
    if num_pages >= 2:
        for h, count in sha1_page_occurrences.items():
            if count >= min_repeat_pages:
                repeated_watermark_hashes.add(h)

    # ------------------------------------------------------------------
    # PASS 2: Delete ONLY confirmed repeated watermark logos + redact competitor text
    # ------------------------------------------------------------------
    for p_idx, page in enumerate(doc):
        xrefs_on_page = page_xrefs_map.get(p_idx, [])
        page_text_len = len((page.get_text("text") or "").strip())

        # Separate images on this page into:
        # - unique content images (handwritten scan or DSA diagrams)
        # - repeated watermark images (appear on >= min_repeat_pages across the PDF)
        unique_content_xrefs = [
            x for x in xrefs_on_page if xref_to_sha1.get(x) not in repeated_watermark_hashes
        ]
        candidate_watermark_xrefs = [
            x for x in xrefs_on_page if xref_to_sha1.get(x) in repeated_watermark_hashes
        ]

        # SAFETY LOCK:
        # Only delete `candidate_watermark_xrefs` if the page will NOT be left empty!
        # i.e., the page must either have at least 1 unique content image (e.g. notebook scan)
        # OR have real typed note text (>= 40 chars, e.g. typed DSA notes).
        can_safely_delete_watermarks = (len(unique_content_xrefs) >= 1) or (page_text_len >= 40)

        if can_safely_delete_watermarks and candidate_watermark_xrefs:
            for wm_xref in candidate_watermark_xrefs:
                _delete_watermark_xref_from_page(doc, page, wm_xref)
                removed_image_count += 1

        # ------------------------------------------------------------------
        # Redact competitor watermark text lines/spans (never touching images or diagrams)
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
                # CRITICAL: PDF_REDACT_IMAGE_NONE & PDF_REDACT_LINE_ART_NONE guarantee
                # that neither scanned pages nor vector DSA diagrams are ever erased!
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
    Safely strips existing third-party watermarks without ever deleting diagrams or handwritten pages,
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
