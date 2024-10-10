import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Set up Telegram bot
TOKEN = '7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4'

# Set up Selenium WebDriver
def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('/chromedriver')  # Adjust the path if needed
    return webdriver.Chrome(service=service, options=chrome_options)

# Command handler for /title
async def get_title(update, context):
    driver = create_webdriver()
    driver.get('https://www.google.com')
    time.sleep(2)  # Wait for the page to load
    title = driver.title
    driver.quit()
    
    await update.message.reply_text(f'The title of the page is: {title}')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("title", get_title))

    application.run_polling()

if __name__ == '__main__':
    main()
