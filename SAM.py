"""
Code for SAM - version 3.0.0

This is the code for the bot in nextcord.

Author: Samuel Alex Koshy (Paradox543#3217 on Discord)
Version start date: 2022/08/25
"""
import os
from datetime import datetime, time, timedelta
from typing import cast

import nextcord
from dotenv import load_dotenv
from nextcord import Embed, TextChannel
from nextcord.ext import tasks
from nextcord.ext.commands import (
    Bot,
    Cog,
    CommandNotFound,
    Context,
    MissingRequiredArgument,
    command,
)
from nextcord.errors import Forbidden

from bot_secrets import (
    DANK_CHANNEL_ID,
    PARADOX_ID,
    SAM_CHANNEL_ID,
    SCORES_CHANNEL_ID,
    color_lamuse,
    servers,
)
from database import og_collection, time_collection, db

load_dotenv()

description = (
    "The Super Assistive Machine is the helpful bot of Countaholics"
    " that gives you roles to count if you have "
    "enough saves. It also tracks stuff like streaks, run time and "
    "many other little helpful features."
)

intents = nextcord.Intents.all()
bot = Bot(
    command_prefix="?",
    intents=intents,
    owner_id=PARADOX_ID,
    description=description,
    case_insensitive=True,
)


@bot.event
async def on_ready():
    """Declare when the bot is ready and works."""
    await bot.change_presence(activity=nextcord.Game("?help"))
    check_time.start()
    print(f"We have logged in as {bot.user}")


@bot.slash_command(guild_ids=servers)
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello")


@bot.command()
async def test(ctx: Context):
    await ctx.send("Reply")


class Vote(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def vote(self, ctx):
        """Vote for the bot"""
        msg = "Thanks for caring about the bot enough to vote for it, "
        msg += "but unfortunately since the bot is private, there is no use "
        msg += "voting for it. Thanks all the same. 🤗 😍"
        await ctx.send(msg)


@tasks.loop(seconds=0.9)
async def check_time():
    time_now = datetime.utcnow().replace(tzinfo=None)
    for cursor in time_collection.find({"time": {"$lt": time_now}}):
        user_id: int = cursor["user"]
        command: str = cursor["command"]
        dm = cursor.get("dm", False)
        if dm:
            user = bot.get_user(user_id)
            if user is None:
                user = await bot.fetch_user(user_id)
            try:
                await user.send(f"Time to {command}.")
            except Forbidden:
                time_collection.update_one(cursor, {"$set": {"dm": False}})
                continue
        else:
            channel_send_id: int = cursor.get(
                "channel",
                SCORES_CHANNEL_ID if command != "work shift" else DANK_CHANNEL_ID,
            )
            channel_send = bot.get_channel(channel_send_id)
            if not isinstance(channel_send, TextChannel):
                return
            if command == "work shift":
                command = f"</{command}:1011560371267579942>"
            await channel_send.send(f"<@{user_id}> time to {command}.")
        time_collection.delete_one(cursor)
    # if dank_collection.find_one({"time":time_now}):
    #     time_cursor = dank_collection.find({"time":time_now})
    #     dank_chnl = bot.get_channel(dank_channel)
    #     for cursor in time_cursor:
    #         user = cursor['user']
    #         command = cursor['command']
    #         await dank_chnl.send(f"<@{user}> time to {command}")
    #         dank_collection.delete_one(cursor)


@bot.event
async def on_command_error(ctx: Context, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Command is missing an argument.")
    elif isinstance(error, CommandNotFound):
        pass
    else:
        raise error


@bot.event
async def on_application_command_error(
    ctx: nextcord.Interaction, error: nextcord.errors.ApplicationError
):
    if isinstance(error, nextcord.errors.ApplicationInvokeError):
        await ctx.send("Something went wrong", ephemeral=True)
        raise error
    else:
        raise error


bot.load_extensions(
    [
        "admin",
        "list",
        "monitor",
        "reminders",
        "stats",
        "tree",
        # "utils",
    ]
)

# bot.run(os.getenv("SAM_TEST"))
bot.run(os.getenv("SAM_TOKEN"))
