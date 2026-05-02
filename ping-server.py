import requests
import json
import os
from datetime import datetime, timezone
import time
import urllib3

# Suppress the warning we get when we intentionally bypass SSL to measure ping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("Running KTU Smart Diagnostic Ping...")
    
    # We test the e-Governance portal, as this is where students actually log in
    target_url = "https://app.ktu.edu.in" 
    
    status = "Offline"
    error_type = "None"
    ping_time = 0
    
    start_time = time.time()
    
    # Step 1: Strict Test (Checks if the site works AND if SSL is valid)
    try:
        response = requests.get(target_url, timeout=10)
        
        if response.status_code == 200:
            status = "Online"
            ping_time = int((time.time() - start_time) * 1000)
        elif response.status_code >= 500:
            status = "Offline"
            error_type = "Server Overloaded (500)"
            
    except requests.exceptions.SSLError:
        print("DETECTED: SSL Certificate Expired!")
        status = "SSL Issue"
        error_type = "Certificate Error"
        
        # The site is actually alive, just insecure. Let's measure the ping anyway.
        try:
            start_time_2 = time.time()
            requests.get(target_url, timeout=10, verify=False)
            ping_time = int((time.time() - start_time_2) * 1000)
        except:
            pass
            
    except requests.exceptions.Timeout:
        print("DETECTED: Server Timeout!")
        status = "Offline"
        error_type = "Connection Timeout"
        
    except Exception as e:
        print(f"DETECTED: General Error - {e}")
        status = "Offline"
        error_type = "Unreachable"

    # Step 2: Save the Data
    timestamp = datetime.now(timezone.utc).isoformat()
    
    new_record = {
        "timestamp": timestamp,
        "status": status,
        "error_type": error_type,
        "ping": ping_time
    }
    
    print(f"Result: {status} | Error: {error_type} | Ping: {ping_time}ms")

    history = []
    if os.path.exists('status-history.json'):
        with open('status-history.json', 'r') as f:
            try: history = json.load(f)
            except: pass
            
    history.insert(0, new_record)
    history = history[:12] # Keep last 12 hours
    
    with open('status-history.json', 'w') as f:
        json.dump(history, f, indent=4)
        
    print("Smart Logbook updated successfully!")

if __name__ == "__main__":
    main()
