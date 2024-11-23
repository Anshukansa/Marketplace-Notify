import os
import asyncio
import random
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from collections import defaultdict

# Telegram bot token
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'YOUR_DATABASE_URL')

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Create table for seen listings if it doesn't exist
def create_seen_listings_table():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seen_listings (
                    id SERIAL PRIMARY KEY,
                    link TEXT UNIQUE
                );
            """)
            conn.commit()
    finally:
        conn.close()

# Check if a listing is already seen
def is_seen(link):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM seen_listings WHERE link = %s;", (link,))
            return cur.fetchone() is not None
    finally:
        conn.close()

# Mark a listing as seen
def mark_as_seen(link):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO seen_listings (link) VALUES (%s) ON CONFLICT DO NOTHING;", (link,))
            conn.commit()
    finally:
        conn.close()

# ChromeDriver setup
def configure_chrome_options():
    """Configure ChromeDriver with optimizations for lightweight scraping."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disable image loading
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    return chrome_options

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# Directly define user data
users = [
    {
        "user_id": 7932502148,  # Example Telegram chat ID
        "location": "melbourne",  # Example location
        "keywords": ["iphone"],  # Example keywords
        "excluded_words": ["Warranty",
            "controller",
            "for",
            "stand",
            "car",
            "names",
            "stereo",
            "Repelacement",
            "Cheapest",
            "LCD",
            "smart",
            "C@$h",
            "Ca$h"],  # Example excluded words
    }
]

# Generate all unique keyword-location pairs
def generate_pairs_and_log(users):
    """Generate unique keyword-location pairs."""
    pairs = set()
    user_pair_map = defaultdict(list)

    for user in users:
        keywords = user["keywords"]
        location = user["location"]
        chat_id = user["user_id"]
        excluded_words = user.get("excluded_words", [])

        for keyword in keywords:
            pair = (keyword, location)
            pairs.add(pair)
            user_pair_map[pair].append({"chat_id": chat_id, "excluded_words": excluded_words})

    return pairs, user_pair_map

# Send messages sequentially to avoid rate-limiting issues
async def send_messages_sequentially(messages):
    """Send messages sequentially to avoid overloading Telegram."""
    for message, chat_id in messages:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
        except TelegramError as e:
            print(f"Failed to send message to {chat_id}: {e}")

# Check listings for a given keyword-location pair
async def check_marketplace_pair(pair, user_data):
    """Check the marketplace for new listings and prepare messages for users."""
    keyword, location = pair
    url = f"https://www.facebook.com/marketplace/{location}/search?minPrice=100&maxPrice=1000&daysSinceListed=1&sortBy=creation_time_descend&query={keyword}"

    # Configure and start Chrome
    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.delete_all_cookies()

    try:
        driver.get(url)
        await asyncio.sleep(60)
        driver.refresh()
        await asyncio.sleep(60)

        # Wait for listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "xjp7ctv"))
        )

        # Parse listings
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all('div', class_='xjp7ctv')

        messages = []
        for listing in listings:
            link_element = listing.find('a', class_='x1i10hfl')
            price_element = listing.find('div', class_='x1gslohp')
            title_element = listing.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')

            if link_element and price_element and title_element:
                link = link_element['href']
                price = price_element.text.strip()
                title = title_element.text.strip()

                # Skip if already seen
                if is_seen(link):
                    continue

                # Mark as seen
                mark_as_seen(link)

                # Prepare messages for relevant users
                for user in user_data[pair]:
                    chat_id = user["chat_id"]
                    excluded_words = user["excluded_words"]

                    # Skip if excluded words are found in title
                    if any(word.lower() in title.lower() for word in excluded_words):
                        continue

                    message = f"Price: {price} ({keyword})\nLink: https://www.facebook.com{link}"
                    messages.append((message, chat_id))

        # Send messages sequentially
        await send_messages_sequentially(messages)

    except Exception as e:
        print(f"Error checking pair {pair}: {e}")
        traceback.print_exc()  # Add this to log the full error traceback
    finally:
        driver.quit()

# Run a single round of monitoring
async def single_round_monitoring(users):
    """Run a single round of monitoring for all user pairs."""
    pairs, user_pair_map = generate_pairs_and_log(users)

    # Create tasks for all pairs
    tasks = [
        check_marketplace_pair(pair, user_pair_map)
        for pair in pairs
    ]

    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    print("Single round completed.")

# Run script
if __name__ == "__main__":
    create_seen_listings_table()  # Ensure the database table exists
    asyncio.run(single_round_monitoring(users))
