import math
import os

import discord
from dice import Dice, evaluate_expression
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

    result = evaluate_expression(dice.calculate_txt)
    if result == None:
        return

    if result.is_calculate and result.is_comparative:
        send_message = (
            dice.display_txt
            + " => "
            + str(
                math.floor(result.calculate_result)
                if result.calculate_result.is_integer()
                else result.calculate_result
            )
            + " => "
            + str("成功" if result.comparative_result else "失敗")
        )
        await message.channel.send(send_message)
    elif result.is_calculate:
        send_message = (
            dice.display_txt
            + " => "
            + str(
                math.floor(result.calculate_result)
                if result.calculate_result.is_integer()
                else result.calculate_result
            )
        )
        await message.channel.send(send_message)
    elif result.is_comparative:
        send_message = (
            dice.display_txt + " => " + str("成功" if result.comparative_result else "失敗")
        )
        await message.channel.send(send_message)


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
