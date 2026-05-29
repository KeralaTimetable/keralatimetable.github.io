import os
import json
import re
import PyPDF2
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types

# --- NEW: FIREBASE IMPORTS ---
import firebase_admin
from firebase_admin import credentials, messaging, db

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
        # Fetch all subscriber tokens from the database
        ref = db.reference('subscribers')
        subscribers = ref.get()
        
        if not subscribers:
            print("📭 No subscribers found in database.")
            return
            
        # Extract just the token strings
        tokens = list(subscribers.keys())
        print(f"📢 Preparing to send push notification to {len(tokens)} devices...")
        
        # Firebase has a limit of 500 tokens per multicast message.
        # This chunks the tokens into batches of 500 automatically.
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
# UTILITY FUNCTIONS
# -------------------------------------------------------------------
def create_seo_slug(title):
    """Converts a title into a clean, URL-friendly string (e.g., ktu-btech-s4-exam)"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

def generate_html_page(title, pdf_filename, html_output_dir="./timetable_pages"):
    """Injects the scraped data into your HTML template and saves the file."""
    os.makedirs(html_output_dir, exist_ok=True)
    
    slug = create_seo_slug(title)
    html_filename = f"{slug}.html"
    html_filepath = os.path.join(html_output_dir, html_filename)
    
    # Relative path from the HTML folder to the PDF folder
    pdf_link = f"../downloads_timetable/{pdf_filename}"
    
    # Your beautiful, advanced HTML template with dynamic placeholders
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="cPHgzg8741NBFQ5HszgVIPA3EMrKJLlj7IHcyLGM2Lo" />
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7313827303298932" crossorigin="anonymous"></script>
    
    <title>[[TITLE]] | KTU Timetable</title>
    <link rel="canonical" href="https://keralatimetable.github.io/timetable_pages/[[SLUG]].html" />

    <meta name="description" content="Download the official [[TITLE]] PDF. Check the latest exam dates, slots, and subjects for the APJAKTU examinations.">
    <meta name="keywords" content="[[TITLE]], KTU Time Table, KTU Exam Date PDF Download, Kerala Tech University, ktu latest updates">
    <meta name="robots" content="index, follow">
    
    <script src="/tailwind-local.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .bg-mesh {
            background-color: #f8fafc;
            background-image: radial-gradient(at 40% 20%, hsla(228,100%,74%,0.15) 0px, transparent 50%),
                              radial-gradient(at 80% 0%, hsla(189,100%,56%,0.15) 0px, transparent 50%),
                              radial-gradient(at 0% 50%, hsla(228,100%,74%,0.15) 0px, transparent 50%);
        }
        .btn-glow { box-shadow: 0 0 20px rgba(79, 70, 229, 0.4); }
    </style>
    
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Kerala Timetable",
      "url": "https://keralatimetable.github.io/",
      "description": "Web application for APJAKTU students providing server status, exam timetables, and academic updates.",
      "applicationCategory": "EducationalApplication",
      "operatingSystem": "All",
      "inLanguage": "en-IN"
    }
    </script>

</head>
<body class="bg-mesh text-slate-800 antialiased flex flex-col min-h-screen relative overflow-x-hidden">

    <div id="navigation-container"></div>

    <main class="flex-grow max-w-3xl mx-auto px-4 py-10 w-full flex flex-col items-center">
        
        <div class="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 p-8 md:p-10 text-center w-full relative overflow-hidden">
            <div class="absolute -top-24 -right-24 w-48 h-48 bg-indigo-50 rounded-full blur-3xl opacity-60"></div>
            
            <div class="relative z-10">
                <div class="inline-flex items-center justify-center p-3 bg-indigo-50 rounded-2xl mb-5 text-indigo-600">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                
                <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-3 tracking-tight">[[TITLE]]</h2>
                <p class="text-slate-500 font-medium mb-8">Official Exam Schedule • <strong>APJAKTU</strong></p>

                <div class="text-left bg-slate-50 border border-slate-100 p-5 rounded-2xl mb-8 text-sm text-slate-600 shadow-inner">
                    <p class="mb-3 leading-relaxed"><strong>Important Update:</strong> The <strong>APJ Abdul Kalam Technological University (APJAKTU)</strong> has officially released this latest exam schedule. Download the secure PDF below to verify your specific exam dates and slot codes.</p>
                </div>

                <div id="download-section" class="py-4 flex flex-col items-center justify-center gap-4">
                    <div id="loading-container" class="flex flex-col items-center justify-center space-y-4 w-full">
                        <div class="w-8 h-8 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                        <p id="timer-text" class="text-lg font-semibold text-slate-700">Connecting to Server in <span id="countdown" class="text-indigo-600 font-bold w-6 inline-block text-center">15</span>s...</p>
                    </div>
                    
                    <a id="download-btn" href="#" target="_blank" class="hidden w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-10 rounded-xl transition-all duration-300 transform hover:-translate-y-1 items-center justify-center gap-2">
                        <svg class="w-5 h-5 inline-block -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Download PDF Timetable
                    </a>

                    <a id="whatsapp-btn" href="https://api.whatsapp.com/send?text=🚨 *[[TITLE]] is Out!* Download the official PDF directly here: https://keralatimetable.github.io/timetable_pages/[[SLUG]].html" target="_blank" class="hidden w-full md:w-auto bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold py-3 px-8 rounded-xl transition-all duration-300 transform hover:-translate-y-1 items-center justify-center gap-2 shadow-sm">
                        <svg class="w-5 h-5 inline-block -mt-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 0C5.385 0 0 5.385 0 12.031c0 2.125.553 4.179 1.604 5.99L.492 23.508l5.635-1.478A11.968 11.968 0 0012.031 24c6.646 0 12.031-5.385 12.031-12.031S18.677 0 12.031 0zm3.834 17.202c-.161.455-.938.868-1.332.915-.36.042-.818.121-2.502-.538-2.035-.798-3.344-2.884-3.444-3.018-.1-.134-.823-1.096-.823-2.091 0-.995.518-1.485.698-1.684.18-.198.39-.248.52-.248.13 0 .26.002.378.007.126.005.293-.048.455.34.168.402.571 1.397.621 1.498.05.1.08.218.015.348-.065.13-.098.212-.195.328-.098.116-.207.248-.293.348-.095.108-.195.228-.083.422.112.194.498.825 1.07 1.335.738.658 1.353.86 1.545.955.193.095.305.08.418-.04.113-.12.485-.563.615-.758.13-.195.26-.163.435-.098.175.065 1.107.522 1.297.618.19.095.318.142.365.222.048.08.048.468-.113.923z"/></svg>
                        Share via WhatsApp
                    </a>

                    <a id="whatsapp-channel-btn" href="https://whatsapp.com/channel/0029Vb7zhxw5vKABedfmht0D" target="_blank" class="hidden w-full md:w-auto bg-slate-800 hover:bg-slate-900 text-white font-bold py-3 px-8 rounded-xl transition-all duration-300 transform hover:-translate-y-1 items-center justify-center gap-2 shadow-sm">
                        <i class="fab fa-whatsapp text-xl"></i>
                        Follow WhatsApp Channel
                    </a>
                </div>

                <div class="mt-12 text-left border-t border-slate-100 pt-8">
                    <h3 class="text-lg font-bold text-slate-800 mb-4">Frequently Asked Questions</h3>
                    <div class="space-y-3">
                        <div class="bg-slate-50 p-4 border border-slate-100 rounded-xl">
                            <h4 class="font-bold text-slate-700 text-sm">When do these exams start?</h4>
                            <p class="text-xs text-slate-500 mt-1">Please refer to the official PDF download above for the exact start dates and subject codes for this batch.</p>
                        </div>
                        <div class="bg-slate-50 p-4 border border-slate-100 rounded-xl">
                            <h4 class="font-bold text-slate-700 text-sm">Is this the final timetable or tentative?</h4>
                            <p class="text-xs text-slate-500 mt-1">This document contains the schedule published directly by the APJ Abdul Kalam Technological University (KTU). We mirror the official portal's data.</p>
                        </div>
                    </div>
                </div>

                <div class="mt-8 pt-8 border-t border-slate-100 text-left">
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Related Topics & Searches</h3>
                    <div class="flex flex-wrap gap-2">
                        <span class="bg-white border border-slate-200 text-slate-500 text-xs px-3 py-1.5 rounded-md">[[TITLE]]</span>
                        <span class="bg-white border border-slate-200 text-slate-500 text-xs px-3 py-1.5 rounded-md">KTU Timetable 2026 PDF</span>
                        <span class="bg-white border border-slate-200 text-slate-500 text-xs px-3 py-1.5 rounded-md">APJAKTU Exam Schedule Download</span>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <footer class="mt-auto border-t border-slate-200/60 bg-white/50 py-8 text-center">
        <div class="max-w-3xl mx-auto px-4">
            <h3 class="text-slate-800 font-bold text-lg mb-2">Kerala Timetable</h3>
            <p class="text-slate-500 text-sm leading-relaxed max-w-lg mx-auto">Providing fast and direct access to university resources. We are an independent platform and not officially affiliated with APJ Abdul Kalam Technological University.</p>
            <div class="mt-4 space-x-4">
                <a href="../about.html" class="text-indigo-600 text-xs font-bold hover:underline">About Us</a>
                <a href="https://keralatimetable.stck.me/profile" target="_blank" class="text-indigo-600 text-xs font-bold hover:underline">Support Us</a>
            </div>
        </div>
    </footer>

    <script src="../components.js?v=12"></script>
    <script>
        // Load navigation menu correctly adjusted for the /timetable_pages/ subfolder
        loadNavigation('', '../', false);
    </script>

    <script>
        // --- Countdown & Download Logic ---
        const pdfLink = "[[PDF_LINK]]";
        let timeLeft = 15;
        
        const countdownEl = document.getElementById('countdown');
        const downloadBtn = document.getElementById('download-btn');
        const whatsappBtn = document.getElementById('whatsapp-btn');
        const whatsappChannelBtn = document.getElementById('whatsapp-channel-btn');
        const loadingContainer = document.getElementById('loading-container');

        const timer = setInterval(() => {
            timeLeft--;
            countdownEl.textContent = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(timer);
                loadingContainer.classList.add('hidden');
                
                // Show Download Button
                downloadBtn.href = pdfLink;
                downloadBtn.classList.remove('hidden');
                downloadBtn.classList.add('flex', 'btn-glow'); 
                
                // Show WhatsApp Buttons
                whatsappBtn.classList.remove('hidden');
                whatsappBtn.classList.add('flex');

                whatsappChannelBtn.classList.remove('hidden');
                whatsappChannelBtn.classList.add('flex');
            }
        }, 1000);
    </script>
</body>
</html>"""

    final_html = html_template.replace('[[TITLE]]', title).replace('[[PDF_LINK]]', pdf_link).replace('[[SLUG]]', slug)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    return html_filepath, f"timetable_pages/{html_filename}"


# -------------------------------------------------------------------
# AI EXTRACTION FUNCTION (UPDATED TO READ FULL PDF)
# -------------------------------------------------------------------
def extract_dashboard_data_with_ai(pdf_path, original_title, pdf_link, html_link):
    """Reads the PDF text and uses Gemini to extract structured dates/tags."""
    print(f"🧠 Asking AI to analyze: {original_title}...")
    
    raw_text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # FIX: Read every single page of the PDF to ensure we catch the final exams
            for i in range(len(reader.pages)):
                text = reader.pages[i].extract_text()
                if text:
                    raw_text += text + "\n"
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

    # Prompt updated to command scanning the entire document
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
    10. viewLink: Return exactly "{html_link}".
    
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
                temperature=0.0, # Lowered for maximum mathematical strictness
            ),
        )
        ai_data = json.loads(response.text)
        print(f"✅ AI Extraction Successful! Start: {ai_data['startDate']} | End: {ai_data['endDate']}")
        return ai_data
    except Exception as e:
        print(f"❌ AI Extraction Failed: {e}")
        return None

# -------------------------------------------------------------------
# CONFIG UPDATER FUNCTION (UNTOUCHED)
# -------------------------------------------------------------------
def update_timetable_config(ai_data_dict, config_path="timetable-config.js"):
    """Safely appends the AI's JSON object into window.timetablesData."""
    if not ai_data_dict: return
    
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
# MAIN SCRAPER FUNCTION
# -------------------------------------------------------------------
def scrape_exam_timetables(pdf_dir="./downloads_timetable", html_dir="./timetable_pages"):
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    
    with sync_playwright() as p:
        print("Launching headless Chromium browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        timetable_metadata = []
        
        def on_response(response):
            if "anon/timetable" in response.url:
                try:
                    data = response.json()
                    if 'content' in data:
                        for idx, item in enumerate(data['content']):
                            timetable_metadata.append({
                                'index': idx,
                                'id': item.get('id'),
                                'title': item.get('timeTableTitle') or item.get('title'),
                                'date': item.get('createdDate', '').split('T')[0],
                                'encryptId': item.get('encryptId'),
                                'fileName': item.get('fileName')
                            })
                        print(f"Captured {len(timetable_metadata)} exam timetables from the API response.")
                except Exception as e:
                    print(f"Error parsing API response: {e}")
                    
        page.on("response", on_response)
        
        print("Navigating to KTU Exam Timetable page...")
        page.goto("https://ktu.edu.in/exam/timetable", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        
        downloaded_files = []
        print(f"\nProcessing {len(timetable_metadata)} timetables:")
        
        for tb in timetable_metadata:
            title = tb['title']
            encrypt_id = tb['encryptId']
            
            if not encrypt_id:
                continue
                
            predicted_filename = f"{tb['date']}_{tb['fileName']}"
            save_path = os.path.join(pdf_dir, predicted_filename)
            
            if os.path.exists(save_path):
                print(f"Skipping (Already Exists): '{title}'")
                continue
                
            print(f"\nDownloading NEW file: '{title}'")
            
            try:
                button_selector = f"button[value='{encrypt_id}']"
                button = page.locator(button_selector)
                
                if button.count() > 0:
                    with page.expect_download(timeout=15000) as download_info:
                        button.click()
                    download = download_info.value
                    
                    filename = f"{tb['date']}_{tb['fileName'] or download.suggested_filename}"
                    save_path = os.path.join(pdf_dir, filename)
                    
                    download.save_as(save_path)
                    print(f" -> PDF Saved: {filename}")
                    
                    # 1. Generate the HTML Sub-page
                    html_filepath, relative_html_link = generate_html_page(title, filename, html_dir)
                    print(f" -> HTML Generated: {html_filepath}")
                    
                    # 2. Extract Data via Gemini AI
                    relative_pdf_link = f"downloads_timetable/{filename}"
                    ai_extracted_data = extract_dashboard_data_with_ai(save_path, title, relative_pdf_link, relative_html_link)
                    
                    # 3. Update the JavaScript Config
                    update_timetable_config(ai_extracted_data)
                    
                    # --- NEW: TRIGGER PUSH NOTIFICATION ---
                    if ai_extracted_data:
                        short_title = ai_extracted_data.get('title', title)
                        send_push_notification(
                            title="🚨 New KTU Timetable Published!",
                            body=f"{short_title} is now available on the dashboard."
                        )
                    
                    downloaded_files.append({
                        "title": title,
                        "date": tb['date'],
                        "filename": filename,
                    })
                else:
                    print(f" -> Error: Download button not found on UI.")
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
