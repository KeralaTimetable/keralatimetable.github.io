from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("--- KTU X-RAY SCRIPT V2 (DEEP SCAN) ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://ktu.edu.in/Menu/announcements"
    
    print(f"Loading {url}...")
    driver.get(url)
    
    print("Waiting 15 seconds for React to build the page...")
    time.sleep(15)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    print("\n--- SCAN 1: LOOKING AT LINK CONTAINERS ---")
    all_links = soup.find_all('a')
    for i, link in enumerate(all_links):
        href = link.get('href', 'NO_LINK')
        # Skip the boring menu links to keep the log clean
        if "Menu" in href or href == "#" or "schools.ktu.edu.in" in href:
            continue
            
        # Get the text of the box wrapping the link (this usually contains the title!)
        parent_text = link.parent.text.strip().replace('\n', ' ')
        print(f"[{i}] HREF: '{href}'")
        print(f"    SURROUNDING TEXT: '{parent_text[:150]}'")

    print("\n--- SCAN 2: LOOKING AT HEADERS (Where titles hide) ---")
    headers = soup.find_all(['h4', 'h5', 'h6', 'strong'])
    for i, h in enumerate(headers[:15]): # Just check the first 15 headers
        text = h.text.strip().replace('\n', ' ')
        if len(text) > 10: # Only print headers that have actual words
            print(f"Header [{i}]: '{text[:100]}'")

    print("\n--- DEBUGGER FINISHED ---")
    driver.quit()

if __name__ == "__main__":
    main()
