import os
import json
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from telegram import Bot
import chromedriver_autoinstaller

# Telegram bot token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Install the ChromeDriver matching the installed Chrome version if not available
chromedriver_autoinstaller.install()

# Set up Selenium with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument('--disable-gpu')

bot = Bot(token=TELEGRAM_TOKEN)

# Store already seen listings per user
user_seen_listings = {}

# Load user data from the JSON-formatted text file
def load_users(filename="users.txt"):
    with open(filename, "r") as file:
        return json.load(file)

# Send message to specific user chat
async def send_telegram_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)

# Check marketplace for specific user with keywords and location
async def check_marketplace(keywords, location, chat_id):
    url_template = f"https://www.facebook.com/marketplace/{location}/search?daysSinceListed=1&sortBy=creation_time_descend&query={{keyword}}&exact=false"

    # Initialize seen listings for this user if not already present
    if chat_id not in user_seen_listings:
        user_seen_listings[chat_id] = set()

    for keyword in keywords:
        url = url_template.format(keyword=keyword)

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Clear browser cache
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})

        try:
            # Open the URL
            driver.get(url)
            await asyncio.sleep(10)  # Wait for the page to load

            # Get page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust this selector based on the actual page structure
            listings = soup.find_all('div', class_='xjp7ctv')  # Replace with actual class

            for listing in listings:
                link_element = listing.find('a', class_='x1i10hfl')  # Adjust as necessary
                price_element = listing.find('div', class_='x1gslohp')
                
                if link_element and price_element:
                    link = link_element['href']
                    price = price_element.text.strip()

                    if link not in user_seen_listings[chat_id]:
                        user_seen_listings[chat_id].add(link)
                        await send_telegram_message(f"Price: {price} ({keyword})\nLink: https://www.facebook.com{link}", chat_id)

        except Exception as e:
            print(f"Error checking marketplace for keyword '{keyword}' and user '{chat_id}': {e}")

        finally:
            driver.quit()  # Close the browser

# Run the marketplace check for each user
async def check_marketplace_for_user(user):
    keywords = user["keywords"]
    location = user["location"]
    chat_id = user["user_id"]

    await check_marketplace(keywords, location, chat_id)

# Main function to load users and run checks in parallel
async def main():
    users = load_users()
    while True:
        # Run scraping for all users in parallel
        await asyncio.gather(*(check_marketplace_for_user(user) for user in users))
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == "__main__":
    asyncio.run(main())