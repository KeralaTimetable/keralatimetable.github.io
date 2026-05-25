import os
import json
import re
from playwright.sync_api import sync_playwright

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
    
    # Your exact HTML template, with [[TITLE]] and [[PDF_LINK]] placeholders
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="cPHgzg8741NBFQ5HszgVIPA3EMrKJLlj7IHcyLGM2Lo" />
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7313827303298932" crossorigin="anonymous"></script>
    
    <title>[[TITLE]] | KTU Timetable Download</title>
    <meta name="description" content="Download the official [[TITLE]] PDF. Check the latest exam dates, slots, and subjects for the APJAKTU examinations.">
    <meta name="robots" content="index, follow">
    
    <script src="https://cdn.tailwindcss.com"></script>
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
                    <p class="mb-3 leading-relaxed"><strong>Important Update:</strong> The <strong>APJ Abdul Kalam Technological University (APJAKTU)</strong> has officially released the latest exam schedule. Download the secure PDF below to verify your specific exam dates and slot codes.</p>
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

                    <a id="whatsapp-channel-btn" href="https://whatsapp.com/channel/0029Vb7zhxw5vKABedfmht0D" target="_blank" class="hidden w-full md:w-auto bg-slate-800 hover:bg-slate-900 text-white font-bold py-3 px-8 rounded-xl transition-all duration-300 transform hover:-translate-y-1 items-center justify-center gap-2 shadow-sm">
                        <i class="fab fa-whatsapp text-xl"></i>
                        Follow WhatsApp Channel
                    </a>
                </div>
            </div>
        </div>

    </main>

    <footer class="mt-auto border-t border-slate-200/60 bg-white/50 py-8 text-center">
        <div class="max-w-3xl mx-auto px-4">
            <h3 class="text-slate-800 font-bold text-lg mb-2">Kerala Timetable</h3>
            <p class="text-slate-500 text-sm leading-relaxed max-w-lg mx-auto">Providing fast and direct access to university resources. We are an independent platform and not officially affiliated with APJ Abdul Kalam Technological University.</p>
        </div>
    </footer>

    <script src="../components.js?v=8"></script>
    <script>
        // Load navigation menu (adjusted relative path for subfolder)
        loadNavigation('', '../', false);

        // --- Countdown & Download Logic ---
        const pdfLink = "[[PDF_LINK]]";
        let timeLeft = 15;
        
        const countdownEl = document.getElementById('countdown');
        const downloadBtn = document.getElementById('download-btn');
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

                // Show WhatsApp Button
                whatsappChannelBtn.classList.remove('hidden');
                whatsappChannelBtn.classList.add('flex');
            }
        }, 1000);
    </script>
</body>
</html>"""

    # Inject the actual Title and PDF link into the template
    final_html = html_template.replace('[[TITLE]]', title).replace('[[PDF_LINK]]', pdf_link)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    return html_filepath

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
                
            # Predict the final filename to see if we already downloaded it in a previous run
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
                    
                    # MAGICAL STEP: Generate the HTML page instantly!
                    html_path = generate_html_page(title, filename, html_dir)
                    print(f" -> HTML Generated: {html_path}")
                    
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
            print(f"[{r['date']}] {r['title']} -> Page Created")
