import requests
import json
import urllib3

# Ignore strict SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_notices():
    print("Bypassing KTU CSRF Security Firewall...")
    
    # Step 1: Create a "Session". This acts like a real browser tab and remembers cookies!
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://ktu.edu.in",
        "Referer": "https://ktu.edu.in/"
    }
    
    try:
        # Step 2: Visit the homepage FIRST to trick the server into giving us the security cookie
        print("Knocking on the front door to get the security token...")
        session.get("https://ktu.edu.in/", headers=headers, verify=False, timeout=15)
        
        # Look inside the cookie jar and steal the XSRF token
        xsrf_token = session.cookies.get('XSRF-TOKEN')
        
        # If we found the token, put it on our wrist (in the headers)
        if xsrf_token:
            headers["X-XSRF-TOKEN"] = xsrf_token
            print("Successfully stole the XSRF-TOKEN!")
        else:
            print("No token found. Proceeding anyway...")

        # Step 3: Now hit the API with our verified session and token!
        print("Fetching notices from the API...")
        api_url = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"
        
        # The payload requesting the first 20 notices
        payload = {"number": 0, "size": 20}
        
        response = session.post(api_url, headers=headers, json=payload, verify=False, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            with open("notices.json", "w") as f:
                json.dump(data, f, indent=4)
                
            print("Success! Bypassed firewall and saved KTU notices.")
        else:
            print(f"Failed. Server returned HTTP {response.status_code}")
            print("Server response:", response.text[:250])
            
    except Exception as e:
        print(f"Error fetching notices: {e}")

if __name__ == "__main__":
    fetch_notices()
