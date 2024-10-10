import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up Telegram bot
TOKEN = '7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4'
CHAT_ID = '5399212579'
bot = Bot(token=TOKEN)

# Set up Selenium WebDriver
def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('/chromedriver')  # Adjust the path if needed
    return webdriver.Chrome(service=service, options=chrome_options)

# Command handler for /title
def get_title(update, context: CallbackContext):
    driver = create_webdriver()
    driver.get('https://www.google.com')
    time.sleep(2)  # Wait for the page to load
    title = driver.title
    driver.quit()
    
    update.message.reply_text(f'The title of the page is: {title}')

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("title", get_title))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
