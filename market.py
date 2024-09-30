from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from telegram import Bot
import time
import asyncio

# Telegram bot token and chat ID variables
TELEGRAM_TOKEN = '7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4'
CHAT_ID = '5399212579'

# Set up Selenium with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
# chrome_options.add_argument("--window-size=1920x1080")

service = Service('app/.chrome-for-testing/chromedriver-linux64/chromedriver') # Update this line for correct chrome driver path

bot = Bot(token=TELEGRAM_TOKEN)

# Store already seen listings
seen_listings = set()

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def check_marketplace(keywords, location):
    url_template = f"https://www.facebook.com/marketplace/{location}/search/?query={{keyword}}"
    
    for keyword in keywords:
        url = url_template.format(keyword=keyword)
        
        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # Open the URL
            driver.get(url)
            await asyncio.sleep(5) 
            # Get page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust this selector based on the actual page structure
            listings = soup.find_all('div', class_='xjp7ctv')  # Replace with actual class

            for listing in listings:
                title_element = listing.find('span', class_='x1lliihq')  # Adjust as necessary
                link_element = listing.find('a', class_='x1i10hfl')  # Adjust as necessary
                
                if title_element and link_element:
                    title = title_element.text.strip()
                    link = link_element['href']
                    
                    if title not in seen_listings:
                        seen_listings.add(title)
                        await send_telegram_message(f"New listing: {title}\nLink: https://www.facebook.com{link}")        

        except Exception as e:
            print(f"Error checking marketplace for keyword '{keyword}': {e}")
        
        finally:
            await send_telegram_message(f"Round Finish: {keyword}")
            driver.quit()  # Close the browser
async def main():
    keywords_input = "iphone 11"#keywords_input = input("Enter keywords (comma-separated): ")
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    location = "melbourne" #location = input("Enter location: ")

    while True:
        await check_marketplace(keywords, location)
        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == "__main__":
    asyncio.run(main())
