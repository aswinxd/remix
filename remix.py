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
user_files = {}  # Dictionary to store user file paths

# Function to apply effects
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
        try:
            ffmpeg.input(input_file).output(output_file, af=filters[effect]).run(overwrite_output=True)
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e}")
            return None

# Start Command
@app.on_message(filters.command("start"))
def start(_, message):
    message.reply_text("Send me a music file to edit! 🎵")

# Handle Audio Files
@app.on_message(filters.audio | filters.voice)
def handle_audio(_, message):
    file_path = message.download()  # Download the audio file
    user_id = message.chat.id
    user_files[user_id] = file_path  # Store the file path for later processing

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

# Callback for Effects
@app.on_callback_query()
def callback_query(client, query):
    effect = query.data
    user_id = query.message.chat.id

    if user_id not in user_files:
        query.answer("❌ No music file found. Please send a new file.")
        return

    input_file = user_files[user_id]
    output_file = f"{input_file}_edited.mp3"

    if not os.path.exists(input_file):
        query.answer("❌ Error: File not found. Try again.")
        return

    query.message.edit_text(f"🔄 Processing {effect}... Please wait.")

    apply_audio_effect(input_file, output_file, effect)

    if os.path.exists(output_file):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption = (f"✅ **Effect Applied:** {effect.replace('_', ' ').title()}\n"
                   f"🆔 **Requested by:** {query.from_user.first_name}\n"
                   f"📅 **Date & Time:** {now}")

        query.message.reply_audio(audio=output_file, caption=caption, thumb=THUMBNAIL_URL,
                                  reply_markup=query.message.reply_markup)  # Keeps buttons
        os.remove(output_file)
    else:
        query.message.edit_text("❌ Failed to process the audio. Try again.")


# Run the bot
app.run()
