from datetime import datetime, timezone
from typing import Union

import nextcord 
from nextcord import Embed, Interaction, Member, SlashOption
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord import utils

from bot_secrets import *
from database import *

class Reminders(commands.Cog):
    """Register reminders for counters."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ogregister", aliases=["ogreg"], help=ogreg_help)
    async def command_ogregister(self, ctx:Context, *dm):
        """Toggle for c!vote reminders as given by users."""
        user_id = ctx.author.id
        counter_post:dict[str, bool] = og_collection.find_one({"_id": user_id})
        rem = counter_post.get("reminder", False)
        dm_data = counter_post.get("dm", False)
        dm_choice = dm_data if len(dm) > 0 and dm[0].lower() == "dm" else None
        await self.ogregister(ctx, user_id, rem, dm_choice)

    @nextcord.slash_command(name="ogregister", 
        description="Toggle reminders, either in channel or dm",
        guild_ids=servers)
    async def slash_ogregister(self, ctx:Interaction, 
            dm_option:str = SlashOption(name="dm", 
                description="Whether you want DM's",
                choices=["True", "False"],
                required=False,
                default=None)
    ):
        """The slash command to call ogregister."""
        user_id = ctx.user.id
        counter_post:dict[str, bool] = og_collection.find_one({"_id": user_id})
        rem:bool = counter_post.get("reminder", False)
        if dm_option == "True":
            dm = False
        elif dm_option == "False":
            dm = True
        else:
            dm = dm_option
        await self.ogregister(ctx, user_id, rem, dm)

    async def ogregister(self, ctx:Union[Context, Interaction], user_id:int, 
            rem:bool, dm:Union[bool, None]):
        """Set reminders for c!vote according to users."""
        if dm is not None:
            if dm is False:
                og_collection.update_one({"_id": user_id},
                    {"$set": {
                        "reminder": True,
                        "dm": True
                    }
                })
                msg = f"<@{user_id}> will now get vote reminders in DM."
            else:
                og_collection.update_one({"_id": user_id},
                    {"$set": {"dm": False}})
                msg = f"<@{user_id}> will not get vote reminders in DM."
        else:
            if rem:
                og_collection.update_one({"_id": user_id}, 
                    {"$set": {"reminder": False}})
                msg = f"<@{user_id}> will no longer get reminders for voting."
            else:
                og_collection.update_one({"_id": user_id},
                    {"$set": {"reminder": True}})
                msg = f"<@{user_id}> will now get reminders for voting."
        await ctx.send(msg)

    @commands.command(name="reminder", aliases=["rm"])
    async def command_reminders(self, ctx:Context, member:Member=None):
        """Shows the list of reminders set for a user."""
        user = member or ctx.author
        await self.reminders(ctx, user)

    @nextcord.slash_command(name="reminders", guild_ids=servers)
    async def slash_reminders(self, ctx:Interaction, 
            member:Member = SlashOption(
                description="The user whose reminders you want to check",
                required=False)
    ):
        """Shows the list of reminders set for a user."""
        user = member or ctx.user
        await self.reminders(ctx, user)

    async def reminders(self, ctx:Union[Interaction, Context], user:Member):
        """Display the reminders of the user."""
        rem_list = time_collection.find({"user":user.id})
        msg = ""
        for item in rem_list:
            rem_time:datetime = item["time"].replace(tzinfo=timezone.utc)
            dm = item.get("dm", False)
            if utils.compute_timedelta(rem_time):
                time_str = utils.format_dt(rem_time, "R")
                if dm:
                    msg += f"{item['command']}[DM] - {time_str}\n"
                else:
                    msg += f"{item['command']} - {time_str}\n"
        if msg == "":
            msg = "No reminders have been set"
        embedVar = Embed(
            title=f"Reminders for {user}",
            description=msg,
            color=color_lamuse
        )
        await ctx.send(embed=embedVar)

    @commands.command()#invoke_without_command=True)
    async def dankregister(self, ctx:Context):
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