import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

@bot.tree.command(name="play", description="Play music")
async def play(interaction: discord.Interaction, query: str):

    if not interaction.user.voice:
        await interaction.response.send_message("Join VC first")
        return

    channel = interaction.user.voice.channel

    vc = interaction.guild.voice_client

    if vc is None:
        vc = await channel.connect()

    await interaction.response.send_message(f"Searching `{query}`")

    loop = asyncio.get_event_loop()

    data = await loop.run_in_executor(
        None,
        lambda: yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info(
            f"ytsearch:{query}",
            download=False
        )
    )

    song = data["entries"][0]
    url = song["url"]
    title = song["title"]

    if vc.is_playing():
        vc.stop()

    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)

    vc.play(source)

    await interaction.followup.send(f"Now playing: {title}")

@bot.tree.command(name="pause")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("Paused")

@bot.tree.command(name="resume")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("Resumed")

@bot.tree.command(name="skip")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("Skipped")

@bot.tree.command(name="leave")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc:
        await vc.disconnect()
        await interaction.response.send_message("Disconnected")

bot.run(TOKEN)
