import asyncio
from typing import Literal

import nextcord
from nextcord import Role, SlashOption, TextChannel
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Context

from bot_secrets import *
from database import *

class AdminCommands(commands.Cog, name="Admin Commands"):
    """Moderators can lock and unlock channels here."""
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name="lock")
    @admin_perms()
    async def lock_command(self, ctx:Context, 
            bot_name:Literal["og", "classic", "abc"], 
            reason:Literal["cooldown", "offline"]):
        """Locks the channel manually."""
        if bot_name == "og":
            channel:TextChannel = self.bot.get_channel(og_channel)
            role:Role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role = ctx.guild.get_role(abc_save_id)
        else:
            return
        overwrites = channel.overwrites_for(role)
        if reason == "cooldown":
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

    @commands.command(name="unlock")
    @admin_perms()
    async def unlock(self,ctx,
            bot_name:Literal['og','classic','abc']):
        """Unlocks the channels manually."""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role:Role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role:Role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role:Role = ctx.guild.get_role(abc_save_id)
        else:
            return
        overwrites = channel.overwrites_for(role)
        overwrites.update(send_messages=True)
        await channel.set_permissions(role,overwrite=overwrites)
        if ctx.channel == channel:
            await ctx.reply("Channel unlocked by moderator")
        else:
            await channel.send("Channel unlocked by moderator")
            await ctx.reply("Done")
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

    @nextcord.slash_command(name="lock", guild_ids=servers)
    @admin_perms()
    async def lock_slash(self, ctx:Interaction,
            bot_name:str = SlashOption(
                description="Bot name",
                choices=["og", "classic", "abc", "prime", "numselli"]),
            reason:str = SlashOption(
                description="Reason for locking the channel",
                choices=["cooldown","offline"])):
        """Locks the channel manually."""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role:Role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role:Role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role:Role = ctx.guild.get_role(abc_save_id)
        elif bot_name == "prime":
            channel = self.bot.get_channel(prime_channel)
            role:Role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "numselli":
            await ctx.send("Locking now")
            role:Role = ctx.guild.get_role(have_save_id)
            for channel_name in numselli_channels:
                channel_id = numselli_channels[channel_name]
                channel = self.bot.get_channel(channel_id)
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=False)
                await channel.set_permissions(role,overwrite=overwrites)
                await channel.send("Channel locked by moderator")
            return
        else:
            return
        overwrites = channel.overwrites_for(role)
        if reason == 'cooldown':
            overwrites.update(send_messages=False)
            await channel.set_permissions(role,overwrite=overwrites)
            if ctx.channel == channel:
                await ctx.send("Channel locked for cooldown for 10 minutes")
            else:
                await channel.send("Channel locked for cooldown for 10 minutes")
                await ctx.send("Done")
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
            if ctx.channel == channel:
                await ctx.send("Channel locked by moderator")
            else:
                await channel.send("Channel locked by moderator")
                await ctx.send("Done")
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

    @nextcord.slash_command(name="unlock",guild_ids=servers)
    @admin_perms()
    async def slash_unlock(self, ctx:Interaction,
            bot_name:str = SlashOption(
                description="Bot name",
                choices=["og","classic","abc","prime","numselli"])):
        """Unlocks the channels manually"""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role:Role = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role:Role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role:Role = ctx.guild.get_role(abc_save_id)
        elif bot_name == "prime":
            channel = self.bot.get_channel(prime_channel)
            role:Role = ctx.guild.get_role(countaholic_id)
        elif bot_name == "numselli":
            await ctx.send("Unlocking now")
            role:Role = ctx.guild.get_role(have_save_id)
            for channel_name in numselli_channels:
                channel_id = numselli_channels[channel_name]
                channel = self.bot.get_channel(channel_id)
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=True)
                await channel.set_permissions(role,overwrite=overwrites)
                await channel.send("Channel unlocked by moderator")
            return
        else:
            return
        overwrites = channel.overwrites_for(role)
        overwrites.update(send_messages=True)
        await channel.set_permissions(role,overwrite=overwrites)
        if ctx.channel == channel:
            await ctx.send("Channel unlocked by moderator")
        else:
            await ctx.send("Done")
            await channel.send("Channel unlocked by moderator")
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

def setup(bot:commands.Bot):
    """The setup command for the cog."""
    bot.add_cog(AdminCommands(bot))