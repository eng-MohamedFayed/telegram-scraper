# Telegram Channel Scraper

## Table of Contents
1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Setup](#setup)
   1. [Telegram API Credentials](#telegram-api-credentials)
   2. [MongoDB Setup](#mongodb-setup)
   3. [Telegram Bot Setup](#telegram-bot-setup)
4. [Modifying the Parsing Structure](#modifying-the-parsing-structure)
5. [Running the Script](#running-the-script)

## Overview

This script is designed to scrape messages from one or multiple Telegram channels and store them in a MongoDB database. It monitors for new messages in real-time and extracts useful information like dates, URLs, and message content. Optionally, it can send notifications to a personal Telegram bot whenever a new message is scraped.

## How It Works

- **Scraping**: The script iterates through all messages in a specified Telegram channel(s) and extracts:
  - The message text.
  - Detected dates in the message.
  - Detected URLs in the message.
  - The message title (first sentence of the message).
  - The description (the remaining content).
  
- **Real-Time Monitoring**: After scraping all past messages, the script monitors for new messages in real-time and continues scraping and storing them in the database.

- **Database Storage**: The scraped messages are stored in MongoDB, ensuring that previously scraped messages are not scraped again to save computing resources.

- **Bot Notifications**: A Telegram bot can notify you about new messages scraped from the specified channel(s).

## Setup

### Telegram API Credentials
1. Go to [my.telegram.org](https://my.telegram.org).
2. Log in with your phone number and create a new app to get:
   - `api_id`
   - `api_hash`
   
3. Replace the following placeholders in the script with your own credentials:
   ```python
   api_id = 'your_api_id'
   api_hash = 'your_api_hash'
   ```

### MongoDB Setup
1. Install MongoDB on your local machine or use a cloud provider (like [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)).
2. Ensure MongoDB is running, and create a database named `telegram_data`:
   ```bash
   mongo
   use telegram_data
   ```
3. The script connects to MongoDB automatically:
   ```python
   mongo_client = MongoClient('mongodb://localhost:27017/')
   ```

### Telegram Bot Setup
Optional

To receive notifications about new messages, you can create a bot:
1. Open Telegram and search for the **BotFather** bot.
2. Create a new bot and get the token.
3. Replace the following placeholder in the script:
   ```python
   bot_token = 'your_bot_token'
   ```
4. Obtain your Telegram chat ID:
   - Open [web.telegram.org](https://web.telegram.org).
   - Go to your **Saved Messages** and get the chat ID from the URL.
5. Replace the placeholder in the script:
   ```python
   chat_id = 'your_chat_id'
   ```

If you do not wish to use the bot, you can comment out the bot-related sections of the code.

## Modifying the Parsing Structure

If you want to change how messages are parsed, the `extract_message_info()` function is where all the parsing logic happens. You can modify the way titles, descriptions, URLs, and dates are extracted.

- **Title**: The current logic treats the first sentence (separated by a period or comma) as the title:
   ```python
   'title': re.split(r'[.,]\s+', message.message)[0]
   ```
   You can change the delimiter or adjust this to suit your needs.

- **Description**: Everything after the title is considered the description:
   ```python
   'description': '\n'.join(message.message.splitlines()[1:])
   ```

- **Date Parsing**: Dates are detected using regular expressions. You can modify the `date_pattern` to match different date formats:
   ```python
   date_pattern = r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|' ...
   ```

## Running the Script

### Step-by-Step Instructions
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your_username/telegram-scraper.git
   cd telegram-scraper
   ```

2. Install the required dependencies:
- **telethon**
- **pymongo**
- **python-telegram-bot**

   ```bash
   pip install telethon pymongo python-telegram-bot
   ```

3. Modify the configuration in the script:
   - Add your `api_id` and `api_hash`.
   - Add the `channel_usernames` of the Telegram channels you want to scrape.
   - Optionally, add the `bot_token` and `chat_id` if you want bot notifications.

4. Start the script:
   ```bash
   python scraping.py
   ```


## Notes
- The script will not re-scrape previously fetched messages, saving computing power.
- You can add multiple channels by extending the `channel_usernames` list.
  
---
## License

This project is licensed under the MIT License.


