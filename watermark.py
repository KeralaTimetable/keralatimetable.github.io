"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper & notes PDFs,
and merge multiple papers/notes into one branded file. Pure-Python, uses PyMuPDF.
Supports A4 Portrait, Landscape, 16:9 PPT, and 4:3 Slide ratios automatically.
"""

from __future__ import annotations
import fitz  # PyMuPDF


def add_watermark(pdf_bytes: bytes,
                  logo_bytes: bytes | None = None,
                  text: str | None = "Downloaded from Keralatimetable.in",
                  logo_scale: float = 0.65,
                  text_color=(0.2, 0.2, 0.2)) -> bytes:
    """Return new PDF bytes with a centered logo and bottom-center text (auto-scales for A4 & PPT ratios)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    logo_ratio = None
    if logo_bytes:
        lp = fitz.open(stream=logo_bytes, filetype="png")
        logo_ratio = lp[0].rect.height / lp[0].rect.width
        lp.close()

    for page in doc:
        r = page.rect
        short_side = min(r.width, r.height)

        # 1) Centered Logo image — uses short_side so 16:9 PPT slides & A4 Portrait both fit properly
        if logo_bytes and logo_ratio:
            w = short_side * logo_scale
            h = w * logo_ratio

            # Safety clamp if logo is very tall on a wide PPT slide
            max_h = r.height * 0.72
            if h > max_h:
                h = max_h
                w = h / logo_ratio

            x0 = r.x0 + (r.width - w) / 2
            y0 = r.y0 + (r.height - h) / 2

            box = fitz.Rect(x0, y0, x0 + w, y0 + h)
            page.insert_image(box, stream=logo_bytes, overlay=True)

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
                overlay=True
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


def brand_papers(pdf_bytes_list: list[bytes],
                 logo_bytes: bytes | None = None,
                 text: str | None = "Downloaded from Keralatimetable.in") -> bytes:
    """Merge a list of PDFs then watermark the whole thing -> branded bytes."""
    merged = merge_pdfs(pdf_bytes_list) if len(pdf_bytes_list) > 1 else pdf_bytes_list[0]
    return add_watermark(merged, logo_bytes=logo_bytes, text=text)


if __name__ == "__main__":
    import sys
    inp, logo, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    pdf = open(inp, "rb").read()
    lg = open(logo, "rb").read()
    open(outp, "wb").write(add_watermark(pdf, logo_bytes=lg, text="Downloaded from Keralatimetable.in"))
    print("wrote", outp)
