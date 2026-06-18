"""
watermark.py
------------
Add your brand watermark (logo + faint diagonal text) to KTU question paper PDFs,
and merge multiple papers into one branded file. Pure-Python, uses PyMuPDF.

This reproduces what KTUSPOT's "library-orchestrator" does:
download -> merge -> stamp logo on every page -> return branded PDF.
"""

from __future__ import annotations
import fitz  # PyMuPDF


def add_watermark(pdf_bytes: bytes,
                  logo_bytes: bytes | None = None,
                  text: str | None = "KTUSPOT.IN",
                  logo_scale: float = 0.22,
                  logo_margin: float = 12,
                  text_opacity: float = 0.12,
                  text_color=(0.55, 0.55, 0.55),
                  angle: int = 45) -> bytes:
    """Return new PDF bytes with a logo (top-right) and a faint diagonal
    repeating text watermark stamped on every page.

    logo_bytes : PNG bytes of your logo (optional)
    text       : diagonal watermark text, e.g. your domain (optional)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    logo_ratio = None
    if logo_bytes:
        lp = fitz.open(stream=logo_bytes, filetype="png")
        logo_ratio = lp[0].rect.height / lp[0].rect.width
        lp.close()

    for page in doc:
        r = page.rect

        # 1) faint diagonal repeating text across the page
        if text:
            tw = fitz.TextWriter(r)
            fs = max(28, r.width / 12)
            for fx, fy in [(0.10, 0.35), (0.30, 0.62), (0.05, 0.85)]:
                tw.append(fitz.Point(r.width * fx, r.height * fy), text, fontsize=fs)
            pivot = fitz.Point(r.width / 2, r.height / 2)
            tw.write_text(page, opacity=text_opacity, color=text_color,
                          morph=(pivot, fitz.Matrix(angle)), overlay=True)

        # 2) logo image, top-right corner
        if logo_bytes and logo_ratio:
            w = r.width * logo_scale
            h = w * logo_ratio
            box = fitz.Rect(r.width - logo_margin - w, logo_margin,
                            r.width - logo_margin, logo_margin + h)
            page.insert_image(box, stream=logo_bytes, overlay=True)

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
                 text: str | None = "KTUSPOT.IN") -> bytes:
    """Merge a list of PDFs then watermark the whole thing -> branded bytes."""
    merged = merge_pdfs(pdf_bytes_list) if len(pdf_bytes_list) > 1 else pdf_bytes_list[0]
    return add_watermark(merged, logo_bytes=logo_bytes, text=text)


if __name__ == "__main__":
    import sys
    # demo: python watermark.py input.pdf logo.png output.pdf
    inp, logo, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    pdf = open(inp, "rb").read()
    lg = open(logo, "rb").read()
    open(outp, "wb").write(add_watermark(pdf, logo_bytes=lg, text="KTUSPOT.IN"))
    print("wrote", outp)
