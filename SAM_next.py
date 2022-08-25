"""
Code for SAM - version 3.0.0

This is the code for the bot in nextcord

Author: Samuel Alex Koshy (Paradox543#3217 on Discord)
Version start date: 2022/08/25
"""

import nextcord
from nextcord.ext import commands

from secrets import TOKEN

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message:nextcord.Message):
    if message.author == bot.user:
        return

    if message.channel.id == 931498728760672276:
        if message.content == "hello":
            await message.reply("Hi")

bot.run(TOKEN)