import math

import nextcord
from nextcord import SlashOption, Interaction
from nextcord.ext import commands

from bot_secrets import *


class Utils(commands.Cog):
    """A few util functions."""

    def __init__(self, bot: commands.Bot):
        """Initialize the cog."""
        self.bot = bot

    # @nextcord.slash_command(name="prime", guild_ids=servers)
    # async def slash_prime(
    #     self, ctx: Interaction, number: int = SlashOption(description="The last number")
    # ):
    #     """Gives the next prime number"""

    #     def prime(num: int):
    #         f = False
    #         for i in range(3, int(math.sqrt(num)) + 1, 2):
    #             if num % i == 0:
    #                 f = True
    #         return f

    #     def next_prime(num: int):
    #         f = True
    #         while f:
    #             if num > 2:
    #                 num += 2
    #             else:
    #                 num += 1
    #             f = prime(num)
    #         return num

    #     if number == 2 or (number > 2 and number % 2 == 1):
    #         next_num = next_prime(number)
    #     else:
    #         next_num = next_prime(number - 1)
    #     await ctx.send(f"`{next_num} is the next prime after {number}`", ephemeral=True)

    # @commands.command(name="prime")
    # async def cmd_prime(self, ctx, number: int):
    #     """Gives the next prime number"""

    #     def prime(num: int):
    #         f = False
    #         for i in range(3, int(math.sqrt(num)) + 1, 2):
    #             if num % i == 0:
    #                 f = True
    #         return f

    #     def next_prime(num: int):
    #         f = True
    #         while f:
    #             if num > 2:
    #                 num += 2
    #             else:
    #                 num += 1
    #             f = prime(num)
    #         return num

    #     if number == 2 or (number > 2 and number % 2 == 1):
    #         next_num = next_prime(number)
    #     else:
    #         next_num = next_prime(number - 1)
    #     await ctx.send(f"`{next_num} is the next prime after {number}`")


def setup(bot):
    """The setup command for the cog."""
    bot.add_cog(Utils(bot))
