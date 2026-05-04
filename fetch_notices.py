import json
from playwright.sync_api import sync_playwright

def fetch_notices_with_browser():
    print("Launching invisible browser to intercept API data...")
    
    with sync_playwright() as p:
        # Launch Chromium with basic anti-bot bypass arguments
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        
        # Disguise the invisible browser as a standard Windows Chrome browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        notices_data = []

        # This is our net: it catches any API response flying by
        def handle_response(response):
            # If the response URL contains our target API and it succeeded (200)
            if "anon/announcemnts" in response.url and response.status == 200:
                print("Bingo! Intercepted the API response.")
                try:
                    notices_data.append(response.json())
                except Exception as e:
                    print("Parse error:", e)

        # Attach the net to the browser
        page.on("response", handle_response)

        try:
            print("Navigating to KTU homepage...")
            
            # wait_until="networkidle" tells the bot to wait until all background APIs finish loading!
            # No more guessing CSS class names!
            page.goto("https://ktu.edu.in/", timeout=60000, wait_until="networkidle")

            if len(notices_data) > 0:
                # We save the LAST item caught, just in case it fired twice
                with open("notices.json", "w") as f:
                    json.dump(notices_data[-1], f, indent=4)
                print("Success! Saved intercepted data to notices.json")
            else:
                print("Error: Reached the page, but didn't catch the API data in transit.")
                print("KTU might require clicking a specific 'Announcements' tab first.")
                
        except Exception as e:
            print(f"Browser automation failed: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_notices_with_browser()
