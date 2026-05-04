import json
import time
from playwright.sync_api import sync_playwright

def fetch_notices_with_browser():
    print("Launching invisible browser to bypass x-Token security...")
    
    with sync_playwright() as p:
        # Launch an invisible Chromium browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        notices_data = []

        # We will set up a "listener" to catch the API response in mid-air
        def handle_response(response):
            if "api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts" in response.url and response.status == 200:
                print("Intercepted the API data successfully!")
                try:
                    data = response.json()
                    notices_data.append(data)
                except Exception as e:
                    print("Failed to parse JSON from interception:", e)

        page.on("response", handle_response)

        try:
            print("Navigating to KTU Announcements page...")
            # We go directly to the page that loads the announcements
            page.goto("https://ktu.edu.in/eu/core/announcements.htm", timeout=60000)
            
            # Wait for the table to load (this ensures the API call was made)
            page.wait_for_selector(".table-responsive", timeout=15000)
            
            # Give it 2 extra seconds just to ensure the interception caught the data
            time.sleep(2)
            
            if len(notices_data) > 0:
                # We successfully caught the data!
                with open("notices.json", "w") as f:
                    json.dump(notices_data[0], f, indent=4)
                print("Success! Saved intercepted data to notices.json")
            else:
                print("Error: Reached the page, but didn't catch the API data in transit.")
                
        except Exception as e:
            print(f"Browser automation failed: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_notices_with_browser()
