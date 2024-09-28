import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio

# Telegram bot token and chat ID variables
TELEGRAM_TOKEN = os.getenv('7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4')  # Get from environment variable
CHAT_ID = os.getenv('5399212579')  # Get from environment variable

# Set up Selenium with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument('--disable-gpu')

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def check_marketplace():
    url = "http://www.google.com"  # Change to a simple URL for testing

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the URL
        driver.get(url)
        await asyncio.sleep(5)  # Wait for the page to load

        # Get page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Example: Print the title of the page
        title = soup.title.string
        await send_telegram_message(f"Page Title: {title}")

    except Exception as e:
        await send_telegram_message(f"Error checking marketplace: {e}")

    finally:
        driver.quit()  # Close the browser

async def main():
    while True:
        await check_marketplace()
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == "__main__":
    asyncio.run(main())
