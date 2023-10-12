import os

import discord
from dice import CalculateResult, Dice, evaluate_expression
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
    dice = Dice(message.content)
    if not dice.is_dice_roll:
        return

    calculate_result = evaluate_expression(dice.calculate_txt)
    if calculate_result == None:
        return

    if calculate_result.is_calculate and calculate_result.is_comparative:
        await message.channel.send(dice.display_txt)
    elif calculate_result.is_calculate:
        await message.channel.send(dice.display_txt)
    elif calculate_result.is_comparative:
        await message.channel.send(dice.display_txt)


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
