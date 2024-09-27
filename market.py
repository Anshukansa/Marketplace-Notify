import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from telegram import Bot
import time
import asyncio
import chromedriver_autoinstaller
import hashlib




# Telegram bot token and chat ID variables
TELEGRAM_TOKEN = '7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4'
CHAT_ID = '5399212579'

# Install the ChromeDriver matching the installed Chrome version if not available
chromedriver_autoinstaller.install()

# Set up Selenium with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument('--disable-gpu')


# service = Service(r'C:\Users\dell\Desktop\Marketplace\chromedriver\chromedriver.exe') # Update this line for correct chrome driver path

bot = Bot(token=TELEGRAM_TOKEN)

# Store already seen listings
seen_listings = set()

def generate_listing_hash(title, url):
    """Generate a unique hash for the listing based on its title and URL."""
    hash_input = f"{title}-{url}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def check_marketplace(keywords, location):
    url_template = f"https://www.facebook.com/marketplace/{location}/search?daysSinceListed=1&sortBy=creation_time_descend&query={{keyword}}&exact=false"
    
    for keyword in keywords:
        url = url_template.format(keyword=keyword)
        
        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Clear browser cache
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})

        # driver = webdriver.Chrome(service=service, options=chrome_options)


        try:
            # Open the URL
            driver.get(url)
            await asyncio.sleep(5) 
            # Get page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust this selector based on the actual page structure
            listings = soup.find_all('div', class_='xjp7ctv')  # Replace with actual class

            for listing in listings:
                # title_element = listing.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')  # Adjust as necessary
                link_element = listing.find('a', class_='x1i10hfl')  # Adjust as necessary
                price_element = listing.find('div', class_='x1gslohp')
                # address_element = listing.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1nxh6w3 x1sibtaa xo1l8bm xi81zsa')

                if price_element:
                    # title = title_element.text.strip()
                    link = link_element['href']
                    price = price_element.text.strip()
                    # address = address_element.text.strip()

                    listing_hash = generate_listing_hash(price, link)

                    if listing_hash not in seen_listings:
                        seen_listings.add(listing_hash)
                        await send_telegram_message(f"Price: {price}\nLink: https://www.facebook.com{link}")

        except Exception as e:
            print(f"Error checking marketplace for keyword '{keyword}': {e}")
        
        finally:
            driver.quit()  # Close the browser
async def main():
    keywords_input = input("Enter keywords (comma-separated): ")
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    location = "melbourne" #location = input("Enter location: ")

    while True:
        await check_marketplace(keywords, location)
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == "__main__":
    asyncio.run(main())