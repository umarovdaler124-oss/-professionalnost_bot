import os
import asyncio
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from shazamio import Shazam

TOKEN = '8999685837:AAGxPI_G-8lFC4zjldqzesL9-sUSDuGl55M'
bot = telebot.TeleBot(TOKEN)

async def recognize_song(filename):
    shazam = Shazam()
    out = await shazam.recognize(filename)
    return out

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Salom! Menga Instagram, TikTok yoki YouTube havolasini yuboring.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith(('http://', 'https://')))
def handle_link(message):
    chat_id = message.chat.id
    url = message.text
    
    status_msg = bot.send_message(chat_id, "⏳ Video va qo'shiq qayta ishlanmoqda...")
    video_file = f"video_{chat_id}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_file,
        'max_filesize': 50 * 1024 * 1024
    }

    try:
        # 1. Videoni yuklab olish
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 2. Videoni foydalanuvchiga yuborish
        with open(video_file, 'rb') as file:
            bot.send_video(chat_id, file, caption="🎥 Videongiz tayyor!")

        # 3. Videodagi qo'shiqni tanish (Shazam)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        shazam_result = loop.run_until_complete(recognize_song(video_file))

        # Agar qo'shiq topilsa:
        if shazam_result and 'track' in shazam_result:
            track = shazam_result['track']
            title = track.get('title', 'Noma\'lum')
            subtitle = track.get('subtitle', 'Noma\'lum')
            query = f"{subtitle} - {title}"

            bot.send_message(chat_id, f"🎵 **Topilgan qo'shiq:** {query}\n⏳ To'liq MP3 shakli yuklanmoqda...")

            # 4. To'liq MP3 versiyasini YouTube'dan qidirib yuklash
            audio_file = f"audio_{chat_id}.mp3"
            ydl_audio_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_file,
                'default_search': 'ytsearch1',
                'max_filesize': 50 * 1024 * 1024
            }

            with YoutubeDL(ydl_audio_opts) as ydl:
                ydl.download([query])

            # MP3 ni yuborish
            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=title, performer=subtitle)

            if os.path.exists(audio_file):
                os.remove(audio_file)

        # Vaqtinchalik faylni o'chirish
        if os.path.exists(video_file):
            os.remove(video_file)
            
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        if os.path.exists(video_file):
            os.remove(video_file)
        bot.edit_message_text("❌ Videoni yuklashda yoki qo'shiqni topishda xatolik bo'ldi.", chat_id, status_msg.message_id)

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
            
