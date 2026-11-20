#!/usr/bin/env python3
"""
KTU 2024 Scheme First Year Syllabus Splitter & JSON Index Builder
Splits Group A, B, C, D official KTU PDFs into clean per-subject PDFs,
strips cover/divider pages, deduplicates common courses across groups/semesters,
and outputs a rich syllabus_first_year.json with metadata, modules & NPTEL links.
"""

import json
import re
from pathlib import Path
import fitz  # PyMuPDF

RAW_DIR = Path("raw-syllabus")
OUT_PDF_DIR = Path("syllabus/pdfs")
OUT_JSON = Path("syllabus/syllabus_first_year.json")
OUT_REPORT = Path("syllabus/build_report.txt")

# Group definitions (Official KTU 2024 B.Tech Grouping)
GROUP_META = {
    "A": {
        "id": "Group A",
        "label": "Group A",
        "branches": "CSE, IT, AI & DS, Cyber Security, CSBS & Allied Branches"
    },
    "B": {
        "id": "Group B",
        "label": "Group B",
        "branches": "ECE, EEE, EIE, Applied Electronics, Robotics, Biomedical & Allied Branches"
    },
    "C": {
        "id": "Group C",
        "label": "Group C",
        "branches": "CE, ME, Chemical, Automobile, Mechatronics, Industrial, Aeronautics, Agriculture, Naval Arch, Polymer, Safety & Allied Branches"
    },
    "D": {
        "id": "Group D",
        "label": "Group D",
        "branches": "Biotechnology, Biochemical Engineering & Food Technology"
    }
}

COURSE_CODE_RE = re.compile(r"\b([A-Z]{4,5}\d{3})\b")


def clean_space(text: str) -> str:
    text = text.replace("\ufffd", "-").replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def get_sorted_lines(page: fitz.Page):
    """Return text lines sorted strictly top-to-bottom (fixes out-of-order PDF streams like GXESL106)."""
    blocks = page.get_text("blocks")
    blocks.sort(key=lambda b: (round(b[1] / 4), b[0]))
    lines = []
    for b in blocks:
        if b[6] != 0:  # skip non-text blocks
            continue
        for ln in b[4].splitlines():
            s = clean_space(ln)
            if s:
                lines.append((b[1], s))  # (y0, text)
    return lines


def is_divider_or_cover_page(page: fitz.Page, page_idx: int) -> bool:
    """Detect cover page (page 0) or section divider pages like 'SEMESTER 1 / GROUP A', 'PROGRAMME CORE 1'."""
    if page_idx == 0:
        return True
    raw = clean_space(page.get_text("text"))
    stripped = re.sub(r"B\.?\s*Tech\s*2024\s*[–-]\s*S1/S2", "", raw, flags=re.I)
    stripped = re.sub(r"APJ\s+Abdul\s+Kalam\s+Technological\s+University\s*\d*", "", stripped, flags=re.I)
    stripped = clean_space(stripped)

    if len(stripped) < 90:
        divider_patterns = [
            r"^SEMESTER\s*[12]\s*GROUP\s*[A-D]$",
            r"^GROUP\s*[A-D]\s*SEMESTER\s*[12]$",
            r"^PROGRAMME\s+CORE(\s+\d+)?$",
            r"^SEMESTER\s*S?[12]$",
            r"^ELECTIVE",
            r"^FIRST\s+YEAR\s+SYLLABUS",
        ]
        for pat in divider_patterns:
            if re.search(pat, stripped, flags=re.I):
                return True
        if len(stripped) < 35 and not re.search(r"(Module|Experiment|CO\d|Text Books|Reference)", stripped, re.I):
            return True
    return False


def detect_course_start(page: fitz.Page):
    """
    Returns dict of course metadata if this page is the FIRST page of a KTU 2024 subject syllabus.
    Otherwise returns None.
    """
    full_text = page.get_text("text")
    has_course_code_lbl = bool(re.search(r"Course\s+Code", full_text, re.I))
    has_cie = bool(re.search(r"CIE\s+Marks", full_text, re.I))
    has_credits = bool(re.search(r"\bCredits\b", full_text, re.I))
    if not (has_course_code_lbl and (has_cie or has_credits)):
        return None

    rect = page.rect
    top_clip = fitz.Rect(0, 0, rect.width, rect.height * 0.48)
    top_text = page.get_text("text", clip=top_clip)

    # Extract Metadata Table Fields first (handles spaces in codes like "PCBBT 205")
    code = cie = ese = credits = ltpr = exam_hours = course_type = ""
    try:
        tables = page.find_tables(clip=top_clip)
        if tables and tables.tables:
            for row in tables.tables[0].extract():
                cells = [clean_space(c or "") for c in row]
                for i in range(len(cells) - 1):
                    k = cells[i].lower()
                    v = cells[i + 1]
                    if not v:
                        continue
                    if "course code" in k and not code:
                        m_code = re.search(r"([A-Z]{4,5}\s*\d{3})\b", v, re.I)
                        if m_code:
                            code = re.sub(r"\s+", "", m_code.group(1)).upper()
                    elif "cie marks" in k and not cie:
                        cie = v
                    elif "ese marks" in k and not ese:
                        ese = v
                    elif k == "credits" and not credits:
                        credits = v
                    elif "teaching hours" in k and not ltpr:
                        ltpr = v
                    elif "exam hours" in k and not exam_hours:
                        exam_hours = v
                    elif "course type" in k and not course_type:
                        course_type = v
    except Exception:
        pass

    # Regex fallback for Course Code (allows optional space before digits)
    if not code:
        code_match = re.search(r"Course\s+Code\s*[:\-]?\s*([A-Z]{4,5}\s*\d{3})\b", top_text, re.I)
        if not code_match:
            code_match = COURSE_CODE_RE.search(top_text)
        if not code_match:
            return None
        code = re.sub(r"\s+", "", code_match.group(1)).upper()

    # Extract spatial lines above the "Course Code" row to reliably get Semester, Title, and Common Note
    sorted_lines = get_sorted_lines(page)
    table_y = rect.height * 0.35
    for y0, text in sorted_lines:
        if re.search(r"Course\s+Code", text, re.I):
            table_y = y0
            break

    header_lines = []
    for y0, text in sorted_lines:
        if y0 >= table_y - 2:
            break
        if re.search(r"^B\.?\s*Tech\s*2024", text, re.I):
            continue
        if re.search(r"^APJ\s+Abdul\s+Kalam", text, re.I):
            continue
        header_lines.append(text)

    sem_label = ""
    common_note = ""
    title_parts = []

    for ln in header_lines:
        if re.match(r"^SEMESTER\b", ln, re.I):
            sem_label = ln
        elif ln.startswith("(") and ln.endswith(")"):
            common_note = ln.strip("() ").strip()
        elif re.search(r"^\(?\s*Common\s+to\b", ln, re.I):
            common_note = ln.strip("() ").strip()
        else:
            title_parts.append(ln)

    raw_title = clean_space(" ".join(title_parts))
    raw_title = re.sub(r"ESSENTIALSTO", "ESSENTIALS TO", raw_title, flags=re.I)
    raw_title = re.sub(r"\s*[-–]\s*([12])$", r" - \1", raw_title)
    title = raw_title.title() if raw_title.isupper() else raw_title
    for acr in ["IPR", "IT", "CAD", "AI", "ML", "IoT", "CSE", "ECE", "EEE", "ME", "CE", "C", "C++", "PCB", "VLSI"]:
        title = re.sub(rf"\b{re.escape(acr)}\b", acr, title, flags=re.I)
    if not title:
        title = code

    # Use KTU 2024 course code numbering first (12x = S1/S2, 1xx = S1, 2xx = S2)
    num_m = re.search(r"(\d{3})$", code)
    if num_m:
        digits = num_m.group(1)
        if digits.startswith("12"):
            semesters = ["S1", "S2"]
        elif digits.startswith("1"):
            semesters = ["S1"]
        elif digits.startswith("2"):
            semesters = ["S2"]
        else:
            semesters = ["S1"]
    else:
        sem_src = sem_label.upper()
        if re.search(r"S?1\s*/\s*S?2", sem_src):
            semesters = ["S1", "S2"]
        elif re.search(r"\bS?2\b", sem_src):
            semesters = ["S2"]
        else:
            semesters = ["S1"]

    # Regex fallbacks if table extraction missed anything (single-line safe)
    if not cie:
        m = re.search(r"CIE\s+Marks[ \t]+(\d+)", top_text, re.I)
        if m:
            cie = m.group(1)
    if not ese:
        m = re.search(r"ESE\s+Marks(?:\s*\([^)]*\))?[ \t]+(\d+)", top_text, re.I)
        if m:
            ese = m.group(1)
    if not credits:
        m = re.search(r"Credits[ \t]+(\d+)", top_text, re.I)
        if m:
            credits = m.group(1)
    if not ltpr:
        m = re.search(r"\b(\d\s*[:\-]\s*\d\s*[:\-]\s*\d\s*[:\-]\s*\d)\b", top_text)
        if m:
            ltpr = m.group(1)
    if ltpr:
        ltpr = re.sub(r"\s*[:\-]\s*", ":", ltpr)
    if not course_type:
        m = re.search(r"Course\s+Type[ \t]+([A-Za-z0-9 &+\-/]+)", top_text, re.I)
        if m and not re.search(r"Course\s+Objectives?", m.group(1), re.I):
            course_type = clean_space(m.group(1))
    if not course_type:
        course_type = "Activity / Theory" if ese == "0" else "Theory"

    return {
        "code": code,
        "title": title,
        "common_note": common_note,
        "semesters": semesters,
        "credits": credits,
        "cie": cie,
        "ese": ese,
        "ltpr": ltpr,
        "exam_hours": exam_hours,
        "course_type": course_type,
    }


def extract_modules_and_links(doc: fitz.Document, start_p: int, end_p: int):
    """Extract concise Module 1-4 snippets and NPTEL/SWAYAM video links from a subject's page range."""
    modules = {}
    video_links = []
    seen_links = set()

    for pno in range(start_p, end_p + 1):
        page = doc[pno]
        txt = page.get_text("text")

        # Extract NPTEL / SWAYAM / course links
        for url in re.findall(r"https?://[^\s\)\]]+", txt):
            url = url.rstrip(".,;")
            if any(dom in url.lower() for dom in ["nptel", "swayam", "youtube", "youtu.be", "nand2tetris", "w3schools", "overthewire", "opentextbc"]):
                if url not in seen_links:
                    seen_links.add(url)
                    video_links.append(url)

        # Extract Modules from KTU 3-column syllabus tables (Module No | Syllabus Description | Contact Hours)
        try:
            tables = page.find_tables()
            for tbl in tables.tables:
                rows = tbl.extract()
                if not rows:
                    continue
                header_str = " ".join(clean_space(x or "") for x in rows[0])
                if re.search(r"(Sl\.?\s*No|Expt\.?\s*No|Experiment|Benchmark\s*Score|Title of the Book|Activity)", header_str, re.I):
                    continue
                for r in rows:
                    if not r or len(r) != 3:
                        continue
                    c0 = clean_space(r[0] or "")
                    c1 = clean_space(r[1] or "")
                    if c0 in ("1", "2", "3", "4") and len(c1) > 25 and not c1.startswith("http"):
                        mod_num = int(c0)
                        if mod_num not in modules:
                            modules[mod_num] = c1[:360] + ("..." if len(c1) > 360 else "")
        except Exception:
            pass

    ordered_mods = [{"no": k, "summary": modules[k]} for k in sorted(modules.keys())]
    return ordered_mods, video_links[:8]


def detect_group_from_filename(path: Path) -> str:
    name = path.stem.upper()
    m = re.search(r"GROUP[\s_\-]*([A-D])", name)
    if m:
        return m.group(1)
    if name in ("A", "B", "C", "D"):
        return name
    return "A"


def process_all_pdfs():
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"[ERROR] No PDFs found in {RAW_DIR.resolve()}")
        return

    # Clean old split PDFs automatically so no stale files remain
    OUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    for old_pdf in OUT_PDF_DIR.glob("*.pdf"):
        old_pdf.unlink()

    master_courses = {}  # keyed by course_code
    report_lines = ["KTU 2024 FIRST YEAR SYLLABUS BUILD REPORT", "=" * 55, ""]

    for pdf_path in pdf_files:
        grp_letter = detect_group_from_filename(pdf_path)
        group_name = f"Group {grp_letter}"
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        report_lines.append(f"SOURCE: {pdf_path.name} ({group_name}) — {total_pages} pages")

        # Pass 1: Locate every subject start page + every divider/cover page
        starts = []
        dividers = set()
        current_section_sem = "S1"

        for i in range(total_pages):
            page = doc[i]
            if is_divider_or_cover_page(page, i):
                dividers.add(i)
                ptxt = page.get_text("text").upper()
                if "SEMESTER 2" in ptxt or "SEMESTER S2" in ptxt:
                    current_section_sem = "S2"
                elif "SEMESTER 1" in ptxt or "SEMESTER S1" in ptxt:
                    current_section_sem = "S1"
                continue

            meta = detect_course_start(page)
            if meta:
                meta["section_sem"] = current_section_sem
                starts.append((i, meta))

        # Pass 2: Compute exact clean page ranges [start_p .. end_p], stripping trailing dividers
        for idx, (start_p, meta) in enumerate(starts):
            next_start = starts[idx + 1][0] if idx + 1 < len(starts) else total_pages
            end_p = next_start - 1

            while end_p > start_p and end_p in dividers:
                end_p -= 1

            code = meta["code"]
            page_count = (end_p - start_p) + 1
            pdf_out_path = OUT_PDF_DIR / f"{code}.pdf"
            rel_pdf_url = f"/syllabus/pdfs/{code}.pdf"

            should_write = (code not in master_courses) or (page_count > master_courses[code]["pages"])
            if should_write:
                sub_doc = fitz.open()
                sub_doc.insert_pdf(doc, from_page=start_p, to_page=end_p)
                sub_doc.save(pdf_out_path, garbage=4, deflate=True)
                sub_doc.close()

            modules, video_links = extract_modules_and_links(doc, start_p, end_p)

            sems_found = set(meta["semesters"])
            if meta["section_sem"] in ("S1", "S2") and len(sems_found) == 0:
                sems_found.add(meta["section_sem"])

            if code not in master_courses:
                master_courses[code] = {
                    "code": code,
                    "title": meta["title"],
                    "common_note": meta["common_note"],
                    "groups": [group_name],
                    "semesters": sorted(sems_found),
                    "credits": meta["credits"],
                    "cie": meta["cie"],
                    "ese": meta["ese"],
                    "ltpr": meta["ltpr"],
                    "exam_hours": meta["exam_hours"],
                    "course_type": meta["course_type"],
                    "pages": page_count,
                    "pdf_url": rel_pdf_url,
                    "modules": modules,
                    "video_links": video_links,
                }
            else:
                entry = master_courses[code]
                if group_name not in entry["groups"]:
                    entry["groups"].append(group_name)
                entry["semesters"] = sorted(set(entry["semesters"]) | sems_found)
                if len(modules) > len(entry["modules"]):
                    entry["modules"] = modules
                if len(video_links) > len(entry["video_links"]):
                    entry["video_links"] = video_links
                if page_count > entry["pages"]:
                    entry["pages"] = page_count

            report_lines.append(
                f"  - {code:10s} | p.{start_p+1:3d}-{end_p+1:3d} ({page_count}p) | {','.join(sorted(sems_found)):5s} | {meta['title']}"
            )

        report_lines.append("")
        doc.close()

    # Sort final list: S1 before S2, then alphabetical by course code
    courses_list = sorted(
        master_courses.values(),
        key=lambda c: (0 if "S1" in c["semesters"] else 1, c["code"])
    )

    payload = {
        "scheme": "2024",
        "level": "First Year (S1 & S2)",
        "groups": list(GROUP_META.values()),
        "total_courses": len(courses_list),
        "courses": courses_list,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[DONE] Extracted {len(courses_list)} unique First Year subjects into {OUT_PDF_DIR}")
    print(f"[DONE] Index written to {OUT_JSON}")
    print(f"[DONE] Report written to {OUT_REPORT}")


if __name__ == "__main__":
    process_all_pdfs()
