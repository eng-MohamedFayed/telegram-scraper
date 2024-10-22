
import re
from datetime import datetime, timezone
from telethon import TelegramClient, events
from pymongo import MongoClient
from telegram import Bot

# Telegram API credentials (replace with your values)
api_id = ''
api_hash = ''
channel_usernames = ['ctinow']  # List of channels to scrape add what you want

# MongoDB setup
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['telegram_data']

# Initialize Telegram client
client = TelegramClient('anon', api_id, api_hash)

# Regular expressions for finding dates and URLs
date_pattern = r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'  \
               r'\b\d{1,2}\s+\w+\s+\d{2,4}\b|'         \
               r'\b\w+\s+\d{2,4}\b|'                   \
               r'\b(?:today|yesterday|last\s+\w+)\b)'

url_pattern = r'https?://[^\s]+'

# Telegram bot setup
bot_token = ''
chat_id = ''  # Your own Telegram chat ID, you can get it by opening web.telegram.org and going to your "saved messages" the id is the number after the # in the url
bot = Bot(token=bot_token)

def extract_message_info(message):
    dates = re.findall(date_pattern, message.message)
    incident_date = dates[0] if dates else None

    urls = re.findall(url_pattern, message.message)

    message_info = {
        'message_id': message.id,
        'date_sent': message.date.strftime('%Y-%m-%d %H:%M:%S'),
        'message': message.message,
        'incident_date': incident_date,
        'urls': urls,
        'title': re.split(r'[.,]\s+', message.message)[0] if message.message else '',
        'description': '\n'.join(message.message.splitlines()[1:]) if message.message else ''
    }

    return message_info

async def scrape_channel(channel_username):
    collection = db[channel_username]  # Create a MongoDB collection for each channel
    
    # Get the latest message date from the database
    last_message = collection.find_one(sort=[("message_id", -1)])  # Find the latest message
    if last_message:
        last_message_date = datetime.strptime(last_message['date_sent'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    else:
        last_message_date = datetime(2024, 10, 18, tzinfo=timezone.utc)  # Default starting point
    
    print(f"Last message date in DB for {channel_username}: {last_message_date}")
    
    # Start fetching messages
    async for message in client.iter_messages(channel_username):
        # Stop iterating if the message is older than the last scraped message
        if message.date < last_message_date:
            print(f"Stopped fetching messages, reached previously scraped messages for {channel_username}")
            break
        
        # Scrape only if there's a message and it's newer than last_message_date
        if message.message and message.date > last_message_date:
            message_info = extract_message_info(message)
            collection.insert_one(message_info)
            print(f"Scraped message {message.id} from {channel_username}")

    # Start monitoring for new messages in the channel
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        message_info = extract_message_info(event.message)
        collection.insert_one(message_info)
        print(f"New message scraped from {channel_username}: {event.message.id}")
        
        # Send a notification via Telegram bot
        await bot.send_message(chat_id, f"New message in {channel_username}:\nTitle: {message_info['title']}\nDate Sent: {message_info['date_sent']}\nIncident Date: {message_info['incident_date']}\nURLs: {', '.join(message_info['urls']) if message_info['urls'] else 'No URLs'}")

async def scrape_messages():
    async with client:
        # Scrape and monitor messages from multiple channels
        for channel_username in channel_usernames:
            await scrape_channel(channel_username)
        print("Monitoring for new messages across all channels...")
        await client.run_until_disconnected()

# Start scraping
client.loop.run_until_complete(scrape_messages())
