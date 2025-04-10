import os
import telebot
from pydub import AudioSegment
import speech_recognition as sr

API_TOKEN = "your telegram bot token here"
bot = telebot.TeleBot(API_TOKEN)

# directory for storing uploaded files
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    try:
        # getting the file_id of the voice message
        file_info = bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        
        # download the file
        downloaded_file = bot.download_file(file_path)
        ogg_file_path = os.path.join(DOWNLOAD_DIR, f"{message.from_user.id}.ogg")
        
        # saving the file locally
        with open(ogg_file_path, "wb") as f:
            f.write(downloaded_file)
        
        # converting OGG to WAV
        wav_file_path = os.path.join(DOWNLOAD_DIR, f"{message.from_user.id}.wav")
        AudioSegment.from_file(ogg_file_path).export(wav_file_path, format="wav")
        
        # text recognition (not always good)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-EN") # specify language
        
        # sending the text to the user
        bot.reply_to(message, f"Recognized text: {text}")
        
        # deleting temporary files
        os.remove(ogg_file_path)
        os.remove(wav_file_path)
    except Exception as e:
        bot.reply_to(message, f"Couldn't process voice message: {e}")

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me a voice message and I'll translate it into text.")

# запуск бота
bot.polling()