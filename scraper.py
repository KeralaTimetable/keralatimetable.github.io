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
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("SUCCESS: Gemini AI is connected!")
else:
    print("WARNING: Gemini API Key NOT FOUND in GitHub Secrets! Using fallback text.")
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
        return "Official KTU notification. Please download the document to verify exam schedules and university guidelines."
    
    prompt = f"""
    You are an expert SEO content writer for a Kerala engineering student portal.
    I have scraped a real academic announcement from the APJ Abdul Kalam Technological University website.
    The title of the announcement is: "{title}"
    
    Write a highly detailed, professional 2-sentence description for a student explaining what this update likely contains. 
    Include SEO keywords naturally. Do not use introductory phrases like "Here is a description", just give me the final description text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "Official KTU notification. Please download the document to verify exam schedules and university guidelines."

def main():
    print("Starting Bulletproof KTU Scraper...")
    
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
        print(f"\n--- Loading: {target_url} ---")
        try:
            driver.get(target_url)
            
            # HARD WAIT: Force it to wait 12 seconds for KTU's database to load the real text
            print("Waiting 12 seconds for React API to load data...")
            time.sleep(12) 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup.find_all('a')
            
            count = 0
            for link_tag in all_links:
                if count >= 8: break # Only grab the top 8 actual announcements
                
                title = link_tag.text.strip()
                doc_link = link_tag.get('href', '')
                
                # --- THE BULLETPROOF FILTER ---
                # Real announcements are long. Menu items are short. 
                # If it's less than 35 characters, it's 100% a menu item. Skip it.
                if len(title) < 35 or doc_link.startswith('#') or 'javascript' in doc_link:
                    continue
                # ------------------------------
                
                if doc_link.startswith('/'):
                    doc_link = "https://ktu.edu.in" + doc_link
                    
                date_str = datetime.now().strftime("%B %d, %Y")
                if doc_link in existing_links:
                    continue
                    
                print(f"Found Real Announcement: {title[:60]}...")
                
                # Call AI to write the content
                ai_description = ask_ai_for_content(title)
                
                file_name = f"{clean_title(title)}.html"
                if len(file_name) > 100: file_name = file_name[:100] + ".html"
                
                new_page = template_html.replace('{{TITLE}}', title)
                new_page = new_page.replace('{{DATE}}', date_str)
                new_page = new_page.replace('{{LINK}}', doc_link)
                new_page = new_page.replace('{{DESCRIPTION}}', ai_description)
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
    print(f"\nSuccess! Added {len(new_updates)} valid pages.")

if __name__ == "__main__":
    main()
