from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai
import json
import os
import re
from datetime import datetime
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- SETUP AI ---
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("SUCCESS: Gemini AI is ready for God Mode!")
else:
    print("CRITICAL ERROR: No Gemini API Key found.")
    exit()
# ----------------

URL_TO_SCRAPE = "https://ktu.edu.in/Menu/announcements"
BASE_WEBSITE_URL = "https://keralatimetable.github.io"

def clean_title(title):
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().lower()
    return slug.replace(' ', '-')

def generate_sitemap(updates):
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    main_pages = ['/index.html', '/updates.html']
    for page in main_pages:
        sitemap_content += f'  <url>\n    <loc>{BASE_WEBSITE_URL}{page}</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    today_date = datetime.now().strftime("%Y-%m-%d")
    for update in updates:
        sitemap_content += f'  <url>\n    <loc>{BASE_WEBSITE_URL}/{update["page_url"]}</loc>\n    <lastmod>{today_date}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    sitemap_content += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

def extract_updates_with_ai(page_text):
    prompt = f"""
    You are an AI data extractor. I am giving you the raw text copied from the KTU University announcements webpage.
    Your task is to find the 5 most recent and important academic notifications (exams, timetables, extensions, etc.).
    Ignore all website menu text (like 'Home', 'Gallery', 'RTI', 'Page 1').

    For each announcement you find, create a 2-sentence SEO-optimized description for engineering students.
    
    You MUST return the data STRICTLY as a JSON array of objects. Do not include any other text, markdown formatting, or backticks.
    Format exactly like this:
    [
      {{"title": "Exact title of the announcement", "description": "Your SEO description here"}},
      {{"title": "Another exact title", "description": "Another description"}}
    ]

    Here is the webpage text:
    {page_text[:8000]}
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        # Clean up in case Gemini adds markdown code blocks
        raw_text = raw_text.replace('```json', '').replace('```', '').strip()
        parsed_json = json.loads(raw_text)
        return parsed_json
    except Exception as e:
        print(f"AI Extraction Failed: {e}")
        print(f"Raw Output was: {response.text}")
        return []

def main():
    print("--- Starting AI God-Mode Scraper ---")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 1. Load the database
    existing_updates = []
    if os.path.exists('updates.json'):
        with open('updates.json', 'r') as f:
            try: existing_updates = json.load(f)
            except: pass
                
    existing_titles = [item.get('title') for item in existing_updates]
    new_updates = []

    with open('article-template.html', 'r') as template_file:
        template_html = template_file.read()

    # 2. Get the website text
    print(f"Loading React App: {URL_TO_SCRAPE}...")
    driver.get(URL_TO_SCRAPE)
    print("Waiting 15 seconds for KTU database to load...")
    time.sleep(15) 
    
    # Grab the raw text off the screen (Just like a human reading it)
    page_text = driver.find_element("tag name", "body").text
    driver.quit()

    print("\n--- Handing webpage text to Gemini AI ---")
    ai_extracted_data = extract_updates_with_ai(page_text)
    
    print(f"Gemini successfully found {len(ai_extracted_data)} real announcements!")

    # 3. Build the pages
    for item in ai_extracted_data:
        title = item.get('title', '')
        description = item.get('description', '')
        
        # Check if we already have this announcement
        if title in existing_titles or len(title) < 15:
            continue
            
        print(f"Building new SEO Page for: {title[:50]}...")
        
        date_str = datetime.now().strftime("%B %d, %Y")
        file_name = f"{clean_title(title)}.html"
        if len(file_name) > 100: file_name = file_name[:100] + ".html"
        
        new_page = template_html.replace('{{TITLE}}', title)
        new_page = new_page.replace('{{DATE}}', date_str)
        new_page = new_page.replace('{{LINK}}', URL_TO_SCRAPE) # Redirect to main board
        new_page = new_page.replace('{{DESCRIPTION}}', description)
        new_page = new_page.replace('{{KEYWORDS}}', title.replace(' ', ', '))

        with open(file_name, 'w', encoding='utf-8') as new_file:
            new_file.write(new_page)
            
        new_updates.append({
            "title": title,
            "date": date_str,
            "page_url": file_name,
            "link": URL_TO_SCRAPE
        })

    # 4. Save everything
    all_updates = new_updates + existing_updates
    with open('updates.json', 'w', encoding='utf-8') as f:
        json.dump(all_updates[:30], f, indent=4)
        
    generate_sitemap(all_updates[:30])
    print(f"\n--- MISSION ACCOMPLISHED: Added {len(new_updates)} new pages ---")

if __name__ == "__main__":
    main()
