import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = '8999685837:AAGxPI_G-8lFC4zjldqzesL9-sUSDuGl55M'
bot = telebot.TeleBot(TOKEN)

user_urls = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Salom! Menga video havolasini yuboring va formatni tanlang.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith(('http://', 'https://')))
def handle_link(message):
    url = message.text
    user_urls[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_video = types.InlineKeyboardButton("🎬 Video (MP4)", callback_data="download_video")
    btn_audio = types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="download_audio")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "Qaysi formatda yuklab olishni xohlaysiz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["download_video", "download_audio"])
def process_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "Havola topilmadi. Qaytadan yuboring!")
        return

    bot.answer_callback_query(call.id, "Yuklash boshlandi...")
    status_msg = bot.send_message(chat_id, "⏳ Fayl qayta ishlanmoqda...")

    if call.data == "download_video":
        filename = f"video_{chat_id}.mp4"
        ydl_opts = {'format': 'best', 'outtmpl': filename, 'max_filesize': 50 * 1024 * 1024}
        is_audio = False
    else:
        filename = f"audio_{chat_id}.mp3"
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': filename, 'max_filesize': 50 * 1024 * 1024}
        is_audio = True

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(filename, 'rb') as file:
            if is_audio:
                bot.send_audio(chat_id, file)
            else:
                bot.send_video(chat_id, file)

        if os.path.exists(filename):
            os.remove(filename)
        
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik yuz berdi: {e}", chat_id, status_msg.message_id)

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
  
