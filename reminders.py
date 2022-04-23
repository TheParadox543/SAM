import discord 
from discord import Embed, Option, Member as dMember
from discord.ext import commands
from datetime import datetime

from bot_secrets import *
from database import *

epoch_time = datetime(1970, 1, 1, tzinfo=None)

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def ogregister(self,ctx):
        """Register for c!vote reminders"""
        register_list = misc.find_one({"_id":"ogregister"})
        userID = ctx.author.id
        if f"{userID}" not in register_list \
                or register_list[f"{userID}"] == False:
            misc.update_one(
                {
                    "_id":"ogregister"
                }, {
                    "$set":
                    {
                        f"{userID}":True
                    }
                }
            )
            msg = f"<@{userID}> is now registered for getting reminders for voting"
            await ctx.send(msg)
        else:
            misc.update_one(
                {
                    "_id":"ogregister"
                }, {
                    "$set":
                    {
                        f"{userID}":False
                    }
                }
            )
            msg = f"<@{userID}> will not get reminders for voting"
            await ctx.send(msg)

    @ogregister.command(name="set")
    @admin_perms()
    async def ogreg_set(self,ctx,user:dMember):
        """Register for c!vote reminders"""
        register_list = misc.find_one({"_id":"ogregister"})
        userID = user.id
        if f"{userID}" not in register_list or register_list[f"{userID}"] == False:
            misc.update_one(
                {
                    "_id":"ogregister"
                }, {
                    "$set":
                    {
                        f"{userID}":True
                    }
                }
            )
            msg = f"<@{userID}> is now registered for getting reminders for voting"
            await ctx.send(msg)
        else:
            misc.update_one(
                {
                    "_id":"ogregister"
                }, {
                    "$set":
                    {
                        f"{userID}":False
                    }
                }
            )
            msg = f"<@{userID}> will not get reminders for voting"
            await ctx.send(msg)

    @commands.command(aliases=['reminder','rm'])
    async def reminders(self, ctx, member:dMember=None):
        """Shows the list of reminders the bot has for a user"""
        user = member or ctx.author
        rem_list = time_collection.find({"user":user.id})
        msg = ""
        time_now = datetime.utcnow().replace(microsecond=0)
        for item in rem_list:
            time_diff = item['time'] - time_now
            time_diff = int(time_diff.total_seconds())
            if time_diff > 0:
                total_seconds = int((item['time'] - epoch_time).total_seconds())
                msg += f"{item['command']} - <t:{total_seconds}:R>\n"
        if msg == "":
            msg = "No reminders have been set"
        embedVar = Embed(
            title=f"Reminders for {user}",
            description=msg,
            color=color_lamuse
        )
        await ctx.send(embed=embedVar)

    @discord.slash_command(name="reminders", guild_ids=servers)
    async def slash_reminders(self, ctx, 
            member:Option(dMember,
                description="The user whose reminders you want to check")=None):
        """Shows the list of reminders the bot has for a user"""
        user = member or ctx.author
        rem_list = time_collection.find({"user":user.id})
        msg = ""
        time_now = datetime.utcnow().replace(microsecond=0)
        for item in rem_list:
            time_diff = item['time'] - time_now
            time_diff = int(time_diff.total_seconds())
            if time_diff > 0:
                total_seconds = int((item['time'] - epoch_time).total_seconds())
                msg += f"{item['command']} - <t:{total_seconds}:R>\n"
        if msg == "":
            msg = "No reminders have been set"
        embedVar = Embed(
            title=f"Reminders for {user}",
            description=msg,
            color=color_lamuse
        )
        await ctx.respond(embed=embedVar)

    @commands.command()#invoke_without_command=True)
    async def dankregister(self,ctx):
        """Register for dank memer reminders"""
        register_list = dank_collection.find_one({"_id":"register"})
        userID = ctx.author.id
        if f"{userID}" not in register_list or register_list[f"{userID}"] == False:
            dank_collection.update_one(
                {
                    "_id":"register"
                }, {
                    "$set":
                    {
                        f"{userID}":True
                    }
                }
            )
            msg = f"<@{userID}> is now registered for getting reminders in dank memer"
            await ctx.send(msg)
        else:
            dank_collection.update_one(
                {
                    "_id":"register"
                }, {
                    "$set":
                    {
                        f"{userID}":False
                    }
                }
            )
            msg = f"<@{userID}> will not get reminders in dank memer"
            await ctx.send(msg)

def setup(bot:commands.Bot):
    bot.add_cog(Reminders(bot))