import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import urllib3

# Suppress SSL warnings (University websites often have expired certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. The two specific KTU URLs you provided
URLS_TO_SCRAPE = [
    "https://ktu.edu.in/Menu/announcements",
    "https://ktu.edu.in/exam/notification"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_title(title):
    # Removes special characters to make a clean URL slug
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().lower()
    return slug.replace(' ', '-')

def main():
    print("Starting KTU Multi-Scraper...")
    
    # Load existing updates to avoid making duplicates
    existing_updates = []
    if os.path.exists('updates.json'):
        with open('updates.json', 'r') as f:
            try:
                existing_updates = json.load(f)
            except json.JSONDecodeError:
                pass
                
    existing_links = [item.get('link') for item in existing_updates]
    new_updates = []

    # Load your HTML Template
    with open('article-template.html', 'r') as template_file:
        template_html = template_file.read()

    # Loop through both URLs (Announcements AND Exams)
    for target_url in URLS_TO_SCRAPE:
        print(f"Scraping: {target_url}")
        try:
            # Added a 15-second timeout so GitHub Actions doesn't freeze if KTU servers are slow
            response = requests.get(target_url, headers=HEADERS, verify=False, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find links in lists or tables (KTU frequently changes their HTML layout)
            # This looks for all 'a' tags inside list items (li) or table rows (tr)
            containers = soup.find_all(['tr', 'li'])
            
            for item in containers[:15]: # Limit to top 15 items per page
                link_tag = item.find('a')
                if not link_tag: 
                    continue
                
                title = link_tag.text.strip()
                doc_link = link_tag.get('href', '')
                
                # Filter out garbage links like "Home" or empty links, ensuring it has enough text to be a real title
                if len(title) < 10 or doc_link.startswith('#') or 'javascript' in doc_link:
                    continue
                    
                # Fix relative links (e.g. if the link is "/attachments/file.pdf")
                if doc_link.startswith('/'):
                    doc_link = "https://ktu.edu.in" + doc_link
                    
                date_str = datetime.now().strftime("%B %d, %Y")
                
                # Skip if we already have this announcement
                if doc_link in existing_links:
                    continue
                    
                print(f"New Update Found: {title[:50]}...")
                
                # Generate new file name
                file_name = f"{clean_title(title)}.html"
                
                # Ensure filename isn't too long for GitHub
                if len(file_name) > 100:
                    file_name = file_name[:100] + ".html"
                
                # Create the new HTML page for SEO
                new_page = template_html.replace('{{TITLE}}', title)
                new_page = new_page.replace('{{DATE}}', date_str)
                new_page = new_page.replace('{{LINK}}', doc_link)
                
                if "exam" in target_url:
                    new_page = new_page.replace('{{DESCRIPTION}}', "Official KTU Exam Notification. Please download the document to verify exam schedules and guidelines.")
                else:
                    new_page = new_page.replace('{{DESCRIPTION}}', "Official KTU Circular and Announcement. Please click below to view the official document.")
                
                new_page = new_page.replace('{{KEYWORDS}}', title.replace(' ', ', '))

                # Save the new HTML page
                with open(file_name, 'w', encoding='utf-8') as new_file:
                    new_file.write(new_page)
                    
                # Add to our JSON database
                new_updates.append({
                    "title": title,
                    "date": date_str,
                    "page_url": file_name,
                    "link": doc_link
                })
                # Add to existing links so we don't duplicate it if it appears on both pages
                existing_links.append(doc_link)

        except Exception as e:
            print(f"An error occurred while scraping {target_url}: {e}")

    # Combine new updates with old ones and save to updates.json
    all_updates = new_updates + existing_updates
    
    # Save the file (keeping the 30 most recent updates so your site doesn't get too slow)
    with open('updates.json', 'w', encoding='utf-8') as f:
        json.dump(all_updates[:30], f, indent=4)

    print(f"Scraping Complete! Added {len(new_updates)} new pages.")

if __name__ == "__main__":
    main()
