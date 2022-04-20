import discord
from discord.ext import commands, bridge
from discord import Option
import asyncio

from secrets import *

def admin_perms():
    """To give permissions to lock and unlock channels if needed"""
    def predicate(ctx):
        return ctx.author.id==717240803789111345 or \
               ctx.author.guild_permissions.manage_channels
    return commands.check(predicate)


class AdminCommands(commands.Cog, name="Admin Commands"):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @admin_perms()
    async def lock(self,ctx,
            bot_name:Option(str,
                description="The bot that needs to be locked",
                choices=["og","classic","abc","prime","numselli"]),
            reason:Option(str,
                description="Reason for locking the channel",
                choices=["cooldown","offline"])):
        """Locks the channel manually. You need to have necessary permissions"""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role = ctx.guild.get_role(abc_save_id)
        else:
            return
        overwrites = channel.overwrites_for(role)
        if reason == 'cooldown':
            overwrites.update(send_messages=False)
            await channel.set_permissions(role,overwrite=overwrites)
            await channel.send("Channel locked for cooldown for 10 minutes")
            misc.update_one(
                {
                    "_id":"override"
                }, {
                    "$set":
                    {
                        f"{bot_name}":True
                    }
                }
            )
            await asyncio.sleep(610)
            overwrites.update(send_messages=True)
            await channel.set_permissions(role,overwrite=overwrites)
            await channel.send("Channel unlocked as cooldown is over")
            misc.update_one(
                {
                    "_id":"override"
                }, {
                    "$set":
                    {
                        f"{bot_name}":False
                    }
                }
            )
        elif reason == 'offline':
            overwrites.update(send_messages=False)
            await channel.set_permissions(role,overwrite=overwrites)
            await channel.send("Channel locked by moderator")
            misc.update_one(
                {
                    "_id":"override"
                }, {
                    "$set":
                    {
                        f"{bot_name}":True
                    }
                }
            )

    @bridge.bridge_command()
    @admin_perms()
    async def unlock(self,ctx,
            bot_name:typing.Literal['og','classic','abc']):
        """Unlocks the channels manually. You need to have necessary permissions"""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role = ctx.guild.get_role(abc_save_id)
        else:
            return
        overwrites = channel.overwrites_for(role)
        overwrites.update(send_messages=True)
        await channel.set_permissions(role,overwrite=overwrites)
        if ctx.channel == channel:
            await ctx.respond("Channel unlocked by moderator")
        else:
            await channel.send("Channel unlocked by moderator")
            await ctx.respond("Done")
        misc.update_one(
            {
                "_id":"override"
            }, {
                "$set":
                {
                    f"{bot_name}":False
                }
            }
        )
