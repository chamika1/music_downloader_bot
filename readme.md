# Telegram Music Download Bot

A stylish Telegram bot that downloads music from YouTube with progress animations and caching system.

## Features
- 🎵 Downloads songs from YouTube using /song command
- 📥 Shows download progress with animations
- 📤 Shows upload progress with file size
- ⚡ Caches songs for faster retrieval
- 🎨 Stylish messages and progress bars
- 📊 Shows song details including duration and view count
- 🎧 Supports audio streaming

## Setup
1. Get your Telegram API credentials:
   - API_ID and API_HASH from https://my.telegram.org/apps
   - BOT_TOKEN from @BotFather

2. Create a storage channel:
   - Create a new channel
   - Add bot as administrator
   - Get channel ID and update STORAGE_CHANNEL_ID in bot.py

3. Install requirements:
   - pip install -r requirements.txt

4. Run the bot:
   - python bot.py



## Usage
- `/start` - Show bot information
- `/song <song name>` - Download a song

## Requirements
- Python 3.7+
- telethon
- yt-dlp
- sqlite3

## Screenshots
[Add some screenshots of your bot in action]

## License
This project is licensed under the MIT License.

## Credits
Made with ❤️ by [Chami]

## Requirements
- Python 3.7+
- telethon
- yt-dlp
- sqlite3

telethon
yt-dlp

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Bot specific
*.session
*.session-journal
songs.db
downloads/

# Environment variables
.env