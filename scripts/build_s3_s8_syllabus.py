#!/usr/bin/env python3
"""
KTU 2024 Scheme S3–S8 Syllabus Splitter & Multi-Branch JSON Index Builder
for keralatimetable.in
"""

import difflib
import json
import re
from pathlib import Path
import pymupdf as fitz

RAW_DIR = Path("raw-syllabus/s3-s8")
OUT_ROOT = Path("syllabus/s3-s8")
OUT_PDF_DIR = OUT_ROOT / "pdfs"
OUT_BRANCHES_JSON = OUT_ROOT / "branches.json"
OUT_SEARCH_JSON = OUT_ROOT / "search_index.json"
OUT_REPORT = OUT_ROOT / "build_report.txt"

BRANCH_META = {
    "CSE":  {"code": "CSE",  "slug": "cse",  "name": "Computer Science and Engineering", "short_name": "CSE", "group": "Group A", "order": 1},
    "AIML": {"code": "AIML", "slug": "aiml", "name": "Computer Science and Engineering (AI & ML)", "short_name": "CSE (AI & ML)", "group": "Group A", "order": 2},
    "ECE":  {"code": "ECE",  "slug": "ece",  "name": "Electronics and Communication Engineering", "short_name": "ECE", "group": "Group B", "order": 3},
    "EEE":  {"code": "EEE",  "slug": "eee",  "name": "Electrical and Electronics Engineering", "short_name": "EEE", "group": "Group B", "order": 4},
    "ME":   {"code": "ME",   "slug": "me",   "name": "Mechanical Engineering", "short_name": "ME", "group": "Group C", "order": 5},
    "CE":   {"code": "CE",   "slug": "ce",   "name": "Civil Engineering", "short_name": "CE", "group": "Group C", "order": 6},
}

# Confirmed official KTU PDF duplicate-code typos
OFFICIAL_CODE_OVERRIDES = {
    ("CSE", "PECST753", "GAME THEORY"): "PECST756",
    ("AIML", "PECST753", "GAME THEORY"): "PECST756",
}

COURSE_CODE_RE = re.compile(r"\b([A-Z]{4,5}\s*\d{3})\b")
URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")
ROMAN_MOD_MAP = {"I": 1, "II": 2, "III": 3, "IV": 4}
SEM_PREFIX_RE = re.compile(
    r"^(?:SEM)?SEMESTER\s*[:\-–—]?\s*(?:S\s*[3-8](?:\s*/\s*S?\s*[3-8])?|[3-8]|VIII|VII|VI|IV|III|V)\b\s*[:\-–—]?\s*",
    re.I,
)

ACRONYMS = [
    "2D", "3D", "5G", "AI", "ML", "DL", "NLP", "LLM", "IoT", "IIoT", "AR", "VR",
    "UI", "UX", "API", "SQL", "NoSQL", "DBMS", "OS", "RTOS", "VLSI", "FPGA",
    "ASIC", "CMOS", "MOS", "DSP", "DIP", "RF", "EMI", "EMC", "PCB", "MEMS",
    "NEMS", "CAD", "CAM", "CAE", "CAPP", "CFD", "CNC", "PLC", "SCADA", "NDT",
    "FEM", "FEA", "FVM", "FMS", "DFMA", "HVAC", "IC", "EV", "HEV", "ICE", "PV",
    "RCC", "GIS", "GPS", "BIM", "AC", "DC", "HVDC", "FACTS", "HV", "LV", "MT",
    "ARM", "RISC", "CISC", "CPU", "GPU", "SDN", "NFV", "VPN", "MPLS", "TCP",
    "IP", "UDP", "HTTP", "HTML5", "CSS", "PHP", "XML", "JSON", "UML", "OOP",
    "PBL", "IPR", "IT", "CSE", "ECE", "EEE", "ME", "CE", "C++", "C", "R",
    "LED", "OLED", "LCD", "LTE", "GSM", "CDMA", "OFDM", "MIMO", "WSN", "MANET",
    "PID", "TQM", "ERP", "MRP", "JIT", "SMED", "OEE", "TPM",
    "I", "II", "III", "IV",
]

BOILERPLATE_PREREQ_RE = re.compile(
    r"^(none|nil|na|n/a|-|--|none\s*/\s*\(?course\s*code\)?|none\s*/)$",
    re.I,
)


def clean_space(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\ufffd", "-").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(raw_title: str, course_code: str = "") -> str:
    t = clean_space(raw_title)
    t = SEM_PREFIX_RE.sub("", t)
    t = re.sub(r"\bBranch\s+Name\s*\(\s*Branch\s+Code\s*\)\s*", "", t, flags=re.I)
    # Only strip branch headers when tagged with an explicit branch code like '(EE)'
    t = re.sub(
        r"\b(?:Engineering\s*\([A-Z]{2,4}\)\s*Electrical\s+and\s+Electronics|"
        r"(?:Electrical\s+and\s+Electronics|Electronics\s+and\s+Communication|Mechanical|Civil|Computer\s+Science\s+and)\s+Engineering\s*\([A-Z]{2,4}\))\s*",
        "", t, flags=re.I,
    )
    t = re.sub(r"\bCOURSE\s+NAME\s*[:\-]?\s*", "", t, flags=re.I)
    t = re.sub(r"\bMICROPROC\s+CESSOR\b", "MICROPROCESSOR", t, flags=re.I)
    t = re.sub(r"\bMANGEMENT\b", "MANAGEMENT", t, flags=re.I)

    if course_code:
        t = re.sub(rf"\b{re.escape(course_code)}\b", "", t, flags=re.I)
    t = re.sub(r"\s*[-–—:]\s*$", "", t)
    t = clean_space(t)

    t = re.sub(r"\s*[–—-]\s*([1-8])$", r" - \1", t)
    t = re.sub(r"\bNON\s*[–—-]\s*DESTRUCTIVE\b", "NON-DESTRUCTIVE", t, flags=re.I)
    t = re.sub(r"\bREAL\s*[–—-]\s*TIME\b", "REAL-TIME", t, flags=re.I)
    t = re.sub(r"\s+([,:;])", r"\1", t)

    letters = [ch for ch in t if ch.isalpha()]
    if letters and (sum(ch.isupper() for ch in letters) / len(letters)) > 0.75:
        t = t.title()

    t = re.sub(r"\b([23])d\b", r"\1D", t)
    t = re.sub(r"'S\b", "'s", t)

    for acr in ACRONYMS:
        t = re.sub(rf"(?<![A-Za-z0-9]){re.escape(acr)}(?![A-Za-z0-9])", acr, t, flags=re.I)
    for small in ["and", "of", "for", "in", "to", "with", "on", "the", "a", "an", "using"]:
        t = re.sub(rf"(?<!^)(?<!:\s)(?<!-\s)\b{small}\b", small, t, flags=re.I)
    return clean_space(t)


def title_similarity(a: str, b: str) -> float:
    na = re.sub(r"[^a-z0-9]+", " ", a.lower()).strip()
    nb = re.sub(r"[^a-z0-9]+", " ", b.lower()).strip()
    if not na or not nb:
        return 0.0
    if na == nb or na in nb or nb in na:
        return 1.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


def get_sorted_visual_lines(page: fitz.Page, max_y: float | None = None):
    d = page.get_text("dict")
    lines = []
    for block in d.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            y0 = line["bbox"][1]
            if max_y is not None and y0 >= max_y:
                continue
            txt = clean_space("".join(span.get("text", "") for span in line.get("spans", [])))
            if txt:
                lines.append((y0, line["bbox"][0], txt))
    lines.sort(key=lambda item: (round(item[0] / 3), item[1]))
    return [(y0, txt) for y0, _, txt in lines]


def detect_branch_code(pdf_path: Path, doc: fitz.Document) -> str:
    name_norm = re.sub(r"[^A-Z0-9]+", " ", pdf_path.stem.upper()).strip()
    filename_rules = [
        ("AIML", r"\b(AIML|AI\s*ML|ARTIFICIAL\s+INTELLIGENCE|CSE\s*AI|CA|AM)\b"),
        ("ECE",  r"\b(ECE|ELECTRONICS\s+AND\s+COMMUNICATION|EC)\b"),
        ("EEE",  r"\b(EEE|ELECTRICAL\s+AND\s+ELECTRONICS|ELECTRICAL|EE)\b"),
        ("ME",   r"\b(ME|MECH|MECHANICAL)\b"),
        ("CE",   r"\b(CE|CIVIL)\b"),
        ("CSE",  r"\b(CSE|COMPUTER\s+SCIENCE|CS)\b"),
    ]
    for bcode, pat in filename_rules:
        if re.search(pat, name_norm):
            return bcode

    sample_txt = " ".join(clean_space(doc[p].get_text("text")) for p in range(min(3, len(doc)))).upper()
    text_rules = [
        ("AIML", r"ARTIFICIAL\s+INTELLIGENCE\s+AND\s+MACHINE\s+LEARNING"),
        ("ECE",  r"ELECTRONICS\s+AND\s+COMMUNICATION"),
        ("EEE",  r"ELECTRICAL\s+AND\s+ELECTRONICS"),
        ("ME",   r"MECHANICAL\s+ENGINEERING"),
        ("CE",   r"CIVIL\s+ENGINEERING"),
        ("CSE",  r"COMPUTER\s+SCIENCE\s+AND\s+ENGINEERING"),
    ]
    for bcode, pat in text_rules:
        if re.search(pat, sample_txt):
            return bcode
    raise ValueError(f"Could not detect branch for file: {pdf_path.name}")


def is_divider_page(page: fitz.Page) -> tuple[bool, str | None]:
    raw = clean_space(page.get_text("text"))
    if re.search(r"Course\s+Code", raw, re.I) and re.search(r"(CIE\s+Marks|\bCredits\b)", raw, re.I):
        return False, None
    if len(raw) < 20 and not page.get_images():
        return True, None
    if len(raw) < 180 and not re.search(
        r"(Course\s+Objectives|SYLLABUS|Course\s+Outcomes|Text\s+Books|Reference\s+Books|Continuous\s+Assessment|Evaluation\s+Pattern|Expt\.?\s*No|Project\s+Quality|Video\s+Links)",
        raw, re.I,
    ):
        sem_m = re.search(r"\bSEMESTER\s*S?([3-8])\b", raw, re.I)
        if sem_m:
            return True, f"S{sem_m.group(1)}"
        if re.search(r"^(PROGRAMME\s+(CORE|ELECTIVE)|OPEN\s+ELECTIVE|B\.?\s*TECH\s+2024)", raw, re.I):
            return True, None
    return False, None


def classify_category(code: str, course_type: str, ltpr: str) -> str:
    c = code.upper()
    ct = course_type.lower()
    m_num = re.search(r"(\d{3})$", c)
    num = int(m_num.group(1)) if m_num else 0

    if c.startswith("UC"):
        return "Common / Humanities"
    if re.match(r"^G[A-Z]", c):
        return "Math & Science"
    if c.startswith("OE") or "open elective" in ct or (c.startswith("PE") and (610 <= num <= 619 or 720 <= num <= 729 or 830 <= num <= 839)):
        return "Open Elective"
    if c.startswith("PE") or "elective" in ct or (c.startswith("PC") and (740 <= num <= 799 or 860 <= num <= 899)):
        return "Program Elective"
    if c.startswith("PB") or "pbl" in ct or (ltpr and ltpr.endswith(":1")):
        return "PBL Core"
    if (len(c) >= 5 and c[4] == "L") or "lab" in ct:
        return "Lab"
    return "Core"


def clean_prerequisites(raw_prereq: str, course_code: str) -> str:
    p = clean_space(raw_prereq)
    if not p or BOILERPLATE_PREREQ_RE.match(p):
        return ""
    if re.sub(r"\s+", "", p).upper() == course_code.upper():
        return ""
    return p


def detect_course_start(page: fitz.Page, branch_code: str, section_sem: str):
    full_text = page.get_text("text")
    if not (re.search(r"Course\s+Code", full_text, re.I) and re.search(r"(CIE\s+Marks|\bCredits\b)", full_text, re.I)):
        return None

    rect = page.rect
    top_clip = fitz.Rect(0, 0, rect.width, rect.height * 0.48)
    top_text = page.get_text("text", clip=top_clip)

    code = cie = ese = credits = ltpr = exam_hours = course_type = prereq = ""
    meta_table_top_y = None

    try:
        tables = page.find_tables(clip=top_clip)
        if tables and tables.tables:
            meta_tbl = tables.tables[0]
            meta_table_top_y = meta_tbl.bbox[1]
            for row in meta_tbl.extract():
                cells = [clean_space(c or "") for c in row]
                for i in range(len(cells) - 1):
                    k = cells[i].lower()
                    v = cells[i + 1]
                    if not v:
                        continue
                    if "course code" in k and not code:
                        m_code = COURSE_CODE_RE.search(v.upper())
                        if m_code:
                            code = re.sub(r"\s+", "", m_code.group(1)).upper()
                    elif "cie marks" in k and not cie:
                        m_num = re.search(r"\d+", v)
                        cie = m_num.group(0) if m_num else v
                    elif "ese marks" in k and not ese:
                        m_num = re.search(r"\d+", v)
                        ese = m_num.group(0) if m_num else v
                    elif k == "credits" and not credits:
                        m_cr = re.search(r"\d+(?:\s*/\s*\d+)?", v)
                        credits = re.sub(r"\s+", "", m_cr.group(0)) if m_cr else v
                    elif "teaching hours" in k and not ltpr:
                        ltpr = v
                    elif "exam hours" in k and not exam_hours:
                        exam_hours = v
                    elif "course type" in k and not course_type:
                        course_type = v
                    elif "prerequisite" in k and not prereq:
                        prereq = v
    except Exception:
        pass

    if not code:
        m = re.search(r"Course\s+Code\s*[:\-]?\s*([A-Z]{4,5}\s*\d{3})\b", top_text, re.I) or COURSE_CODE_RE.search(top_text.upper())
        if not m:
            return None
        code = re.sub(r"\s+", "", m.group(1)).upper()

    # Anchor cutoff to the exact 'Course Code' visual line (handles titles inside row 0 of metadata table)
    all_top_lines = get_sorted_visual_lines(page, max_y=rect.height * 0.45)
    cutoff_y = meta_table_top_y if meta_table_top_y is not None else rect.height * 0.35
    for y0, txt in all_top_lines:
        if re.search(r"Course\s+Code", txt, re.I):
            cutoff_y = y0
            break

    header_lines = []
    for y0, text in all_top_lines:
        if y0 >= cutoff_y - 2:
            break
        if re.fullmatch(r"\d{1,2}", text):
            continue
        if re.search(r"^(B\.?\s*Tech\s*2024|APJ\s+Abdul\s+Kalam|Branch\s+Name\s*\(\s*Branch\s+Code\s*\))$", text, re.I):
            continue
        if re.search(
            r"^(?:Electrical\s+and\s+Electronics|Electronics\s+and\s+Communication|Mechanical|Civil|Computer\s+Science\s+and)\s+Engineering\s*\([A-Z]{2,4}\)$",
            text, re.I,
        ):
            continue
        if re.search(r"(Course\s+Code|CIE\s+Marks)", text, re.I):
            break
        header_lines.append(text)

    sem_label = ""
    common_note = ""
    title_parts = []
    for ln in header_lines:
        if re.match(r"^(?:SEM)?SEMESTER\b", ln, re.I):
            sem_label = ln
            after_sem = SEM_PREFIX_RE.sub("", ln).strip()
            if after_sem:
                title_parts.append(after_sem)
        elif (ln.startswith("(") and ln.endswith(")")) or re.search(r"^\(?\s*Common\s+(to|with)\b", ln, re.I):
            common_note = ln.strip("() ").strip()
        else:
            title_parts.append(ln)

    raw_title = clean_space(" ".join(title_parts))
    title = normalize_title(raw_title, course_code=code) if raw_title else code
    if not title:
        title = code

    raw_code = code
    override_note = ""
    for (ov_branch, ov_raw, ov_title_sub), fixed_code in OFFICIAL_CODE_OVERRIDES.items():
        if ov_branch in (branch_code, "ANY") and code == ov_raw and ov_title_sub in raw_title.upper():
            code = fixed_code
            override_note = f"Official KTU PDF printed {raw_code}; mapped to {fixed_code}"
            break

    sems_found = set()
    sem_src = sem_label.upper()
    dual_m = re.search(r"S?\s*([3-8])\s*/\s*S?\s*([3-8])", sem_src)
    if dual_m:
        sems_found.add(f"S{dual_m.group(1)}")
        sems_found.add(f"S{dual_m.group(2)}")
    elif section_sem:
        sems_found.add(section_sem)
    else:
        single_m = re.search(r"SEMESTER\s*[:\-]?\s*S?\s*([3-8])\b", sem_src)
        if single_m:
            sems_found.add(f"S{single_m.group(1)}")
        else:
            dm = re.search(r"([3-8])\d{2}$", code)
            sems_found.add(f"S{dm.group(1)}" if dm else "S3")

    flat_top = clean_space(top_text)
    if not cie:
        m = re.search(r"CIE\s+Marks\s+(\d+)", flat_top, re.I)
        if m:
            cie = m.group(1)
    if not ese:
        m = re.search(r"ESE\s+Marks\s+(\d+)", flat_top, re.I)
        if m:
            ese = m.group(1)
    if not ltpr:
        m = re.search(r"\b(\d\s*[:\-]\s*\d\s*[:\-]\s*\d\s*[:\-]\s*\d)\b", flat_top)
        if m:
            ltpr = m.group(1)
    if ltpr:
        m_ltpr = re.search(r"(\d\s*[:\-]\s*\d\s*[:\-]\s*\d\s*[:\-]\s*\d)", ltpr)
        if m_ltpr:
            ltpr = re.sub(r"\s*[:\-]\s*", ":", m_ltpr.group(1))
    if not credits:
        m = re.search(r"Credits\s+(\d+(?:\s*/\s*\d+)?)", flat_top, re.I)
        if m:
            credits = re.sub(r"\s+", "", m.group(1))
    # Fill blank credits on standard 0:0:3:0 Labs (e.g. EEE PCEEL508)
    if not credits and ltpr == "0:0:3:0" and (len(code) >= 5 and code[4] == "L"):
        credits = "2"

    if not course_type:
        if len(code) >= 5 and code[4] == "L":
            course_type = "Lab"
        elif code.startswith("PB"):
            course_type = "PBL"
        elif code.startswith("OE"):
            course_type = "Open Elective"
        elif code.startswith("PE"):
            course_type = "Elective"
        else:
            course_type = "Theory"

    prereq_clean = clean_prerequisites(prereq, code)
    category = classify_category(code, course_type, ltpr)

    return {
        "code": code,
        "raw_code": raw_code,
        "override_note": override_note,
        "title": title,
        "common_note": common_note,
        "semesters": sorted(sems_found),
        "category": category,
        "credits": credits,
        "honours_option": "/" in credits,
        "cie": cie,
        "ese": ese,
        "ltpr": ltpr,
        "exam_hours": exam_hours,
        "course_type": course_type,
        "prerequisites": prereq_clean,
    }


def sanitize_url(url: str) -> str:
    u = url.strip().rstrip(".,;\\")
    u = re.sub(r"^(https?://)nptel/", r"\1nptel.ac.in/", u, flags=re.I)
    low = u.lower()
    if low.startswith("chrome-extension://"):
        return ""
    if re.fullmatch(r"https?://(www\.)?youtube\.com/?", low):
        return ""
    if not re.match(r"^https?://[a-z0-9.-]+\.[a-z]{2,}", low):
        return ""
    return u


def extract_urls_from_cell(raw_cell: str) -> list[str]:
    if not raw_cell:
        return []
    lines = [ln.strip() for ln in raw_cell.replace("\ufffd", "-").splitlines() if ln.strip()]
    stitched = []
    for ln in lines:
        if stitched:
            prev = stitched[-1]
            prev_url_m = re.search(r"(https?://\S+)$", prev)
            if prev_url_m and not re.match(r"^(https?://|\d+\.|\(|Module|Unit|Lecture|Prof|By\b|NOC\b|Case\b|Link\s*:)", ln, re.I):
                prev_url = prev_url_m.group(1)
                first_tok = ln.split()[0]
                yt_short = re.search(r"youtu\.be/([A-Za-z0-9_-]+)$", prev_url)
                yt_watch = re.search(r"v=([A-Za-z0-9_-]+)$", prev_url)
                looks_truncated = (
                    prev_url.endswith(("=", "-", "_", "/", "&", "?"))
                    or (yt_short and len(yt_short.group(1)) < 11)
                    or (yt_watch and len(yt_watch.group(1)) < 11)
                    or ("list=" in prev_url and "&index=" not in prev_url and re.fullmatch(r"[A-Za-z0-9_\-=&]+", first_tok))
                    or ("courses/" in prev_url and re.fullmatch(r"[a-z0-9_\-/]+", first_tok))
                )
                if looks_truncated and re.fullmatch(r"[A-Za-z0-9_\-=&?/.%]+", first_tok):
                    rest = ln[len(first_tok):].strip()
                    stitched[-1] = prev + first_tok + ((" " + rest) if rest else "")
                    continue
        stitched.append(ln)

    found = []
    for ln in stitched:
        for u in URL_RE.findall(ln):
            su = sanitize_url(u)
            if su:
                found.append(su)
    return found


def parse_module_number(cell_text: str) -> int | None:
    s = clean_space(cell_text).upper()
    m = re.fullmatch(r"(?:MODULE\s*[-:]?\s*)?([1-4]|I{1,3}|IV)\.?", s)
    if not m:
        return None
    val = m.group(1)
    return int(val) if val.isdigit() else ROMAN_MOD_MAP.get(val)


def extract_modules_text_fallback(doc: fitz.Document, start_p: int, end_p: int) -> dict[int, str]:
    chunks = []
    for pno in range(start_p, min(end_p + 1, start_p + 4)):
        txt = doc[pno].get_text("text")
        chunks.append(txt)
        if re.search(r"Course\s+Assessment\s+Method|Continuous\s+Internal\s+Evaluation", txt, re.I):
            break
    joined = "\n".join(chunks)
    m_start = re.search(r"\bSYLLABUS\b", joined, re.I)
    if not m_start:
        return {}
    body = joined[m_start.end():]
    m_end = re.search(r"Course\s+Assessment\s+Method|Continuous\s+Internal\s+Evaluation|Suggestion\s+on\s+Project", body, re.I)
    if m_end:
        body = body[:m_end.start()]

    mods = {}
    current = None
    for raw_ln in body.splitlines():
        ln = clean_space(raw_ln)
        if not ln or re.fullmatch(r"(Module|Modu|le\s*No\.?|No\.?|Syllabus\s+Description|Contact|Hours|\d{1,2})", ln, re.I):
            if re.fullmatch(r"[1-4]", ln):
                num = int(ln)
                if num not in mods and (current is None or num == current + 1):
                    current = num
                    mods[current] = ""
            continue
        m_inline = re.match(r"^(?:Module\s*[-:]?\s*)?([1-4])\s+(.{20,})$", ln, re.I)
        if m_inline:
            num = int(m_inline.group(1))
            if num not in mods and (current is None or num == current + 1):
                current = num
                mods[current] = m_inline.group(2)
                continue
        if current is not None:
            mods[current] = (mods[current] + " " + ln).strip()
    return {k: v for k, v in mods.items() if len(v) > 25}


def extract_subject_details(doc: fitz.Document, start_p: int, end_p: int, is_lab: bool):
    modules = {}
    experiments = []
    video_links = []
    seen_links = set()

    last_mod_num = 0
    in_syllabus_zone = True

    for pno in range(start_p, end_p + 1):
        page = doc[pno]
        txt = page.get_text("text")

        pass_after_page = bool(re.search(r"Course\s+Assessment\s+Method|Continuous\s+Internal\s+Evaluation", txt, re.I))
        has_video_section = bool(re.search(r"(Video\s+Links|\bLinks\b)", txt, re.I)) and (
            "http" in txt.lower() or bool(page.get_links())
        )
        if not (in_syllabus_zone or has_video_section):
            continue

        try:
            tables = page.find_tables()
        except Exception:
            tables = None

        if not tables or not tables.tables:
            if pass_after_page:
                in_syllabus_zone = False
            continue

        page_links = page.get_links() if has_video_section else []

        for tbl in tables.tables:
            rows = tbl.extract()
            if not rows:
                continue

            top_rows_str = " ".join(clean_space(c or "") for r in rows[:2] for c in (r or []))

            # 1) VIDEO LINKS TABLE
            if re.search(r"(Video\s+Links|Link\s+ID)", top_rows_str, re.I):
                tbl_rect = fitz.Rect(tbl.bbox) + (-4, -4, 4, 4)
                for lk in page_links:
                    uri = lk.get("uri")
                    lrect = lk.get("from")
                    if uri and lrect and tbl_rect.intersects(lrect):
                        su = sanitize_url(uri)
                        if su and su not in seen_links:
                            seen_links.add(su)
                            video_links.append(su)
                for r in rows:
                    for cell in (r or []):
                        for su in extract_urls_from_cell(cell or ""):
                            if any(existing.startswith(su) and len(existing) > len(su) for existing in video_links):
                                continue
                            if su not in seen_links:
                                seen_links.add(su)
                                video_links.append(su)
                continue

            if not in_syllabus_zone:
                continue

            if re.search(
                r"(Course\s+Code|CIE\s+Marks|Attendance|Part\s+A\b.*Part\s+B|Course\s+Outcome|\bPO1\b|"
                r"Text\s+Books|Reference\s+Books|Data\s+Books|PBL\s+Course|Evaluation\s+for|Sl\.?\s*No|Reflective\s+Journal)",
                top_rows_str, re.I,
            ):
                continue

            # 2) LAB EXPERIMENTS TABLE
            if is_lab:
                for r in rows:
                    if not r or len(r) < 2:
                        continue
                    cells = [clean_space(x or "") for x in r]
                    c0 = cells[0]
                    c1 = max(cells[1:], key=len) if len(cells) > 1 else ""
                    if re.search(r"^Expt\.?\s*No\.?$", c0, re.I) or re.fullmatch(r"Experiments", c1, re.I):
                        continue
                    if re.search(r"^(Part\s+[A-C12]|Warm\s+up|Wireshark|Socket|Cisco|Note\s*:|Out\s+of\s+\d+|A\s+minimum\s+of)", c1, re.I):
                        continue
                    if re.fullmatch(r"([A-C]?\d+\.?|Part\s+[AB]|Study)", c0, re.I) and len(c1) > 10:
                        experiments.append({"no": c0.rstrip("."), "title": c1[:220] + ("..." if len(c1) > 220 else "")})
                continue

            # 3) THEORY SYLLABUS TABLE
            for r in rows:
                if not r or len(r) < 2:
                    continue
                cells = [clean_space(x or "") for x in r]
                c0 = cells[0]

                if re.fullmatch(r"(Modu\s*le(\s*No\.?)?|No\.?)", c0, re.I) or any(
                    re.fullmatch(r"Syllabus\s+Description", c, re.I) for c in cells
                ):
                    continue

                mod_num = parse_module_number(c0)
                candidate_cells = cells[1:] if (mod_num is not None or c0 == "") else cells
                non_num_cells = [c for c in candidate_cells if c and not re.fullmatch(r"\d{1,2}(\s*hrs?\.?)?", c, re.I)]
                c1 = max(non_num_cells, key=len) if non_num_cells else ""
                if len(c1) < 15 or c1.startswith("http"):
                    continue

                last_cell = cells[-1]
                has_hours = bool(re.fullmatch(r"\d{1,2}", last_cell))

                if mod_num is not None:
                    last_mod_num = mod_num
                    modules[mod_num] = (modules.get(mod_num, "") + " " + c1).strip()
                elif c0 == "" and last_mod_num in (1, 2, 3, 4):
                    if has_hours and last_mod_num < 4 and (last_mod_num + 1) not in modules and len(modules.get(last_mod_num, "")) > 80:
                        last_mod_num += 1
                        modules[last_mod_num] = c1
                    else:
                        modules[last_mod_num] = (modules.get(last_mod_num, "") + " " + c1).strip()

        if pass_after_page:
            in_syllabus_zone = False

    if not is_lab and len(modules) < 4:
        fb = extract_modules_text_fallback(doc, start_p, end_p)
        for k, v in fb.items():
            if k not in modules:
                modules[k] = v

    ordered_mods = [
        {
            "no": k,
            "summary": clean_space(modules[k])[:380] + ("..." if len(clean_space(modules[k])) > 380 else ""),
        }
        for k in sorted(modules.keys())
    ]
    return ordered_mods, experiments, video_links[:10]


def check_pdf_quality_score(doc: fitz.Document, start_p: int, end_p: int, credits: str) -> int:
    score = (end_p - start_p + 1) * 10
    if credits and credits != "0":
        score += 40
    full_txt = clean_space(" ".join(doc[p].get_text("text") for p in range(start_p, end_p + 1)))
    if re.search(r"Attendance\s+Assignment.*?\b0\s+15\s+12\.5", full_txt, re.I):
        score -= 50
    return score


def process_all_s3_s8_pdfs():
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"[ERROR] No PDFs found in {RAW_DIR.resolve()}")
        return

    OUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    for old_pdf in OUT_PDF_DIR.glob("*.pdf"):
        old_pdf.unlink()

    branch_files = []
    skipped_files = []
    for pdf_path in pdf_files:
        size_kb = pdf_path.stat().st_size / 1024
        head = pdf_path.read_bytes()[:32]
        if not head.startswith(b"%PDF"):
            msg = f"[SKIPPED] {pdf_path.name} ({size_kb:.1f} KB) is NOT a valid PDF (header={head!r})"
            print(msg)
            skipped_files.append(msg)
            continue
        try:
            doc = fitz.open(pdf_path)
            bcode = detect_branch_code(pdf_path, doc)
            doc.close()
            branch_files.append((BRANCH_META[bcode]["order"], bcode, pdf_path))
        except Exception as e:
            msg = f"[SKIPPED] {pdf_path.name} ({size_kb:.1f} KB) failed to open: {e}"
            print(msg)
            skipped_files.append(msg)

    branch_files.sort(key=lambda x: x[0])

    canonical_courses = {}
    code_to_ids = {}
    branch_records = {}

    report = ["KTU 2024 S3–S8 SYLLABUS BUILD REPORT", "=" * 65, ""]
    qa_warnings = list(skipped_files)

    for _, branch_code, pdf_path in branch_files:
        bmeta = BRANCH_META[branch_code]
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        report.append(f"SOURCE: {pdf_path.name} -> {branch_code} ({bmeta['name']}) — {total_pages} pages")

        starts = []
        dividers = set()
        current_section_sem = "S3"

        for i in range(total_pages):
            page = doc[i]
            is_div, div_sem = is_divider_page(page)
            if is_div:
                dividers.add(i)
                if div_sem:
                    current_section_sem = div_sem
                continue

            meta = detect_course_start(page, branch_code, current_section_sem)
            if meta:
                starts.append((i, meta))

        branch_records[branch_code] = {}

        for idx, (start_p, meta) in enumerate(starts):
            next_start = starts[idx + 1][0] if idx + 1 < len(starts) else total_pages
            end_p = next_start - 1
            while end_p > start_p and end_p in dividers:
                end_p -= 1

            code = meta["code"]
            page_count = (end_p - start_p) + 1
            is_lab = meta["category"] == "Lab"

            if meta["override_note"]:
                qa_warnings.append(f"[OVERRIDE] {branch_code} p.{start_p+1}: {meta['override_note']} ({meta['title']})")

            unique_id = None
            existing_ids = code_to_ids.get(code, [])
            for eid in existing_ids:
                if title_similarity(canonical_courses[eid]["title"], meta["title"]) >= 0.72:
                    unique_id = eid
                    break

            if unique_id is None:
                if not existing_ids:
                    unique_id = code
                else:
                    suffix = len(existing_ids) + 1
                    unique_id = f"{code}_{suffix}"
                    qa_warnings.append(
                        f"[COLLISION] {branch_code} p.{start_p+1}: Code '{code}' used for DIFFERENT title "
                        f"'{meta['title']}' (existing: '{canonical_courses[existing_ids[0]]['title']}'). "
                        f"Saved safely as {unique_id}.pdf"
                    )
                code_to_ids.setdefault(code, []).append(unique_id)

            pdf_out_path = OUT_PDF_DIR / f"{unique_id}.pdf"
            rel_pdf_url = f"/syllabus/s3-s8/pdfs/{unique_id}.pdf"
            quality_score = check_pdf_quality_score(doc, start_p, end_p, meta["credits"])

            modules, experiments, video_links = extract_subject_details(doc, start_p, end_p, is_lab)

            if meta["credits"] in ("", "0"):
                qa_warnings.append(f"[CREDITS] {branch_code} {code} (p.{start_p+1}): Suspicious credits='{meta['credits']}' ({meta['title']})")
            if not is_lab and len(modules) < 4:
                qa_warnings.append(f"[MODULES] {branch_code} {code} (p.{start_p+1}): Extracted {len(modules)}/4 modules ({meta['title']})")
            if page_count < 2 or (not is_lab and page_count > 12) or (is_lab and page_count > 15):
                qa_warnings.append(f"[PAGES] {branch_code} {code} (p.{start_p+1}-{end_p+1}): Unusual length {page_count}p ({meta['title']})")
            if meta["category"] == "PBL Core" and meta["cie"] == "40" and meta["ese"] == "60":
                qa_warnings.append(f"[CIE/ESE] {branch_code} {code} (p.{start_p+1}): PBL course has CIE=40/ESE=60 in top table ({meta['title']})")

            should_write_pdf = (
                unique_id not in canonical_courses
                or quality_score > canonical_courses[unique_id]["_quality_score"]
            )
            if should_write_pdf:
                sub_doc = fitz.open()
                sub_doc.insert_pdf(doc, from_page=start_p, to_page=end_p)
                sub_doc.save(pdf_out_path, garbage=4, deflate=True)
                sub_doc.close()

            if unique_id not in canonical_courses:
                canonical_courses[unique_id] = {
                    "id": unique_id,
                    "code": code,
                    "title": meta["title"],
                    "category": meta["category"],
                    "common_note": meta["common_note"],
                    "branches": [branch_code],
                    "semesters": list(meta["semesters"]),
                    "credits": meta["credits"],
                    "honours_option": meta["honours_option"],
                    "cie": meta["cie"],
                    "ese": meta["ese"],
                    "ltpr": meta["ltpr"],
                    "exam_hours": meta["exam_hours"],
                    "course_type": meta["course_type"],
                    "prerequisites": meta["prerequisites"],
                    "pages": page_count,
                    "pdf_url": rel_pdf_url,
                    "modules": modules,
                    "experiments_count": len(experiments),
                    "experiments": experiments[:15],
                    "video_links": video_links,
                    "_quality_score": quality_score,
                }
            else:
                entry = canonical_courses[unique_id]
                if branch_code not in entry["branches"]:
                    entry["branches"].append(branch_code)
                entry["semesters"] = sorted(set(entry["semesters"]) | set(meta["semesters"]))
                if entry["credits"] in ("", "0") and meta["credits"] not in ("", "0"):
                    entry["credits"] = meta["credits"]
                    entry["honours_option"] = meta["honours_option"]
                if len(modules) > len(entry["modules"]):
                    entry["modules"] = modules
                if len(experiments) > entry["experiments_count"]:
                    entry["experiments_count"] = len(experiments)
                    entry["experiments"] = experiments[:15]
                if len(video_links) > len(entry["video_links"]):
                    entry["video_links"] = video_links
                if not entry["prerequisites"] and meta["prerequisites"]:
                    entry["prerequisites"] = meta["prerequisites"]
                if should_write_pdf:
                    entry["pages"] = page_count
                    entry["_quality_score"] = quality_score

            if unique_id not in branch_records[branch_code]:
                branch_records[branch_code][unique_id] = {
                    "semesters": set(meta["semesters"]),
                    "category": meta["category"],
                }
            else:
                branch_records[branch_code][unique_id]["semesters"].update(meta["semesters"])

            report.append(
                f"  - {unique_id:10s} | p.{start_p+1:3d}-{end_p+1:3d} ({page_count:2d}p) | "
                f"{','.join(meta['semesters']):5s} | {meta['category']:19s} | cr:{meta['credits']:3s} | {meta['title']}"
            )

        report.append("")
        doc.close()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    branches_manifest = []

    category_order = {
        "Core": 1,
        "PBL Core": 2,
        "Math & Science": 3,
        "Common / Humanities": 4,
        "Lab": 5,
        "Program Elective": 6,
        "Open Elective": 7,
    }

    for _, branch_code, _ in branch_files:
        bmeta = BRANCH_META[branch_code]
        b_courses = []

        for uid, brec in branch_records[branch_code].items():
            master = canonical_courses[uid]
            b_sems = sorted(brec["semesters"])
            b_courses.append({
                "id": master["id"],
                "code": master["code"],
                "title": master["title"],
                "category": brec["category"],
                "semesters": b_sems,
                "credits": master["credits"],
                "honours_option": master["honours_option"],
                "cie": master["cie"],
                "ese": master["ese"],
                "ltpr": master["ltpr"],
                "exam_hours": master["exam_hours"],
                "course_type": master["course_type"],
                "prerequisites": master["prerequisites"],
                "common_note": master["common_note"],
                "shared_branches": master["branches"],
                "pages": master["pages"],
                "pdf_url": master["pdf_url"],
                "modules": master["modules"],
                "experiments_count": master["experiments_count"],
                "experiments": master["experiments"],
                "video_links": master["video_links"],
            })

        b_courses.sort(
            key=lambda c: (
                int(c["semesters"][0][1:]),
                category_order.get(c["category"], 99),
                c["code"],
            )
        )

        sem_counts = {}
        cat_counts = {}
        for c in b_courses:
            for s in c["semesters"]:
                sem_counts[s] = sem_counts.get(s, 0) + 1
            cat_counts[c["category"]] = cat_counts.get(c["category"], 0) + 1

        (OUT_ROOT / f"{bmeta['slug']}.json").write_text(
            json.dumps(
                {
                    "scheme": "2024",
                    "level": "S3–S8",
                    "branch": {k: bmeta[k] for k in ("code", "slug", "name", "short_name", "group")},
                    "total_courses": len(b_courses),
                    "semester_counts": dict(sorted(sem_counts.items())),
                    "category_counts": cat_counts,
                    "courses": b_courses,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        branches_manifest.append({
            "code": bmeta["code"],
            "slug": bmeta["slug"],
            "name": bmeta["name"],
            "short_name": bmeta["short_name"],
            "group": bmeta["group"],
            "total_courses": len(b_courses),
            "semester_counts": dict(sorted(sem_counts.items())),
            "json_url": f"/syllabus/s3-s8/{bmeta['slug']}.json",
        })

    OUT_BRANCHES_JSON.write_text(
        json.dumps(
            {
                "scheme": "2024",
                "level": "S3–S8",
                "total_branches": len(branches_manifest),
                "total_unique_courses": len(canonical_courses),
                "branches": branches_manifest,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    search_items = sorted(
        (
            {
                "id": c["id"],
                "code": c["code"],
                "title": c["title"],
                "category": c["category"],
                "credits": c["credits"],
                "branches": c["branches"],
                "semesters": c["semesters"],
                "pdf_url": c["pdf_url"],
            }
            for c in canonical_courses.values()
        ),
        key=lambda x: (int(x["semesters"][0][1:]), x["code"]),
    )
    OUT_SEARCH_JSON.write_text(
        json.dumps(
            {
                "scheme": "2024",
                "total_unique_courses": len(search_items),
                "courses": search_items,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    report.append("=" * 65)
    report.append(f"SUMMARY: {len(branches_manifest)} branches | {len(canonical_courses)} unique deduplicated PDFs")
    report.append(f"QA WARNINGS ({len(qa_warnings)}):")
    if qa_warnings:
        for w in qa_warnings:
            report.append(f"  {w}")
    else:
        report.append("  None! All checks passed cleanly.")

    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    print(f"[DONE] Processed {len(branches_manifest)} branches -> {len(canonical_courses)} unique PDFs in {OUT_PDF_DIR}")
    print(f"[DONE] Manifest: {OUT_BRANCHES_JSON}")
    print(f"[DONE] Search Index: {OUT_SEARCH_JSON}")
    print(f"[DONE] QA Report ({len(qa_warnings)} notices): {OUT_REPORT}")


if __name__ == "__main__":
    process_all_s3_s8_pdfs()
