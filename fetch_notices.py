import requests
import json
import urllib3

# Ignore strict SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_notices_api():
    print("Testing the 'Amnesia' API Bypass...")
    
    API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"
    
    # We deliberately REMOVE the Origin, Referer, and complex User-Agent.
    # We want to look like a dumb internal script, not a web browser.
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }
    
    payload = {
        "number": 0,
        "size": 20
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, verify=False, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            with open("notices.json", "w") as f:
                json.dump(data, f, indent=4)
                
            print("JACKPOT! The Amnesia bypass worked. Data saved!")
        else:
            print(f"Failed. Server returned HTTP {response.status_code}")
            print("Response:", response.text[:250])
            
    except Exception as e:
        print(f"API request failed: {e}")

if __name__ == "__main__":
    fetch_notices_api()
