import os
import json
import re
import ssl
import base64
import time
import requests
from requests.adapters import HTTPAdapter
import urllib3
import PyPDF2
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types

# Optional Camoufox anti-detect browser support
try:
    from camoufox.sync_api import Camoufox
    HAS_CAMOUFOX = True
except ImportError:
    HAS_CAMOUFOX = False

# --- FIREBASE IMPORTS ---
import firebase_admin
from firebase_admin import credentials, messaging, db

# Disable SSL warnings when bypassing KTU's misconfigured SSL certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# -------------------------------------------------------------------
# CUSTOM TLS ADAPTER FOR KTU (Fixes "peer closed connection" resets)
# -------------------------------------------------------------------
class KTUTLSAdapter(HTTPAdapter):
    """Configures OpenSSL SECLEVEL=1 and legacy renegotiation so KTU's server doesn't drop connections."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        except Exception:
            pass
        if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
            ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def get_ktu_http_session() -> requests.Session:
    session = requests.Session()
    adapter = KTUTLSAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


KTU_SESSION = get_ktu_http_session()

# -------------------------------------------------------------------
# FIREBASE SETUP
# -------------------------------------------------------------------
firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_creds_json:
    try:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://kerala-timetable-db-default-rtdb.asia-southeast1.firebasedatabase.app'
        })
        print("✅ Firebase Admin initialized successfully.")
    except Exception as e:
        print(f"⚠️ Firebase Init Error: {e}")
else:
    print("⚠️ FIREBASE_CREDENTIALS not found in environment variables. Push notifications will be skipped.")


def send_push_notification(title, body):
    """Fetches tokens from Firebase, broadcasts via FCM v1 send_each, and prunes dead tokens."""
    if not firebase_creds_json:
        print("⏭️ Skipping Push: No Firebase credentials found.")
        return

    try:
        ref = db.reference('subscribers')
        subscribers = ref.get()

        if not subscribers:
            print("📭 No subscribers found in database.")
            return

        tokens = list(subscribers.keys())
        print(f"📢 Preparing to send push notification to {len(tokens)} devices...")

        success_total = 0
        failure_total = 0
        stale_tokens = []

        for i in range(0, len(tokens), 500):
            batch_tokens = tokens[i:i + 500]
            messages = [
                messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    token=tok
                )
                for tok in batch_tokens
            ]
            response = messaging.send_each(messages)
            success_total += response.success_count
            failure_total += response.failure_count

            for tok, send_res in zip(batch_tokens, response.responses):
                if not send_res.success and send_res.exception:
                    err_str = str(send_res.exception).upper()
                    if "UNREGISTERED" in err_str or "NOT_FOUND" in err_str or "INVALID" in err_str:
                        stale_tokens.append(tok)

        print(f"🚀 Push Sent! Success: {success_total} | Failed: {failure_total}")

        if stale_tokens:
            for dead_tok in stale_tokens:
                ref.child(dead_tok).delete()
            print(f"🧹 Cleaned up {len(stale_tokens)} expired/unregistered subscriber token(s).")

    except Exception as e:
        print(f"❌ Error sending push notification: {e}")


# -------------------------------------------------------------------
# AI SETUP & EXTENDED SCHEMA
# -------------------------------------------------------------------
client = genai.Client() if os.environ.get("GEMINI_API_KEY") else None


class TimetableData(BaseModel):
    # Core Dashboard Config Fields
    id: str
    title: str
    semester: str
    categoryBadge: str
    type: str
    scheme: str
    startDate: str
    endDate: str
    viewLink: str
    pdfLink: str
    # Rich S3-Template Page Fields
    courseBadge: str
    seoTitleTag: str
    slug: str
    subtitleInfo: str
    startDateFormatted: str
    endDateFormatted: str
    faqSecondQuestion: str
    faqSecondAnswer: str


# -------------------------------------------------------------------
# KTU TITLE CLEANER & SEO SLUG GENERATOR
# -------------------------------------------------------------------
def clean_ktu_raw_title(raw_title: str) -> dict:
    """Cleans messy KTU notification titles into the exact S3 standard format."""
    t = raw_title.strip()
    has_wp = bool(re.search(r'working\s+professionals|\(wp\)', t, flags=re.I))

    # 1. Strip prefixes like "APJAKTU - ", "KTU - ", "Detailed Time Table of", "Time Table of"
    t = re.sub(r'^(?:apjaktu|ktu)\s*[\-–:]+\s*', '', t, flags=re.I)
    t = re.sub(r'^(?:detailed\s+)?time\s*table\s+(?:of|for)\s+', '', t, flags=re.I)

    # 2. Strip suffixes like "- Notification - reg:", "Notification"
    t = re.sub(r'[\s\-–:]*notification(?:\s*[\-–:]\s*reg\s*:?)?.*$', '', t, flags=re.I)

    # 3. Strip Working Professionals clauses from the main title (moved to subtitle)
    t = re.sub(r',?\s*including\s*\(wp\)\s*(?:\([r,\s*s]+\))?', '', t, flags=re.I)
    t = re.sub(r'\s*/\s*working\s+professionals.*$', '', t, flags=re.I)

    # 4. Normalize "Examinations," or "Examination" or "Exam," -> "Exam"
    t = re.sub(r'\bexaminations?\b\s*,?', 'Exam', t, flags=re.I)
    t = re.sub(r'\bExam\s*,', 'Exam', t, flags=re.I)

    # 5. Normalize "(R,S)" spacing -> "(R, S)"
    t = re.sub(r'\(\s*R\s*,\s*S\s*\)', '(R, S)', t, flags=re.I)
    t = re.sub(r'\(\s*R\s*\)', '(R)', t, flags=re.I)
    t = re.sub(r'\(\s*S\s*\)', '(S)', t, flags=re.I)

    # 6. Extract Scheme and place "(YYYY Scheme)" cleanly at the end
    scheme_match = re.search(r'\((\d{4}\s+Scheme)\)', t, flags=re.I)
    scheme_str = "2024 Scheme"
    if scheme_match:
        scheme_str = scheme_match.group(1).title()
        t_no_scheme = re.sub(r'\(\d{4}\s+Scheme\)', '', t, flags=re.I).strip()
        t_no_scheme = re.sub(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s+Exam\b',
            r'Exam \1',
            t_no_scheme,
            flags=re.I
        )
        if not re.search(r'\bExam\b', t_no_scheme, flags=re.I):
            t_no_scheme = re.sub(
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
                r'Exam \1',
                t_no_scheme,
                flags=re.I
            )
        t = f"{t_no_scheme} ({scheme_str})"

    t = re.sub(r'\s+', ' ', t).strip(' ,-')

    # Extract Semester (e.g., S3, S5, S7)
    sem_match = re.search(r'\b(S[1-8])\b', t, flags=re.I)
    semester = sem_match.group(1).upper() if sem_match else "Exam"

    # Extract Course Badge (e.g., "B.Tech S3 (R, S)", "BBA Honours S5 (R)")
    badge_match = re.match(r'^(.+?\bS[1-8]\s*(?:\([R,\sS]+\))?)', t, flags=re.I)
    course_badge = badge_match.group(1).strip() if badge_match else f"KTU {semester}"

    # Build SEO <title> Tag
    seo_title = re.sub(
        r'\bExam\b\s*(.*)$',
        r'Exam Timetable Download \1',
        t,
        flags=re.I
    ).replace('(R, S)', '(R,S)')
    if not seo_title.upper().startswith("KTU "):
        seo_title = f"KTU {seo_title}"

    # Build Subtitle
    subtitle = (
        "Official APJAKTU Notification • Including Working Professionals (R, S)"
        if has_wp else
        "Verified University Examination Schedule • Official APJAKTU Notification"
    )

    return {
        "clean_title": t,
        "semester": semester,
        "course_badge": course_badge,
        "scheme": scheme_str,
        "seo_title": seo_title,
        "subtitle": subtitle
    }


def create_seo_slug(title: str) -> str:
    """Converts a clean title into the exact S3 style SEO slug."""
    s = title.lower()
    s = re.sub(r'^ktu\s+', '', s)
    s = s.replace('b.tech', 'btech').replace('m.tech', 'mtech').replace('b.arch', 'barch').replace('b.des', 'bdes')
    s = re.sub(r'\(\s*r\s*,\s*s\s*\)', 'regular-supply', s)
    s = re.sub(r'\(\s*r\s*\)', 'regular', s)
    s = re.sub(r'\(\s*s\s*\)', 'supply', s)
    s = re.sub(r'\bexaminations?\b|\bexam\b', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def sanitize_filename(name):
    """Ensures PDF filenames don't contain invalid OS path characters."""
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name))
    clean = re.sub(r'\s+', '_', clean)
    if not clean.lower().endswith('.pdf'):
        clean += '.pdf'
    return clean


def build_unique_pdf_filename(title: str, raw_att_name: str, encrypt_id: str) -> str:
    """Builds a clean, unique filename so 'Notification.pdf' attachments never collide."""
    cleaned_title = clean_ktu_raw_title(title)["clean_title"]
    slug_base = create_seo_slug(cleaned_title)
    if not raw_att_name or raw_att_name.strip().lower() in ("notification", "notification.pdf", "timetable", "time table", "attachment"):
        return sanitize_filename(f"{slug_base}.pdf")
    return sanitize_filename(raw_att_name)


def is_timetable_notification(title: str) -> bool:
    """Checks whether an announcement title is an exam timetable notification."""
    t = title.lower()
    if any(exclude in t for exclude in ["registration", "result", "valuation", "fee", "refund", "answer script", "notified"]):
        return False
    if "time table" in t or "timetable" in t or "date sheet" in t:
        return True
    if re.search(r'\bs[1-8]\b.*\bexam(?:inations?)?\b.*\b202[4-9]\b', t):
        return True
    return False


# -------------------------------------------------------------------
# LIQUID GLASS HTML GENERATOR (100% EXACT S3 TIMETABLE DESIGN)
# -------------------------------------------------------------------
def generate_html_page(raw_title, pdf_filename, ai_data=None, html_output_dir="./timetable_pages"):
    """Injects the scraped & AI data into the exact S3 Liquid Glass HTML template and saves the file."""
    os.makedirs(html_output_dir, exist_ok=True)

    fallback_info = clean_ktu_raw_title(raw_title)

    clean_title = (ai_data.get("title") if ai_data else None) or fallback_info["clean_title"]
    clean_title = re.sub(r'^KTU\s+', '', clean_title, flags=re.I).strip()

    slug = create_seo_slug((ai_data.get("slug") if ai_data else None) or clean_title)
    semester = (ai_data.get("semester") if ai_data else None) or fallback_info["semester"]
    scheme = (ai_data.get("scheme") if ai_data else None) or fallback_info["scheme"]
    course_badge = (ai_data.get("courseBadge") if ai_data else None) or fallback_info["course_badge"]
    seo_title_tag = (ai_data.get("seoTitleTag") if ai_data else None) or fallback_info["seo_title"]
    subtitle_info = (ai_data.get("subtitleInfo") if ai_data else None) or fallback_info["subtitle"]

    course_sem_label = re.sub(r'\s*\([R,\sS]+\)', '', course_badge).strip()
    faq_1_q = f"When do the {course_sem_label} ({scheme}) exams start and end?"

    start_fmt = ai_data.get("startDateFormatted") if ai_data else None
    end_fmt = ai_data.get("endDateFormatted") if ai_data else None
    if start_fmt and end_fmt and "refer" not in start_fmt.lower():
        faq_1_a = (
            f"The {clean_title} examinations begin on <strong>{start_fmt}</strong> "
            f"and conclude on <strong>{end_fmt}</strong>. Please check the official PDF download above for your specific subject codes."
        )
    else:
        faq_1_a = (
            f"Please refer to the official {clean_title} PDF download above for the exact subject-wise start and end dates, "
            f"FN/AN session timings, and slot codes for your specific branch."
        )

    faq_2_q = (ai_data.get("faqSecondQuestion") if ai_data else None) or "Does this timetable include Working Professionals (WP)?"
    faq_2_a = (ai_data.get("faqSecondAnswer") if ai_data else None) or (
        f"Please check the official APJAKTU notification header in the PDF above for {clean_title} "
        f"to verify whether Working Professionals (WP) or supplementary batches are included under the {scheme}."
    )

    html_filename = f"{slug}.html"
    html_filepath = os.path.join(html_output_dir, html_filename)
    pdf_link = f"../downloads_timetable/{pdf_filename}"

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <meta name="google-site-verification" content="cPHgzg8741NBFQ5HszgVIPA3EMrKJLlj7IHcyLGM2Lo" />
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7313827303298932" crossorigin="anonymous"></script>
    
    <title>[[SEO_TITLE_TAG]] | Kerala Timetable</title>
    <link rel="canonical" href="https://keralatimetable.in/timetable_pages/[[SLUG]].html" />

    <meta name="description" content="Download the official [[CLEAN_TITLE]] PDF. Check the latest exam dates, slots, and subjects for APJAKTU examinations.">
    <meta name="keywords" content="[[CLEAN_TITLE]], KTU [[SEMESTER]] [[SCHEME]] Timetable PDF, KTU Time Table, KTU Exam Date PDF Download, Kerala Tech University, Kerala Timetable">
    <meta name="robots" content="index, follow">
    
    <script src="/tailwind-local.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* Liquid Mesh Canvas (Light Mode Default - Dark Mode overridden by components.js) */
        .bg-mesh {
            background-color: #f4f7fb;
            background-image: 
                radial-gradient(at 12% 15%, rgba(99, 102, 241, 0.16) 0px, transparent 50%),
                radial-gradient(at 88% 10%, rgba(14, 165, 233, 0.15) 0px, transparent 50%),
                radial-gradient(at 50% 90%, rgba(16, 185, 129, 0.11) 0px, transparent 55%);
            background-attachment: fixed;
        }

        /* Authentic Liquid Glass Surface (Light Mode) */
        .real-glass {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.82) 0%, rgba(255, 255, 255, 0.64) 100%);
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            border: 1.5px solid rgba(255, 255, 255, 0.85);
            box-shadow: 
                inset 0 1px 1px 0 rgba(255, 255, 255, 0.95),
                0 20px 50px -12px rgba(15, 23, 42, 0.08);
        }

        /* Recessed Inner Liquid Glass (Light Mode) */
        .inner-glass {
            background: rgba(248, 250, 252, 0.72);
            backdrop-filter: blur(14px) saturate(160%);
            -webkit-backdrop-filter: blur(14px) saturate(160%);
            border: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: inset 0 2px 6px rgba(15, 23, 42, 0.03);
        }

        /* Interactive Hybrid Cards (Light Mode) */
        .hybrid-card {
            background: rgba(255, 255, 255, 0.76);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1.5px solid rgba(226, 232, 240, 0.85);
            box-shadow: 0 8px 24px -6px rgba(15, 23, 42, 0.05);
            transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .hybrid-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.45);
            box-shadow: 0 14px 30px -8px rgba(79, 70, 229, 0.14);
        }

        .ambient-orb {
            filter: blur(60px);
            -webkit-filter: blur(60px);
            pointer-events: none;
        }

        .btn-glow {
            box-shadow: 0 14px 30px -6px rgba(79, 70, 229, 0.48), inset 0 1px 0 0 rgba(255, 255, 255, 0.35);
        }
        .btn-glow:hover {
            box-shadow: 0 18px 36px -6px rgba(79, 70, 229, 0.62), inset 0 1px 0 0 rgba(255, 255, 255, 0.45);
        }

        @keyframes sheenSweep {
            0% { transform: translateX(-120%) skewX(-18deg); }
            100% { transform: translateX(220%) skewX(-18deg); }
        }
        .sheen-effect {
            position: relative;
            overflow: hidden;
        }
        .sheen-effect::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 45%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.28), transparent);
            animation: sheenSweep 3.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            pointer-events: none;
        }

        .progress-ring__circle {
            transition: stroke-dashoffset 0.95s linear;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }

        details > summary { list-style: none; }
        details > summary::-webkit-details-marker { display: none; }
        details[open] summary .faq-chevron { transform: rotate(180deg); }
    </style>
    
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Kerala Timetable",
      "url": "https://keralatimetable.in/",
      "description": "Web application for APJAKTU students providing server status, exam timetables, and academic updates.",
      "applicationCategory": "EducationalApplication",
      "operatingSystem": "All",
      "inLanguage": "en-IN"
    }
    </script>

    <link rel="icon" href="/favicon.png" type="image/png">
    <meta property="og:site_name" content="Kerala Timetable">
    <meta property="og:title" content="[[CLEAN_TITLE]] + Timetable Download">
    <meta property="og:description" content="Download the official [[CLEAN_TITLE]] Timetable PDF.">
    <meta property="og:image" content="https://www.keralatimetable.in/social-preview.png">
    <meta property="og:type" content="website">
</head>

<body class="bg-mesh text-slate-800 antialiased flex flex-col min-h-screen relative overflow-x-hidden selection:bg-indigo-500 selection:text-white">

    <div class="ambient-orb fixed -top-24 -left-24 w-96 h-96 bg-indigo-400/20 rounded-full -z-10"></div>
    <div class="ambient-orb fixed top-1/3 -right-28 w-80 h-80 bg-sky-400/20 rounded-full -z-10"></div>

    <div id="navigation-container"></div>

    <main class="flex-grow max-w-3xl mx-auto px-4 sm:px-6 pt-5 pb-14 w-full flex flex-col items-center">
        
        <!-- Top Mobile-Friendly Breadcrumb & Verified Status Bar -->
        <div class="w-full flex items-center justify-between gap-2 mb-4 sm:mb-6">
            <a href="/timetable.html" class="inline-flex items-center gap-2 px-3.5 py-2 rounded-full text-xs sm:text-sm font-bold text-slate-700 bg-white/80 hover:bg-white border border-slate-200/80 shadow-sm transition-all active:scale-95">
                <i class="fas fa-arrow-left text-indigo-600 text-xs"></i>
                <span>All Timetables</span>
            </a>

            <div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-700 text-[11px] sm:text-xs font-extrabold tracking-tight shadow-sm">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Official KTU Mirror</span>
            </div>
        </div>

        <!-- Master Liquid Glass Timetable Card -->
        <section class="real-glass rounded-[2rem] sm:rounded-[2.25rem] p-5 sm:p-8 md:p-10 w-full relative overflow-hidden">
            
            <div class="ambient-orb absolute -top-28 -right-28 w-56 h-56 bg-indigo-500/15 rounded-full pointer-events-none"></div>

            <div class="relative z-10 flex flex-col items-center text-center">
                
                <!-- Floating Glass Document Emblem -->
                <div class="glass-folder w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-3xl bg-indigo-50/90 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-5 shadow-md relative">
                    <i class="fas fa-file-pdf text-2xl sm:text-3xl"></i>
                    <span class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 text-white text-[10px] flex items-center justify-center shadow border-2 border-white dark:border-slate-900">
                        <i class="fas fa-check"></i>
                    </span>
                </div>

                <!-- Metadata Badges -->
                <div class="flex flex-wrap items-center justify-center gap-2 mb-3.5">
                    <span class="px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200/60 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider">
                        <i class="fas fa-graduation-cap mr-1"></i> [[COURSE_BADGE]]
                    </span>
                    <span class="px-3 py-1 rounded-full bg-blue-50 border border-blue-200/60 text-blue-700 text-[11px] font-extrabold uppercase tracking-wider">
                        <i class="fas fa-layer-group mr-1"></i> [[SCHEME]]
                    </span>
                </div>

                <!-- Main SEO Heading -->
                <h1 class="text-xl sm:text-2xl md:text-3xl lg:text-[32px] font-extrabold text-slate-900 mb-3 tracking-tight leading-snug max-w-2xl">
                    KTU [[CLEAN_TITLE]] <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-sky-500">Timetable Download</span>
                </h1>
                
                <p class="text-xs sm:text-sm text-slate-500 font-semibold mb-6">
                    [[SUBTITLE_INFO]]
                </p>

                <!-- Recessed Inner Glass Notice Box -->
                <div class="inner-glass w-full rounded-2xl p-4 sm:p-5 mb-6 text-left flex items-start gap-3.5">
                    <div class="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                        <i class="fas fa-info-circle text-sm"></i>
                    </div>
                    <div class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        <strong class="text-slate-900 font-bold">Important Update:</strong> The <strong>APJ Abdul Kalam Technological University (APJAKTU)</strong> has officially published this examination timetable. Verify your subject codes, slot letters, and examination dates in the official PDF below.
                    </div>
                </div>

                <!-- ========================================================= -->
                <!-- LIQUID GLASS COUNTDOWN & DOWNLOAD ENGINE                  -->
                <!-- ========================================================= -->
                <div id="download-section" class="w-full py-2 flex flex-col items-center justify-center">
                    
                    <!-- State 1: Interactive Countdown Ring -->
                    <div id="loading-container" class="inner-glass w-full rounded-3xl p-6 sm:p-7 flex flex-col items-center justify-center space-y-4 transition-all duration-300">
                        <div class="relative w-20 h-20 flex items-center justify-center">
                            <svg class="w-20 h-20" viewBox="0 0 80 80">
                                <circle class="text-slate-200 dark:text-slate-800" stroke-width="6" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                                <circle id="countdown-ring" class="progress-ring__circle text-indigo-600" stroke-width="6" stroke-dasharray="213.6" stroke-dashoffset="0" stroke-linecap="round" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span id="countdown" class="text-xl font-extrabold text-indigo-600 leading-none">15</span>
                                <span class="text-[9px] font-bold uppercase tracking-widest text-slate-400 mt-0.5">sec</span>
                            </div>
                        </div>

                        <div class="text-center space-y-1">
                            <p id="timer-text" class="text-sm sm:text-base font-extrabold text-slate-800">
                                Preparing Official [[SEMESTER]] Timetable PDF...
                            </p>
                            <p id="timer-subtext" class="text-xs font-medium text-slate-500">
                                Bypassing KTU portal congestion for instant download
                            </p>
                        </div>

                        <div class="w-full max-w-xs h-1.5 bg-slate-200/80 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div id="countdown-bar" class="h-full bg-gradient-to-r from-indigo-600 via-sky-500 to-emerald-400 rounded-full transition-all duration-1000 ease-linear" style="width: 7%;"></div>
                        </div>
                    </div>

                    <!-- State 2: Ready Action Dock -->
                    <div id="ready-actions" class="hidden w-full flex-col gap-3 sm:gap-3.5 animate-fadeIn">
                        
                        <a id="download-btn" href="#" target="_blank" rel="noopener" class="sheen-effect btn-glow w-full bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600 text-white font-extrabold text-sm sm:text-base py-4 px-6 rounded-2xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-[0.99] flex items-center justify-center gap-3">
                            <i class="fas fa-cloud-download-alt text-lg"></i>
                            <span>Download Official PDF Timetable</span>
                            <span class="px-2 py-0.5 rounded-full bg-white/20 text-[10px] font-black uppercase tracking-wider ml-1">PDF</span>
                        </a>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 w-full">
                            <a id="whatsapp-btn" href="https://api.whatsapp.com/send?text=🚨 *[[CLEAN_TITLE]] Timetable is Out!* Download the official PDF directly here: https://www.keralatimetable.in/timetable_pages/[[SLUG]].html" target="_blank" rel="noopener noreferrer" class="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold text-xs sm:text-sm py-3.5 px-5 rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 shadow-md shadow-emerald-500/20">
                                <i class="fab fa-whatsapp text-base"></i>
                                <span>Share with Classmates</span>
                            </a>

                            <button id="copy-link-btn" type="button" class="w-full bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs sm:text-sm py-3.5 px-5 rounded-xl border border-slate-200/90 transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 shadow-sm">
                                <i class="fas fa-link text-indigo-600 text-xs"></i>
                                <span id="copy-link-text">Copy Direct Link</span>
                            </button>
                        </div>

                        <a id="whatsapp-channel-btn" href="https://whatsapp.com/channel/0029Vb7zhxw5vKABedfmht0D" target="_blank" rel="noopener noreferrer" class="inner-glass w-full p-3.5 rounded-xl hover:border-emerald-400/60 transition-all flex items-center justify-between gap-3 group">
                            <div class="flex items-center gap-3 text-left">
                                <div class="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200/60 text-emerald-600 flex items-center justify-center shrink-0">
                                    <i class="fab fa-whatsapp text-lg"></i>
                                </div>
                                <div>
                                    <p class="text-xs sm:text-sm font-extrabold text-slate-800 leading-tight">Get Instant Exam Alerts on WhatsApp</p>
                                    <p class="text-[11px] font-medium text-slate-500">Join 6,000+ KTU students on our official channel</p>
                                </div>
                            </div>
                            <span class="px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 group-hover:bg-emerald-500 group-hover:text-white text-xs font-extrabold transition-colors shrink-0">
                                Follow <i class="fas fa-arrow-right text-[10px] ml-1"></i>
                            </span>
                        </a>
                    </div>

                </div>

                <!-- Companion Study Resources -->
                <div class="w-full mt-8 pt-7 border-t border-slate-200/70 dark:border-white/10 text-left">
                    <div class="flex items-center justify-between mb-3.5">
                        <h2 class="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                            <i class="fas fa-sparkles text-indigo-500 mr-1"></i> Prepare for this Exam
                        </h2>
                        <span class="text-[11px] font-bold text-indigo-600 dark:text-indigo-400">Free KTU Resources</span>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <a href="/notes.html" class="hybrid-card p-4 rounded-2xl flex items-center justify-between gap-3 group">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                                    <i class="fas fa-book-open text-sm"></i>
                                </div>
                                <div>
                                    <h3 class="text-xs sm:text-sm font-extrabold text-slate-800">KTU Study Notes</h3>
                                    <p class="text-[11px] font-medium text-slate-500">All modules & schemes PDF</p>
                                </div>
                            </div>
                            <div class="w-7 h-7 rounded-full bg-white border border-slate-200/80 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-indigo-600 transition-all shrink-0">
                                <i class="fas fa-chevron-right text-[10px]"></i>
                            </div>
                        </a>

                        <a href="/pyq.html" class="hybrid-card p-4 rounded-2xl flex items-center justify-between gap-3 group">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center shrink-0">
                                    <i class="fas fa-file-alt text-sm"></i>
                                </div>
                                <div>
                                    <h3 class="text-xs sm:text-sm font-extrabold text-slate-800">Previous Year Papers</h3>
                                    <p class="text-[11px] font-medium text-slate-500">Official university PYQs</p>
                                </div>
                            </div>
                            <div class="w-7 h-7 rounded-full bg-white border border-slate-200/80 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-indigo-600 transition-all shrink-0">
                                <i class="fas fa-chevron-right text-[10px]"></i>
                            </div>
                        </a>
                    </div>
                </div>

                <!-- Interactive Liquid Glass FAQs -->
                <div class="w-full mt-8 pt-7 border-t border-slate-200/70 dark:border-white/10 text-left">
                    <h2 class="text-sm sm:text-base font-extrabold text-slate-800 mb-3.5 flex items-center gap-2">
                        <i class="fas fa-question-circle text-indigo-500"></i>
                        <span>Frequently Asked Questions</span>
                    </h2>

                    <div class="space-y-2.5">
                        <details class="inner-glass rounded-2xl group overflow-hidden" open>
                            <summary class="p-4 cursor-pointer flex items-center justify-between gap-3 font-bold text-slate-800 text-xs sm:text-sm select-none">
                                <span>[[FAQ_1_QUESTION]]</span>
                                <i class="fas fa-chevron-down faq-chevron text-slate-400 text-xs transition-transform duration-200"></i>
                            </summary>
                            <div class="px-4 pb-4 text-xs text-slate-600 leading-relaxed border-t border-slate-200/50 dark:border-white/5 pt-3">
                                [[FAQ_1_ANSWER]]
                            </div>
                        </details>

                        <details class="inner-glass rounded-2xl group overflow-hidden">
                            <summary class="p-4 cursor-pointer flex items-center justify-between gap-3 font-bold text-slate-800 text-xs sm:text-sm select-none">
                                <span>[[FAQ_2_QUESTION]]</span>
                                <i class="fas fa-chevron-down faq-chevron text-slate-400 text-xs transition-transform duration-200"></i>
                            </summary>
                            <div class="px-4 pb-4 text-xs text-slate-600 leading-relaxed border-t border-slate-200/50 dark:border-white/5 pt-3">
                                [[FAQ_2_ANSWER]]
                            </div>
                        </details>
                    </div>
                </div>

                <!-- SEO Tag Pills -->
                <div class="w-full mt-7 pt-6 border-t border-slate-200/70 dark:border-white/10 text-left">
                    <h3 class="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2.5">Related Searches</h3>
                    <div class="flex flex-wrap gap-1.5 sm:gap-2">
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">[[CLEAN_TITLE]]</span>
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">KTU [[SCHEME]] [[SEMESTER]] Exam Date</span>
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">APJAKTU Exam Schedule</span>
                    </div>
                </div>

            </div>
        </section>

    </main>

    <footer class="mt-auto border-t border-slate-200/60 bg-white/60 backdrop-blur-md py-8 text-center">
        <div class="max-w-3xl mx-auto px-4">
            <h3 class="text-slate-800 font-extrabold text-base sm:text-lg mb-1.5">Kerala Timetable</h3>
            <p class="text-slate-500 text-xs sm:text-sm leading-relaxed max-w-lg mx-auto">
                Providing fast, liquid-smooth access to university resources. We are an independent student platform and not officially affiliated with APJ Abdul Kalam Technological University.
            </p>
            <div class="mt-4 flex items-center justify-center gap-5">
                <a href="/timetable.html" class="text-indigo-600 text-xs font-extrabold hover:underline">Timetables</a>
                <a href="/notes.html" class="text-indigo-600 text-xs font-extrabold hover:underline">Notes</a>
                <a href="/about.html" class="text-indigo-600 text-xs font-extrabold hover:underline">About Us</a>
                <a href="/contact-us.html" class="text-indigo-600 text-xs font-extrabold hover:underline">Contact</a>
            </div>
        </div>
    </footer>

    <script src="../components.js?v=12"></script>
    <script>
        loadNavigation('timetable', '../', false);
    </script>

    <script>
        const pdfLink = "[[PDF_LINK]]";
        const totalTime = 15;
        let timeLeft = totalTime;
        
        const countdownEl = document.getElementById('countdown');
        const ringEl = document.getElementById('countdown-ring');
        const barEl = document.getElementById('countdown-bar');
        const timerSubtext = document.getElementById('timer-subtext');
        const loadingContainer = document.getElementById('loading-container');
        const readyActions = document.getElementById('ready-actions');
        const downloadBtn = document.getElementById('download-btn');
        const copyLinkBtn = document.getElementById('copy-link-btn');
        const copyLinkText = document.getElementById('copy-link-text');

        const circumference = 2 * Math.PI * 34;

        const timer = setInterval(() => {
            timeLeft--;
            if (countdownEl) countdownEl.textContent = timeLeft;

            const elapsed = totalTime - timeLeft;
            const offset = circumference - (elapsed / totalTime) * circumference;
            if (ringEl) ringEl.style.strokeDashoffset = offset;
            if (barEl) barEl.style.width = `${Math.min(100, Math.round((elapsed / totalTime) * 100))}%`;

            if (timeLeft === 8 && timerSubtext) {
                timerSubtext.textContent = "Verifying official APJAKTU PDF signature...";
            } else if (timeLeft === 3 && timerSubtext) {
                timerSubtext.textContent = "Almost ready! Unlocking direct download...";
            }

            if (timeLeft <= 0) {
                clearInterval(timer);
                loadingContainer.classList.add('hidden');
                
                downloadBtn.href = pdfLink;
                readyActions.classList.remove('hidden');
                readyActions.classList.add('flex');

                if (typeof window.triggerCapsule === 'function') {
                    window.triggerCapsule('success', 'Timetable PDF Ready to Download!');
                }
            }
        }, 1000);

        copyLinkBtn?.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(window.location.href);
                if (copyLinkText) copyLinkText.textContent = 'Link Copied!';
                if (typeof window.triggerCapsule === 'function') {
                    window.triggerCapsule('success', 'Page link copied to clipboard');
                }
                setTimeout(() => {
                    if (copyLinkText) copyLinkText.textContent = 'Copy Direct Link';
                }, 2500);
            } catch (err) {
                if (typeof window.triggerCapsule === 'function') {
                    window.triggerCapsule('amber', 'Could not copy link');
                }
            }
        });
    </script>
</body>
</html>"""

    replacements = {
        "[[SEO_TITLE_TAG]]": seo_title_tag,
        "[[CLEAN_TITLE]]": clean_title,
        "[[SLUG]]": slug,
        "[[SEMESTER]]": semester,
        "[[SCHEME]]": scheme,
        "[[COURSE_BADGE]]": course_badge,
        "[[SUBTITLE_INFO]]": subtitle_info,
        "[[FAQ_1_QUESTION]]": faq_1_q,
        "[[FAQ_1_ANSWER]]": faq_1_a,
        "[[FAQ_2_QUESTION]]": faq_2_q,
        "[[FAQ_2_ANSWER]]": faq_2_a,
        "[[PDF_LINK]]": pdf_link,
    }

    final_html = html_template
    for key, val in replacements.items():
        final_html = final_html.replace(key, str(val))

    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)

    return html_filepath, f"timetable_pages/{html_filename}"


# -------------------------------------------------------------------
# AI EXTRACTION FUNCTION (READS FULL PDF & FORMATS LIKE S3 PAGE)
# -------------------------------------------------------------------
def extract_dashboard_data_with_ai(pdf_path, original_title, pdf_link):
    """Reads the PDF text and uses Gemini to extract structured dates, S3-style titles, Order No, and FAQs."""
    if not client:
        print("⚠️ GEMINI_API_KEY not set. Using regex fallback metadata.")
        return None

    print(f"🧠 Asking AI to analyze: {original_title}...")

    raw_text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i in range(len(reader.pages)):
                text = reader.pages[i].extract_text()
                if text:
                    raw_text += text + "\n"
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

    pre_cleaned = clean_ktu_raw_title(original_title)

    prompt = f"""
    You are an expert KTU (APJAKTU) examination data extractor. Analyze this KTU exam timetable text and notification title.
    Original Raw KTU Title: {original_title}
    Pre-cleaned Reference Title: {pre_cleaned['clean_title']}
    
    Tasks based on the schema:
    1. id: Create a short, unique snake_case ID (e.g., "btech_s3_nov2026_2024").
    2. title: Format the title in the EXACT S3 standard pattern:
       "[Course] [Semester] ([R, S] or [R]) Exam [Month] [Year] ([YYYY] Scheme)"
       Do NOT include "Detailed Time Table of", "Notification", "KTU", or "/Working Professionals" inside `title`.
    3. courseBadge: Short course + semester + (R, S)/(R) badge (e.g., "B.Tech S3 (R, S)", "BBA Honours S5 (R)", "MBA S3 (R, S)").
    4. seoTitleTag: Format like "KTU B.Tech S3 (R,S) Exam Timetable Download November 2026 (2024 Scheme)".
    5. slug: URL-friendly slug expanding (R, S) to regular-supply and (R) to regular, without the word "exam" (e.g., "btech-s3-regular-supply-november-2026-2024-scheme").
    6. subtitleInfo: Extract the KTU Order/Notification number from the PDF text if present and whether Working Professionals are included.
    7. startDate: Scan the ENTIRE document and find the VERY FIRST exam date and time. Format: YYYY-MM-DDTHH:MM:SS
    8. endDate: Scan the ENTIRE document and find the VERY LAST/LATEST exam date and time. Format: YYYY-MM-DDTHH:MM:SS
    9. startDateFormatted: Human-readable first exam date with day of week and Slot if mentioned (e.g., "Tuesday, November 24, 2026 (Slot A)").
    10. endDateFormatted: Human-readable last exam date with day of week and Slot if mentioned (e.g., "Tuesday, December 8, 2026 (Slot G)").
    11. faqSecondQuestion: "Does this timetable include Working Professionals (WP)?" (or a relevant second FAQ question for this specific degree).
    12. faqSecondAnswer: A clear 1-sentence answer referencing the official Notification No., date, and whether Working Professionals (WP) or regular/supply batches are covered.
    13. semester: Extract the specific semester (e.g., 'S3', 'S5', 'S7').
    14. categoryBadge: Extract a category for filtering (e.g., 'S1', 'S3', 'S5', 'S7').
    15. type: 'Regular', 'Supply', 'Honours', or 'Regular/Supply'.
    16. scheme: (e.g., '2024 Scheme', '2019 Scheme', '2020 Scheme').
    17. pdfLink: Return exactly "{pdf_link}".
    18. viewLink: Return an empty string ("").
    
    Messy PDF Text:
    {raw_text[:40000]} 
    """

    for model_name in ("gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.5-flash"):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TimetableData,
                    temperature=0.0,
                ),
            )
            ai_data = json.loads(response.text)
            print(f"✅ AI Extraction Successful ({model_name})! Title: {ai_data['title']} | Start: {ai_data['startDate']} | End: {ai_data['endDate']}")
            return ai_data
        except Exception as e:
            print(f"⚠️ AI Extraction attempt with {model_name} failed: {e}")

    return None


# -------------------------------------------------------------------
# CONFIG UPDATER FUNCTION
# -------------------------------------------------------------------
def update_timetable_config(ai_data_dict, config_path="timetable-config.js"):
    """Safely appends the clean 10-key JSON object into window.timetablesData without duplicating IDs."""
    if not ai_data_dict:
        return

    dashboard_keys = [
        "id", "title", "semester", "categoryBadge", "type",
        "scheme", "startDate", "endDate", "viewLink", "pdfLink"
    ]
    clean_dashboard_dict = {k: ai_data_dict[k] for k in dashboard_keys if k in ai_data_dict}

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "window.timetablesData = [\n];"

        if f'"{clean_dashboard_dict.get("id")}"' in content or f'"{clean_dashboard_dict.get("pdfLink")}"' in content:
            print(f"ℹ️ Entry '{clean_dashboard_dict.get('id')}' already in {config_path}, skipping duplicate config entry.")
            return

        clean_json = json.dumps(clean_dashboard_dict, indent=4)

        last_bracket_idx = content.rfind(']')
        if last_bracket_idx != -1:
            array_content = content[content.find('[') + 1:last_bracket_idx].strip()
            if array_content:
                new_content = content[:last_bracket_idx] + ",\n" + clean_json + "\n" + content[last_bracket_idx:]
            else:
                new_content = content[:last_bracket_idx] + "\n" + clean_json + "\n" + content[last_bracket_idx:]

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("💾 Dashboard config updated!")
        else:
            print("❌ Error: Could not find closing bracket in config file.")

    except Exception as e:
        print(f"❌ Error updating config: {e}")


# -------------------------------------------------------------------
# KTU PORTAL API & NON-SPAMMING TURNSTILE SOLVER
# -------------------------------------------------------------------
KTU_TIMETABLE_API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/timetable"
KTU_ANNOUNCEMENTS_API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"
KTU_ATTACHMENT_API_URLS = [
    "https://api.ktu.edu.in/ktu-web-portal-api/anon/getAttachment",
    "https://api.ktu.edu.in/ktu-web-portal-api/service/anon/getAttachments",
]
KTU_MIRROR_API_BASE = os.environ.get(
    "KTU_MIRROR_API_BASE",
    "https://ktu-announcements-api-wxk8.onrender.com"
)

KTU_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://ktu.edu.in",
    "Referer": "https://ktu.edu.in/"
}


def get_page_turnstile_token(page) -> str:
    """Reads any active Cloudflare Turnstile token from the page DOM, inputs, or window.turnstile."""
    try:
        token = page.evaluate(
            """() => {
                try {
                    const inputs = document.querySelectorAll('input[name="cf-turnstile-response"], input[name*="turnstile"], textarea[name="cf-turnstile-response"]');
                    for (const el of inputs) {
                        if (el && el.value && el.value.length > 20) return el.value;
                    }
                    if (window.turnstile && typeof window.turnstile.getResponse === 'function') {
                        const r = window.turnstile.getResponse();
                        if (r && r.length > 20) return r;
                    }
                } catch (e) {}
                return "";
            }"""
        )
        return token or ""
    except Exception:
        return ""


def click_turnstile_checkbox_once(page) -> bool:
    """
    Finds the Cloudflare Turnstile iframe and clicks the checkbox coordinates ONCE.
    Does not spam-click so the verification spinner can finish without resetting.
    """
    try:
        iframe_locators = page.locator(
            "iframe[src*='cloudflare'], iframe[src*='turnstile'], iframe[title*='Cloudflare'], iframe[title*='Widget']"
        )
        count = iframe_locators.count()
        for i in range(count):
            el = iframe_locators.nth(i)
            if not el.is_visible():
                continue
            box = el.bounding_box()
            if box and box["width"] > 30 and box["height"] > 20:
                click_x = box["x"] + 28
                click_y = box["y"] + (box["height"] / 2)
                page.mouse.move(click_x - 15, click_y - 8, steps=6)
                page.wait_for_timeout(180)
                page.mouse.click(click_x, click_y)
                return True

        for frame in page.frames:
            frame_url = (frame.url or "").lower()
            if "challenges.cloudflare.com" in frame_url or "turnstile" in frame_url:
                try:
                    frame_el = frame.frame_element()
                    box = frame_el.bounding_box()
                    if box and box["width"] > 30 and box["height"] > 20:
                        click_x = box["x"] + 28
                        click_y = box["y"] + (box["height"] / 2)
                        page.mouse.move(click_x - 12, click_y - 6, steps=5)
                        page.wait_for_timeout(180)
                        page.mouse.click(click_x, click_y)
                        return True
                except Exception:
                    pass
    except Exception:
        pass
    return False


def wait_for_turnstile_or_data(page, captured_state: dict, timetable_metadata: list, max_wait_sec: int = 28) -> str:
    """
    Waits for Turnstile to auto-solve or clicks it at most ONCE every 14 seconds.
    Returns the captured Turnstile token if found.
    """
    last_click_time = 0.0
    click_attempts = 0
    start_ts = time.time()

    while (time.time() - start_ts) < max_wait_sec:
        page.wait_for_timeout(1500)

        # 1. Check if token already captured via network or DOM
        tok = get_page_turnstile_token(page) or captured_state.get("x_token") or ""
        if tok:
            captured_state["x_token"] = tok
            return tok

        # 2. Check if data or download buttons already rendered
        if timetable_metadata:
            return captured_state.get("x_token") or ""
        try:
            if page.locator("button[value], a.btn-outline-primary, button.btn-outline-primary").count() > 0:
                return captured_state.get("x_token") or ""
        except Exception:
            pass

        # 3. Click Turnstile ONLY if at least 14s have elapsed since last click (max 2 clicks total)
        now = time.time()
        if click_attempts < 2 and (now - last_click_time) >= 14.0 and (now - start_ts) >= 4.0:
            if click_turnstile_checkbox_once(page):
                click_attempts += 1
                last_click_time = now
                print(f"🛡️ [Click {click_attempts}/2] Clicked Cloudflare Turnstile checkbox — waiting up to 14s for verification...")

    return get_page_turnstile_token(page) or captured_state.get("x_token") or ""


def parse_ktu_timetable_items(content_list, filter_timetables_only=False):
    """Normalizes raw KTU JSON timetable/announcement objects into a clean list with unique filenames."""
    parsed = []
    if not isinstance(content_list, list):
        return parsed

    for idx, item in enumerate(content_list):
        if not isinstance(item, dict):
            continue
        title = (
            item.get("timeTableTitle")
            or item.get("title")
            or item.get("subject")
            or item.get("notificationTitle")
            or "KTU Exam Timetable"
        ).strip()

        if filter_timetables_only and not is_timetable_notification(title):
            continue

        date_raw = (
            item.get("createdDate")
            or item.get("publishedOn")
            or item.get("announcementDate")
            or item.get("date")
            or "2026"
        )
        date_str = str(date_raw).split("T")[0].split(" ")[0]

        # 1. Direct encryptId
        enc_id = item.get("encryptId") or item.get("encryptAttachmentId")
        raw_name = item.get("fileName") or item.get("attachmentName") or ""

        if enc_id:
            parsed.append({
                "index": idx,
                "id": item.get("id"),
                "title": title,
                "buttonText": raw_name.strip(),
                "date": date_str,
                "encryptId": enc_id,
                "fileName": build_unique_pdf_filename(title, raw_name, enc_id)
            })
        # 2. Official KTU attachmentList
        elif isinstance(item.get("attachmentList"), list):
            for att in item["attachmentList"]:
                att_enc = att.get("encryptId") or att.get("encryptAttachmentId")
                att_name = att.get("attachmentName") or att.get("fileName") or ""
                if att_enc:
                    parsed.append({
                        "index": idx,
                        "id": item.get("id"),
                        "title": title,
                        "buttonText": att_name.strip(),
                        "date": date_str,
                        "encryptId": att_enc,
                        "fileName": build_unique_pdf_filename(title, att_name, att_enc)
                    })
        # 3. Mirror API attachments array ([{"name": "Notification", "encrypt_id": "AAAebw=="}])
        elif isinstance(item.get("attachments"), list):
            for att in item["attachments"]:
                att_enc = att.get("encrypt_id") or att.get("encryptId")
                att_name = att.get("name") or att.get("fileName") or ""
                if att_enc:
                    parsed.append({
                        "index": idx,
                        "id": item.get("id"),
                        "title": title,
                        "buttonText": att_name.strip(),
                        "date": date_str,
                        "encryptId": att_enc,
                        "fileName": build_unique_pdf_filename(title, att_name, att_enc)
                    })
    return parsed


def fetch_ktu_list_via_browser(page, x_token: str) -> list:
    """
    Directly executes fetch() inside the browser context to query KTU's timetable & announcements APIs
    in case Angular did not auto-fire the request after Turnstile completed.
    """
    endpoints = [
        (KTU_TIMETABLE_API_URL, False),
        (KTU_ANNOUNCEMENTS_API_URL, True),
    ]
    collected = []

    for api_url, is_ann in endpoints:
        try:
            payload_body = {"size": 20, "page": 0, "searchText": ""}
            if x_token:
                payload_body["token"] = x_token

            res = page.evaluate(
                """async ({ url, payload, xToken }) => {
                    try {
                        const headers = {
                            "Accept": "application/json, text/plain, */*",
                            "Content-Type": "application/json"
                        };
                        if (xToken) {
                            headers["x-token"] = xToken;
                            headers["X-Token"] = xToken;
                        }
                        const r = await fetch(url, {
                            method: "POST",
                            headers,
                            body: JSON.stringify(payload)
                        });
                        if (!r.ok) return { ok: false, status: r.status };
                        const text = await r.text();
                        return { ok: true, text };
                    } catch (e) {
                        return { ok: false, error: String(e) };
                    }
                }""",
                {"url": api_url, "payload": payload_body, "xToken": x_token or ""}
            )
            if isinstance(res, dict) and res.get("ok") and res.get("text"):
                data = json.loads(res["text"])
                content_list = (
                    data.get("content")
                    if isinstance(data, dict) and isinstance(data.get("content"), list)
                    else (data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), list) else (data if isinstance(data, list) else None))
                )
                if content_list:
                    items = parse_ktu_timetable_items(content_list, filter_timetables_only=is_ann)
                    if items:
                        print(f"✅ In-Browser API Fetch succeeded ({api_url}): {len(items)} timetable(s) found.")
                        collected.extend(items)
                        break
        except Exception:
            pass

    return collected


def save_raw_or_base64_pdf(raw_bytes_or_text, save_path) -> bool:
    """Decodes raw PDF bytes or JSON/base64 attachment responses from KTU's getAttachment endpoint."""
    if isinstance(raw_bytes_or_text, bytes):
        if raw_bytes_or_text.startswith(b"%PDF"):
            with open(save_path, "wb") as f:
                f.write(raw_bytes_or_text)
            return True
        idx = raw_bytes_or_text.find(b"%PDF-")
        if 0 < idx < 128:
            with open(save_path, "wb") as f:
                f.write(raw_bytes_or_text[idx:])
            return True
        try:
            raw_bytes_or_text = raw_bytes_or_text.decode("utf-8", errors="ignore")
        except Exception:
            return False

    if isinstance(raw_bytes_or_text, str):
        text = raw_bytes_or_text.strip()
        if not text:
            return False
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                b64_str = (
                    data.get("file")
                    or data.get("data")
                    or data.get("attachment")
                    or data.get("content")
                    or data.get("fileData")
                    or data.get("byteData")
                    or data.get("response")
                )
                if isinstance(b64_str, str) and b64_str:
                    pdf_bytes = base64.b64decode(b64_str)
                    if b"%PDF" in pdf_bytes[:64]:
                        with open(save_path, "wb") as f:
                            f.write(pdf_bytes[pdf_bytes.find(b"%PDF"):])
                        return True
            elif isinstance(data, str):
                pdf_bytes = base64.b64decode(data)
                if b"%PDF" in pdf_bytes[:64]:
                    with open(save_path, "wb") as f:
                        f.write(pdf_bytes[pdf_bytes.find(b"%PDF"):])
                    return True
        except Exception:
            try:
                pdf_bytes = base64.b64decode(text.strip('"'))
                if b"%PDF" in pdf_bytes[:64]:
                    with open(save_path, "wb") as f:
                        f.write(pdf_bytes[pdf_bytes.find(b"%PDF"):])
                    return True
            except Exception:
                pass
    return False


def download_pdf_via_browser_fetch(page, encrypt_id: str, x_token: str, save_path: str) -> bool:
    """
    Executes fetch() inside the live Camoufox/Playwright browser context on ktu.edu.in.
    Tries JSON body, token-enriched JSON body, and form-urlencoded body.
    """
    fresh_token = get_page_turnstile_token(page) or x_token or ""

    payload_variants = [
        {"contentType": "application/json", "body": json.dumps({"encryptId": encrypt_id})},
        {"contentType": "application/json", "body": json.dumps({"encryptId": encrypt_id, "token": fresh_token})},
        {"contentType": "application/x-www-form-urlencoded", "body": f"encryptId={requests.utils.quote(encrypt_id, safe='')}"},
    ]

    for api_url in KTU_ATTACHMENT_API_URLS:
        for variant in payload_variants:
            try:
                result = page.evaluate(
                    """async ({ url, contentType, bodyStr, xToken }) => {
                        try {
                            const headers = {
                                "Accept": "application/json, text/plain, application/pdf, */*",
                                "Content-Type": contentType
                            };
                            if (xToken) {
                                headers["x-token"] = xToken;
                                headers["X-Token"] = xToken;
                            }
                            const res = await fetch(url, {
                                method: "POST",
                                headers,
                                body: bodyStr,
                                credentials: "include"
                            });
                            if (!res.ok) {
                                return { ok: false, status: res.status };
                            }
                            const buf = await res.arrayBuffer();
                            const bytes = new Uint8Array(buf);
                            if (bytes.length < 200) {
                                return { ok: false, status: res.status, len: bytes.length };
                            }
                            let binary = "";
                            const chunkSize = 0x8000;
                            for (let i = 0; i < bytes.length; i += chunkSize) {
                                binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
                            }
                            return { ok: true, status: res.status, b64: btoa(binary) };
                        } catch (e) {
                            return { ok: false, error: String(e) };
                        }
                    }""",
                    {
                        "url": api_url,
                        "contentType": variant["contentType"],
                        "bodyStr": variant["body"],
                        "xToken": fresh_token
                    }
                )
                if isinstance(result, dict) and result.get("ok") and result.get("b64"):
                    raw_bytes = base64.b64decode(result["b64"])
                    if save_raw_or_base64_pdf(raw_bytes, save_path):
                        return True
            except Exception:
                pass
    return False


def download_pdf_from_ktu_api(encrypt_id: str, save_path: str, x_token: str = None, cookies: list = None) -> bool:
    """
    Downloads a PDF using:
    1. KTU's official `getAttachment` endpoint over a custom SECLEVEL=1 TLS session + browser cookies
    2. Community Camoufox pre-cached mirror endpoint (`/download/{encrypt_id}`) with retry
    """
    headers = dict(KTU_HEADERS)
    if x_token:
        headers["x-token"] = x_token
        headers["X-Token"] = x_token

    if cookies:
        for c in cookies:
            if c.get("name") and c.get("value"):
                KTU_SESSION.cookies.set(c["name"], c["value"])

    # 1. Direct KTU API with custom TLS adapter
    for url in KTU_ATTACHMENT_API_URLS:
        for payload in ({"encryptId": encrypt_id}, {"encryptId": encrypt_id, "token": x_token or ""}):
            try:
                res = KTU_SESSION.post(
                    url,
                    json=payload,
                    headers=headers,
                    verify=False,
                    timeout=30
                )
                if res.status_code == 200 and len(res.content) > 500:
                    if save_raw_or_base64_pdf(res.content, save_path):
                        return True
            except Exception:
                pass

    # 2. Fallback: Camoufox Mirror API download endpoint (try raw and URL-encoded with backoff)
    candidate_ids = []
    for cid in (encrypt_id, requests.utils.quote(encrypt_id, safe="")):
        if cid not in candidate_ids:
            candidate_ids.append(cid)

    for attempt in range(2):
        for cid in candidate_ids:
            try:
                mirror_download_url = f"{KTU_MIRROR_API_BASE.rstrip('/')}/download/{cid}"
                res = KTU_SESSION.get(mirror_download_url, timeout=60)
                if res.status_code == 200 and len(res.content) > 500:
                    if save_raw_or_base64_pdf(res.content, save_path):
                        return True
                elif attempt == 1:
                    print(f" -> Mirror /download/{cid} status: {res.status_code} ({res.text[:90]})")
            except Exception as e:
                if attempt == 1:
                    print(f" -> Mirror download error: {e}")
        time.sleep(3)

    return False


def fetch_timetables_from_mirror_api() -> list:
    """Fallback fetcher using the Camoufox-backed KTU Announcements API."""
    endpoint = f"{KTU_MIRROR_API_BASE.rstrip('/')}/announcements"
    print(f"🌐 Querying Camoufox Pre-Cached Mirror API ({endpoint}) [up to 75s for Render cold start]...")
    for attempt in range(2):
        try:
            res = KTU_SESSION.get(endpoint, timeout=75)
            if res.status_code == 200:
                payload = res.json()
                data_list = payload.get("data") if isinstance(payload, dict) else (payload if isinstance(payload, list) else [])
                items = parse_ktu_timetable_items(data_list, filter_timetables_only=True)
                print(f"✅ Mirror API returned {len(items)} timetable attachment(s) out of {len(data_list)} recent notifications.")
                return items
        except Exception as e:
            print(f"⚠️ Mirror API attempt {attempt + 1} note: {e}")
            time.sleep(4)
    return []


def process_downloaded_pdf(save_path, filename, title, date_str, html_dir):
    """Runs AI extraction, generates the S3-Template Liquid Glass HTML page, updates config, and sends push notification."""
    relative_pdf_link = f"downloads_timetable/{filename}"
    ai_extracted_data = extract_dashboard_data_with_ai(save_path, title, relative_pdf_link)

    if ai_extracted_data:
        short_title = ai_extracted_data.get('title', clean_ktu_raw_title(title)['clean_title'])
        html_filepath, relative_html_link = generate_html_page(title, filename, ai_data=ai_extracted_data, html_output_dir=html_dir)
        print(f" -> HTML Generated: {html_filepath}")

        ai_extracted_data['viewLink'] = relative_html_link
        update_timetable_config(ai_extracted_data)

        send_push_notification(
            title="🚨 New KTU Timetable Published!",
            body=f"{short_title} is now available on the dashboard."
        )
    else:
        fallback_clean = clean_ktu_raw_title(title)
        html_filepath, relative_html_link = generate_html_page(title, filename, ai_data=None, html_output_dir=html_dir)
        print(f" -> HTML Generated (Regex Clean Fallback): {html_filepath}")

        fallback_dashboard = {
            "id": create_seo_slug(fallback_clean["clean_title"]).replace("-", "_")[:45],
            "title": fallback_clean["clean_title"],
            "semester": fallback_clean["semester"],
            "categoryBadge": fallback_clean["semester"],
            "type": "Regular/Supply" if "(R, S)" in fallback_clean["clean_title"] else "Regular",
            "scheme": fallback_clean["scheme"],
            "startDate": f"{date_str}T09:30:00",
            "endDate": f"{date_str}T12:30:00",
            "viewLink": relative_html_link,
            "pdfLink": relative_pdf_link
        }
        update_timetable_config(fallback_dashboard)

        send_push_notification(
            title="🚨 New KTU Timetable Published!",
            body=f"{fallback_clean['clean_title']} is now available on the dashboard."
        )

    return {
        "title": title,
        "date": date_str,
        "filename": filename,
    }


# -------------------------------------------------------------------
# UNIFIED PAGE SCRAPER & IN-BROWSER DOWNLOADER
# -------------------------------------------------------------------
def _scrape_and_download_with_page(page, pdf_dir, html_dir):
    """Keeps the browser session ALIVE during both metadata discovery AND PDF downloading."""
    timetable_metadata = []
    seen_encrypt_ids = set()
    captured_state = {"x_token": None, "last_attachment_body": None}
    downloaded_files = []

    def on_request(request):
        tok = request.headers.get("x-token") or request.headers.get("X-Token")
        if tok:
            captured_state["x_token"] = tok

    def on_response(response):
        if response.request.method == "OPTIONS":
            return
        url_lower = response.url.lower()

        req_token = response.request.headers.get("x-token") or response.request.headers.get("X-Token")
        if req_token:
            captured_state["x_token"] = req_token

        if "getattachment" in url_lower and response.status == 200:
            try:
                captured_state["last_attachment_body"] = response.body()
            except Exception:
                pass
            return

        if ("/anon/timetable" in url_lower or "/anon/announcemnts" in url_lower or "timetable" in url_lower) and response.status == 200:
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                return
            try:
                raw_body = response.text()
                if not raw_body or not raw_body.strip():
                    return
                data = json.loads(raw_body)
                content_list = (
                    data.get("content")
                    if isinstance(data, dict) and isinstance(data.get("content"), list)
                    else (data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), list) else (data if isinstance(data, list) else None))
                )
                if content_list:
                    is_ann = "announcemnt" in url_lower
                    parsed_items = parse_ktu_timetable_items(content_list, filter_timetables_only=is_ann)
                    added = 0
                    for item in parsed_items:
                        if item["encryptId"] not in seen_encrypt_ids:
                            seen_encrypt_ids.add(item["encryptId"])
                            timetable_metadata.append(item)
                            added += 1
                    if added > 0:
                        print(f"✅ Captured {added} timetable(s) from KTU API ({response.url}) | x-tokenPresent={bool(captured_state.get('x_token'))}")
            except Exception as e:
                print(f"⚠️ Non-fatal JSON parse note on {response.url}: {e}")

    page.on("request", on_request)
    page.on("response", on_response)

    target_pages = [
        "https://ktu.edu.in/exam/timetable",
        "https://ktu.edu.in/Menu/announcements",
    ]

    for url in target_pages:
        if timetable_metadata:
            break
        print(f"Navigating to {url} ...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except Exception as nav_err:
            print(f"⚠️ Navigation warning ({nav_err}), continuing...")

        # Wait cleanly for Turnstile without spam-clicking
        tok = wait_for_turnstile_or_data(page, captured_state, timetable_metadata, max_wait_sec=28)
        if tok:
            print(f"🔑 Turnstile token active (len={len(tok)})!")

        # If Angular didn't fire the XHR automatically, fetch directly inside the browser context
        if not timetable_metadata:
            browser_items = fetch_ktu_list_via_browser(page, captured_state.get("x_token"))
            for item in browser_items:
                if item["encryptId"] not in seen_encrypt_ids:
                    seen_encrypt_ids.add(item["encryptId"])
                    timetable_metadata.append(item)

    # Fallback to Pre-Cached Mirror API for metadata list while keeping browser open for PDF fetch
    if not timetable_metadata:
        print("⚠️ Direct KTU portal returned empty list. Switching to Pre-Cached Camoufox Mirror API...")
        mirror_items = fetch_timetables_from_mirror_api()
        for item in mirror_items:
            if item["encryptId"] not in seen_encrypt_ids:
                seen_encrypt_ids.add(item["encryptId"])
                timetable_metadata.append(item)

    print(f"\n📋 Processing {len(timetable_metadata)} timetable(s):")

    try:
        browser_cookies = page.context.cookies()
    except Exception:
        browser_cookies = []

    for tb in timetable_metadata:
        title = tb['title']
        encrypt_id = tb['encryptId']

        if not encrypt_id:
            continue

        predicted_filename = sanitize_filename(f"{tb['date']}_{tb['fileName']}")
        save_path = os.path.join(pdf_dir, predicted_filename)

        if os.path.exists(save_path):
            print(f"⏭️ Skipping (Already Exists): '{title}'")
            continue

        print(f"\n⬇️ Downloading NEW timetable: '{title}' (encryptId={encrypt_id})")
        downloaded_ok = False
        filename = predicted_filename

        # Method A: In-browser fetch() using the live page's Turnstile token & TLS session
        if download_pdf_via_browser_fetch(page, encrypt_id, captured_state.get("x_token"), save_path):
            print(f" -> PDF Saved via In-Browser Fetch: {filename}")
            downloaded_ok = True

        # Method B: Click the button in the live browser (if rendered on page)
        if not downloaded_ok:
            try:
                button = page.locator(f"button[value='{encrypt_id}']")
                if button.count() == 0:
                    card = page.locator("div.card, tr, li").filter(has_text=title[:35])
                    if card.count() > 0:
                        button = card.first.locator("button, a.btn")
                if button.count() > 0:
                    captured_state["last_attachment_body"] = None
                    button.first.scroll_into_view_if_needed()
                    try:
                        with page.expect_download(timeout=15000) as download_info:
                            button.first.click()
                        download = download_info.value
                        dl_suggested = download.suggested_filename
                        if dl_suggested and dl_suggested.lower() not in ("notification.pdf", "notification"):
                            filename = sanitize_filename(f"{tb['date']}_{dl_suggested}")
                            save_path = os.path.join(pdf_dir, filename)
                        download.save_as(save_path)
                        print(f" -> PDF Saved via Browser Download: {filename}")
                        downloaded_ok = True
                    except Exception:
                        page.wait_for_timeout(3000)
                        if captured_state.get("last_attachment_body"):
                            if save_raw_or_base64_pdf(captured_state["last_attachment_body"], save_path):
                                print(f" -> PDF Saved via Intercepted /getAttachment XHR Response: {filename}")
                                downloaded_ok = True
            except Exception as click_err:
                print(f" -> Browser click note: {click_err}")

        # Method C: Direct KTU TLS Session (SECLEVEL=1) + Mirror `/download/{encrypt_id}`
        if not downloaded_ok:
            if download_pdf_from_ktu_api(
                encrypt_id,
                save_path,
                x_token=captured_state.get("x_token"),
                cookies=browser_cookies
            ):
                print(f" -> PDF Saved via Direct/Mirror API: {filename}")
                downloaded_ok = True
            else:
                print(f" -> ❌ Failed to download PDF for '{title}'")

        if downloaded_ok:
            result = process_downloaded_pdf(save_path, filename, title, tb['date'], html_dir)
            downloaded_files.append(result)
            page.wait_for_timeout(1200)

    return downloaded_files, len(timetable_metadata)


def scrape_exam_timetables(pdf_dir="./downloads_timetable", html_dir="./timetable_pages"):
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)

    # -------------------------------------------------------------------
    # TIER 1: CAMOUFOX ANTI-DETECT BROWSER (Headed inside Xvfb for Turnstile)
    # -------------------------------------------------------------------
    if HAS_CAMOUFOX:
        has_display = bool(os.environ.get("DISPLAY"))
        camoufox_headless_mode = False if has_display else "virtual"
        print(f"🦊 Launching Camoufox Anti-Detect Browser (headless={camoufox_headless_mode}, DISPLAY={os.environ.get('DISPLAY')})...")
        try:
            with Camoufox(
                headless=camoufox_headless_mode,
                geoip=True,
                disable_coop=True,
                humanize=True,
                i_know_what_im_doing=True
            ) as browser:
                page = browser.new_page(ignore_https_errors=True)
                downloaded_files, count = _scrape_and_download_with_page(page, pdf_dir, html_dir)
                if downloaded_files:
                    return downloaded_files
        except Exception as cam_err:
            print(f"⚠️ Camoufox session warning: {cam_err}")

    # -------------------------------------------------------------------
    # TIER 2: PLAYWRIGHT STEALTH + MIRROR API FALLBACK
    # -------------------------------------------------------------------
    print("🌐 Launching Playwright Browser (with Non-Spam Turnstile Handler & Mirror Fallback)...")
    with sync_playwright() as p:
        has_display = bool(os.environ.get("DISPLAY"))
        browser = p.chromium.launch(
            headless=not has_display,
            args=[
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        context = browser.new_context(
            user_agent=KTU_HEADERS["User-Agent"],
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            ignore_https_errors=True
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        downloaded_files, _ = _scrape_and_download_with_page(page, pdf_dir, html_dir)
        browser.close()
        return downloaded_files


if __name__ == "__main__":
    results = scrape_exam_timetables()
    print("\n" + "=" * 50 + "\n          NEW DOWNLOADS SUMMARY\n" + "=" * 50)
    if not results:
        print("No new timetables found today.")
    else:
        for r in results:
            print(f"[{r['date']}] {r['title']} -> Page & Config Updated (Push Sent)")
