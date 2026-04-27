from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import os
import re
from datetime import datetime
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- SETUP AI ---
# Grab the secret key from GitHub Actions
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Using Gemini Flash - it is extremely fast and perfect for text generation
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("WARNING: No Gemini API Key found. AI features will be disabled.")
    model = None
# ----------------

URLS_TO_SCRAPE = [
    "https://ktu.edu.in/Menu/announcements",
    "https://ktu.edu.in/exam/notification"
]

BASE_WEBSITE_URL = "https://keralatimetable.github.io"

def clean_title(title):
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().lower()
    return slug.replace(' ', '-')

def generate_sitemap(updates):
    print("Generating XML Sitemap...")
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

def ask_ai_for_content(title):
    if not model:
        return "Official KTU notification. Please download the document to verify schedules and guidelines."
    
    prompt = f"""
    You are an expert SEO content writer for a Kerala engineering student portal.
    I have scraped a link from the APJ Abdul Kalam Technological University website.
    The title of the link is: "{title}"
    
    Task 1: If this title sounds like a generic website menu item (e.g., 'Gallery', 'Mandatory Disclosures', 'Contact Us', 'Read More'), reply EXACTLY with the word "JUNK".
    Task 2: If it is a real academic, exam, or university announcement, write a highly detailed, professional 2-sentence description for a student. Include keywords naturally. 
    Do not use introductory phrases, just give me the final description.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text
    except Exception as e:
        print(f"AI Error: {e}")
        return "Official KTU notification. Download the document to view details."

def main():
    print("Starting AI-Powered Chrome Scraper...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    existing_updates = []
    if os.path.exists('updates.json'):
        with open('updates.json', 'r') as f:
            try: existing_updates = json.load(f)
            except: pass
                
    existing_links = [item.get('link') for item in existing_updates]
    new_updates = []

    with open('article-template.html', 'r') as template_file:
        template_html = template_file.read()

    for target_url in URLS_TO_SCRAPE:
        print(f"Loading: {target_url}")
        try:
            driver.get(target_url)
            time.sleep(15) 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup.find_all('a')
            
            count = 0
            for link_tag in all_links:
                if count >= 10: break # Process top 10 to save AI API limits
                
                title = link_tag.text.strip()
                doc_link = link_tag.get('href', '')
                
                # Basic filter to save AI calls
                if len(title) < 20 or doc_link.startswith('#') or 'javascript' in doc_link:
                    continue
                if '/Menu/' in doc_link and target_url not in doc_link:
                    continue
                if doc_link.startswith('/'):
                    doc_link = "https://ktu.edu.in" + doc_link
                    
                date_str = datetime.now().strftime("%B %d, %Y")
                if doc_link in existing_links:
                    continue
                    
                print(f"Analyzing with AI: {title[:50]}...")
                
                # --- ASK THE AI ---
                ai_description = ask_ai_for_content(title)
                
                if "JUNK" in ai_description:
                    print("AI rejected this as a junk link. Skipping.")
                    continue
                # ------------------
                
                file_name = f"{clean_title(title)}.html"
                if len(file_name) > 100: file_name = file_name[:100] + ".html"
                
                new_page = template_html.replace('{{TITLE}}', title)
                new_page = new_page.replace('{{DATE}}', date_str)
                new_page = new_page.replace('{{LINK}}', doc_link)
                new_page = new_page.replace('{{DESCRIPTION}}', ai_description) # AI Text Injected!
                new_page = new_page.replace('{{KEYWORDS}}', title.replace(' ', ', '))

                with open(file_name, 'w', encoding='utf-8') as new_file:
                    new_file.write(new_page)
                    
                new_updates.append({
                    "title": title,
                    "date": date_str,
                    "page_url": file_name,
                    "link": doc_link
                })
                existing_links.append(doc_link)
                count += 1

        except Exception as e:
            print(f"Error scraping {target_url}: {e}")

    driver.quit()

    all_updates = new_updates + existing_updates
    with open('updates.json', 'w', encoding='utf-8') as f:
        json.dump(all_updates[:30], f, indent=4)
        
    generate_sitemap(all_updates[:30])
    print(f"Success! Added {len(new_updates)} AI-generated pages.")

if __name__ == "__main__":
    main()
