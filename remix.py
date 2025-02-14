import os
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image


API_ID = "12799559"
API_HASH = "077254e69d93d08357f25bb5f4504580"
BOT_TOKEN = "1710500911:AAGbfJaizS8PsGAds-9ZWTSgbc3B2zTI8OI"

app = Client("music_editor", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


THUMBNAIL_URL = "https://envs.sh/ENC.jpg"

def apply_audio_effect(input_file, output_file, effect):
    filters = {
        "slow_reverb": "atempo=0.85, aecho=0.8:0.88:60:0.4",
        "fast_reverb": "atempo=1.2, aecho=0.8:0.88:60:0.4",
        "lofi": "atempo=0.85, equalizer=f=1000:t=h:width=200:g=-10",
        "bass_boost": "bass=g=10",
        "reverse": "areverse",
        "karaoke": "pan=stereo|c0=0.5*FL-0.5*FR|c1=0.5*FR-0.5*FL",
        "increase_volume": "volume=2.0"
    }
    if effect in filters:
        ffmpeg.input(input_file).output(output_file, af=filters[effect]).run(overwrite_output=True)


@app.on_message(filters.command("start"))
def start(_, message):
    message.reply_text("Send me a music file to edit! 🎵")


@app.on_message(filters.audio | filters.voice)
def handle_audio(_, message):
    buttons = [
        [InlineKeyboardButton("🎧 Slow Reverb", callback_data="slow_reverb"),
         InlineKeyboardButton("⚡ Fast Reverb", callback_data="fast_reverb")],
        [InlineKeyboardButton("🎶 Make it Lofi", callback_data="lofi"),
         InlineKeyboardButton("🔊 Bass Boost", callback_data="bass_boost")],
        [InlineKeyboardButton("🔄 Reverse Audio", callback_data="reverse"),
         InlineKeyboardButton("🎤 Karaoke Mode", callback_data="karaoke")],
        [InlineKeyboardButton("🔊 Increase Volume", callback_data="increase_volume")]
    ]
    
    message.reply_text(
        "Choose an effect to apply:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


    file_path = message.download()


    message.chat.id, file_path


@app.on_callback_query()
def callback_query(client, query):
    effect = query.data
    user_id = query.message.chat.id
    input_file = f"{user_id}.mp3"
    output_file = f"{user_id}_edited.mp3"


    apply_audio_effect(input_file, output_file, effect)


    query.message.reply_audio(audio=output_file, thumb=THUMBNAIL_URL, caption=f"Here is your {effect} version! 🎶")

    os.remove(input_file)
    os.remove(output_file)

app.run()
