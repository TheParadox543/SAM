import asyncio
from datetime import timedelta
from typing import Literal, Union

import nextcord
from nextcord import Permissions, Role, SlashOption, TextChannel
from nextcord import Interaction, Member
from nextcord.ext import commands
from nextcord.ext.commands import Context, Bot, Cog
from nextcord.utils import format_dt, sleep_until, utcnow

from bot_secrets import *
from database import find_run_data, misc, bot_channels, bot_role

lock_str = {True: "unlocked", False: "locked"}


async def lock_unlock_on_command(
    bot: Bot,
    ctx: Context | Interaction,
    bot_name: Member,
    lock: bool,
):
    if ctx.guild is None:
        return
    bot_id = bot_name.id
    if bot_id not in bot_channels:
        await ctx.send("There are no channels linked with this user")
        return
    role = ctx.guild.get_role(bot_role[bot_id])
    if role is None:
        await ctx.send("Could not find the role")
        return
    await ctx.send(f"Channels related to {bot_name.mention} will be {lock_str[lock]}.")
    for bot_channel in bot_channels[bot_id]:
        channel = bot.get_channel(bot_channel)
        if not isinstance(channel, TextChannel):
            await ctx.send("Could not find the channel")
            return
        overwrites = channel.overwrites_for(role)
        overwrites.update(send_messages=lock)
        await channel.set_permissions(role, overwrite=overwrites)
        if channel != ctx.channel:
            await channel.send(f"Channel {lock_str[lock]} by moderator")


class AdminCommands(Cog, name="Admin Commands"):
    """Moderators can lock and unlock channels here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="lock")
    @admin_perms()
    async def lock_command(
        self,
        ctx: Context,
        bot: Member,
    ):
        """Locks the channel manually."""
        await lock_unlock_on_command(self.bot, ctx, bot, False)

    @commands.command(name="unlock")
    @admin_perms()
    async def unlock(
        self,
        ctx: Context,
        bot: Member,
    ):
        """Unlocks the channels manually."""
        await lock_unlock_on_command(self.bot, ctx, bot, True)

    @nextcord.slash_command(
        name="lock",
        guild_ids=servers,
        default_member_permissions=Permissions(manage_channels=True),
    )
    @admin_perms()
    async def lock_slash(
        self,
        ctx: Interaction,
        bot_name: Member = SlashOption(name="bot", description="Bot name"),
    ):
        """Locks the channel manually."""
        await lock_unlock_on_command(self.bot, ctx, bot_name, False)

    @nextcord.slash_command(name="unlock", guild_ids=servers)
    @admin_perms()
    async def slash_unlock(
        self,
        ctx: Interaction,
        bot_name: Member = SlashOption(name="bot", description="Bot name"),
    ):
        """Unlocks the channels manually"""
        await lock_unlock_on_command(self.bot, ctx, bot_name, True)

    @nextcord.slash_command(
        name="cooldown",
        description="Set a channel for cooldown",
        guild_ids=servers,
        dm_permission=False,
        default_member_permissions=Permissions(manage_channels=True),
    )
    async def slash_cooldown(self, ctx: Interaction):
        """Set cooldown for channels"""
        await self.cooldown(ctx)

    @commands.command(name="cooldown", aliases=["cd"])
    @admin_perms()
    async def cmd_cooldown(self, ctx: Context):
        """Lock the channel for a cooldown."""
        await self.cooldown(ctx)

    async def cooldown(self, ctx: Union[Interaction, Context]):
        """Lock the necessary channels for cooldowns."""

        if ctx.guild is None:
            return
        channel = ctx.guild.get_channel(OG_CHANNEL_ID)
        if not isinstance(channel, TextChannel):
            return
        role = ctx.guild.get_role(OG_SAVE_ID)
        if role is None:
            return
        run_data = find_run_data(OG_CHANNEL_ID)
        if run_data is None:
            time_last = utcnow()
        else:
            time_last = run_data.time_last
        sleep = time_last + timedelta(minutes=10)
        if sleep < utcnow():
            await ctx.send("There is no need for cooldown")
            return
        overwrites = channel.overwrites_for(role)
        overwrites.send_messages = False
        await channel.set_permissions(role, overwrite=overwrites)
        await ctx.send(f"Channel is on cooldown till {format_dt(sleep, 'T')}")
        await sleep_until(sleep)
        overwrites.send_messages = True
        await channel.set_permissions(role, overwrite=overwrites)
        await channel.send("Channel is now unlocked")


def setup(bot: Bot):
    """The setup command for the cog."""
    bot.add_cog(AdminCommands(bot))
