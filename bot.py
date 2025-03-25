from telethon import TelegramClient, events
from yt_dlp import YoutubeDL
import os
from urllib.parse import quote
import sqlite3
import asyncio
import time
import re
import logging
import base64  # Add this import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace these with your own values from https://my.telegram.org/apps
API_ID = '27847998'
API_HASH = '9650c8af044f1a3e7cf4659c64ca667a'
BOT_TOKEN = '7700748885:AAEXtKxcPcX79Y1SAP7utKrRdnZpM1SQ_8I'

# Add this constant at the top with other configs
STORAGE_CHANNEL_ID = -1002413626339  # Replace with your channel ID

# Add these constants for styling
LOGO = """
🎵 𝙈𝙪𝙨𝙞𝙘 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙧 🎵
"""

HELP_TEXT = """
𝙃𝙤𝙬 𝙩𝙤 𝙪𝙨𝙚 𝙢𝙚? 🤔

1️⃣ Send /song command followed by song name
2️⃣ Wait while I search and download
3️⃣ Enjoy your music! 🎧

𝙀𝙭𝙖𝙢𝙥𝙡𝙚:
/song mage wela
/song shape of you

𝙈𝙖𝙙𝙚 𝙬𝙞 ❤️ 𝙗𝙮 @your_username
"""

SEARCHING_TEXT = """
🔍 𝙎𝙚𝙖𝙧𝙘𝙝𝙞𝙣𝙜...
𝙎𝙤𝙣𝙜: {}
"""

FOUND_IN_DB = """
✨ 𝙁𝙤𝙪𝙣𝙙 𝙞𝙣 𝙙𝙖𝙩𝙖𝙗𝙖𝙨𝙚!
𝙎𝙚𝙣𝙙𝙞𝙣𝙜 𝙣𝙤𝙬...
"""

# Update the animations with a more stylish design
DOWNLOAD_ANIMATIONS = [
    """
📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...

[□□□□□□□□□□] 0%
⚡️ 𝙎𝙥𝙚𝙚𝙙: ▰▰▰▰▰
    """,
    """
📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...

[■□□□□□□□□□] 20%
⚡️ 𝙎𝙥𝙚𝙚𝙙: ▰▰▰▱▰
    """,
    """
📥 𝘿𝙤𝙬𝙣��𝙤𝙖𝙙𝙞𝙣𝙜...

[■■■□□□□□□□] 40%
⚡️ 𝙎𝙥𝙚𝙚𝙙: ▰▰▰▱▱
    """,
    """
📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...

[■■■■■□□□□□] 60%
⚡️ 𝙎𝙥𝙚𝙚𝙙: ▰▰▱▱▱
    """,
    """
📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...

[■■■■■■■□□□] 80%
⚡️ 𝙎𝙥𝙚𝙚𝙙: ▰▱▱▱▱
    """,
    """
📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...

[■■■■■■■■■■] 100%
✅ 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙!
    """
]

# Add this new constant for caption styling
CAPTION_TEMPLATE = """
🎵 𝙎𝙤𝙣𝙜 𝙄𝙣𝙛𝙤𝙧𝙢𝙖𝙩𝙞𝙤𝙣 🎵

🎧 𝙏𝙞𝙩𝙡𝙚: {}
🎤 𝘼𝙧𝙩𝙞𝙨𝙩: {}
⌚ 𝘿𝙪𝙧𝙖𝙩𝙞𝙤𝙣: {}
👀 𝙑𝙞𝙚𝙬𝙨: {}

📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙙 𝘽𝙮: @{} 🇱🇰
"""

# Add these helper functions for formatting
def format_duration(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def format_views(count):
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    return str(count)

# Initialize the client
# Initialize the client with a new session name
bot = TelegramClient('music_bot_new', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Adding YouTube Cookies to Your Bot for Heroku Deployment

# To solve the YouTube blocking issue on Heroku, you need to add cookies to your YouTube-DL requests. This will make your requests appear as if they're coming from a logged-in browser. Here's how to implement this:

# First, Export Your YouTube Cookies

# You'll need to export cookies from a browser where you're logged into YouTube. You can use browser extensions like "Get cookies.txt" for Chrome or "Cookie Quick Manager" for Firefox to export cookies to a .txt file.

# Modify Your Code to Use Cookies

# Here's how to update your code to use cookies:

# Check if running on Heroku
is_heroku = os.environ.get('DYNO') is not None

# YouTube-DL options
# Add this near the top of your file, after the imports
import base64

ydl_opts = {
    'format': '140',  # Using specific format code for m4a audio
    'outtmpl': 'downloads/%(id)s.%(ext)s',  # Temporarily use ID, we'll rename later
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'cookiefile': 'youtube_cookies.txt',  # Add this line to use cookies
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
}

# Setup cookies for YouTube
if is_heroku:
    # Get cookies from environment variable
    cookies_b64 = os.environ.get('YOUTUBE_COOKIES')
    if cookies_b64:
        logger.info("Found YOUTUBE_COOKIES environment variable, decoding...")
        try:
            cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
            # Write cookies to a temporary file
            with open('youtube_cookies.txt', 'w') as f:
                f.write(cookies_content)
            logger.info("Successfully wrote cookies to file")
            ydl_opts['cookiefile'] = 'youtube_cookies.txt'
        except Exception as e:
            logger.error(f"Error decoding cookies: {str(e)}")
    else:
        logger.warning("No YOUTUBE_COOKIES environment variable found")
        
        # Try to use the cookies file directly if it exists
        if os.path.exists('youtube_cookies.txt'):
            logger.info("Using existing youtube_cookies.txt file")
            ydl_opts['cookiefile'] = 'youtube_cookies.txt'
        else:
            logger.warning("No cookies file found, YouTube downloads may fail")
else:
    # Local development - use cookies file directly if it exists
    if os.path.exists('youtube_cookies.txt'):
        logger.info("Using local youtube_cookies.txt file")
        ydl_opts['cookiefile'] = 'youtube_cookies.txt'
    else:
        logger.warning("No local cookies file found, YouTube downloads may fail")

# Add this function to reset the database
def reset_db():
    logger.info("Resetting database...")
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS songs')
    conn.commit()
    conn.close()
    init_db()
    logger.info("Database reset complete")

# Modify init_db to log
def init_db():
    logger.info("Initializing database...")
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs
                 (title TEXT, title_en TEXT, message_id INTEGER, file_id TEXT)''')
    conn.commit()
    conn.close()
    logger.info("Database initialization complete")

# Store song info with both titles
async def store_song(title, title_en, message_id):
    logger.info(f"Storing song: {title} ({title_en})")
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('INSERT INTO songs VALUES (?,?,?,?)', (title, title_en, message_id, None))
    conn.commit()
    conn.close()
    logger.info("Song stored successfully")

# Modified find_song function to search both titles
def find_song(query):
    logger.info(f"Searching for song: {query}")
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT title, title_en, message_id FROM songs')
        all_songs = c.fetchall()
        logger.info(f"Found {len(all_songs)} songs in database")
    except sqlite3.OperationalError as e:
        logger.error(f"Database error: {e}")
        all_songs = []
    conn.close()

    # Clean search query
    clean_query = query.lower().strip()
    
    # First try exact match on both titles
    for title, title_en, message_id in all_songs:
        if (clean_query == title.lower().strip() or 
            clean_query == title_en.lower().strip()):
            return message_id
            
    # Then try partial match on both titles
    for title, title_en, message_id in all_songs:
        if (clean_query in title.lower().strip() or 
            clean_query in title_en.lower().strip()):
            return message_id
            
    return None

# Update the progress animation function
async def progress_animation(message):
    """Shows an animated progress indicator"""
    current = 0
    while True:
        try:
            await message.edit(DOWNLOAD_ANIMATIONS[current])
            current = (current + 1) % (len(DOWNLOAD_ANIMATIONS) - 1)  # Don't loop back to start
            await asyncio.sleep(1)  # Slower animation for better visibility
        except:
            break

# Update the start handler
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply(LOGO + HELP_TEXT)

@bot.on(events.NewMessage(pattern='/song'))
async def download_song(event):
    try:
        query = event.raw_text.split('/song', 1)[1].strip()
        
        if not query:
            await event.reply('Please provide a song name. Usage: /song <song name>')
            return

        processing_msg = await event.reply(
            SEARCHING_TEXT.format(query)
        )

        try:
            # Check if song exists in database
            message_id = find_song(query)
            if message_id:
                stored_message = await bot.get_messages(STORAGE_CHANNEL_ID, ids=message_id)
                if stored_message and stored_message.audio:
                    await processing_msg.edit(FOUND_IN_DB)
                    await stored_message.forward_to(event.chat_id)
                    await processing_msg.delete()
                    return

            # If song not found, download it
            with YoutubeDL(ydl_opts) as ydl:
                # Search for the video
                search_query = f"ytsearch1:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info

                # Start download animation
                progress_task = asyncio.create_task(progress_animation(processing_msg))
                await asyncio.sleep(0.5)  # Small delay to ensure animation starts

                try:
                    # Create downloads directory if it doesn't exist
                    if not os.path.exists('downloads'):
                        os.makedirs('downloads')
                        
                    # Download the song
                    await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: ydl.download([f"https://www.youtube.com/watch?v={video['id']}"])
                    )
                finally:
                    progress_task.cancel()

                # Create safe filename from title
                safe_title = sanitize_filename(video['title'])
                safe_filename = f"downloads/{safe_title}.m4a"

                # Rename the downloaded file
                old_path = f"downloads/{video['id']}.m4a"
                try:
                    os.rename(old_path, safe_filename)
                except:
                    safe_filename = old_path  # Fallback to ID-based filename if rename fails

                # Format duration
                duration_seconds = int(video.get('duration', 0))  # Convert to integer
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                duration_str = f"{minutes}:{seconds:02d}"

                # Format view count
                view_count = video.get('view_count', 0)
                view_count_str = f"{view_count:,}"

                # Create styled caption
                caption = CAPTION_TEMPLATE.format(
                    video['title'],
                    video.get('uploader', '𝙐𝙣𝙠𝙣𝙤𝙬𝙣'),
                    format_duration(video.get('duration', 0)),
                    format_views(video.get('view_count', 0)),
                    (await bot.get_me()).username
                )

                # Use safe filename for sending with progress
                await processing_msg.edit("📤 𝙋𝙧𝙚𝙥𝙖𝙧𝙞𝙣𝙜 𝙩𝙤 𝙪𝙥𝙡𝙤𝙖𝙙...")
                
                sent_message = await bot.send_file(
                    event.chat_id,
                    safe_filename,
                    caption=caption,
                    supports_streaming=True,
                    progress_callback=lambda current, total: asyncio.create_task(
                        upload_progress_callback(current, total, processing_msg)
                    )
                )

                # Forward to storage channel and store info in database
                stored_msg = await sent_message.forward_to(STORAGE_CHANNEL_ID)
                # Store both Sinhala and English/Romanized titles
                await store_song(
                    video['title'],  # Original title (Sinhala)
                    "mage wela",     # English/Romanized version - you'll need to map this
                    stored_msg.id
                )

                await processing_msg.delete()
                os.remove(safe_filename)  # Remove using safe filename

        except Exception as e:
            # Make sure to cancel any running progress animation
            try:
                progress_task.cancel()
            except:
                pass
            await processing_msg.edit(
                f"❌ 𝙀𝙧𝙧𝙨𝙧: 𝘾𝙤𝙪𝙡𝙙 𝙣𝙤𝙩 𝙙𝙤𝙬𝙣𝙡𝙤𝙖𝙙 𝙨𝙚𝙡𝙚 𝙨𝙜𝙚𝙡.\n𝙋𝙡𝙚𝙖𝙨 𝙩𝙧𝙮 𝙖𝙜𝙖𝙞𝙣."
            )

    except Exception as e:
        await event.reply('❌ An error occurred. Please try again.')
        print(f"Error: {str(e)}")

def sanitize_filename(title):
    """Convert title to safe filename by removing/replacing problematic characters"""
    # Replace invalid characters with underscore
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Remove emojis and special characters but keep unicode letters (like Sinhala)
    safe_name = ''.join(c for c in safe_name if c.isprintable())
    # Limit filename length
    safe_name = safe_name[:100]
    return safe_name.strip()

# Add these new animation constants
UPLOAD_ANIMATIONS = [
    """
📤 𝙐𝙥𝙡𝙤𝙖𝙙𝙞𝙣𝙜 𝙩𝙤 𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢...

[□□□□□□□□□□] 0%
📶 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: 0/{} MB
    """,
    """
📤 𝙐𝙥𝙡𝙤𝙖𝙙𝙞𝙣𝙜 𝙩𝙤 𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢...

[■■□□□□□□□□] 20%
📶 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: {:.1f}/{} MB
    """,
    # ... other states ...
]

# Add upload progress callback
async def upload_progress_callback(current, total, message):
    try:
        percent = int((current * 100) / total)
        current_mb = current / 1024 / 1024
        total_mb = total / 1024 / 1024
        
        progress_bar = "■" * int(percent/10) + "□" * (10 - int(percent/10))
        
        await message.edit(
            f"""
📤 𝙐𝙥𝙡𝙤𝙖𝙙𝙞𝙣𝙜 𝙩𝙤 𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢...

[{progress_bar}] {percent}%
📶 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: {current_mb:.1f}/{total_mb:.1f} MB
            """
        )
    except:
        pass

# Initialize database when bot starts
reset_db()  # Comment this out after first run
init_db()
print("Bot is running...")
bot.run_until_disconnected()