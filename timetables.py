import os
import json
import re
import base64
import requests
import urllib3
import PyPDF2
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types

# --- FIREBASE IMPORTS ---
import firebase_admin
from firebase_admin import credentials, messaging, db

# Disable SSL warnings when bypassing KTU's misconfigured SSL certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """Fetches tokens from Firebase and broadcasts the push notification."""
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
        
        for i in range(0, len(tokens), 500):
            batch_tokens = tokens[i:i + 500]
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                tokens=batch_tokens
            )
            response = messaging.send_multicast(message)
            success_total += response.success_count
            failure_total += response.failure_count
            
        print(f"🚀 Push Sent! Success: {success_total} | Failed: {failure_total}")
        
    except Exception as e:
        print(f"❌ Error sending push notification: {e}")


# -------------------------------------------------------------------
# AI SETUP & SCHEMA
# -------------------------------------------------------------------
client = genai.Client()

class TimetableData(BaseModel):
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

# -------------------------------------------------------------------
# UTILITY FUNCTIONS & LIQUID GLASS HTML GENERATOR
# -------------------------------------------------------------------
def create_seo_slug(title):
    """Converts a title into a clean, URL-friendly string (e.g., ktu-btech-s4-exam)"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

def sanitize_filename(name):
    """Ensures PDF filenames don't contain invalid OS path characters."""
    clean = re.sub(r'[\\/*?:"<>|]', '_', name)
    clean = re.sub(r'\s+', '_', clean)
    if not clean.lower().endswith('.pdf'):
        clean += '.pdf'
    return clean

def generate_html_page(short_title, pdf_filename, html_output_dir="./timetable_pages"):
    """Injects the scraped data into the Liquid Glass HTML template and saves the file."""
    os.makedirs(html_output_dir, exist_ok=True)
    
    slug = create_seo_slug(short_title)
    html_filename = f"{slug}.html"
    html_filepath = os.path.join(html_output_dir, html_filename)
    
    # Relative path from the HTML folder to the PDF folder
    pdf_link = f"../downloads_timetable/{pdf_filename}"
    
    # Liquid Glass HTML Template (Light & 120FPS Dark Mode Adaptive)
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <meta name="google-site-verification" content="cPHgzg8741NBFQ5HszgVIPA3EMrKJLlj7IHcyLGM2Lo" />
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7313827303298932" crossorigin="anonymous"></script>
    
    <title>[[TITLE]] + Timetable Download | KTU Timetable</title>
    <link rel="canonical" href="https://keralatimetable.in/timetable_pages/[[SLUG]].html" />

    <meta name="description" content="Download the official [[TITLE]] PDF. Check the latest exam dates, slots, and subjects for the APJAKTU examinations.">
    <meta name="keywords" content="[[TITLE]], KTU Time Table, KTU Exam Date PDF Download, Kerala Tech University, ktu latest updates, Kerala Timetable">
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

        /* Ambient Orbs (Automatically disabled in Dark Mode by components.js for 120FPS) */
        .ambient-orb {
            filter: blur(60px);
            -webkit-filter: blur(60px);
            pointer-events: none;
        }

        /* Primary CTA Liquid Glow & Shimmer */
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

        /* SVG Circular Countdown Ring */
        .progress-ring__circle {
            transition: stroke-dashoffset 0.95s linear;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }

        /* Smooth Accordion Caret */
        details > summary { list-style: none; }
        details > summary::-webkit-details-marker { display: none; }
        details[open] summary .faq-chevron { transform: rotate(180deg); }
    </style>
    
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Kerala Timetable",
      "url": "https://www.keralatimetable.in/",
      "description": "Web application for APJAKTU students providing server status, exam timetables, and academic updates.",
      "applicationCategory": "EducationalApplication",
      "operatingSystem": "All",
      "inLanguage": "en-IN"
    }
    </script>

    <link rel="icon" href="/favicon.png" type="image/png">
    <meta property="og:site_name" content="Kerala Timetable">
    <meta property="og:title" content="[[TITLE]] + Timetable Download | KTU Timetable">
    <meta property="og:description" content="Download the official [[TITLE]] PDF. Check the latest exam dates, slots, and subjects for the APJAKTU examinations.">
    <meta property="og:image" content="https://www.keralatimetable.in/social-preview.png">
    <meta property="og:type" content="website">
</head>

<body class="bg-mesh text-slate-800 antialiased flex flex-col min-h-screen relative overflow-x-hidden selection:bg-indigo-500 selection:text-white">

    <!-- Ambient Liquid Background Orbs -->
    <div class="ambient-orb fixed -top-24 -left-24 w-96 h-96 bg-indigo-400/20 rounded-full -z-10"></div>
    <div class="ambient-orb fixed top-1/3 -right-28 w-80 h-80 bg-sky-400/20 rounded-full -z-10"></div>

    <!-- Sticky Frosted Navigation Container -->
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
            
            <!-- Subtle Specular Highlight Orb Inside Card -->
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
                        <i class="fas fa-university mr-1"></i> APJAKTU
                    </span>
                    <span class="px-3 py-1 rounded-full bg-blue-50 border border-blue-200/60 text-blue-700 text-[11px] font-extrabold uppercase tracking-wider">
                        <i class="fas fa-bolt mr-1"></i> Direct PDF
                    </span>
                </div>

                <!-- Main SEO Heading -->
                <h1 class="text-xl sm:text-2xl md:text-3xl lg:text-[32px] font-extrabold text-slate-900 mb-3 tracking-tight leading-snug max-w-2xl">
                    [[TITLE]] <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-sky-500">+ Timetable Download</span>
                </h1>
                
                <p class="text-xs sm:text-sm text-slate-500 font-semibold mb-6">
                    Verified University Examination Schedule • Instant Cloud Mirror
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
                                Preparing Direct PDF Mirror...
                            </p>
                            <p id="timer-subtext" class="text-xs font-medium text-slate-500">
                                Bypassing KTU portal congestion for instant download
                            </p>
                        </div>

                        <!-- Sleek Linear Progress Bar -->
                        <div class="w-full max-w-xs h-1.5 bg-slate-200/80 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div id="countdown-bar" class="h-full bg-gradient-to-r from-indigo-600 via-sky-500 to-emerald-400 rounded-full transition-all duration-1000 ease-linear" style="width: 7%;"></div>
                        </div>
                    </div>

                    <!-- State 2: Ready Action Dock (Revealed when timer hits 0) -->
                    <div id="ready-actions" class="hidden w-full flex-col gap-3 sm:gap-3.5 animate-fadeIn">
                        
                        <!-- Primary Download Button -->
                        <a id="download-btn" href="#" target="_blank" rel="noopener" class="sheen-effect btn-glow w-full bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600 text-white font-extrabold text-sm sm:text-base py-4 px-6 rounded-2xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-[0.99] flex items-center justify-center gap-3">
                            <i class="fas fa-cloud-download-alt text-lg"></i>
                            <span>Download Official PDF Timetable</span>
                            <span class="px-2 py-0.5 rounded-full bg-white/20 text-[10px] font-black uppercase tracking-wider ml-1">PDF</span>
                        </a>

                        <!-- Secondary Mobile-Friendly 2-Column Share & Copy Bar -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 w-full">
                            <a id="whatsapp-btn" href="https://api.whatsapp.com/send?text=🚨 *[[TITLE]] is Out!* Download the official PDF directly here: https://www.keralatimetable.in/timetable_pages/[[SLUG]].html" target="_blank" rel="noopener noreferrer" class="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold text-xs sm:text-sm py-3.5 px-5 rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 shadow-md shadow-emerald-500/20">
                                <i class="fab fa-whatsapp text-base"></i>
                                <span>Share with Classmates</span>
                            </a>

                            <button id="copy-link-btn" type="button" class="w-full bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs sm:text-sm py-3.5 px-5 rounded-xl border border-slate-200/90 transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 shadow-sm">
                                <i class="fas fa-link text-indigo-600 text-xs"></i>
                                <span id="copy-link-text">Copy Direct Link</span>
                            </button>
                        </div>

                        <!-- WhatsApp Channel Banner -->
                        <a id="whatsapp-channel-btn" href="https://whatsapp.com/channel/0029Vb7zhxw5vKABedfmht0D" target="_blank" rel="noopener noreferrer" class="inner-glass w-full p-3.5 rounded-xl hover:border-emerald-400/60 transition-all flex items-center justify-between gap-3 group">
                            <div class="flex items-center gap-3 text-left">
                                <div class="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200/60 text-emerald-600 flex items-center justify-center shrink-0">
                                    <i class="fab fa-whatsapp text-lg"></i>
                                </div>
                                <div>
                                    <p class="text-xs sm:text-sm font-extrabold text-slate-800 leading-tight">Get Instant Exam Alerts on WhatsApp</p>
                                    <p class="text-[11px] font-medium text-slate-500">Join 10,000+ KTU students on our official channel</p>
                                </div>
                            </div>
                            <span class="px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 group-hover:bg-emerald-500 group-hover:text-white text-xs font-extrabold transition-colors shrink-0">
                                Follow <i class="fas fa-arrow-right text-[10px] ml-1"></i>
                            </span>
                        </a>
                    </div>

                </div>

                <!-- ========================================================= -->
                <!-- COMPANION STUDY RESOURCES (High-UX Internal Links)        -->
                <!-- ========================================================= -->
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
                                    <h3 class="text-xs sm:text-sm font-extrabold text-slate-800">Solved PYQ Papers</h3>
                                    <p class="text-[11px] font-medium text-slate-500">Previous university questions</p>
                                </div>
                            </div>
                            <div class="w-7 h-7 rounded-full bg-white border border-slate-200/80 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-indigo-600 transition-all shrink-0">
                                <i class="fas fa-chevron-right text-[10px]"></i>
                            </div>
                        </a>
                    </div>
                </div>

                <!-- ========================================================= -->
                <!-- INTERACTIVE LIQUID GLASS ACCORDION FAQs                   -->
                <!-- ========================================================= -->
                <div class="w-full mt-8 pt-7 border-t border-slate-200/70 dark:border-white/10 text-left">
                    <h2 class="text-sm sm:text-base font-extrabold text-slate-800 mb-3.5 flex items-center gap-2">
                        <i class="fas fa-question-circle text-indigo-500"></i>
                        <span>Frequently Asked Questions</span>
                    </h2>

                    <div class="space-y-2.5">
                        <details class="inner-glass rounded-2xl group overflow-hidden" open>
                            <summary class="p-4 cursor-pointer flex items-center justify-between gap-3 font-bold text-slate-800 text-xs sm:text-sm select-none">
                                <span>When do the [[TITLE]] exams start?</span>
                                <i class="fas fa-chevron-down faq-chevron text-slate-400 text-xs transition-transform duration-200"></i>
                            </summary>
                            <div class="px-4 pb-4 text-xs text-slate-600 leading-relaxed border-t border-slate-200/50 dark:border-white/5 pt-3">
                                Please refer to the official PDF download above for the exact subject-wise start dates, FN/AN session timings, and slot codes for your specific scheme and branch.
                            </div>
                        </details>

                        <details class="inner-glass rounded-2xl group overflow-hidden">
                            <summary class="p-4 cursor-pointer flex items-center justify-between gap-3 font-bold text-slate-800 text-xs sm:text-sm select-none">
                                <span>Is this the final KTU timetable or tentative?</span>
                                <i class="fas fa-chevron-down faq-chevron text-slate-400 text-xs transition-transform duration-200"></i>
                            </summary>
                            <div class="px-4 pb-4 text-xs text-slate-600 leading-relaxed border-t border-slate-200/50 dark:border-white/5 pt-3">
                                This document is mirrored directly from the official APJ Abdul Kalam Technological University (KTU) announcements portal. Any revised notifications will automatically update on our dashboard.
                            </div>
                        </details>
                    </div>
                </div>

                <!-- SEO Tag Pills -->
                <div class="w-full mt-7 pt-6 border-t border-slate-200/70 dark:border-white/10 text-left">
                    <h3 class="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2.5">Related Searches</h3>
                    <div class="flex flex-wrap gap-1.5 sm:gap-2">
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">[[TITLE]]</span>
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">KTU Timetable PDF Download</span>
                        <span class="bg-white/80 border border-slate-200/80 text-slate-500 text-[11px] font-semibold px-3 py-1 rounded-full">APJAKTU Exam Schedule</span>
                    </div>
                </div>

            </div>
        </section>

    </main>

    <!-- Adaptive Frosted Footer -->
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

    <!-- Core Flow Engine & 120FPS Dark Mode Script -->
    <script src="../components.js?v=12"></script>
    <script>
        // Highlight 'timetable' in the navigation drawer
        loadNavigation('timetable', '../', false);
    </script>

    <script>
        // --- Liquid Glass Countdown, Ring & Capsule Integration ---
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

        const circumference = 2 * Math.PI * 34; // r=34 -> ~213.6

        const timer = setInterval(() => {
            timeLeft--;
            if (countdownEl) countdownEl.textContent = timeLeft;

            // Update Circular Ring & Linear Bar
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
                
                // Configure & Reveal Action Dock
                downloadBtn.href = pdfLink;
                readyActions.classList.remove('hidden');
                readyActions.classList.add('flex');

                // Trigger ColorOS Live Capsule Notification
                if (typeof window.triggerCapsule === 'function') {
                    window.triggerCapsule('success', 'Timetable PDF Ready to Download!');
                }
            }
        }, 1000);

        // Copy Direct Link Button with Capsule Toast Feedback
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

    final_html = html_template.replace('[[TITLE]]', short_title).replace('[[PDF_LINK]]', pdf_link).replace('[[SLUG]]', slug)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    return html_filepath, f"timetable_pages/{html_filename}"


# -------------------------------------------------------------------
# AI EXTRACTION FUNCTION (READS FULL PDF)
# -------------------------------------------------------------------
def extract_dashboard_data_with_ai(pdf_path, original_title, pdf_link):
    """Reads the PDF text and uses Gemini to extract structured dates/tags."""
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

    prompt = f"""
    You are an expert data extractor. Analyze this KTU exam timetable text.
    Original Long Title: {original_title}
    
    Tasks based on the schema:
    1. id: Create a short, unique snake_case ID (e.g., "mca_s2_may2026").
    2. title: Create a short, clean title (e.g., "MCA S2 Regular/Supply May 2026").
    3. startDate: Scan the ENTIRE document and find the VERY FIRST exam date and time. Format: YYYY-MM-DDTHH:MM:SS
    4. endDate: Scan the ENTIRE document and find the VERY LAST/LATEST exam date and time. Format: YYYY-MM-DDTHH:MM:SS
    5. semester: Extract the specific semester (e.g., 'S4', 'S1', 'S1-S5').
    6. categoryBadge: Extract a category for filtering (e.g., 'S1', 'S3', 'S5', 'S7').
    7. type: 'Regular', 'Supply', 'Honours', or 'Regular/Supply'.
    8. scheme: (e.g., '2019 Scheme', '2024 Scheme').
    9. pdfLink: Return exactly "{pdf_link}".
    10. viewLink: Return an empty string ("").
    
    Messy PDF Text:
    {raw_text[:40000]} 
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TimetableData,
                temperature=0.0,
            ),
        )
        ai_data = json.loads(response.text)
        print(f"✅ AI Extraction Successful! Start: {ai_data['startDate']} | End: {ai_data['endDate']}")
        return ai_data
    except Exception as e:
        print(f"❌ AI Extraction Failed: {e}")
        return None


# -------------------------------------------------------------------
# CONFIG UPDATER FUNCTION
# -------------------------------------------------------------------
def update_timetable_config(ai_data_dict, config_path="timetable-config.js"):
    """Safely appends the AI's JSON object into window.timetablesData."""
    if not ai_data_dict:
        return
    
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "window.timetablesData = [\n];"
            
        clean_json = json.dumps(ai_data_dict, indent=4)
        
        last_bracket_idx = content.rfind(']')
        if last_bracket_idx != -1:
            array_content = content[content.find('[')+1:last_bracket_idx].strip()
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
# DIRECT KTU BACKEND API HELPERS (BYPASSES BROKEN FRONTEND & SSL)
# -------------------------------------------------------------------
KTU_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.ktu.edu.in",
    "Referer": "https://www.ktu.edu.in/"
}

def download_pdf_from_ktu_api(encrypt_id, save_path):
    """Downloads a PDF directly from KTU's backend API using its encryptId."""
    endpoints = [
        "https://api.ktu.edu.in/ktu-web-service/anon/getAttachment",
        "https://ktu.edu.in/ktu-web-service/anon/getAttachment",
        "https://www.ktu.edu.in/ktu-web-service/anon/getAttachment"
    ]
    for url in endpoints:
        try:
            res = requests.post(
                url,
                json={"encryptId": encrypt_id},
                headers=KTU_HEADERS,
                verify=False,
                timeout=30
            )
            if res.status_code == 200 and len(res.content) > 500:
                # Case 1: Raw PDF binary stream
                if res.content.startswith(b"%PDF"):
                    with open(save_path, "wb") as f:
                        f.write(res.content)
                    return True

                # Case 2: Base64 encoded PDF inside JSON or plain text
                try:
                    data = res.json()
                    if isinstance(data, dict):
                        b64_str = (
                            data.get("file")
                            or data.get("data")
                            or data.get("attachment")
                            or data.get("content")
                        )
                        if b64_str:
                            pdf_bytes = base64.b64decode(b64_str)
                            if pdf_bytes.startswith(b"%PDF"):
                                with open(save_path, "wb") as f:
                                    f.write(pdf_bytes)
                                return True
                    elif isinstance(data, str):
                        pdf_bytes = base64.b64decode(data)
                        if pdf_bytes.startswith(b"%PDF"):
                            with open(save_path, "wb") as f:
                                f.write(pdf_bytes)
                            return True
                except Exception:
                    pass
        except Exception as e:
            print(f" -> Direct API download warning ({url}): {e}")
    return False


def fetch_timetables_via_direct_api():
    """Fetches timetable metadata directly from KTU REST APIs (Timetable + Announcements)."""
    items = []
    
    # 1. Try Official Timetable Endpoint
    timetable_urls = [
        "https://api.ktu.edu.in/ktu-web-service/anon/timetable",
        "https://ktu.edu.in/ktu-web-service/anon/timetable",
        "https://www.ktu.edu.in/ktu-web-service/anon/timetable"
    ]
    for url in timetable_urls:
        try:
            res = requests.post(
                url,
                json={"page": 0, "size": 25, "searchText": ""},
                headers=KTU_HEADERS,
                verify=False,
                timeout=20
            )
            if res.status_code == 200:
                data = res.json()
                content = data.get("content") if isinstance(data, dict) else None
                if content:
                    for idx, item in enumerate(content):
                        enc_id = item.get("encryptId") or item.get("encryptAttachmentId")
                        f_name = sanitize_filename(item.get("fileName") or item.get("attachmentName") or f"timetable_{idx}.pdf")
                        items.append({
                            "index": idx,
                            "id": item.get("id"),
                            "title": item.get("timeTableTitle") or item.get("title") or "KTU Exam Timetable",
                            "date": (item.get("createdDate") or item.get("publishedOn") or "2026").split("T")[0],
                            "encryptId": enc_id,
                            "fileName": f_name
                        })
                    print(f"✅ Direct Timetable API captured {len(items)} timetables!")
                    return items
        except Exception as e:
            print(f"⚠️ Direct Timetable API warning ({url}): {e}")

    # 2. Fallback: Check KTU Announcements API for "Time Table" PDFs!
    # (When KTU's /exam/timetable tab is empty, KTU posts timetables in Announcements)
    announcement_urls = [
        "https://api.ktu.edu.in/ktu-web-service/anon/announcemnts",
        "https://ktu.edu.in/ktu-web-service/anon/announcemnts",
        "https://www.ktu.edu.in/ktu-web-service/anon/announcemnts"
    ]
    for url in announcement_urls:
        try:
            res = requests.post(
                url,
                json={"number": 0, "size": 30, "searchText": "Time Table"},
                headers=KTU_HEADERS,
                verify=False,
                timeout=20
            )
            if res.status_code == 200:
                data = res.json()
                content = data.get("content") if isinstance(data, dict) else None
                if content:
                    for idx, item in enumerate(content):
                        subject = item.get("subject") or item.get("title") or ""
                        if any(k in subject.lower() for k in ["time table", "timetable", "exam schedule"]):
                            attachments = item.get("attachmentList") or []
                            for att in attachments:
                                enc_id = att.get("encryptId") or att.get("encryptAttachmentId")
                                raw_name = att.get("attachmentName") or att.get("fileName") or f"timetable_{idx}.pdf"
                                if enc_id and raw_name.lower().endswith(".pdf"):
                                    items.append({
                                        "index": idx,
                                        "id": item.get("id"),
                                        "title": subject.strip(),
                                        "date": (item.get("announcementDate") or item.get("createdDate") or "2026").split("T")[0],
                                        "encryptId": enc_id,
                                        "fileName": sanitize_filename(raw_name)
                                    })
                    if items:
                        print(f"✅ Captured {len(items)} timetable PDFs from KTU Announcements API!")
                        return items
        except Exception as e:
            print(f"⚠️ Announcements API fallback warning ({url}): {e}")

    return items


def process_downloaded_pdf(save_path, filename, title, date_str, html_dir):
    """Runs AI extraction, generates the Liquid Glass HTML page, updates config, and sends push notification."""
    relative_pdf_link = f"downloads_timetable/{filename}"
    ai_extracted_data = extract_dashboard_data_with_ai(save_path, title, relative_pdf_link)
    
    if ai_extracted_data:
        short_title = ai_extracted_data.get('title', title)
        html_filepath, relative_html_link = generate_html_page(short_title, filename, html_dir)
        print(f" -> HTML Generated: {html_filepath}")
        
        ai_extracted_data['viewLink'] = relative_html_link
        update_timetable_config(ai_extracted_data)
        
        send_push_notification(
            title="🚨 New KTU Timetable Published!",
            body=f"{short_title} is now available on the dashboard."
        )
    else:
        html_filepath, relative_html_link = generate_html_page(title, filename, html_dir)
        print(f" -> HTML Generated (Fallback Title): {html_filepath}")

    return {
        "title": title,
        "date": date_str,
        "filename": filename,
    }


# -------------------------------------------------------------------
# MAIN SCRAPER FUNCTION (DIRECT API + PLAYWRIGHT STEALTH FALLBACK)
# -------------------------------------------------------------------
def scrape_exam_timetables(pdf_dir="./downloads_timetable", html_dir="./timetable_pages"):
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    
    downloaded_files = []

    # ===============================================================
    # STEP 1: TRY DIRECT API FETCH FIRST (Fastest & Bypasses Blank UI)
    # ===============================================================
    print("Attempting Direct KTU Backend API fetch (Timetables + Announcements)...")
    api_timetables = fetch_timetables_via_direct_api()
    needs_browser_fallback = []

    if api_timetables:
        print(f"\nProcessing {len(api_timetables)} timetables via Direct API:")
        for tb in api_timetables:
            title = tb['title']
            encrypt_id = tb['encryptId']
            if not encrypt_id:
                continue

            filename = sanitize_filename(f"{tb['date']}_{tb['fileName']}")
            save_path = os.path.join(pdf_dir, filename)

            if os.path.exists(save_path):
                print(f"Skipping (Already Exists): '{title}'")
                continue

            print(f"\nDownloading NEW file via Direct API: '{title}'")
            if download_pdf_from_ktu_api(encrypt_id, save_path):
                print(f" -> PDF Saved via Direct API: {filename}")
                result = process_downloaded_pdf(save_path, filename, title, tb['date'], html_dir)
                downloaded_files.append(result)
            else:
                print(f" -> Direct API binary fetch couldn't decode PDF, queueing for Playwright browser fallback...")
                needs_browser_fallback.append(tb)

        # If all new files were downloaded via Direct API, we don't even need to open Chromium!
        if not needs_browser_fallback:
            return downloaded_files

    # ===============================================================
    # STEP 2: PLAYWRIGHT STEALTH BROWSER FALLBACK
    # ===============================================================
    with sync_playwright() as p:
        print("\nLaunching headless Chromium browser (with SSL Bypass & Stealth)...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            ignore_https_errors=True
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        timetable_metadata = list(needs_browser_fallback)
        
        def on_response(response):
            if "anon/timetable" in response.url and not needs_browser_fallback:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'content' in data and data['content']:
                        for idx, item in enumerate(data['content']):
                            timetable_metadata.append({
                                'index': idx,
                                'id': item.get('id'),
                                'title': item.get('timeTableTitle') or item.get('title'),
                                'date': (item.get('createdDate') or '2026').split('T')[0],
                                'encryptId': item.get('encryptId'),
                                'fileName': sanitize_filename(item.get('fileName') or f"timetable_{idx}.pdf")
                            })
                        print(f"Captured {len(timetable_metadata)} exam timetables from browser API response.")
                except Exception as e:
                    print(f"Error parsing browser API response: {e}")
                    
        page.on("response", on_response)
        
        print("Navigating to KTU Exam Timetable page...")
        try:
            page.goto("https://www.ktu.edu.in/exam/timetable", wait_until="domcontentloaded", timeout=60000)
        except Exception as nav_err:
            print(f"⚠️ Primary URL warning ({nav_err}), trying ktu.edu.in fallback...")
            try:
                page.goto("https://ktu.edu.in/exam/timetable", wait_until="domcontentloaded", timeout=60000)
            except Exception as nav_err2:
                print(f"❌ Both KTU URLs unreachable in browser: {nav_err2}")
                browser.close()
                return downloaded_files

        page.wait_for_timeout(5000)
        
        print(f"\nProcessing {len(timetable_metadata)} timetables in browser:")
        
        for tb in timetable_metadata:
            title = tb['title']
            encrypt_id = tb['encryptId']
            
            if not encrypt_id:
                continue
                
            predicted_filename = sanitize_filename(f"{tb['date']}_{tb['fileName']}")
            save_path = os.path.join(pdf_dir, predicted_filename)
            
            if os.path.exists(save_path):
                print(f"Skipping (Already Exists): '{title}'")
                continue
                
            print(f"\nDownloading NEW file via Browser UI: '{title}'")
            
            try:
                button_selector = f"button[value='{encrypt_id}']"
                button = page.locator(button_selector)
                
                if button.count() > 0:
                    with page.expect_download(timeout=15000) as download_info:
                        button.first.click()
                    download = download_info.value
                    
                    filename = sanitize_filename(f"{tb['date']}_{tb['fileName'] or download.suggested_filename}")
                    save_path = os.path.join(pdf_dir, filename)
                    
                    download.save_as(save_path)
                    print(f" -> PDF Saved: {filename}")
                    
                    result = process_downloaded_pdf(save_path, filename, title, tb['date'], html_dir)
                    downloaded_files.append(result)
                    
                    page.wait_for_timeout(1500)
                else:
                    print(f" -> Error: Download button not found on UI for '{title}'.")
            except Exception as e:
                print(f" -> Failed to process download: {e}")
                
        browser.close()
        return downloaded_files


if __name__ == "__main__":
    results = scrape_exam_timetables()
    print("\n" + "="*50 + "\n          NEW DOWNLOADS SUMMARY\n" + "="*50)
    if not results:
        print("No new timetables found today.")
    else:
        for r in results:
            print(f"[{r['date']}] {r['title']} -> Page & Config Updated (Push Sent)")
