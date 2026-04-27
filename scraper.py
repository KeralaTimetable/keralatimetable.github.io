from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("--- KTU X-RAY DEBUGGER SCRIPT ---")
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
    
    # Grab the HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_links = soup.find_all('a')
    
    print(f"\n--- FOUND {len(all_links)} LINKS ON THE PAGE ---")
    
    for i, link in enumerate(all_links):
        # Clean up the text so it prints nicely
        text = link.text.strip().replace('\n', ' ')
        href = link.get('href', 'NO_LINK')
        
        # Print every single link so we can read KTU's structure
        if len(text) > 2 or "pdf" in href.lower() or "attachment" in href.lower():
            print(f"[{i}] TEXT: '{text[:80]}' | HREF: '{href}'")
            
    print("\n--- DEBUGGER FINISHED ---")
    driver.quit()

if __name__ == "__main__":
    main()
