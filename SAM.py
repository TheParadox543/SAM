from datetime import datetime, time, timedelta
import requests

import nextcord
from nextcord import Embed, TextChannel
from nextcord.ext import commands, tasks
from nextcord.ext.commands.core import Context

from bot_secrets import *
from database import *

descr = "The Super Assistive Machine gives you roles to count if you have "
descr += "enough saves. It also tracks stuff like streaks, run time and "
descr += "many other little helpful features."

intents = nextcord.Intents.all()
"""Creating object of the bot"""
bot = commands.Bot(
    command_prefix=("?"),
    case_insensitive=True,
    strip_after_prefix=True,
    owner_id=paradox_id,
    intents=intents,
    description=descr,
)

@bot.event
async def on_ready():
    """To log when the bot is ready for use"""
    await bot.change_presence(activity=nextcord.Game("?help"))
    check_time.start()
    daily.start()
    print(f"We have logged in as {bot.user}")

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vote(self, ctx):
        """Vote for the bot"""
        msg = "Thanks for caring about the bot enough to vote for it, "
        msg += "but unfortunately since the bot is private, there is no use "
        msg += "voting for it. Thanks all the same. 🤗 😍"
        await ctx.send(msg)

@tasks.loop(seconds=0.9)
async def check_time():
    time_now = datetime.utcnow().replace(tzinfo=None, microsecond=0)
    if time_collection.find_one({"time":time_now}):
        time_cursor = time_collection.find({"time":time_now})
        for cursor in time_cursor:
            user_id:int = cursor["user"]
            command:str = cursor["command"]
            dm = cursor.get("dm", False)
            if dm:
                user = bot.get_user(user_id)
                if user is None:
                    user = await bot.fetch_user(user_id)
                await user.send(f"Time to {command}.")
            else:
                channel_send_id:int = cursor.get("channel", 
                    scores_channel if command != "work shift" else dank_channel)
                channel_send:TextChannel = bot.get_channel(channel_send_id)
                if command == "work shift":
                    command = f"</{command}:1011560371267579942>"
                await channel_send.send(f"<@{user_id}> time to {command}.")

@tasks.loop(time=time(hour=23,minute=59,second=59,tzinfo=None))
async def daily():
    time = datetime.utcnow().isoformat()[:10]
    cursor = og_collection.find({
            "daily":{
                "$gte": 1
            }
        }, {
            "name": 1,
            "daily": 1,
        }
    ).sort("daily", -1)
    msg = "Total numbers counted today: <!@#TOTALCOUNTED!@#>"
    total = 0
    i = 0
    for user in cursor:
        i += 1 
        name = user.get("name", "Unknown")
        daily = user.get("daily", ">1")
        try:
            total += int(daily)
        except:
            pass
        msg += f"\n{i}. {name} - {daily}"
    msg = msg.replace("<!@#TOTALCOUNTED!@#>", str(total), 1)
    embedVar = Embed(title=f"{time}", description=msg, color=color_lamuse)
    scores:TextChannel = bot.get_channel(sam_channel)
    await scores.send(embed=embedVar)
    og_collection.update_many({
            "daily": {
                "$gte": 1
            }
        }, {
            "$set": {
                "daily": 0
            }
        }
    )

@bot.event
async def on_command_error(ctx:Context, error):
    if isinstance(error, commands.MissingPermissions):
        msg = "You do not have the required permissions to use this command"
        await ctx.reply(msg)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Command is missing an argument")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("You don't have the required permissions. ")
    elif isinstance(error, commands.BadLiteralArgument):
        await ctx.reply("Not a valid choice")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MemberNotFound):
        await ctx.reply("Member not found")
    else:
        raise error

@bot.event
async def on_application_command_error(ctx:nextcord.Interaction, 
        error:nextcord.errors.ApplicationError):
    if isinstance(error, nextcord.errors.ApplicationInvokeError):
        ctx.send("Something went wrong", ephemeral=True)
    else:
        raise error

r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

bot.load_extensions([
    "admincommands",
    "list",
    "monitor",
    "reminders",
    "stats",
    "utils",
])
bot.add_cog(Vote(bot))

bot.run(BOT_TOKEN)