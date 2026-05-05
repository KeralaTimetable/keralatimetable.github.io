import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_alert_api():
    print("Connecting to the ktunotes.live API...")
    
    # The exact URL you found in your Network tab!
    url = "https://alert.ktunotes.live/api/notifications"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            print("Successfully connected! Here is the raw data:")
            data = response.json()
            
            # Print the first 1000 characters of the JSON nicely formatted
            print(json.dumps(data, indent=2)[:1000])
            
        else:
            print(f"Failed. HTTP {response.status_code}")
            
    except Exception as e:
        print(f"API Fetch failed: {e}")

if __name__ == "__main__":
    fetch_alert_api()
