import os
from playwright.sync_api import sync_playwright
from fastapi import FastAPI
import time

# Set the Playwright browsers path environment variable
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

app = FastAPI()

def search_rightmove_properties(location):
    # Start up our web browser
    with sync_playwright() as p:
        # Launch the browser - setting headless=True for deployment on Render
        # Using channel="chrome" to avoid executable path issues
        browser = p.chromium.launch(
            headless=True,
            channel="chrome"
        )
        
        # Open a new page (like opening a new tab)
        page = browser.new_page()
        
        try:
            # Go to Rightmove
            print(f"Going to Rightmove...")
            page.goto("https://www.rightmove.co.uk/")
            
            # Handle the cookie popup
            print("Looking for cookie popup...")
            try:
                page.wait_for_selector('#onetrust-accept-btn-handler', timeout=10000)
                page.click('#onetrust-accept-btn-handler')
                print("Accepted cookies")
            except Exception as e:
                print(f"Cookie popup not found or couldn't be clicked: {e}")
                # Continue anyway as the popup might not appear
            
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
            page.wait_for_load_state('networkidle')
            
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
            
            if not summary:
                return ["No properties found. The search might have failed or there are no results for this location."]
                
            return summary
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return [f"Error searching for properties: {str(e)}"]
        finally:
            # Close the browser
            browser.close()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/search")
def search(location: str):
    return {"results": search_rightmove_properties(location)}

# Run the search locally
if __name__ == "__main__":
    print("\nRunning Rightmove search locally...")
    results = search_rightmove_properties("Reading")
    print("\nHere's your property summary:")
    for result in results:
        print(result)