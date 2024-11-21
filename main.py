import os
import time
import instaloader
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Initialize Instaloader
insta_loader = instaloader.Instaloader()

# Define Instagram username for session handling
INSTAGRAM_USERNAME = "your_instagram_username"  # Replace with your username

def login_to_instagram():
    """Log in to Instagram using a saved session if available."""
    try:
        # Attempt to load the session from the file
        insta_loader.load_session_from_file(INSTAGRAM_USERNAME)
        print("✅ Successfully loaded Instagram session.")
    except FileNotFoundError:
        print("❌ No session file found. Please generate one using the `generate_session.py` script.")
        exit(1)
    except Exception as e:
        print(f"⚠️ Failed to load session: {e}")
        exit(1)

# Function to scrape videos by hashtag
def scrape_videos(hashtag, limit=5):
    """Scrape up to 'limit' video URLs for a given hashtag."""
    videos = []
    try:
        hashtag_posts = instaloader.Hashtag.from_name(insta_loader.context, hashtag).get_posts()
        for post in hashtag_posts:
            if post.is_video:
                videos.append(post.video_url)
                if len(videos) >= limit:
                    break
            time.sleep(2)  # Add a delay between requests to prevent rate limits
    except Exception as e:
        print(f"⚠️ Error while scraping videos: {e}")
    return videos

# Telegram command handler
def search_instagram(update: Update, context: CallbackContext):
    """Handles the /search command to fetch Instagram videos."""
    if not context.args:
        update.message.reply_text("❓ Usage: /search <hashtag> [limit]\nExample: /search travel 5")
        return

    hashtag = context.args[0]
    limit = int(context.args[1]) if len(context.args) > 1 else 5
    update.message.reply_text(f"🔍 Searching Instagram for up to {limit} videos with **#{hashtag}**...\nPlease hold on! ⏳")

    videos = scrape_videos(hashtag, limit)
    if not videos:
        update.message.reply_text(f"❌ No videos found for **#{hashtag}** or Instagram blocked access!")
        return

    update.message.reply_text(f"✅ Found **{len(videos)} video(s)** for **#{hashtag}**. Preparing to send... 📦")

    for i, video_url in enumerate(videos, start=1):
        try:
            update.message.reply_text(f"📥 **Downloading video {i}...**")
            update.message.reply_video(video=video_url, caption=f"🎥 **Video {i} from #{hashtag}**")
            update.message.reply_text(f"✅ **Video {i} sent successfully!** 🎉")
        except Exception as e:
            update.message.reply_text(f"⚠️ Error sending video {i}: {e}")

    update.message.reply_text("🚀 All videos sent! Use /search <hashtag> to find more. 🌟")

# Main function to run the Telegram bot
def main():
    """Main function to run the Telegram bot."""
    TELEGRAM_TOKEN = "your_telegram_bot_token"  # Replace with your bot token

    # Login to Instagram
    login_to_instagram()

    # Initialize the bot
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("search", search_instagram))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
