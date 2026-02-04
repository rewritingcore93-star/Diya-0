import asyncio

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types import StreamType

import yt_dlp

from config import API_ID, API_HASH, BOT_TOKEN


# Bot client
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# User client (for VC)
user = Client(
    "user",
    api_id=API_ID,
    api_hash=API_HASH
)

call = PyTgCalls(user)


YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}


def download_audio(url):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@bot.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("🎵 VC Music Bot Ready!\nStart VC then use /play link")


@bot.on_message(filters.command("play"))
async def play(_, msg):

    if len(msg.command) < 2:
        await msg.reply("❌ Use:\n/play YouTubeLink")
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

        await msg.reply("▶️ Playing!")

    except Exception as e:
        await msg.reply(f"❌ Error:\n{e}")


async def main():

    print("VC Music Bot Running...")

    await user.start()
    await bot.start()
    await call.start()

    while True:
        await asyncio.sleep(1000)


if __name__ == "__main__":
    asyncio.run(main())
