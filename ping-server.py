import requests
import json
import os
from datetime import datetime, timezone
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# We now check multiple KTU endpoints independently
SERVICES = {
    "KTU Main Website": "https://ktu.edu.in",
    "e-Governance Portal (Login)": "https://app.ktu.edu.in",
    "KTU API Server": "https://api.ktu.edu.in"
}

def check_service(name, url):
    status = "Offline"
    error_type = "Timeout"
    ping_time = 0
    start_time = time.time()
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            status = "Online"
            error_type = "None"
            ping_time = int((time.time() - start_time) * 1000)
        elif response.status_code >= 500:
            error_type = f"Server Error ({response.status_code})"
    except requests.exceptions.SSLError:
        status = "SSL Issue"
        error_type = "Certificate Error"
        try:
            start_2 = time.time()
            requests.get(url, timeout=10, verify=False)
            ping_time = int((time.time() - start_2) * 1000)
        except: pass
    except requests.exceptions.Timeout:
        error_type = "Timeout"
    except Exception as e:
        error_type = "Unreachable"
        
    return {"status": status, "error_type": error_type, "ping": ping_time}

def main():
    print("Running KTU Multi-Service Ping...")
    results = {}
    down_count = 0
    ssl_issue = False
    
    for name, url in SERVICES.items():
        res = check_service(name, url)
        results[name] = res
        print(f"{name}: {res['status']} ({res['ping']}ms)")
        
        if res['status'] == "Offline": down_count += 1
        if res['status'] == "SSL Issue": ssl_issue = True
        
    # Determine the overall global status
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
    history = history[:12] # Keep last 12 hours
    
    with open('status-history.json', 'w') as f:
        json.dump(history, f, indent=4)
        
    print(f"Logbook updated! Overall Status: {overall}")

if __name__ == "__main__":
    main()
