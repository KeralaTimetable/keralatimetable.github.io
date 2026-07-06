import requests
import json
import time
from datetime import datetime, timezone
import urllib3

# Suppress the console warnings when we do our fallback check
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_SERVICES = [
    {"name": "KTU Main Website", "url": "https://ktu.edu.in"},
    {"name": "KTU Login Portal", "url": "https://app.ktu.edu.in"},
    {"name": "KTU API Server", "url": "https://api.ktu.edu.in"}
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def ping_servers():
    print("Running KTU Smart Stealth Ping...")
    results = {}
    down_count = 0
    ssl_count = 0

    for svc in TARGET_SERVICES:
        start_time = time.time()
        try:
            # STEP 1: Normal strict ping
            response = requests.get(svc["url"], headers=HEADERS, timeout=15)
            ping_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code < 400:
                results[svc["name"]] = {"status": "Online", "ping": ping_ms}
                print(f"{svc['name']}: Online ({ping_ms}ms)")
            elif response.status_code < 500:
                results[svc["name"]] = {"status": f"Online (HTTP {response.status_code})", "ping": ping_ms}
                print(f"{svc['name']}: Online but returning Client Error (HTTP {response.status_code})")
            else:
                # This will cleanly catch 500, 502, 503, 504 Gateway errors
                results[svc["name"]] = {"status": f"Offline (HTTP {response.status_code})", "ping": "Error"}
                print(f"{svc['name']}: Offline (HTTP {response.status_code})")
                down_count += 1
                
        except requests.exceptions.SSLError:
            # STEP 2: Server threw an SSL error. Let's do a fallback check to verify if the server is actually alive.
            try:
                fallback_start = time.time()
                fallback = requests.get(svc["url"], headers=HEADERS, timeout=15, verify=False)
                ping_ms = int((time.time() - fallback_start) * 1000)
                
                if fallback.status_code < 400:
                    results[svc["name"]] = {"status": "Online", "ping": ping_ms}
                    print(f"{svc['name']}: Online (CA Mismatch Bypassed)")
                elif fallback.status_code < 500:
                    results[svc["name"]] = {"status": f"Online (HTTP {fallback.status_code})", "ping": ping_ms}
                    print(f"{svc['name']}: Online but returning Client Error (CA Mismatch, HTTP {fallback.status_code})")
                else:
                    results[svc["name"]] = {"status": f"Offline (HTTP {fallback.status_code})", "ping": "Error"}
                    print(f"{svc['name']}: Offline (HTTP {fallback.status_code})")
                    down_count += 1
                    
            except requests.exceptions.Timeout:
                # Captures if the server hangs infinitely during fallback
                results[svc["name"]] = {"status": "Offline (Connection Timeout)", "ping": "Timeout"}
                print(f"{svc['name']}: Offline (Connection Timeout)")
                down_count += 1
                
            except requests.exceptions.RequestException:
                # If the fallback ALSO crashes, it means KTU is having a genuine, massive SSL/Connection failure.
                results[svc["name"]] = {"status": "SSL Issue", "ping": "Blocked"}
                print(f"{svc['name']}: Genuine SSL/Connection Issue Detected")
                ssl_count += 1
                
        except requests.exceptions.Timeout:
             # Captures if the server hangs infinitely on the very first try
             results[svc["name"]] = {"status": "Offline (Connection Timeout)", "ping": "Timeout"}
             print(f"{svc['name']}: Offline (Connection Timeout)")
             down_count += 1
             
        except requests.exceptions.RequestException:
            results[svc["name"]] = {"status": "Offline (Network Error)", "ping": "Error"}
            print(f"{svc['name']}: Offline (Network/Routing Error)")
            down_count += 1

    # Determine Overall Status
    if down_count == len(TARGET_SERVICES):
        overall = "Major Outage"
    elif down_count > 0:
        overall = "Partial Outage"
    elif ssl_count > 0:
        overall = "SSL Issues Detected"
    else:
        overall = "All Systems Operational"

    utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    new_record = {
        "timestamp": utc_time,
        "overall_status": overall,
        "services": results
    }

    try:
        with open("status-history.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.insert(0, new_record)
    history = history[:12] # Keep only the last 12 entries to prevent the file from getting too large

    with open("status-history.json", "w") as f:
        json.dump(history, f, indent=4)

    print(f"Logbook updated! Overall Status: {overall}")

if __name__ == "__main__":
    ping_servers()
