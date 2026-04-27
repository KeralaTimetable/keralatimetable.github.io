from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{BASE_WEBSITE_URL}{page}</loc>\n'
        sitemap_content += '    <changefreq>daily</changefreq>\n'
        sitemap_content += '    <priority>1.0</priority>\n'
        sitemap_content += '  </url>\n'

    today_date = datetime.now().strftime("%Y-%m-%d")
    for update in updates:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{BASE_WEBSITE_URL}/{update["page_url"]}</loc>\n'
        sitemap_content += f'    <lastmod>{today_date}</lastmod>\n'
        sitemap_content += '    <changefreq>monthly</changefreq>\n'
        sitemap_content += '    <priority>0.8</priority>\n'
        sitemap_content += '  </url>\n'

    sitemap_content += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

def main():
    print("Starting Headless Chrome Scraper...")
    
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
            try:
                existing_updates = json.load(f)
            except json.JSONDecodeError:
                pass
                
    existing_links = [item.get('link') for item in existing_updates]
    new_updates = []

    with open('article-template.html', 'r') as template_file:
        template_html = template_file.read()

    for target_url in URLS_TO_SCRAPE:
        print(f"Loading Javascript for: {target_url}")
        try:
            driver.get(target_url)
            
            # --- SLOW SERVER FIX ---
            print("Waiting 15 seconds for slow KTU servers...")
            time.sleep(60) 
            
            # Scroll down the page to trigger 'Lazy Load' scripts
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3) # Wait 3 more seconds after scrolling just in case
            # -----------------------
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup.find_all('a')
            
            count = 0
            for link_tag in all_links:
                if count >= 15: break
                
                title = link_tag.text.strip()
                doc_link = link_tag.get('href', '')
                
                if len(title) < 25 or doc_link.startswith('#') or 'javascript' in doc_link:
                    continue
                    
                blacklist = [
                    'mandatory disclosure', 'gallery', 'tenders', 'contact us', 
                    'events', 'announcements', 'about us', 'administration', 
                    'academics', 'research', 'student corner', 'read more'
                ]
                if any(word in title.lower() for word in blacklist):
                    continue
                    
                if '/Menu/' in doc_link and target_url not in doc_link:
                    continue
                    
                if doc_link.startswith('/'):
                    doc_link = "https://ktu.edu.in" + doc_link
                    
                date_str = datetime.now().strftime("%B %d, %Y")
                
                if doc_link in existing_links:
                    continue
                    
                print(f"Found REAL Data: {title[:50]}...")
                
                file_name = f"{clean_title(title)}.html"
                if len(file_name) > 100:
                    file_name = file_name[:100] + ".html"
                
                new_page = template_html.replace('{{TITLE}}', title)
                new_page = new_page.replace('{{DATE}}', date_str)
                new_page = new_page.replace('{{LINK}}', doc_link)
                
                if "exam" in target_url:
                    new_page = new_page.replace('{{DESCRIPTION}}', "Official KTU Exam Notification. Please download the document to verify exam schedules and guidelines.")
                else:
                    new_page = new_page.replace('{{DESCRIPTION}}', "Official KTU Circular and Announcement. Please click below to view the official document.")
                
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
    print(f"Success! Added {len(new_updates)} new items.")

if __name__ == "__main__":
    main()
