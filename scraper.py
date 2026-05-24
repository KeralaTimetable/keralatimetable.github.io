import os
import json
from playwright.sync_api import sync_playwright

def scrape_academic_calendars(output_dir="./downloads"):
    """
    Scrapes the KTU academic calendar list, captures the metadata from the 
    API response, and downloads each academic calendar PDF locally.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        print("Launching headless Chromium browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        calendar_metadata = []
        
        # Intercept and capture the metadata from the JSON API payload
        def on_response(response):
            if "anon/academicCalendar" in response.url:
                try:
                    data = response.json()
                    if 'content' in data:
                        for idx, item in enumerate(data['content']):
                            calendar_metadata.append({
                                'index': idx,
                                'id': item.get('id'),
                                'title': item.get('academicCalendarTitle'),
                                'date': item.get('publishedOn') or item.get('createdDate', '').split('T')[0],
                                'encryptAttachmentId': item.get('encryptAttachmentId'),
                                'attachmentName': item.get('attachmentName')
                            })
                        print(f"Captured {len(calendar_metadata)} calendar entries from KTU API.")
                except Exception as e:
                    print(f"Error parsing API response: {e}")
                    
        page.on("response", on_response)
        
        print("Navigating to KTU Academic Calendars...")
        page.goto("https://ktu.edu.in/academics/academic_calendar", wait_until="domcontentloaded", timeout=60000)

        # Buffer to allow all AJAX scripts to complete and render
        page.wait_for_timeout(4000) 
        
        downloaded_files = []
        print(f"\nProcessing {len(calendar_metadata)} downloads:")
        
        for cal in calendar_metadata:
            title = cal['title']
            encrypt_id = cal['encryptAttachmentId']
            
            if not encrypt_id:
                print(f"Skipping (No attachment available): '{title}'")
                continue
                
            print(f"\nDownloading: '{title}' (Published: {cal['date']})")
            
            # Find the button on the page that corresponds to this encryptId
            try:
                # Buttons on the page have an attribute: value="encryptAttachmentId"
                button_selector = f"button[value='{encrypt_id}']"
                button = page.locator(button_selector)
                
                if button.count() > 0:
                    # Expect the browser-level download event when the button is clicked
                    with page.expect_download(timeout=15000) as download_info:
                        button.click()
                    download = download_info.value
                    
                    # Generate a clean file name
                    filename = f"{cal['date']}_{cal['attachmentName'] or download.suggested_filename}"
                    save_path = os.path.join(output_dir, filename)
                    
                    # Save the stream to disk
                    download.save_as(save_path)
                    print(f" -> Saved successfully to: {save_path}")
                    
                    downloaded_files.append({
                        "title": title,
                        "date": cal['date'],
                        "filename": filename,
                        "path": save_path
                    })
                else:
                    print(f" -> Error: Download button for ID '{encrypt_id}' not found on UI.")
            except Exception as e:
                print(f" -> Failed to process download: {e}")
                
        browser.close()
        return downloaded_files

if __name__ == "__main__":
    results = scrape_academic_calendars()
    print("\n" + "="*40 + "\n          DOWNLOADS SUMMARY\n" + "="*40)
    for r in results:
        print(f"[{r['date']}] {r['title']} -> {r['filename']}")
