import asyncio
import os
import requests

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types import StreamType

import yt_dlp

from config import BOT_TOKEN, API_ID, API_HASH


# Reset old connections
def reset_updates(token):
    url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
    requests.get(url)


reset_updates(BOT_TOKEN)


# Pyrogram Client (Bot)
app = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Voice Call Client
call = PyTgCalls(app)


YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}


def download_audio(url):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("🎵 VC Music Bot is Ready!\nUse /play <YouTube link>")


@app.on_message(filters.command("play"))
async def play(_, msg):

    if len(msg.command) < 2:
        await msg.reply("❌ Give YouTube link.\nExample:\n/play https://youtu.be/...")
        return

    url = msg.command[1]

    await msg.reply("⬇️ Downloading...")

    try:
        file = download_audio(url)

        await call.join_group_call(
            msg.chat.id,
            AudioPiped(file),
            stream_type=StreamType().pulse_stream
        )

        await msg.reply("▶️ Playing in VC!")

    except Exception as e:
        await msg.reply(f"❌ Error:\n{e}")


async def main():
    await app.start()
    await call.start()

    print("Music bot running...")

    while True:
        await asyncio.sleep(1000)


if __name__ == "__main__":
    asyncio.run(main())
