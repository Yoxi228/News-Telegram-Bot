# News Aggregator Telegram Bot

This bot aggregates news from VK and Twitter and sends them to a Telegram chat. It supports adding new sources and runs on a 10-minute schedule.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
VK_ACCESS_TOKEN=your_vk_access_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

3. Run the bot:
```bash
python main.py
```

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/add_vk_source <group_id>` - Add VK group as a news source
- `/add_twitter_source <username>` - Add Twitter account as a news source
- `/list_sources` - List all current news sources
- `/remove_source <source_id>` - Remove a news source

## Features

- Aggregates news from VK groups and Twitter accounts
- Runs on a 10-minute schedule
- Stores sources in JSON format
- Includes logging functionality
- Easy to add and remove news sources 