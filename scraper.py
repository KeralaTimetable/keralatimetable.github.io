import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS_TO_SCRAPE = [
    "https://ktu.edu.in/Menu/announcements",
    "https://ktu.edu.in/exam/notification"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_WEBSITE_URL = "https://keralatimetable.github.io"

def clean_title(title):
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().lower()
    return slug.replace(' ', '-')

def generate_sitemap(updates):
    print("Generating XML Sitemap...")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 1. Add your static main pages first
    main_pages = ['/index.html', '/updates.html']
    for page in main_pages:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{BASE_WEBSITE_URL}{page}</loc>\n'
        sitemap_content += '    <changefreq>daily</changefreq>\n'
        sitemap_content += '    <priority>1.0</priority>\n'
        sitemap_content += '  </url>\n'

    # 2. Add all the auto-generated announcement pages
    today_date = datetime.now().strftime("%Y-%m-%d")
    for update in updates:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{BASE_WEBSITE_URL}/{update["page_url"]}</loc>\n'
        sitemap_content += f'    <lastmod>{today_date}</lastmod>\n'
        sitemap_content += '    <changefreq>monthly</changefreq>\n'
        sitemap_content += '    <priority>0.8</priority>\n'
        sitemap_content += '  </url>\n'

    sitemap_content += '</urlset>'

    # Save to sitemap.xml
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Sitemap successfully created!")

def main():
    print("Starting KTU Multi-Scraper...")
    
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
        print(f"Scraping: {target_url}")
        try:
            response = requests.get(target_url, headers=HEADERS, verify=False, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            containers = soup.find_all(['tr', 'li'])
            
            for item in containers[:15]: 
                link_tag = item.find('a')
                if not link_tag: 
                    continue
                
                title = link_tag.text.strip()
                doc_link = link_tag.get('href', '')
                
                if len(title) < 10 or doc_link.startswith('#') or 'javascript' in doc_link:
                    continue
                    
                if doc_link.startswith('/'):
                    doc_link = "https://ktu.edu.in" + doc_link
                    
                date_str = datetime.now().strftime("%B %d, %Y")
                
                if doc_link in existing_links:
                    continue
                    
                print(f"New Update Found: {title[:50]}...")
                
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

        except Exception as e:
            print(f"An error occurred while scraping {target_url}: {e}")

    # Combine updates and save
    all_updates = new_updates + existing_updates
    with open('updates.json', 'w', encoding='utf-8') as f:
        json.dump(all_updates[:30], f, indent=4) # Keep top 30
        
    # Trigger the new sitemap generator!
    generate_sitemap(all_updates[:30])

    print(f"Scraping Complete! Added {len(new_updates)} new pages.")

if __name__ == "__main__":
    main()
