import os
import instaloader
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Initialize Instaloader
insta_loader = instaloader.Instaloader()

# Use environment variables for credentials
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Login function with session support
def login_to_instagram():
    """Log in to Instagram, using a saved session if available."""
    try:
        # Attempt to load an existing session
        insta_loader.load_session_from_file(INSTAGRAM_USERNAME)
        print("✅ Successfully loaded Instagram session.")
    except FileNotFoundError:
        # If no session exists, log in with credentials
        print("🔑 No session found. Logging in with credentials...")
        insta_loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        insta_loader.save_session_to_file()
        print("✅ Logged in and saved session.")

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

def main():
    """Main function to run the Telegram bot."""
    TELEGRAM_TOKEN = "7636008956:AAHjbBso-7kAw5tNtCL6wyJRer509Fr3CdQ"  # Bot token

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
