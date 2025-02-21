from playwright.sync_api import sync_playwright
from fastapi import FastAPI
import time

app = FastAPI()

def search_rightmove_properties(location):
    # Start up our web browser
    with sync_playwright() as p:
        # Launch the browser - setting headless=True for deployment on Render
        browser = p.chromium.launch(headless=True)
        
        # Open a new page (like opening a new tab)
        page = browser.new_page()
        
        try:
            # Go to Rightmove
            print(f"Going to Rightmove...")
            page.goto("https://www.rightmove.co.uk/")
            
            # Handle the cookie popup
            print("Looking for cookie popup...")
            page.wait_for_selector('#onetrust-accept-btn-handler')
            page.click('#onetrust-accept-btn-handler')
            print("Accepted cookies")
            
            # Wait for the search box to appear
            print("Looking for search box...")
            page.wait_for_selector('#ta_searchInput')
            
            # Type in the location
            print("Entering location...")
            page.fill('#ta_searchInput', location)
            
            # Wait a moment for suggestions to appear
            time.sleep(2)
            
            # Click the "For Sale" button
            print("Clicking For Sale...")
            page.click('[data-testid="forSaleCta"]')
            
            # Wait a moment for the "Search properties" button to appear and click it
            print("Clicking Search properties...")
            page.wait_for_selector('#submit', state="visible")
            
            # Scroll into view before clicking
            search_button = page.locator('#submit')
            search_button.scroll_into_view_if_needed()
            search_button.click()
            
            print("Search properties button clicked.")
            
            # Wait for the results page to load
            print("Waiting for results...")
            time.sleep(5)
            
            # Get property listings
            properties = page.query_selector_all('.propertyCard')
            
            # Create a summary of the first few properties
            summary = []
            for i, property in enumerate(properties[:5]):  # Get first 5 properties
                price = property.query_selector('.propertyCard-priceValue')
                address = property.query_selector('.propertyCard-address')
                description = property.query_selector('.propertyCard-description')
                
                if price and address:
                    price_text = price.inner_text()
                    address_text = address.inner_text()
                    desc_text = description.inner_text() if description else "No description available"
                    
                    summary.append(f"Property {i+1}:\nPrice: {price_text}\nAddress: {address_text}\nDescription: {desc_text}\n")
            
            return summary
            
        finally:
            # Close the browser
            browser.close()

@app.get("/search")
def search(location: str):
    return search_rightmove_properties(location)

# Run the search locally
if __name__ == "__main__":
    print("\nRunning Rightmove search locally...")
    results = search_rightmove_properties("Reading")
    print("\nHere's your property summary:")
    print(results)
