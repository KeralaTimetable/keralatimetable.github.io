import requests
import json
import urllib3

# Ignore strict SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_notices():
    print("Bypassing KTU CSRF Security Firewall (Attempt 2)...")
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://ktu.edu.in",
        "Referer": "https://ktu.edu.in/"
    }
    
    api_url = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"
    
    try:
        # Step 1: Knock directly on the API's door to get the security token
        print("Pinging the API server to extract the security cookie...")
        
        # We do a simple GET request first. The server will likely throw an error, 
        # but it will STILL hand us the CSRF token in the process!
        session.get(api_url, headers=headers, verify=False, timeout=15)
        
        # Dig through the cookie jar to find the token (ignoring case)
        xsrf_token = None
        for cookie in session.cookies:
            if cookie.name.upper() == 'XSRF-TOKEN':
                xsrf_token = cookie.value
                break
                
        if xsrf_token:
            headers["X-XSRF-TOKEN"] = xsrf_token
            print("Successfully stole the XSRF-TOKEN from the API!")
        else:
            print("Still no token found. Trying to proceed anyway...")

        # Step 2: Now send the real request with the token attached!
        print("Fetching notices...")
        payload = {"number": 0, "size": 20}
        
        # Most modern APIs use POST for this, but we will test it.
        response = session.post(api_url, headers=headers, json=payload, verify=False, timeout=15)
        
        # If POST fails, try GET just in case!
        if response.status_code != 200:
            print(f"POST failed (HTTP {response.status_code}), trying GET instead...")
            response = session.get(api_url, headers=headers, params=payload, verify=False, timeout=15)

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
