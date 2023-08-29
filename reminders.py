from datetime import datetime, timezone
from typing import Union, Literal, cast

import nextcord
from nextcord import Embed, Interaction, SlashOption, Member
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord import utils

from bot_secrets import *
from database import (
    find_user_stats,
    track_collection,
    ogreg_help,
    og_collection,
    time_collection,
    EPOCH,
)


class TrackView(nextcord.ui.View):
    """Create a view for tracking reminders and helpers for counters."""

    def __init__(self, user: Member, *, timeout=5):
        super().__init__(timeout=timeout)
        self.user = user

    # async def on_timeout(self) -> None:
    #     for child in self.children:
    #         self.remove_item(child)
    #     await self..edit(view=self)
    #     return await super().on_timeout()

    @nextcord.ui.button(label="All reminders.", style=nextcord.ButtonStyle.green)
    async def button_all(self, button, interaction: Interaction):
        await interaction.response.send_message("Selected all reminders.")

    @nextcord.ui.button(label="All DM's available.", style=nextcord.ButtonStyle.blurple)
    async def button_dm(self, button, interaction: Interaction):
        await interaction.response.send_message("Selected all dms.")

    @nextcord.ui.button(label="No reminders", style=nextcord.ButtonStyle.red)
    async def button_none(self, button, interaction: Interaction):
        await interaction.response.send_message("Selected no reminders.")

    @nextcord.ui.select(
        placeholder="Select one of these.",
        min_values=1,
        options=[
            nextcord.SelectOption(label="One", description="Hey"),
            nextcord.SelectOption(label="Two"),
        ],
    )
    async def select_callback(self, select, interaction: Interaction):
        # self.remove_item(select)
        await interaction.response.edit_message(content=f"{select.values}", view=self)

    def update_embed(self):
        counter_post = track_collection.find_one({"_id": f"{self.user.id}"})
        # print(self.user.id)
        # print(counter_post)
        return counter_post


class Reminders(commands.Cog):
    """Register reminders for counters."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=servers)
    async def track(self, ctx: Interaction):
        if not isinstance(ctx.user, Member):
            await ctx.send("Error")
            return
        view = TrackView(ctx.user)
        embedVar = view.update_embed()
        # * This works, removes
        # * view.remove_item(view.select_callback)
        message = await ctx.response.send_message(embedVar, view=view)
        # await view.wait()
        # view.clear_items()
        # await message.edit(view=view)

    @commands.command(name="track")
    async def view_c(self, ctx: Context):
        if not isinstance(ctx.author, Member):
            await ctx.send("Error")
            return
        view = TrackView(ctx.author)
        embedVar = view.update_embed()
        message = await ctx.send(embedVar, view=view)

    @commands.command(name="ogregister", aliases=["ogreg"], help=ogreg_help)
    async def command_ogregister(self, ctx: Context, *dm):
        """Toggle for c!vote reminders as given by users."""
        user_id = ctx.author.id
        counter_post = og_collection.find_one({"_id": f"{user_id}"})
        if not isinstance(counter_post, dict):
            return
        rem = counter_post.get("reminder", False)
        dm_data = counter_post.get("dm", False)
        dm_choice = dm_data if len(dm) > 0 and dm[0].lower() == "dm" else None
        await self.ogregister(ctx, user_id, rem, dm_choice)

    @nextcord.slash_command(
        name="ogregister",
        description="Toggle reminders, either in channel or dm",
        guild_ids=servers,
    )
    async def slash_ogregister(
        self,
        ctx: Interaction,
        dm_option: bool = SlashOption(
            name="dm",
            description="Whether you want DM's",
            choices=[True, False],
            required=False,
            default=None,
        ),
    ):
        """The slash command to call ogregister."""
        if ctx.user is None:
            return
        user_id = ctx.user.id
        counter_post = find_user_stats(user_id, OG_BOT_ID)
        if not isinstance(counter_post, dict):
            await ctx.send("Could not find user")
            return
        rem: bool = counter_post.get("reminder", False)
        if dm_option == "True":
            dm = False
        elif dm_option == "False":
            dm = True
        else:
            dm = dm_option
        await self.ogregister(ctx, user_id, rem, dm)

    async def ogregister(
        self,
        ctx: Union[Context, Interaction],
        user_id: int,
        rem: bool,
        dm: Union[bool, None],
    ):
        """Set reminders for c!vote according to users."""
        if dm is not None:
            if dm is False:
                og_collection.update_one(
                    {"_id": f"{user_id}"}, {"$set": {"reminder": True, "dm": True}}
                )
                msg = f"<@{user_id}> will now get vote reminders in DM."
            else:
                og_collection.update_one({"_id": f"{user_id}"}, {"$set": {"dm": False}})
                msg = f"<@{user_id}> will not get vote reminders in DM."
        else:
            if rem:
                og_collection.update_one(
                    {"_id": f"{user_id}"}, {"$set": {"reminder": False}}
                )
                msg = f"<@{user_id}> will no longer get reminders for voting."
            else:
                og_collection.update_one(
                    {"_id": f"{user_id}"}, {"$set": {"reminder": True}}
                )
                msg = f"<@{user_id}> will now get reminders for voting."
        await ctx.send(msg)

    @commands.command(name="reminder", aliases=["rm"])
    async def command_reminders(self, ctx: Context, member: Member | None = None):
        """Shows the list of reminders set for a user."""
        user = member or cast(Member, ctx.author)
        await self.reminders(ctx, user)

    @nextcord.slash_command(name="reminders", guild_ids=servers)
    async def slash_reminders(
        self,
        ctx: Interaction,
        member: Member = SlashOption(
            description="The user whose reminders you want to check", required=False
        ),
    ):
        """Shows the list of reminders set for a user."""
        user = member or ctx.user
        await self.reminders(ctx, user)

    async def reminders(self, ctx: Union[Interaction, Context], user: Member):
        """Display the reminders of the user."""
        rem_list = time_collection.find({"user": user.id})
        msg = ""
        for item in rem_list:
            rem_time: datetime = item.get("time", EPOCH).replace(tzinfo=timezone.utc)
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
            title=f"Reminders for {user.name}", description=msg, color=color_lamuse
        )
        await ctx.send(embed=embedVar)

    # @commands.command()  # invoke_without_command=True)
    # async def dankregister(self, ctx: Context, dm: str | None = None):
    #     """Register for dank memer reminders."""
    #     user_id = ctx.author.id
    #     post = time_collection.find_one(
    #         {
    #             "user": user_id,
    #             "command": "work shift",
    #         }
    #     )
    #     if post is not None:
    #         if dm is not None:
    #             dm_data: bool = post.get("dm", False)
    #             time_collection.update_one(
    #                 {
    #                     "user": user_id,
    #                     "command": "work shift",
    #                 },
    #                 {
    #                     "$set": {
    #                         "dm": not dm_data,
    #                     }
    #                 },
    #             )
    #             if dm_data:
    #                 msg = f"<@{user_id}> will no longer get dank reminders in DM."
    #             else:
    #                 msg = f"<@{user_id}> will now get dank reminders in DM."
    #         else:
    #             time_collection.delete_one(
    #                 {
    #                     "user": user_id,
    #                     "command": "work shift",
    #                 }
    #             )
    #             msg = f"<@{user_id}> will no longer get dank reminders."
    #     else:
    #         if dm is not None:
    #             dm = True
    #             msg = f"<@{user_id}> will get dank reminders in dm."
    #         else:
    #             dm = False
    #             msg = f"<@{user_id}> will get dank reminders."
    #         time_collection.insert_one(
    #             {
    #                 "user": user_id,
    #                 "command": "work shift",
    #                 "dm": dm,
    #             }
    #         )
    #     await ctx.send(msg)


def setup(bot: commands.Bot):
    """The setup command for the cog."""
    bot.add_cog(Reminders(bot))
