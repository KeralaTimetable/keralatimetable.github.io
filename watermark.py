"""
watermark.py
------------
Add your brand watermark (centered logo + bottom text) to KTU question paper PDFs,
and merge multiple papers into one branded file. Pure-Python, uses PyMuPDF.
"""

from __future__ import annotations
import fitz  # PyMuPDF


def add_watermark(pdf_bytes: bytes,
                  logo_bytes: bytes | None = None,
                  text: str | None = "Downloaded from Keralatimetable.in",
                  logo_scale: float = 0.65,
                  text_color=(0.2, 0.2, 0.2)) -> bytes:
    """Return new PDF bytes with a centered logo and bottom-center text."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    logo_ratio = None
    if logo_bytes:
        lp = fitz.open(stream=logo_bytes, filetype="png")
        logo_ratio = lp[0].rect.height / lp[0].rect.width
        lp.close()

    for page in doc:
        r = page.rect

        # 1) Large Logo image, centered in the middle of the page
        if logo_bytes and logo_ratio:
            w = r.width * logo_scale
            h = w * logo_ratio
            
            # Calculate coordinates for absolute center
            x0 = (r.width - w) / 2
            y0 = (r.height - h) / 2
            
            box = fitz.Rect(x0, y0, x0 + w, y0 + h)
            # overlay=True puts it on top. It respects native PNG transparency.
            page.insert_image(box, stream=logo_bytes, overlay=True)

        # 2) Text watermark, bottom center, full opacity
        if text:
            font_size = 12
            # Calculate text width to perfectly center it horizontally
            text_length = fitz.get_text_length(text, fontname="helv", fontsize=font_size)
            x_text = (r.width - text_length) / 2
            y_text = r.height - 30  # 30 units up from the bottom edge
            
            # Insert text at the calculated point with full opacity
            page.insert_text(fitz.Point(x_text, y_text), text, fontsize=font_size, fontname="helv", color=text_color, overlay=True)

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
    # demo: python watermark.py input.pdf logo.png output.pdf
    inp, logo, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    pdf = open(inp, "rb").read()
    lg = open(logo, "rb").read()
    open(outp, "wb").write(add_watermark(pdf, logo_bytes=lg, text="Downloaded from Keralatimetable.in"))
    print("wrote", outp)

