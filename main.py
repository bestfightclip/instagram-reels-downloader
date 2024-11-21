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

def scrape_videos(hashtag, limit=5):
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
        print(f"⚠️ Error while scraping videos: {e}")
    return videos

def search_instagram(update: Update, context: CallbackContext):
    """
    Handles the /search command to fetch Instagram videos for a hashtag.
    """
    if not context.args:
        update.message.reply_text("❓ Usage: /search <hashtag> [limit]\nExample: /search travel 5")
        return

    hashtag = context.args[0]
    limit = int(context.args[1]) if len(context.args) > 1 else 5
    update.message.reply_text(f"🔍 Searching Instagram for up to {limit} videos with **#{hashtag}**...\nPlease wait! ⏳")

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
    """
    Main function to run the Telegram bot.
    """
    TELEGRAM_TOKEN = "7636008956:AAHjbBso-7kAw5tNtCL6wyJRer509Fr3CdQ"  # Your Telegram bot token

    login_to_instagram()  # Log in to Instagram

    application = Application.builder().token(TELEGRAM_TOKEN).build()  # Updated for v20.x

    # Register the /search command handler
    application.add_handler(CommandHandler("search", search_instagram))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
