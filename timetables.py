import os
import json
import re
import PyPDF2
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types

# -------------------------------------------------------------------
# AI SETUP & SCHEMA
# -------------------------------------------------------------------
# Initialize the SDK client using your hidden GitHub Secret
client = genai.Client()

# This schema exactly matches the keys expected by your timetable.html JS
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
    
    # Your exact HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[[TITLE]] | KTU Timetable Download</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: sans-serif; background-color: #f8fafc; }
    </style>
</head>
<body class="text-slate-800 antialiased flex flex-col min-h-screen">
    <main class="flex-grow max-w-3xl mx-auto px-4 py-10 w-full text-center">
        <h2 class="text-3xl font-extrabold mb-3">[[TITLE]]</h2>
        <a href="[[PDF_LINK]]" class="bg-indigo-600 text-white font-bold py-4 px-10 rounded-xl">Download PDF Timetable</a>
    </main>
</body>
</html>"""

    final_html = html_template.replace('[[TITLE]]', title).replace('[[PDF_LINK]]', pdf_link)
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    return html_filepath, f"timetable_pages/{html_filename}"

# -------------------------------------------------------------------
# AI EXTRACTION FUNCTION
# -------------------------------------------------------------------
def extract_dashboard_data_with_ai(pdf_path, original_title, pdf_link, html_link):
    """Reads the PDF text and uses Gemini 3.5 Flash to extract structured dates/tags."""
    print(f"🧠 Asking AI to analyze: {original_title}...")
    
    raw_text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i in range(min(2, len(reader.pages))):
                raw_text += reader.pages[i].extract_text() + "\n"
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

    # Prompt forces strict 24-hour 'T' format for JavaScript Date parsing
    prompt = f"""
    You are an expert data extractor. Analyze this KTU exam timetable text.
    Original Long Title: {original_title}
    
    Tasks based on the schema:
    1. id: Create a short, unique snake_case ID (e.g., "mca_s2_may2026").
    2. title: Create a short, clean title (e.g., "MCA S2 Regular/Supply May 2026").
    3. startDate: Find the earliest exam date and time. MUST be formatted EXACTLY like this: YYYY-MM-DDTHH:MM:SS (Use 24-hour time and the 'T' separator).
    4. endDate: Find the latest exam date and time. MUST be formatted EXACTLY like this: YYYY-MM-DDTHH:MM:SS (Use 24-hour time and the 'T' separator).
    5. semester: Extract the specific semester (e.g., 'S4', 'S1', 'S1-S5').
    6. categoryBadge: Extract a category for filtering (e.g., 'S1', 'S3', 'S5', 'S7').
    7. type: 'Regular', 'Supply', 'Honours', or 'Regular/Supply'.
    8. scheme: (e.g., '2019 Scheme', '2024 Scheme').
    9. pdfLink: Return exactly "{pdf_link}".
    10. viewLink: Return exactly "{html_link}".
    
    Messy PDF Text:
    {raw_text[:8000]} 
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TimetableData,
                temperature=0.1, 
            ),
        )
        ai_data = json.loads(response.text)
        print(f"✅ AI Extraction Successful! Start: {ai_data['startDate']}")
        return ai_data
    except Exception as e:
        print(f"❌ AI Extraction Failed: {e}")
        return None

# -------------------------------------------------------------------
# CONFIG UPDATER FUNCTION
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
        
        # Robust method to inject into the JavaScript array
        last_bracket_idx = content.rfind(']')
        if last_bracket_idx != -1:
            array_content = content[content.find('[')+1:last_bracket_idx].strip()
            if array_content:
                # Array already has items, prepend with comma
                new_content = content[:last_bracket_idx] + ",\n" + clean_json + "\n" + content[last_bracket_idx:]
            else:
                # Array is empty
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
            print(f"[{r['date']}] {r['title']} -> Page & Config Updated")
