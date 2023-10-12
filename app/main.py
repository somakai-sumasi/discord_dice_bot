import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
intents = discord.Intents.all()
activity = discord.Activity(name="MyBot", type=discord.ActivityType.custom)
bot = commands.Bot(
    command_prefix="!", intents=intents, activity=activity, help_command=None
)


# bot起動時
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


# メッセージ受信時のイベント
@bot.event
async def on_message(message: discord.Message):
    ...


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
