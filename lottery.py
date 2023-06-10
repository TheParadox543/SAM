from nextcord import Interaction, Member, slash_command
from nextcord.ext.commands import Bot, Cog

from database import lottery_collection


class Lottery(Cog):
    """Manage the lottery system for the server"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(guild_ids=[892553570208088064])
    async def lottery(self, ctx: Interaction):
        """Lottery base command"""

    @lottery.subcommand()
    async def join(self, ctx: Interaction):
        """Join the lottery"""
        user = ctx.user
        if not isinstance(user, Member):
            return

        if lottery_collection.find_one({"_id": f"{user.id}"}):
            join_msg = "You have already joined the lottery."
            lottery_collection.update_one(
                {"_id": f"{user.id}"},
                {"$set": {"name": user.name}},
            )
        else:
            lottery_collection.insert_one(
                {
                    "_id": user.id,
                    "name": user.name,
                    "odds": 1,
                    "premium": 0,
                }
            )
            # logger_lottery.info(f"{user.id} joined the lottery")
            join_msg = "You have successfully joined the lottery."
        await ctx.send(join_msg)

    @lottery.subcommand()
    async def leave(self, ctx: Interaction):
        """Leave the lottery"""
        user = ctx.user
        if not isinstance(user, Member):
            return

        # counter = find_user_by_id(user)
        if lottery_collection.find_one({"_id": f"{user.id}"}):
            lottery_collection.delete_one({"_id": f"{user.id}"})
            leave_msg = "You have left the lottery."
            # logger_lottery.info(f"{user.id} left the lottery")
        else:
            leave_msg = "You had not joined the lottery to leave it."
        await ctx.send(leave_msg)


def setup(bot: Bot):
    bot.add_cog(Lottery(bot))
