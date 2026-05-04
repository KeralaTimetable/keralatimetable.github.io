import requests
import json
import time
from datetime import datetime, timezone, timedelta
import urllib3

# This tells Python to ignore strict SSL certificate warnings (act like Chrome)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# THESE NAMES MUST MATCH YOUR STATUS.HTML EXACTLY
TARGET_SERVICES = [
    {"name": "KTU Main Website", "url": "https://ktu.edu.in"},
    {"name": "KTU Login Portal", "url": "https://app.ktu.edu.in"},
    {"name": "KTU API Server", "url": "https://api.ktu.edu.in"}
]

# Disguise the bot as a normal Windows computer using Google Chrome
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
            # verify=False is the magic trick that bypasses the strict Python SSL block
            response = requests.get(svc["url"], headers=HEADERS, timeout=15, verify=False)
            ping_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code < 500:
                results[svc["name"]] = {"status": "Online", "ping": ping_ms}
                print(f"{svc['name']}: Online ({ping_ms}ms)")
            else:
                results[svc["name"]] = {"status": "Offline", "ping": "Timeout"}
                print(f"{svc['name']}: Offline (HTTP {response.status_code})")
                down_count += 1
                
        except requests.exceptions.SSLError:
            # We still catch this just in case, but verify=False makes it very rare now
            results[svc["name"]] = {"status": "SSL Issue", "ping": "Blocked"}
            print(f"{svc['name']}: SSL Issue")
            ssl_count += 1
            
        except requests.exceptions.RequestException:
            results[svc["name"]] = {"status": "Offline", "ping": "Timeout"}
            print(f"{svc['name']}: Offline (Timeout/Blocked)")
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

    # IST Time Conversion
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    
    new_record = {
        "timestamp": ist_time.isoformat(),
        "overall_status": overall,
        "services": results
    }

    # Save to history file
    try:
        with open("status-history.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.insert(0, new_record)
    history = history[:12] # Keep only the last 12 hours

    with open("status-history.json", "w") as f:
        json.dump(history, f, indent=4)

    print(f"Logbook updated! Overall Status: {overall}")

if __name__ == "__main__":
    ping_servers()
