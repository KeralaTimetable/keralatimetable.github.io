import requests
import json
import os
from datetime import datetime, timezone
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure these names match your HTML exactly!
SERVICES = {
    "KTU Main Website": "https://ktu.edu.in",
    "e-Governance Portal": "https://app.ktu.edu.in",
    "KTU API Server": "https://api.ktu.edu.in"
}

# THE DISGUISE: Pretend to be a real human on Google Chrome (Windows 11)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

def check_service(name, url):
    status = "Offline"
    error_type = "Timeout"
    ping_time = 0
    start_time = time.time()
    
    try:
        # Pass the disguise headers and increase timeout slightly to 15s
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        
        # If we get ANY valid response back (even a 403 Forbidden), the server is physically online
        if response.status_code < 500:
            status = "Online"
            error_type = "None"
            ping_time = int((time.time() - start_time) * 1000)
        else:
            error_type = f"Server Error ({response.status_code})"
            
    except requests.exceptions.Timeout:
        error_type = "Timeout"
    except Exception as e:
        error_type = "Unreachable"
        
    return {"status": status, "error_type": error_type, "ping": ping_time}

def main():
    print("Running KTU Stealth Ping...")
    results = {}
    down_count = 0
    ssl_issue = False
    
    for name, url in SERVICES.items():
        res = check_service(name, url)
        
        # If the standard stealth ping failed, do a hardcore SSL check just for the portal
        if res['status'] == "Offline" and "app.ktu" in url:
            try:
                requests.get(url, headers=HEADERS, timeout=10)
            except requests.exceptions.SSLError:
                res['status'] = "SSL Issue"
                res['error_type'] = "Certificate Error"
                ssl_issue = True
            except: pass

        results[name] = res
        print(f"{name}: {res['status']} ({res['ping']}ms)")
        
        if res['status'] == "Offline": down_count += 1
        if res['status'] == "SSL Issue": ssl_issue = True
        
    if down_count == len(SERVICES):
        overall = "Major Outage"
    elif down_count > 0:
        overall = "Partial Outage"
    elif ssl_issue:
        overall = "SSL Issues Detected"
    else:
        overall = "All Systems Operational"

    new_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "services": results
    }

    history = []
    if os.path.exists('status-history.json'):
        with open('status-history.json', 'r') as f:
            try: history = json.load(f)
            except: pass
            
    history.insert(0, new_record)
    history = history[:12]
    
    with open('status-history.json', 'w') as f:
        json.dump(history, f, indent=4)
        
    print(f"Logbook updated! Overall Status: {overall}")

if __name__ == "__main__":
    main()
