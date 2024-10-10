import time
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up Telegram bot
TOKEN = '7621738371:AAFzRuvAFroszoqE-ciZp8Eyg-km7GloMq4'
CHAT_ID = '5399212579'
bot = Bot(token=TOKEN)

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_service = Service('/usr/local/bin/chromedriver')  # Path for chromedriver in Heroku

def send_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get("http://google.com")  # Change to any URL you want to visit
    time.sleep(5)  # Wait for the page to load
    send_message("Visited google.com")
    driver.quit()

if __name__ == "__main__":
    main()
