import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from telegram import Bot
import time
import asyncio
import chromedriver_autoinstaller

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

        try:
            # Open the URL
            driver.get(url)

            # Wait for listings to load
            await asyncio.sleep(10)

            # Get page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust this selector based on the actual page structure
            listings = soup.find_all('div', class_='xjp7ctv')  # Replace with actual class

            if listings:
                for listing in listings:
                    link_element = listing.find('a', class_='x1i10hfl')  # Adjust as necessary
                    price_element = listing.find('div', class_='x1gslohp')  # Adjust as necessary

                    if price_element and link_element:
                        link = link_element['href']
                        price = price_element.text.strip()

                        await send_telegram_message(f"Price: {price}\nLink: https://www.facebook.com{link}")
            else:
                print(f"No listings found for keyword '{keyword}'")

        except Exception as e:
            print(f"Error checking marketplace for keyword '{keyword}': {e}")
            await send_telegram_message(f"Error: {str(e)}")

        finally:
            await send_telegram_message("Round Finish")
            driver.quit()  # Close the browser

async def main():
    keywords_input = "iphone"  # keywords_input = input("Enter keywords (comma-separated): ")
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    location = "melbourne"  # location = input("Enter location: ")

    while True:
        await check_marketplace(keywords, location)
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == "__main__":
    asyncio.run(main())
