"""
Code for SAM - version 3.0.0

This is the code for the bot in nextcord

Author: Samuel Alex Koshy (Paradox543#3217 on Discord)
Version start date: 2022/08/25
"""

import nextcord
from nextcord.ext import commands

import bot_secrets

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("!!testing"):
            await message.channel.send("Test success")

@bot.command()
async def test(ctx):
    print("test")
    await ctx.reply("Pong!")

@bot.slash_command(guild_ids=[892553570208088064])
async def test(ctx):
    print("Hey")
    await ctx.send("Hey")

@bot.event
async def on_message(message:nextcord.Message):
    if message.author == bot.user:
        return

    content = message.content

    if content.startswith("!!"):
        if content[2:].startswith("hello"):
            print("Hi")
            await message.channel.send("Hi")

    if message.channel.id == 931498728760672276:
        if message.content == "hello":
            await message.reply("Hi")

bot.add_cog(Test(bot))

bot.run(bot_secrets.BOT_TEST)