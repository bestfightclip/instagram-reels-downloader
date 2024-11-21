import os
import base64
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import time

# Initialize Instaloader
insta_loader = instaloader.Instaloader()

# Instagram username
INSTAGRAM_USERNAME = "contexdogs"  # Your Instagram username

def prepare_session():
    """
    Decodes session.txt into a binary session file (session-<username>)
    if it doesn't already exist.
    """
    session_filename = f"session-{INSTAGRAM_USERNAME}"
    if not os.path.exists(session_filename):
        try:
            print("🔄 Decoding session file from session.txt...")
            with open("session.txt", "r") as encoded_file:
                encoded_data = encoded_file.read()
            with open(session_filename, "wb") as session_file:
                session_file.write(base64.b64decode(encoded_data))
            print(f"✅ Session file created: {os.path.abspath(session_filename)}")
        except Exception as e:
            print(f"⚠️ Failed to prepare session file: {e}")
            exit(1)
    else:
        print(f"✅ Session file already exists: {os.path.abspath(session_filename)}")

def login_to_instagram():
    """
    Logs in to Instagram using the decoded session file.
    """
    prepare_session()
    try:
        # Ensure the session file is in the current working directory
        session_filename = f"session-{INSTAGRAM_USERNAME}"
        session_path = os.path.abspath(session_filename)

        # Debugging: Print session path and working directory
        print(f"📂 Session path: {session_path}")
        print(f"📂 Current working directory: {os.getcwd()}")

        # Load the session directly from the absolute path
        insta_loader.load_session_from_file(INSTAGRAM_USERNAME, filename=session_path)
        print("✅ Successfully loaded Instagram session.")
    except FileNotFoundError:
        print(f"❌ Session file not found at {session_path}. Ensure 'session.txt' is deployed correctly.")
        exit(1)
    except Exception as e:
        print(f"⚠️ Failed to load session: {e}")
        exit(1)

async def scrape_by_keyword(keyword, limit=5):
    """
    Scrapes up to 'limit' Instagram videos with the given keyword in their captions.
    """
    videos = []
    try:
        # Scraping all posts in a random hashtag
        for post in insta_loader.get_posts_by_hashtag("dog"):  # Searching in a general hashtag, like "dog"
            if keyword.lower() in post.caption.lower() and post.is_video:
                videos.append(post.video_url)
                if len(videos) >= limit:
                    break
            time.sleep(2)  # Delay to prevent rate-limiting
    except Exception as e:
        print(f"⚠️ Error while scraping videos with keyword '{keyword}': {e}")
    return videos

async def scrape_videos(hashtag, limit=5):
    """
    Scrapes up to 'limit' video URLs from Instagram for a given hashtag.
    """
    videos = []
    try:
        hashtag_posts = instaloader.Hashtag.from_name(insta_loader.context, hashtag).get_posts()
        for post in hashtag_posts:
            if post.is_video:
                videos.append(post.video_url)
                if len(videos) >= limit:
                    break
            time.sleep(2)  # Delay to prevent rate-limiting
    except Exception as e:
        print(f"⚠️ Error while scraping videos for hashtag {hashtag}: {e}")
    return videos

async def search_instagram(update: Update, context: CallbackContext):
    """
    Handles the /search command to fetch Instagram videos for a hashtag or keyword.
    """
    if not context.args:
        await update.message.reply_text("❓ Usage: /search <hashtag/keyword> [limit]\nExample: /search travel 5")
        return

    query = context.args[0]  # Can be either a hashtag or a keyword
    limit = int(context.args[1]) if len(context.args) > 1 else 5

    # Check if the first argument starts with a hashtag
    if query.startswith("#"):
        # Search by hashtag
        await update.message.reply_text(f"🔍 Searching Instagram for up to {limit} videos with **#{query}**...\nPlease wait! ⏳")
        videos = await scrape_videos(query[1:], limit)  # Removing the '#' from the hashtag
    else:
        # Search by keyword in captions
        await update.message.reply_text(f"🔍 Searching Instagram for up to {limit} videos with **{query}** in captions...\nPlease wait! ⏳")
        videos = await scrape_by_keyword(query, limit)

    if not videos:
        await update.message.reply_text(f"❌ No videos found for **{query}** or Instagram blocked access!")
        return

    await update.message.reply_text(f"✅ Found **{len(videos)} video(s)** for **{query}**. Preparing to send... 📦")

    for i, video_url in enumerate(videos, start=1):
        try:
            await update.message.reply_text(f"📥 **Downloading video {i}...**")
            await update.message.reply_video(video=video_url, caption=f"🎥 **Video {i} from {query}**")
            await update.message.reply_text(f"✅ **Video {i} sent successfully!** 🎉")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error sending video {i}: {e}")

    await update.message.reply_text("🚀 All videos sent! Use /search <hashtag> to find more. 🌟")

async def help_command(update: Update, context: CallbackContext):
    """Handles the /help command."""
    await update.message.reply_text(
        "🆘 Here's a list of available commands:\n\n"
        "/search <hashtag/keyword> [limit] - Find Instagram videos for a hashtag or keyword\n"
        "/help - Show this help message"
    )

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    await update.message.reply_text("👋 Welcome to the Instagram Video Scraper bot! Use /search <hashtag/keyword> to get started.")

def main():
    """
    Main function to run the Telegram bot.
    """
    TELEGRAM_TOKEN = "7636008956:AAHjbBso-7kAw5tNtCL6wyJRer509Fr3CdQ"  # Your Telegram bot token

    login_to_instagram()  # Log in to Instagram

    application = Application.builder().token(TELEGRAM_TOKEN).build()  # Updated for v20.x

    # Register the /search, /help, and /start command handlers
    application.add_handler(CommandHandler("search", search_instagram))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start_command))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
