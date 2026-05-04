import requests
import json
import urllib3

# Ignore strict SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"

def fetch_notices():
    print("Fetching latest notices from KTU API...")
    
    # We must look EXACTLY like the official KTU website to bypass the 500 error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://ktu.edu.in/",
        "Origin": "https://ktu.edu.in",
        "Content-Type": "application/json"
    }
    
    # Modern APIs usually require pagination data to know how many notices to send
    payload = {
        "number": 0,
        "size": 20
    }
    
    try:
        # ATTEMPT 1: Try a POST request (Standard for University APIs)
        response = requests.post(API_URL, headers=headers, json=payload, verify=False, timeout=15)
        
        # ATTEMPT 2: If it actually wanted a GET request, fallback to GET
        if response.status_code in [500, 405, 400]:
            print(f"POST returned {response.status_code}, trying GET instead...")
            response = requests.get(API_URL, headers=headers, verify=False, timeout=15)

        # Check if we finally got the data (HTTP 200 OK)
        if response.status_code == 200:
            data = response.json()
            
            with open("notices.json", "w") as f:
                json.dump(data, f, indent=4)
                
            print("Success! Saved KTU notices to notices.json")
        else:
            print(f"Failed to fetch. KTU Server returned HTTP {response.status_code}")
            # Print the server's complaint so we can debug it if it fails again
            print("Server response:", response.text[:250]) 
            
    except Exception as e:
        print(f"Error fetching notices: {e}")

if __name__ == "__main__":
    fetch_notices()
