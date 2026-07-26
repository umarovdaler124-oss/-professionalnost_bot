import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = '8999685837:AAGxPI_G-8lFC4zjldqzesL9-sUSDuGl55M'
bot = telebot.TeleBot(TOKEN)

CAPTION_TEXT = "💖 Bizning botimiz orqali yuklab olindi!"

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Salom! Instagram, TikTok yoki YouTube havolasini yuboring.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith(('http://', 'https://')))
def handle_link(message):
    chat_id = message.chat.id
    url = message.text
    
    status_msg = bot.send_message(chat_id, "⏳ Video va audio tayyorlanmoqda...")
    video_file = f"video_{chat_id}.mp4"
    audio_file = f"audio_{chat_id}.mp3"
    
    ydl_video_opts = {
        'format': 'best',
        'outtmpl': video_file,
        'max_filesize': 50 * 1024 * 1024
    }

    try:
        # 1. Videoni yuklab yuborish
        with YoutubeDL(ydl_video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video audio')
            uploader = info.get('uploader', 'Noma\'lum')

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📩 Do'stlarga ulashish", switch_inline_query=""))

        with open(video_file, 'rb') as file:
            bot.send_video(chat_id, file, caption=CAPTION_TEXT, reply_markup=markup)

        # 2. Audioni alohida MP3 qilib ajratib yuborish
        ydl_audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'max_filesize': 50 * 1024 * 1024
        }

        with YoutubeDL(ydl_audio_opts) as ydl:
            ydl.download([url])

        if os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=title, performer=uploader)

        # Tozalash
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)
        bot.edit_message_text("❌ Videoni yuklab bo'lmadi. Havolani tekshirib ko'ring.", chat_id, status_msg.message_id)

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
            
