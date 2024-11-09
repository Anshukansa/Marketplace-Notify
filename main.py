import os
import json
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from telegram import Bot

# Telegram bot token
TELEGRAM_TOKEN = '7714782007:AAEgB8XlRut-5HhKNWHaY7tBg1B6nCodci8'
CHAT_ID = '5399212579'

# Fetch the Chrome binary and ChromeDriver paths from environment variables
chrome_binary_path = os.getenv('CHROME_BINARY_PATH', '/default/path/to/chrome')  # Default if not set
chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/default/path/to/chromedriver')  # Default if not set

# Ensure that the environment variables are set correctly
if not chrome_binary_path or not chromedriver_path:
    raise ValueError("Chrome binary path or ChromeDriver path environment variables not set")

# Check if the files exist at these paths
if not os.path.isfile(chrome_binary_path):
    raise FileNotFoundError(f"Chrome binary not found at {chrome_binary_path}")
if not os.path.isfile(chromedriver_path):
    raise FileNotFoundError(f"ChromeDriver binary not found at {chromedriver_path}")

# Set up Chrome options
chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Initialize the ChromeDriver service
service = Service(chromedriver_path)

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

bot = Bot(token=TELEGRAM_TOKEN)

# Store already seen listings
seen_listings = set()


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
            await asyncio.sleep(10)
            # Get page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust this selector based on the actual page structure
            listings = soup.find_all('div', class_='xjp7ctv')  # Replace with actual class

            for listing in listings:
                #title_element = listing.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')  # Adjust as necessary
                link_element = listing.find('a', class_='x1i10hfl')  # Adjust as necessary
                price_element = listing.find('div', class_='x1gslohp')
                #address_element = listing.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1nxh6w3 x1sibtaa xo1l8bm xi81zsa')

                if price_element:
                    #title = title_element.text.strip()
                    link = link_element['href']
                    price = price_element.text.strip()
                    #address = address_element.text.strip()

                    if link not in seen_listings:
                        seen_listings.add(link)
                        await send_telegram_message(f"Price: {price} ({keyword})\nLink: https://www.facebook.com{link}")

        except Exception as e:
            print(f"Error checking marketplace for keyword '{keyword}': {e}")

        finally:
            #await send_telegram_message(f"Round Finish: {keyword}")
            driver.quit()  # Close the browser

async def main():
    keywords_input = "iphone 11, iphone 12, iphone 13, iphone 14" #keywords_input = input("Enter keywords (comma-separated): ")
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    location = "melbourne" #location = input("Enter location: ")

    while True:
        await check_marketplace(keywords, location)
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check


if __name__ == "__main__":
    asyncio.run(main())
