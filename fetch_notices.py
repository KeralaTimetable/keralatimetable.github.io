import json
from playwright.sync_api import sync_playwright

def fetch_notices_with_browser():
    print("Launching invisible browser to intercept API data...")
    
    with sync_playwright() as p:
        # Launch Chromium with anti-bot bypass arguments
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        
        # Disguise the invisible browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        notices_data = []

        # This is our upgraded net: it catches any API response flying by
        def handle_response(response):
            # We broadened the search to just look for the word "announcement" anywhere in the URL
            if "announcement" in response.url.lower() and response.status == 200:
                try:
                    data = response.json()
                    # Check if the data looks like the real notices (either a list or a dictionary with 'content')
                    if isinstance(data, list) or (isinstance(data, dict) and 'content' in data):
                        print(f"Bingo! Intercepted data from: {response.url}")
                        notices_data.append(data)
                except Exception:
                    # If it's not a JSON file (like an image or CSS file with 'announcement' in the name), ignore it
                    pass

        # Attach the net to the browser
        page.on("response", handle_response)

        try:
            print("Navigating to the new KTU Announcements page...")
            
            # Use the EXACT new URL you just provided
            page.goto("https://ktu.edu.in/Menu/announcements", timeout=60000, wait_until="networkidle")

            if len(notices_data) > 0:
                # We save the LAST valid item caught
                with open("notices.json", "w") as f:
                    json.dump(notices_data[-1], f, indent=4)
                print("Success! Saved intercepted data to notices.json")
            else:
                print("Error: Reached the page, but didn't catch the API data in transit.")
                print("The API might be loading under a completely different name.")
                
        except Exception as e:
            print(f"Browser automation failed: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_notices_with_browser()
