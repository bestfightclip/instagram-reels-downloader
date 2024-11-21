import telebot
import os
from instaloader import Instaloader, Post

# Replace with your Bot Token
BOT_TOKEN = "your_bot_token_here"
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Instaloader
loader = Instaloader()

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

            # Download video temporarily
            video_file = f"{shortcode}.mp4"
            os.system(f"wget -O {video_file} {video_url}")

            # Send the video back to the user
            with open(video_file, "rb") as video:
                bot.send_video(message.chat.id, video, caption="🎬 Here’s your Reel! Enjoy! 🌟")

            # Clean up
            os.remove(video_file)
        else:
            bot.reply_to(message, "⚠️ This link does not lead to a video Reel. 🧐", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* Unable to download the Reel. Please try again later. 🛠️\n\n_Error Details:_ `{e}`", parse_mode="Markdown")

# Polling to keep the bot running
bot.polling()
