import telebot
import os
from instaloader import Instaloader, Post
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get the bot token from the .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize the bot and Instaloader
bot = telebot.TeleBot(BOT_TOKEN)
loader = Instaloader()

# Optional: Load Instagram session for authenticated access
# Replace 'your_username' with your Instagram username
try:
    loader.load_session_from_file("your_username")
except FileNotFoundError:
    print("No Instagram session file found. You may face limitations when accessing some videos.")

# Start Command
@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(
        message,
        "👋 Hello there! I’m your *Instagram Reel Downloader Bot*! 🌀\n\n"
        "📥 *Send me a link* to an Instagram Reel, and I'll download it for you.\n\n"
        "💡 *Commands you can use:*\n"
        "/start - Restart the bot\n"
        "/help - Get instructions\n"
        "/about - Learn more about this bot\n"
        "✨ Let’s get started!"
        , parse_mode="Markdown"
    )

# Help Command
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.reply_to(
        message,
        "🛠️ *How to use this bot:*\n\n"
        "1️⃣ Find an Instagram Reel you want to download.\n"
        "2️⃣ Copy the *link* of the Reel (e.g., `https://www.instagram.com/reel/...`).\n"
        "3️⃣ Paste the link here, and I'll fetch the video for you! 🚀\n\n"
        "💬 Still stuck? Let me know!"
        , parse_mode="Markdown"
    )

# About Command
@bot.message_handler(commands=['about'])
def about_message(message):
    bot.reply_to(
        message,
        "🤖 *About Me:*\n\n"
        "I’m a bot created to help you download Instagram Reels with ease! 💾\n"
        "Send me a valid Instagram Reel link, and I’ll handle the rest. 🎥\n\n"
        "✨ *Powered by:* Instaloader\n"
        "👨‍💻 *Created by:* [@notbruc](https://t.me/notbruc)"
        , parse_mode="Markdown"
    )

# Main Logic: Handle Instagram Links
@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def download_reel(message):
    url = message.text.strip()
    bot.send_chat_action(message.chat.id, "typing")  # Show "typing..." animation

    try:
        # Extract shortcode from the URL
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            bot.reply_to(message, "⚠️ *Invalid URL.* Please make sure it's a Reel link. 🤔", parse_mode="Markdown")
            return

        # Load the post using Instaloader
        post = Post.from_shortcode(loader.context, shortcode)

        # Check if the post is a video
        if post.is_video:
            video_url = post.video_url

            # Spoof browser headers to bypass 403 error
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(video_url, headers=headers, stream=True)

            if response.status_code == 200:
                # Save the video temporarily
                video_file = f"{shortcode}.mp4"
                with open(video_file, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                # Send the video back to the user
                with open(video_file, "rb") as video:
                    bot.send_video(message.chat.id, video, caption="🎬 Here’s your Reel! Enjoy! 🌟")

                # Clean up
                os.remove(video_file)
            else:
                bot.reply_to(message, "⚠️ Failed to download the video. Instagram may be blocking the request. 🛠️")
        else:
            bot.reply_to(message, "⚠️ This link does not lead to a video Reel. 🧐", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* Unable to download the Reel. Please try again later. 🛠️\n\n_Error Details:_ `{e}`", parse_mode="Markdown")

# Polling to keep the bot running
bot.polling()
