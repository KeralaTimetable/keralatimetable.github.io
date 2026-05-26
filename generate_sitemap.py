import os
from datetime import datetime, timezone

# --- CONFIGURATION ---
BASE_URL = "https://keralatimetable.github.io/"
# Folders or files you DO NOT want in Google Search
EXCLUDED_DIRS = ['.git', '.github', 'downloads_timetable'] 
EXCLUDED_FILES = ['components.js', 'poll-config.js', 'timetable-config.js', '404.html']

def generate_sitemap():
    print("🔍 Scanning repository for HTML files...")
    
    urls = []
    
    # Walk through all directories and files in the repo
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if file.endswith('.html') and file not in EXCLUDED_FILES:
                # Get the file path
                file_path = os.path.join(root, file)
                
                # Clean up the path for the URL
                # Convert './timetable_pages/file.html' to 'timetable_pages/file.html'
                clean_path = file_path.replace('./', '').replace('\\', '/')
                
                # Create the full live URL
                if clean_path == 'index.html':
                    loc = BASE_URL
                    priority = "1.0"
                    changefreq = "daily"
                else:
                    loc = BASE_URL + clean_path
                    priority = "0.8"
                    changefreq = "weekly"
                
                # Get the last modified date of the file
                mod_time = os.path.getmtime(file_path)
                lastmod = datetime.fromtimestamp(mod_time, tz=timezone.utc).strftime('%Y-%m-%d')
                
                urls.append({
                    'loc': loc,
                    'lastmod': lastmod,
                    'changefreq': changefreq,
                    'priority': priority
                })

    # --- BUILD THE XML ---
    print(f"✅ Found {len(urls)} pages. Building sitemap.xml...")
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
        
    xml_content += '</urlset>'
    
    # Save the file
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
        
    print("🚀 sitemap.xml successfully generated!")

if __name__ == "__main__":
    generate_sitemap()
