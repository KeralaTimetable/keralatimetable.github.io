import requests
import json
import urllib3

# Ignore SSL warnings just like our status bot
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"

def fetch_notices():
    print("Fetching latest notices from KTU API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(API_URL, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save the raw JSON data directly to our repository
            with open("notices.json", "w") as f:
                json.dump(data, f, indent=4)
                
            print(f"Success! Saved KTU notices to notices.json")
        else:
            print(f"Failed to fetch. KTU Server returned HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching notices: {e}")

if __name__ == "__main__":
    fetch_notices()
