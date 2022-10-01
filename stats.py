import math
from typing import Literal, Union

import nextcord
from nextcord import Embed, Interaction, Member, SlashOption
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.ui import View

from bot_secrets import *
from database import *

class Stats(commands.Cog):
    """The cog containing the commnds to check the stats of the user."""

    def __init__(self, bot:commands.Bot):
        """Initialize the cog."""
        self.bot = bot

    @nextcord.slash_command(guild_ids=servers)
    async def id(self, ctx:Context, user:Member):
        """Gives a user's id without pinging them"""
        await ctx.send(f"{user.id}")

    @commands.command(name="user", aliases=['u'])
    async def user_command(self, ctx:Context, member:Member=None):
        """Displays user stats in the guild"""
        user = member or ctx.author
        embedVar = Embed(title=f"User stats for {user}",color=color_lamuse)
        embedVar.set_thumbnail(url=user.display_avatar)
        user_post = og_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post.get('correct',0)
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            daily = user_post.get('daily',0)
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
            msg += f"\nSaves: {current_saves}/{user_post['total_saves']}"
            msg += f"\n\nCurrent Streak: {user_post['streak']}"
            msg += f"\nHighest Streak: {user_post['high']}"
            msg += f"\nDaily: {daily}" 
            embedVar.add_field(name=mode_list["1"],value=msg)
        user_post = classic_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            if total == 0:
                rate = 0
            else:
                rate = correct/total*100
                str_rate = str(rate)[:6]
            msg = f"Rate: {str_rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\n\n\nCurrent Streak: {user_post['streak']}"
            msg += f"\nHighest Streak: {user_post['high']}"
            embedVar.add_field(name=mode_list["2"],value=msg)
        # user_post = abc_collection.find_one({"_id":user.id})
        # if user_post:
        #     correct = user_post['correct']
        #     wrong = user_post.get('wrong',0)
        #     total = correct + wrong
        #     if total == 0:
        #         rate = 0
        #     else:
        #         rate = round(float(correct/total)*100,2)
        #     current_saves = user_post['current_saves']
        #     if current_saves == int(current_saves):
        #         current_saves = int(current_saves)
        #     else:
        #         current_saves = round(current_saves,2)
        #     msg = f"Rate: {rate}%"
        #     msg += f"\nCorrect: {correct}"
        #     msg += f"\nWrong: {wrong}"
        #     msg += f"\nSaves: {current_saves}/{user_post['total_saves']}"
        #     msg += f"\n\nCurrent Streak: {user_post['streak']}"
        #     msg += f"\nHighest Streak: {user_post['high']}"
        #     embedVar.add_field(name=mode_list["3"],value=msg)
        user_post = beta_collection.find_one({"_id":user.id})
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
            msg += f"\nSaves: {current_saves}/{user_post['total_saves']}"
            embedVar.add_field(name=mode_list["4"],value=msg)
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
            msg += f"\nSaves: {current_saves}/{user_post['total_saves']}"
            msg += f"\n\nCurrent Streak: {user_post.get('streak',0)}"
            msg += f"\nHighest Streak: {user_post.get('high',0)}"
            embedVar.add_field(name=mode_list["5"],value=msg)
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
        # elif mode == "abc":
        #     counter_cursor = abc_collection.find(
        #         {},
        #         {'name':1,'streak':1,'_id':0}
        #     ).sort("streak",-1).skip(i).limit(10)
        #     title_msg = "Current streaks for abc counting"
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
        # elif mode == "abc":
        #     title_msg = "Current streaks for ABC counting"
        #     while msg == "":
        #         i = (page - 1) * 10
        #         counter_cursor = abc_collection.find(
        #             {'streak':{"$gte":1}},
        #             {'name':1,'streak':1,'_id':0}
        #         ).sort("streak",-1).skip(i).limit(10)
        #         for counter in counter_cursor:
        #             i+=1
        #             msg += f"{i}. {counter['name']} - {counter['streak']}\n"
        #         if msg=="":
        #             counter_num = abc_collection.count_documents(
        #                 {
        #                     'streak':
        #                     {
        #                         '$gte':1
        #                     }
        #                 }
        #             )
        #             page = int(counter_num/10)
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
        # elif mode == 3:
        #     counter_cursor = abc_collection.find(
        #         {},
        #         {'name':1,'high':1,'_id':0}
        #     ).sort("high",-1).skip(i).limit(10)
        #     title_msg = "Highest streaks for abc counting"
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
        # elif mode == "abc":
        #     title_msg = "Highest streaks for ABC counting"
        #     while msg == "":
        #         i = (page - 1) * 10
        #         counter_cursor = abc_collection.find(
        #             {'high':{"$gte":1}},
        #             {'name':1,'high':1,'_id':0}
        #         ).sort("high",-1).skip(i).limit(10)
        #         for counter in counter_cursor:
        #             i+=1
        #             msg += f"{i}. {counter['name']} - {counter['high']}\n"
        #         if msg=="":
        #             counter_num = abc_collection.count_documents(
        #                 {
        #                     'high':
        #                     {
        #                         '$gte':1
        #                     }
        #                 }
        #             )
        #             page = int(counter_num/10)
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

    @commands.command(aliases=["ru"])
    async def rankup(self, ctx:Context, member:Member=None):
        """Shows the number of counts required to increase stats"""
        user = member or ctx.author
        msg = ""
        
        user_post:dict = og_collection.find_one(
            {
                "_id":user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            rate = round(float(correct/total),5)
            if rate >= 0.9998:
                msg += "`counting`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + 0.000005
                x = math.ceil((new_rate * total - correct)/(1 - new_rate))
                new_cor = correct + x
                new_rate = str(round((rate + 0.00001)*100,3))[:6]
                msg += f"`counting`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"
        user_post = classic_collection.find_one(
            {
                "_id":user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            rate = correct/total
            str_rate = str(rate)[:6]
            rate = float(str_rate)
            if rate >= 0.9998:
                msg += "`classic`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + 0.0001
                x = math.ceil((new_rate * total - correct)/(1 - new_rate))
                new_cor = correct + x
                new_rate = str(round(new_rate*100,2))[:5]
                msg += f"`classic`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"
        user_post = beta_collection.find_one(
            {
                "_id":user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            rate = round(float(correct/total),4)
            if rate >= 0.9998:
                msg += "`alphabeta`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + 0.00005
                x = math.ceil((new_rate * total - correct)/(1 - new_rate))
                new_cor = correct + x
                new_rate = str(round((rate + 0.0001)*100,2))[:5]
                msg += f"`alphabeta`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"
        user_post = numselli_collection.find_one(
            {
                "_id":user.id
            }, {
                "correct":1,
                "wrong":1
            }
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post.get('wrong',0)
            total = correct + wrong
            rate = round(float(correct/total),4)
            if rate >= 0.9998:
                msg += "`numselli`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + 0.00005
                x = math.ceil((new_rate * total - correct)/(1 - new_rate))
                new_cor = correct + x
                new_rate = str(round((rate + 0.0001)*100,2))[:5]
                msg += f"`numselli`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"
        title_msg = f"Rank up stats for {user}"
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)

    @commands.command(name="alt")
    async def alt(self, ctx:Context, user:Member):
        """Replaces alt streaks for main streaks (only in og for now)"""
        alt_id = ctx.author.id
        main_id = user.id
        og_collection.update_one(
            {
                "_id":alt_id
            }, {
                "$set":
                {
                    "streak":"No streaks",
                    "high":"No streaks",
                    "alt":main_id
                }
            }
        )
        classic_collection.update_one(
            {
                "_id":alt_id
            }, {
                "$set":
                {
                    "streak":"No streaks",
                    "high":"No streaks",
                    "alt":main_id
                }
            }
        )
        numselli_collection.update_one(
            {
                "_id":alt_id
            }, {
                "$set":
                {
                    "streak":"No streaks",
                    "high":"No streaks",
                    "alt":main_id
                }
            }
        )
        await ctx.send(f"Streaks of {ctx.author} will be given to {user}")

def setup(bot:commands.Bot):
    bot.add_cog(Stats(bot))