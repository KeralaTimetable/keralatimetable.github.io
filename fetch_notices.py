import requests
import json
import urllib3

# Ignore SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_save_notices():
    print("Fetching live data from the Alert API...")
    
    url = "https://alert.ktunotes.live/api/notifications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    try:
        # 1. Download the clean JSON data
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            api_data = response.json()
            
            if api_data.get("success"):
                raw_notifications = api_data.get("notifications", [])
                formatted_notices = []
                
                # 2. Translate their data into YOUR website's format
                for notice in raw_notifications:
                    formatted_notices.append({
                        "subject": notice.get("title", "KTU Update"),
                        "announcementDate": notice.get("date", "Recent"),
                        "urlHref": notice.get("link", "https://ktu.edu.in/Menu/announcements"),
                        "attachmentList": [{"title": "Read More"}]  # This triggers the button on your site
                    })
                
                # 3. Save the formatted data to your notices.json file
                with open("notices.json", "w", encoding="utf-8") as f:
                    json.dump({"content": formatted_notices}, f, indent=4)
                    
                print(f"VICTORY! Successfully translated and saved {len(formatted_notices)} notices.")
                
            else:
                print("Connected to API, but it returned success: false")
                
        else:
            print(f"Failed. Server returned HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Fatal error fetching data: {e}")

if __name__ == "__main__":
    fetch_and_save_notices()
