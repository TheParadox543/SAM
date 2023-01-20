import decimal
from decimal import Decimal, ROUND_UP
from typing import Literal, Union

import nextcord
from nextcord import Button, ButtonStyle, Embed, Interaction, Member, SlashOption
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.ui import View

from bot_secrets import *
from database import *
from dicttypes import *

alt_start_msg = "So {alt}, you want to transfer your streaks to {main}. Well, that's cool. Although keep in mind that only from this point onwards do I track that you are an alt of {main}. This means that your current streak will not be added to your main, neither will your streak be saved anywhere else. \n\nRed button means that your streaks have already been transferred to someone else.\nGreen button means you have already transferred streaks to the {main}.\nGrey means no streaks have been transferred."

class Stats(commands.Cog):
    """The cog containing the commnds to check the stats of the user."""

    def __init__(self, bot:commands.Bot):
        """Initialize the cog."""
        self.bot = bot
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

    @nextcord.slash_command(guild_ids=servers)
    async def id(self, ctx:Context, user:Member):
        """Gives a user's id without pinging them"""
        await ctx.send(f"{user.id}")

    @commands.command(name="user", aliases=['u'])
    async def user_command(self, ctx:Context, member:Member=None):
        """Displays user stats in the guild"""
        user = member or ctx.author
        embedVar = Embed(title=f"User stats for {user}", color=color_lamuse)
        embedVar.set_thumbnail(url=user.display_avatar)
        user_post = og_collection.find_one({"_id":user.id})
        if user_post is not None:
            correct = user_post.get("correct", 0)
            wrong = user_post.get("wrong", 0)
            total = correct + wrong
            daily = user_post.get("daily", 0)
            streak = user_post.get("streak", 0)
            high = user_post.get("high", 0)
            total_saves = user_post.get("total_saves", 3)
            if total == 0:
                rate = 0
            else:
                rate = round(float(correct/total)*100,3)
            current_saves = user_post["current_saves"]
            if current_saves == int(current_saves):
                current_saves = int(current_saves)
            else:
                current_saves = round(current_saves,2)
            msg = f"Rate: {rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\nSaves: {current_saves}/{total_saves}"
            msg += f"\n\nCurrent Streak: {streak}"
            msg += f"\nHighest Streak: {high}"
            msg += f"\nDaily: {daily}" 
            msg += "\n`c!user`"
            embedVar.add_field(name=mode_list["1"], value=msg)
        user_post = classic_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            streak = user_post.get("streak", 0)
            high = user_post.get("high", 0)
            if total == 0:
                rate = 0
            else:
                rate = correct/total*100
                str_rate = str(rate)[:6]
            msg = f"Rate: {str_rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\n\n\nCurrent Streak: {streak}"
            msg += f"\nHighest Streak: {high}"
            msg += "\n\n</stats user:1002372595754217554>"
            embedVar.add_field(name=mode_list["2"], value=msg)
        user_post = beta_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post.get("correct", 0)
            wrong = user_post.get('wrong', 0)
            total = correct + wrong
            streak = user_post.get("streak", 0)
            high = user_post.get("high", 0)
            if total == 0:
                rate = 0
            else:
                rate = round(float(correct/total)*100,2)
            current_saves = user_post.get('current_saves', 0)
            if current_saves == int(current_saves):
                current_saves = int(current_saves)
            else:
                current_saves = round(current_saves, 2)
            total_saves = user_post.get("total_saves", 5)
            msg = f"Rate: {rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\nSaves: {current_saves}/{total_saves}"
            msg += f"\n\nCurrent Streak: {streak}"
            msg += f"\nHighest Streak: {high}"
            msg += f"\n\n`abc?u`"
            embedVar.add_field(name=mode_list["4"], value=msg)
        user_post = numselli_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            if total == 0:
                rate = 0
            else:
                rate = round(float(correct/total)*100,2)
            current_saves = user_post['current_saves']
            if current_saves == int(current_saves):
                current_saves = int(current_saves)
            else:
                current_saves = round(current_saves,2)
            msg = f"Rate: {rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\nSaves: {current_saves}/{user_post.get('total_saves', 2)}"
            msg += f"\n\nCurrent Streak: {user_post.get('streak', 0)}"
            msg += f"\nHighest Streak: {user_post.get('high', 0)}"
            msg += "\n\n</user:918251622059098182>"
            embedVar.add_field(name=mode_list["5"], value=msg)
        await ctx.send(embed=embedVar)

    @commands.command(name="currentscore", aliases=["cs"])
    async def currentscore_command(self, ctx:Context,
            mode:Literal["og", "classic", "numselli"]="og",
            page:int=1):
        """Shows the streak currentscores"""
        i = (page-1) * 10
        msg = ""
        if mode == "og":
            counter_cursor = og_collection.find(
                {
                    "streak":
                    {
                        "$gte":1
                    }
                }, {
                    'name':1,
                    'streak':1,
                    '_id':0
                }
            ).sort("streak",-1).skip(i).limit(10)
            title_msg = "Current streaks for og counting"
        elif mode == "classic":
            counter_cursor = classic_collection.find(
                {
                    "streak":
                    {
                        "$gte":1
                    }
                }, {
                    'name':1,
                    'streak':1,
                    '_id':0
                }
            ).sort("streak",-1).skip(i).limit(10)
            title_msg = "Current streaks for classic counting"
        elif mode == "numselli":
            counter_cursor = numselli_collection.find(
                {
                    "streak":
                    {
                        "$gte":1
                    }
                }, {
                    "name":1,
                    "streak":1,
                    "_id":0
                }
            ).sort("streak",-1).skip(i).limit(10)
            title_msg = "Current Streaks for numselli counting"
        else:
            return
        for counter in counter_cursor:
            i+=1
            name = counter.get('name',"Unknown")
            streak = counter.get('streak',0)
            msg += f"{i}. {name} - {streak}\n"
        if msg!="":
            embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
            embedVar.set_footer(text=f"Page: {page}")
            await ctx.send(embed=embedVar)
        else:
            return

    @nextcord.slash_command(name="currentscore",guild_ids=servers)
    async def currentscore_slash(self, ctx:Interaction,
            mode:str = SlashOption(
                description="Leaderboard mode",
                choices=["og","classic","numselli"]),#'abc'
            page:int = SlashOption(
                description="The page number of the leaderboard",
                default=1)
    ):
        """Shows the streak currentscores"""
        msg = ""
        if mode == "og":
            title_msg = "Current streaks for og counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = og_collection.find(
                    {
                        'streak':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'streak':1,
                        '_id':0
                    }
                ).sort("streak",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name',"Unknown")
                    streak = counter.get('streak',0)
                    msg += f"{i}. {name} - {streak}\n"
                if msg=="":
                    counter_num = og_collection.count_documents(
                        {
                            'streak':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        elif mode == "classic":
            title_msg = "Current streaks for classic counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = classic_collection.find(
                    {
                        'streak':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'streak':1,
                        '_id':0
                    }
                ).sort("streak",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name',"Unknown")
                    streak = counter.get('streak',0)
                    msg += f"{i}. {name} - {streak}\n"
                if msg=="":
                    counter_num = classic_collection.count_documents(
                        {
                            'streak':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        elif mode == "numselli":
            title_msg = "Current streaks for numselli counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = numselli_collection.find(
                    {
                        'streak':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'streak':1,
                        '_id':0
                    }
                ).sort("streak",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name',"Unknown")
                    streak = counter.get('streak',0)
                    msg += f"{i}. {name} - {streak}\n"
                if msg=="":
                    counter_num = numselli_collection.count_documents(
                        {
                            'streak':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        else:
            return
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        embedVar.set_footer(text=f"Page: {page}")
        await ctx.send(embed=embedVar)

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard_command(self, ctx:Context,
            mode:Literal["og", "classic", "numselli"],
            page:int=1):
        """Shows the streak highscores"""
        i=(page-1)*10
        msg = ""
        if mode == "og":
            counter_cursor = og_collection.find(
                {
                    "high":
                    {
                        "$gte":1
                    }
                }, {
                    'name':1,
                    'high':1,
                    '_id':0
                }
            ).sort("high",-1).skip(i).limit(10)
            title_msg = "Highest streaks for og counting"
        elif mode == "classic":
            counter_cursor = classic_collection.find(
                {
                    "high":
                    {
                        "$gte":1
                    }
                }, {
                    'name':1,
                    'high':1,
                    '_id':0
                }
            ).sort("high",-1).skip(i).limit(10)
            title_msg = "Highest streaks for classic counting"
        elif mode == "numselli":
            counter_cursor = numselli_collection.find(
                {
                    "high":
                    {
                        "$gte":1
                    }
                }, {
                    "name":1,
                    "high":1,
                    "_id":0
                }
            ).sort("high",-1).skip(i).limit(10)
            title_msg = "Highest Streaks for numselli counting"
        else:
            return
        for counter in counter_cursor:
            i+=1
            name = counter.get('name',"Unknown")
            high = counter.get('high',0)
            msg += f"{i}. {name} - {high}\n"
        if msg!="":
            embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
            embedVar.set_footer(text=f"Page: {page}")
            await ctx.send(embed=embedVar)
        else:
            return

    @nextcord.slash_command(name="leaderboard", guild_ids=servers)
    async def leaderboard_slash(self, ctx:Interaction,
            mode:str=SlashOption(
                description="Leaderboard type",
                choices=["og","classic","numselli"]),#'abc'
            page:int=SlashOption(
                description="The page number of the leaderboard",
                default=1)):
        """Shows the streak highscores"""
        msg = ""
        if mode == "og":
            title_msg = "Highest streaks for og counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = og_collection.find(
                    {
                        'high':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'high':1,
                        '_id':0
                    }
                ).sort("high",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name', 'Unknown')
                    high = counter.get('high',0)
                    msg += f"{i}. {name} - {high}\n"
                if msg=="":
                    counter_num = og_collection.count_documents(
                        {
                            'high':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        elif mode == "classic":
            title_msg = "Highest streaks for classic counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = classic_collection.find(
                    {
                        'high':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'high':1,
                        '_id':0
                    }
                ).sort("high",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name',"Unknown")
                    high = counter.get('high',0)
                    msg += f"{i}. {name} - {high}\n"
                if msg=="":
                    counter_num = classic_collection.count_documents(
                        {
                            'high':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        elif mode == "numselli":
            title_msg = "Highest streaks for numselli counting"
            while msg == "":
                i = (page - 1) * 10
                counter_cursor = numselli_collection.find(
                    {
                        'high':
                        {
                            "$gte":1
                        }
                    }, {
                        'name':1,
                        'high':1,
                        '_id':0
                    }
                ).sort("high",-1).skip(i).limit(10)
                for counter in counter_cursor:
                    i+=1
                    name = counter.get('name',"Unknown")
                    high = counter.get('high',0)
                    msg += f"{i}. {name} - {high}\n"
                if msg=="":
                    counter_num = numselli_collection.count_documents(
                        {
                            'high':
                            {
                                '$gte':1
                            }
                        }
                    )
                    page = int(counter_num/10)
        else:
            return
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        embedVar.set_footer(text=f"Page: {page}")
        await ctx.send(embed=embedVar)

    @commands.command(name="rankup", aliases=["ru"])
    async def rankup_cmd(self, ctx:Context, member:Member=None):
        """Shows the number of counts required to increase stats"""
        user = member or ctx.author
        msg = ""

        og_post:Optional[OGCounter] = og_collection.find_one({
                "_id": user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if og_post is not None:
            correct = Decimal(og_post.get("correct", 0))
            wrong = Decimal(og_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`counting`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.000005")
                x = ((new_rate * total - correct)/(1 - new_rate)).quantize(
                    Decimal("1"), ROUND_UP)
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.000"))
                msg += f"`counting`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        classic_post:Optional[ClassicCounter] = classic_collection.find_one({
                "_id": user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if classic_post is not None:
            correct = Decimal(classic_post.get("correct", 0))
            wrong = Decimal(classic_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct/total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`classic`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                decimal.getcontext().prec = 8
                new_rate = rate + Decimal("0.000005")
                x = ((new_rate * total - correct)/(1 - new_rate)).quantize(
                    Decimal("1"), ROUND_UP)
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.000"))
                msg += f"`classic`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        beta_post: Optional[BetaCounter] = beta_collection.find_one({
                "_id": user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if beta_post is not None:
            correct = Decimal(beta_post.get("correct", 0))
            wrong = Decimal(beta_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct/total).quantize(Decimal("1.0000"))
            if rate >= Decimal("0.9998"):
                msg += "`alphabeta`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.00005")
                x = ((new_rate * total - correct)/(1 - new_rate)).quantize(
                    Decimal("1"), ROUND_UP)
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.00"))
                msg += f"`alphabeta`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        numselli_post: Optional[NumselliCounter] = numselli_collection.find_one({
                "_id": user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if numselli_post is not None:
            correct = Decimal(numselli_post.get("correct", 0))
            wrong = Decimal(numselli_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct/total).quantize(Decimal("1.0000"))
            if rate >= Decimal("0.9998"):
                msg += "`numselli`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.00005")
                x = ((new_rate * total - correct)/(1 - new_rate)).quantize(
                    Decimal("1"), ROUND_UP)
                # print(x)
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.00"))
                msg += f"`numselli`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        if msg == "":
            msg = "Run counting commands first!"

        title_msg = f"Rank up stats for {user}"
        embedVar = Embed(title=title_msg, description=msg, color=color_lamuse)
        await ctx.send(embed=embedVar)

    @commands.command(name="alt")
    async def alt(self, ctx:Context, user:Optional[Member]=None):
        """Replaces alt streaks for main streaks"""
        # * user should accept transfer
        if user is not None:
            alt_id = ctx.author.id
            main_id = user.id
            if alt_id == main_id:
                await ctx.send("Cannot make self an alt.")
                return

            transfer = AltView(ctx.author, user)
            if transfer.streaks == 0:
                await ctx.send(f"Can't transfer streaks. Check if revelant stats are there.")
            else:
                descr = alt_start_msg.replace("{alt}", f"`{ctx.author.display_name}`")
                descr = descr.replace("{main}", f"`{user.display_name}`")
                embedVar = Embed(color=color_lamuse, description=descr)
                await ctx.send(embed=embedVar, view=transfer)
        else:
            return

class AltView(View):
    """
    Register an account as an alt and let streak counts be 
    given to a main account.
    """

    def __init__(self, alt: Member, main: Member):
        """Initialize the view."""
        super().__init__()
        self.alt = alt
        self.main = main
        self.streaks = 5
        self.og_btn: Button
        self.classic_btn: Button
        self.beta_btn: Button
        self.num_btn: Button
        self.call_data()

    @nextcord.ui.button(label="og")
    async def og_btn(self, button: Button, interaction: Interaction):
        """Select og option."""
        if interaction.user != self.alt:
            return  # ! can't send message, running into run time error
        if self.og is True:
            button.style = ButtonStyle.grey
            self.og = None
        else:
            button.style = ButtonStyle.green
            self.og = True
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label="classic", style=ButtonStyle.danger)
    async def classic_btn(self, button: Button, interaction: Interaction) -> Button:
        """Select classic option."""
        if interaction.user != self.alt:
            return
        if self.classic is True:
            button.style = ButtonStyle.grey
            self.classic = None
        else:
            button.style = ButtonStyle.green
            self.classic = True
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label="beta", style=ButtonStyle.primary)
    async def beta_btn(self, button: Button, interaction: Interaction):
        """Select beta option."""
        if interaction.user != self.alt:
            return
        if self.beta is True:
            button.style = ButtonStyle.grey
            self.beta = None
        else:
            button.style = ButtonStyle.green
            self.beta = True
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label="numselli", style=ButtonStyle.secondary)
    async def num_btn(self, button: Button, interaction: Interaction):
        """Select numselli option."""
        if interaction.user != self.alt:
            return
        if self.num is True:
            button.style = ButtonStyle.grey
            self.num = None
        else:
            button.style = ButtonStyle.green
            self.num = True
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label="PROCEED", row=1, style=ButtonStyle.green)
    async def accept_btn(self, button: Button, interaction: Interaction):
        """Accept combining of streaks."""
        if interaction.user != self.alt:
            return
        child: Button
        for child in self.children:
            child.disabled = not child.disabled
        msg = f"{self.main.mention} do you accept the transfer of streaks?\n The "
        msg += "buttons in green represent the streaks being transferred to you."
        await interaction.response.edit_message(content=msg,
                                                embed=None, view=self)

    @nextcord.ui.button(label="CANCEL", row=1, style=ButtonStyle.red)
    async def decline_btn(self, button: Button, interaction: Interaction):
        """Decline combining of streaks."""
        if interaction.user != self.alt:
            return
        child: Button
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="You have cancelled the transfer.",
                                                embed=None, view=self)

    @nextcord.ui.button(label="ACCEPT", row=2, style=ButtonStyle.green, disabled=True)
    async def main_accept_btn(self, button: Button, interaction: Interaction):
        """Accept combining of streaks."""
        if interaction.user != self.main:
            return
        child: Button
        for child in self.children:
            child.disabled = True
        msg = f"Streaks have been transferred. Check stats of {self.alt.mention}."
        await interaction.response.edit_message(content=msg, view=self)
        send_msg = self.set_data()

    @nextcord.ui.button(label="DECLINE", row=2, style=ButtonStyle.red, disabled=True)
    async def main_decline_btn(self, button: Button, interaction: Interaction):
        """Decline combining of streaks."""
        if interaction.user != self.main:
            return
        child: Button
        for child in self.children:
            child.disabled = True
        msg = "You have declined accepting the transfer."
        await interaction.response.edit_message(content=msg, view=self)

    def call_data(self):
        """Check the stats of the alt account and set initial view of the view."""
        self.og_alt: Optional[OGCounter] = og_collection.find_one({
            "_id": self.alt.id})
        self.og_main: Optional[OGCounter] = og_collection.find_one({
            "_id": self.main.id})
        if self.og_alt is None or self.og_main is None:
            self.remove_item(self.og_btn)
            self.og = False
            self.streaks -= 1
        elif "alt" in self.og_alt and self.og_alt["alt"] == self.main.id:
            self.og = True
            self.og_btn.style = ButtonStyle.green
        elif "alt" in self.og_alt:
            self.og = False
            self.og_btn.style = ButtonStyle.red
        else:
            self.og = None
            self.og_btn.style = ButtonStyle.grey

        self.classic_alt: Optional[ClassicCounter] = classic_collection.find_one({
            "_id": self.alt.id})
        self.classic_main: Optional[ClassicCounter] = classic_collection.find_one({
            "_id": self.main.id})
        if self.classic_alt is None or self.classic_main is None:
            self.remove_item(self.classic_btn)
            self.classic = False
            self.streaks -= 1
        elif "alt" in self.classic_alt and self.classic_alt["alt"] == self.main.id:
            self.classic = True
            self.classic_btn.style = ButtonStyle.green
        elif "alt" in self.classic_alt:
            self.classic = False
            self.classic_btn.style = ButtonStyle.red
        else:
            self.classic = None
            self.classic_btn.style = ButtonStyle.grey

        self.beta_alt: Optional[BetaCounter] = beta_collection.find_one({
            "_id": self.alt.id})
        self.beta_main: Optional[BetaCounter] = beta_collection.find_one({
            "_id": self.main.id})
        if self.beta_alt is None or self.beta_main is None:
            self.remove_item(self.beta_btn)
            self.beta = False
            self.streaks -= 1
        elif "alt" in self.beta_alt and self.beta_alt["alt"] == self.main.id:
            self.beta = True
            self.beta_btn.style = ButtonStyle.green
        elif "alt" in self.beta_alt:
            self.beta = False
            self.beta_btn.style = ButtonStyle.red
        else:
            self.beta = None
            self.beta_btn.style = ButtonStyle.grey

        self.num_alt: Optional[NumselliCounter] = numselli_collection.find_one({
            "_id": self.alt.id})
        self.num_main: Optional[NumselliCounter] = numselli_collection.find_one({
            "_id": self.main.id})
        if self.num_alt is None or self.num_main is None:
            self.remove_item(self.num_btn)
            self.num = False
            self.streaks -= 1
        elif "alt" in self.num_alt and self.num_alt["alt"] == self.main.id:
            self.num = True
            self.num_btn.style = ButtonStyle.green
        elif "alt" in self.num_alt:
            self.num = False
            self.num_btn.style = ButtonStyle.red
        else:
            self.num = None
            self.num_btn.style = ButtonStyle.grey

    def set_data(self):
        """Set the data of transfer streaks in the database."""
        msg = ""
        if self.og_alt is not None and self.og_main is not None:
            if self.og is True and ("alt" not in self.og_alt
                                    or self.og_alt["alt"] != self.main.id):
                og_collection.update_one(
                    {"_id": self.alt.id}, {
                        "$set": {
                            "streak": f"{self.main.name}",
                            "high": f"{self.main.name}",
                            "alt": self.main.id
                        }
                    }
                )
                if "alt" in self.og_main:
                    og_collection.update_one({
                        "_id": self.main.id
                    }, {
                        "$unset": {"alt": 1, },
                        "$set": {"streak": 0, "high": 0},
                    })
                msg += "\nOG streaks have been transferred."
            elif (self.og is None and "alt" in self.og_alt):
                og_collection.update_one({
                    "_id": self.alt.id
                }, {
                    "$unset": {"alt": 1},
                    "$set": {"streak": 0, "high": 0}
                })

        if self.classic_alt is not None and self.classic_main is not None:
            if self.classic is True and ("alt" not in self.classic_alt or
                                         self.classic_alt["alt"] != self.main.id):
                classic_collection.update_one(
                    {"_id": self.alt.id}, {
                        "$set": {
                            "streak": f"{self.main.name}",
                            "high": f"{self.main.name}",
                            "alt": self.main.id
                        }
                    }
                )
                if "alt" in self.classic_main:
                    classic_collection.update_one(
                        {"_id": self.main.id}, {
                            "$unset": {"alt": 1, },
                            "$set": {"streak": 0, "high": 0},
                        }
                    )
                msg += "\nClassic streaks have been transferred."
            elif (self.classic is None and "alt" in self.classic_alt):
                classic_collection.update_one({
                    "_id": self.alt.id
                }, {
                    "$unset": {"alt": 1},
                    "$set": {"streak": 0, "high": 0}
                })

        if self.beta_alt is not None and self.beta_main is not None:
            if self.beta is True and ("alt" not in self.beta_alt or
                                      self.beta_alt["alt"] != self.main.id):
                beta_collection.update_one(
                    {"_id": self.alt.id}, {
                        "$set": {
                            "streak": f"{self.main.name}",
                            "high": f"{self.main.name}",
                            "alt": self.main.id
                        }
                    }
                )
                if "alt" in self.beta_main:
                    beta_collection.update_one(
                        {"_id": self.main.id}, {
                            "$unset": {"alt": 1, },
                            "$set": {"streak": 0, "high": 0},
                        }
                    )
                msg += "\Beta streaks have been transferred."
            elif (self.beta is None and "alt" in self.beta_alt):
                beta_collection.update_one({
                    "_id": self.alt.id
                }, {
                    "$unset": {"alt": 1},
                    "$set": {"streak": 0, "high": 0}
                })

        if self.num_alt is not None and self.num_main is not None:
            if self.num is True and ("alt" not in self.num_alt or
                                     self.num_alt["alt"] != self.main.id):
                numselli_collection.update_one(
                    {"_id": self.alt.id}, {
                        "$set": {
                            "streak": f"{self.main}",
                            "high": f"{self.main}",
                            "alt": self.main.id
                        }
                    }
                )
                if "alt" in self.num_main:
                    numselli_collection.update_one({
                        "_id": self.main.id
                    }, {
                        "$unset": {"alt": 1},
                        "$set": {"streak": 0, "high": 0},
                    })
                msg += "\nNumselli streaks have been transferred."
            elif (self.num is None and "alt" in self.num_alt):
                numselli_collection.update_one({
                    "_id": self.alt.id
                }, {
                    "$unset": {"alt": 1},
                    "$set": {"streak": 0, "high": 0}
                })

        return msg

def setup(bot:commands.Bot):
    bot.add_cog(Stats(bot))