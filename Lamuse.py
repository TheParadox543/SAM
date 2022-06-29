import discord
from discord import Embed, Option, Member, Role as dRole
from discord.ext import commands, tasks
import typing
import re
import math
import requests
from datetime import datetime, timedelta, timezone, tzinfo
import asyncio
from pymongo import MongoClient
import certifi

import secrets

"""Program data"""
ca = certifi.where()
cluster = MongoClient(secrets.MONGO_DB_CONNECTION_STRING,tlsCAFile=ca)
db = cluster['lamuse']
og_collection = db['ogcollection']
classic_collection = db['classiccollection']
abc_collection = db['abccollection']
beta_collection = db['betacollection']
numselli_collection = db['numsellicollection']
misc = db['misc']
time_collection = db['time']
dank_collection = db['dank']
epoch_time = datetime(1970,1,1,tzinfo=None)

"""Bot data"""
lamuse_id = 756905904104013825
paradox_id = 717240803789111345
color_lamuse = 0x0a53c7
servers = [892553570208088064] #countaholics

"""Discord data"""
og_bot = 510016054391734273
og_channel = 892555565040025661
classic_bot = 639599059036012605
classic_channel = 893235324149432360
abc_bot = 789949322032316416
abc_channel = 893227104538345473
beta_bot = 835110241129201684
beta_channel = 921868532101300274
numselli_bot = 726560538145849374 
numselli_channels = {
    "whole": 898624615713239090,
    "letters": 898626111238447144,
    "binary": 893237436157669377,
    "decimal": 893236828189130792,
    "hex": 897773402050416670,
    "roman": 918433594005946388,
    "two": 917596780881920040,
    "five": 919101015930843167,
    "ten": 919102249110753321,
    "hundred": 919102646927892492
}
prime_bot = 754680630037577859
prime_channel = 893234574300172358
# sasha_bot = 862060226798682174
# sasha_channel = 893237900257419304
scores_channel = 898287795733417984
bot_channel = 892731445376860241
mile_channel = 929606005535408159
workshop_channel = 931498728760672276
dank_bot = 270904126974590976
dank_channel = 903015721653653584

dishonorable_id:int = 894404278507167775
countaholic_id:int = 893225025455390760
og_save_id:int = 913491333111500820
abc_save_id:int = 914130459259187260
beta_save_id:int = 930087029562290236
have_save_id:int = 912396018987978844
alphacounter_id:int = 930089232729514024
betacounter_id:int = 930041154634940416

track_list = [
    og_channel,
    classic_channel, 
    abc_channel, 
    beta_channel, 
    numselli_channels["letters"],
    numselli_channels['binary'],
    numselli_channels['hex']
]
emoji_list = [
    "<a:confetti:914965969661751309>", 
    "<a:catjump:915069990951059467>", 
    "<a:pepeflame:914966371752882217", 
    "<a:pepelaugh:924117672550105089>",
    "<a:rainbowboy:930683298710159360>",
    "<a:hypeboy:914966295592710194>",
    "<a:pepecoolclap:930683139028844544>", 
    "<a:rainbowglowstickvibeslow:915069470198865961>"
]
mode_list = {
    "1": "**counting**",
    "2": "**countingclassic**",
    "3": "**ABC Counting**",
    "4": "**AlphaBeta**",
    "5": "**Numselli**"
}

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=("?"),
    case_insensitive=True,
    owner_id=paradox_id,
    intents=intents
)

def admin_perms():
    """To give permissions to lock and unlock channels if needed"""
    def predicate(ctx):
        return ctx.author.id==717240803789111345 or \
               ctx.author.guild_permissions.manage_channels
    return commands.check(predicate)

def letter_calc(word: str):
    """To calculate the value of word in abc channels"""
    num = 0
    pos = len(word) - 1
    for letter in word:
        lett = ord(letter)
        if lett > 64 and lett < 91:
            lett = lett - 64
        else:
            return -1
        num += lett * 26 ** pos
        pos = pos - 1
    return num

@bot.event
async def on_ready():
    """To log when the bot is ready for use"""
    await bot.change_presence(activity=discord.Game("?help"))
    check_time.start()
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=servers)
@admin_perms()
async def lock(ctx,
        bot_name:Option(str,
            description="Bot name",
            choices=["og","classic","abc","prime","numselli"]),
        reason:Option(str,
            description="Reason for locking the channel",
            choices=["cooldown","offline"])):
    """Locks the channel manually. You need to have necessary permissions"""
    if bot_name == "og":
        channel = bot.get_channel(og_channel)
        role:dRole = ctx.guild.get_role(og_save_id)
    elif bot_name == "classic":
        channel = bot.get_channel(classic_channel)
        role:dRole = ctx.guild.get_role(countaholic_id)
    elif bot_name == "abc":
        channel = bot.get_channel(abc_channel)
        role:dRole = ctx.guild.get_role(abc_save_id)
    elif bot_name == "prime":
        channel = bot.get_channel(prime_channel)
        role:dRole = ctx.guild.get_role(countaholic_id)
    elif bot_name == "numselli":
        await ctx.respond("Locking now")
        role:dRole = ctx.guild.get_role(have_save_id)
        for channel_name in numselli_channels:
            channel_id = numselli_channels[channel_name]
            channel = bot.get_channel(channel_id)
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
            await ctx.respond("Channel locked for cooldown for 10 minutes")
        else:
            await channel.send("Channel locked for cooldown for 10 minutes")
            await ctx.respond("Done")
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
            await ctx.respond("Channel locked by moderator")
        else:
            await channel.send("Channel locked by moderator")
            await ctx.respond("Done")
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

@bot.slash_command(guild_ids=servers)
@admin_perms()
async def unlock(ctx,
        bot_name:Option(str,
            description="Bot name",
            choices=["og","classic","abc","prime","numselli"])):
    """Unlocks the channels manually. You need to have necessary permissions"""
    if bot_name == "og":
        channel = bot.get_channel(og_channel)
        role:dRole = ctx.guild.get_role(og_save_id)
    elif bot_name == "classic":
        channel = bot.get_channel(classic_channel)
        role:dRole = ctx.guild.get_role(countaholic_id)
    elif bot_name == "abc":
        channel = bot.get_channel(abc_channel)
        role:dRole = ctx.guild.get_role(abc_save_id)
    elif bot_name == "prime":
        channel = bot.get_channel(prime_channel)
        role:dRole = ctx.guild.get_role(countaholic_id)
    elif bot_name == "numselli":
        await ctx.respond("Unlocking now")
        role:dRole = ctx.guild.get_role(have_save_id)
        for channel_name in numselli_channels:
            channel_id = numselli_channels[channel_name]
            channel = bot.get_channel(channel_id)
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
        await ctx.respond("Channel unlocked by moderator")
    else:
        await ctx.respond("Done")
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

@bot.slash_command(guild_ids=servers)
async def checklist(ctx,
        type_check:Option(str,
            description="List type",
            choices=['og','b','vote'])): #'a'
    """Displays the list of people registered to receive saves"""
    msg = ""
    if type_check == 'og':
        counter_list = og_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':{'name':1}
            }
        ])
        for counter in counter_list:
            msg += f"{counter['name']}\n"
        title_msg = "List of og counters registered by the bot"
    # elif type_check == "a":
    #     counter_list = abc_collection.aggregate([
    #         {
    #             '$match':{'counter':True}
    #         },
    #         {
    #             '$project':{'name':1}
    #         }
    #     ])
    #     for counter in counter_list:
    #         msg += f"{counter['name']}\n"
    #     title_msg = "List of ABC counters registered by the bot"
    elif type_check == "b":
        counter_list = beta_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':{'name':1}
            }
        ])
        for counter in counter_list:
            msg += f"{counter['name']}\n"
        title_msg = "List of AlphaBeta counters registered by the bot"
    elif type_check == "vote":
        counter_list = misc.find_one({"_id":"ogregister"},{"_id":0})
        for user_id in counter_list:
            if counter_list[f"{user_id}"] == True:
                user = ctx.guild.get_member(int(user_id))
                msg += f"{user}\n"
        title_msg = "Counters who opted in for vote reminders"
    else:
        return
    embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
    await ctx.respond(embed=embedVar)

@bot.slash_command(guild_ids=servers)
async def leaderboard(ctx,
        mode:Option(str,
            description="Leaderboard type",
            choices=["og","classic"]),#'abc'
        page:Option(int,
            description="The page number of the leaderboard")=1):
    """Shows the streak highscores"""
    msg = ""
    if mode == "og":
        title_msg = "Highest streaks for og counting"
        while msg == "":
            i = (page - 1) * 10
            counter_cursor = og_collection.find(
                {'high':{"$gte":1}},
                {'name':1,'high':1,'_id':0}
            ).sort("high",-1).skip(i).limit(10)
            for counter in counter_cursor:
                i+=1
                msg += f"{i}. {counter['name']} - {counter['high']}\n"
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
                {'high':{"$gte":1}},
                {'name':1,'high':1,'_id':0}
            ).sort("high",-1).skip(i).limit(10)
            for counter in counter_cursor:
                i+=1
                msg += f"{i}. {counter['name']} - {counter['high']}\n"
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
    else:
        return
    embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
    embedVar.set_footer(text=f"Page: {page}")
    await ctx.respond(embed=embedVar)

@bot.slash_command(guild_ids=servers)
async def currentscores(ctx,
        mode:Option(str,
            description="Leaderboard type",
            choices=["og","classic"]),#'abc'
        page:Option(int,
            description="The page number of the leaderboard")=1):
    """Shows the streak currentscores"""
    msg = ""
    if mode == "og":
        title_msg = "Current streaks for og counting"
        while msg == "":
            i = (page - 1) * 10
            counter_cursor = og_collection.find(
                {'streak':{"$gte":1}},
                {'name':1,'streak':1,'_id':0}
            ).sort("streak",-1).skip(i).limit(10)
            for counter in counter_cursor:
                i+=1
                msg += f"{i}. {counter['name']} - {counter['streak']}\n"
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
                {'streak':{"$gte":1}},
                {'name':1,'streak':1,'_id':0}
            ).sort("streak",-1).skip(i).limit(10)
            for counter in counter_cursor:
                i+=1
                msg += f"{i}. {counter['name']} - {counter['streak']}\n"
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
    else:
        return
    embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
    embedVar.set_footer(text=f"Page: {page}")
    await ctx.respond(embed=embedVar)

@bot.slash_command(guild_ids=servers)
async def id(ctx,user:Member):
    """Gives a user's id without pinging them"""
    await ctx.respond(f"{user.id}")

@bot.slash_command(guild_ids=servers)
async def run(ctx):
    """Gives the time when the run started"""
    run_time = time_collection.find_one({"_id":"run"})
    time_now = datetime.utcnow().replace(microsecond=0)
    time_diff = time_now - run_time["time_last"]
    if time_diff >= timedelta(minutes=10):
        await ctx.send("It's been a while since a run")
    else:
        total_seconds = int((run_time["time_start"]-epoch_time).total_seconds())
        await ctx.respond(f"Run started at <t:{total_seconds}:T>")

@bot.slash_command(guild_ids=servers)
async def reminders(ctx):
    """Shows the list of reminders the bot has for a user"""
    rem_list = time_collection.find({"user":ctx.author.id})
    msg = ""
    time_now = datetime.utcnow().replace(microsecond=0)
    for item in rem_list:
        time_diff = item['time'] - time_now
        time_diff = int(time_diff.total_seconds())
        if time_diff > 0:
            total_seconds = int((item['time'] - epoch_time).total_seconds())
            msg += f"{item['command']} - <t:{total_seconds}:R>\n"
    embedVar = Embed(title=f"Reminders for {ctx.author}",description=msg,color=color_lamuse)
    await ctx.respond(embed=embedVar)

@bot.slash_command(guild_ids=servers)
async def prime(ctx, number:Option(int,description="The last number")):
    """Gives the next prime number"""
    
    def prime(num:int):
        f = False
        for i in range(3,int(math.sqrt(num))+1,2):
            if num % i ==0:
                f = True
        return f

    def next_prime(num:int):
        f = True
        while(f):
            if num > 2:
                num += 2
            else:
                num += 1
            f = prime(num)
        return num

    if number == 2 or (number>2 and number%2==1):
        next_num = next_prime(number)
    else:
        next_num = next_prime(number-1)
    await ctx.respond(f"`{next_num} is the next prime after {number}`")


class AdminCommands(commands.Cog, name="Admin Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_perms()
    async def lock(self,ctx,
            bot_name:typing.Literal['og','classic','abc'],
            reason:typing.Literal['cooldown','offline']):
        """Locks the channel manually. You need to have necessary permissions"""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role:dRole = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role:dRole = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role:dRole = ctx.guild.get_role(abc_save_id)
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

    @commands.command()
    @admin_perms()
    async def unlock(self,ctx,
            bot_name:typing.Literal['og','classic','abc']):
        """Unlocks the channels manually. You need to have necessary permissions"""
        if bot_name == "og":
            channel = self.bot.get_channel(og_channel)
            role:dRole = ctx.guild.get_role(og_save_id)
        elif bot_name == "classic":
            channel = self.bot.get_channel(classic_channel)
            role:dRole = ctx.guild.get_role(countaholic_id)
        elif bot_name == "abc":
            channel = self.bot.get_channel(abc_channel)
            role:dRole = ctx.guild.get_role(abc_save_id)
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


class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ol'])
    async def oglist(self, ctx):
        """Gives a list of users who want to receive saves for og counting"""
        saves_list = og_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':
                {
                    '_id':0,
                    'name':1,
                    'save_slot':{'$subtract':['$total_saves','$current_saves']}
                }
            },
            {
                '$sort':{'save_slot':-1}
            }
        ])
        msg = ""
        for counter in saves_list:
            if int(counter['save_slot']) > 0:
                msg += f"{counter['name']} - {counter['save_slot']}\n"
        title_msg = "Counters who could use a save in og-counting"
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)
    
    @commands.group(aliases=['ocounter','oc'],invoke_without_command=True)
    async def ogcounter(self, ctx):
        """
        Registers a counter as og-counters to receive saves from users who have extra saves
        """
        user = ctx.author
        user_post = og_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                msg = f"<@{user.id}> is an og-counter. "
                msg += "Your name will appear in `oglist`"
            elif user_post['counter'] == True:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                msg = f"<@{user.id}> is no longer an og-counter. "
                msg += "Your name will not appear in `oglist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @ogcounter.command(name="set")
    @admin_perms()
    async def og_set(self,ctx,user:Member):
        """Used to set another counter as ogcounter by admin"""
        user_post = og_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                msg = f"<@{user.id}> is an og-counter. "
                msg += "Your name will appear in `oglist`"
            elif user_post['counter'] == True:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                msg = f"<@{user.id}> is no longer an og-counter. "
                msg += "Your name will not appear in `oglist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    # @commands.command()
    # async def alphacounter(self,ctx):
    #     """Registers a counter as abc counters who want gifts"""
    #     user = ctx.author
    #     alphacounter_role = ctx.guild.get_role(alphacounter_id)
    #     if abc_collection.find_one({"_id":user.id}):
    #         user_post = abc_collection.find_one({"_id":user.id}, {"counter":1})
    #         if 'counter' not in user_post or user_post['counter'] == False:
    #             abc_collection.update_one(
    #                 {
    #                     "_id":user.id
    #                 }, {
    #                     "$set":
    #                     {
    #                         "counter":True
    #                     }
    #                 }
    #             )
    #             await user.add_roles(alphacounter_role)
    #             msg = f"<@{user.id}> is an ABC counter. "
    #             msg += "Your name will appear in `alist`."
    #             await ctx.send(msg)
    #         elif user_post['counter'] == True:
    #             abc_collection.update_one(
    #                 {
    #                     "_id":user.id
    #                 }, {
    #                     "$set":
    #                     {
    #                         "counter":False
    #                     }
    #                 }
    #             )
    #             await user.remove_roles(alphacounter_role)
    #             msg = f"<@{user.id}> is no longer an ABC counter. "
    #             msg += "Your name will not appear in `alist`."
    #             await ctx.send(msg)
    #     else:
    #         abc_collection.insert_one(
    #             {
    #                 "_id":user.id,
    #                 "name":f"{user}",
    #                 "correct":0,
    #                 "wrong":0,
    #                 "current_saves":0,
    #                 "total_saves":5,
    #                 "streak":0,
    #                 "high":0,
    #                 "counter":True
    #             }
    #         )
    #         await user.add_roles(alphacounter_role)
    #         msg = f"<@{user.id}> is an ABC counter. "
    #         msg += "Your name will appear in `alist`."

    # @commands.command()
    # async def alist(self,ctx):
    #     """Gives the list of counters who can receive abc gifts"""
    #     saves_list = abc_collection.aggregate([
    #         {
    #             '$match':{'counter':True}
    #         },
    #         {
    #             '$project':
    #             {
    #                 '_id':0,
    #                 'name':1,
    #                 'save_slot':{'$subtract': ['$total_saves','$current_saves']}
    #             }
    #         },
    #         {
    #             '$sort': {'save_slot':-1}
    #         }
    #     ])
    #     msg = ""
    #     for counter in saves_list:
    #         if int(counter['save_slot']) > 0:
    #             msg += f"{counter['name']} - {counter['save_slot']}\n"
    #     title_msg = "ABC counters who could use a save"
    #     embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
    #     await ctx.send(embed=embedVar)

    @commands.command(aliases=['bl'])
    async def blist(self, ctx):
        """Gives the list of counters who can receive AlphaBeta gifts"""
        saves_list = beta_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':
                {
                    '_id':0,
                    'name':1,
                    'save_slot':{'$subtract': ['$total_saves','$current_saves']}
                }
            },
            {
                '$sort': {'save_slot':-1}
            }
        ])
        msg = ""
        for counter in saves_list:
            if int(counter['save_slot']) > 0:
                msg += f"{counter['name']} - {counter['save_slot']}\n"
        title_msg = "AlphaBeta counters who could use a save"
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)

    @commands.group(aliases=['bcounter','bc'],imvoke_without_command=True)
    async def betacounter(self, ctx):
        """Registers a counter as AlphaBeta counters"""
        user = ctx.author
        betacounter_role:dRole = ctx.guild.get_role(betacounter_id)
        user_post = beta_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                await user.add_roles(betacounter_role)
                msg = f"<@{user.id}> is an AlphaBeta counter. "
                msg += "Your name will appear in `blist`"
            elif user_post['counter'] == True:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                await user.remove_roles(betacounter_role)
                msg = f"<@{user.id}> is no longer an AlphaBeta counter. "
                msg += "Your name will not appear in `blist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @betacounter.command(name='set')
    @admin_perms()
    async def beta_set(self, ctx, user:Member):
        """Used to set another counter as AlphaBeta counter by an admin"""
        betacounter_role:dRole = ctx.guild.get_role(betacounter_id)
        user_post = beta_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                await user.add_roles(betacounter_role)
                msg = f"<@{user.id}> is an AlphaBeta counter. "
                msg += "Your name will appear in `blist`"
            elif user_post['counter'] == True:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                await user.remove_roles(betacounter_role)
                msg = f"<@{user.id}> is no longer an AlphaBeta counter. "
                msg += "Your name will not appear in `blist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @commands.command()
    async def checklist(self,ctx,type_check:typing.Literal['og','b','vote']): #'a'
        """Displays the list of people registered to receive saves"""
        msg = ""
        if type_check == 'og':
            counter_list = og_collection.aggregate([
                {
                    '$match':{'counter':True}
                },
                {
                    '$project':{'name':1}
                }
            ])
            for counter in counter_list:
                msg += f"{counter['name']}\n"
            title_msg = "List of og counters registered by the bot"
        # elif type_check == "a":
        #     counter_list = abc_collection.aggregate([
        #         {
        #             '$match':{'counter':True}
        #         },
        #         {
        #             '$project':{'name':1}
        #         }
        #     ])
        #     for counter in counter_list:
        #         msg += f"{counter['name']}\n"
        #     title_msg = "List of ABC counters registered by the bot"
        elif type_check == "b":
            counter_list = beta_collection.aggregate([
                {
                    '$match':{'counter':True}
                },
                {
                    '$project':{'name':1}
                }
            ])
            for counter in counter_list:
                msg += f"{counter['name']}\n"
            title_msg = "List of AlphaBeta counters registered by the bot"
        elif type_check == "vote":
            counter_list = misc.find_one({"_id":"ogregister"},{"_id":0})
            for user_id in counter_list:
                if counter_list[f"{user_id}"] == True:
                    user = ctx.guild.get_member(int(user_id))
                    msg += f"{user}\n"
            title_msg = "Counters who opted in for vote reminders"
        else:
            return
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['u'])
    async def user(self,ctx,member:Member=None):
        """Displays user stats in the guild"""
        user = member or ctx.author
        embedVar = Embed(title=f"User stats for {user}",color=color_lamuse)
        embedVar.set_thumbnail(url=user.display_avatar)
        user_post = og_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post['correct']
            if 'wrong' in user_post:
                wrong = user_post['wrong']
            else:
                wrong = 0
            total = correct + wrong
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
            embedVar.add_field(name=mode_list["1"],value=msg)
        user_post = classic_collection.find_one({"_id":user.id})
        if user_post:
            correct = user_post['correct']
            if 'wrong' in user_post:
                wrong = user_post['wrong']
            else:
                wrong = 0
            total = correct + wrong
            if total == 0:
                rate = 0
            else:
                rate = correct/total*100
                str_rate = str(rate)[:5]
            msg = f"Rate: {str_rate}%"
            msg += f"\nCorrect: {correct}"
            msg += f"\nWrong: {wrong}"
            msg += f"\n\n\nCurrent Streak: {user_post['streak']}"
            msg += f"\nHighest Streak: {user_post['high']}"
            embedVar.add_field(name=mode_list["2"],value=msg)
        # user_post = abc_collection.find_one({"_id":user.id})
        # if user_post:
        #     correct = user_post['correct']
        #     if 'wrong' in user_post:
        #         wrong = user_post['wrong']
        #     else:
        #         wrong = 0
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
            if 'wrong' in user_post:
                wrong = user_post['wrong']
            else:
                wrong = 0
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
            if 'wrong' in user_post:
                wrong = user_post['wrong']
            else:
                wrong = 0
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
            embedVar.add_field(name=mode_list["5"],value=msg)
        await ctx.send(embed=embedVar)
    
    @commands.command(aliases=["cs"])
    async def currentscore(self,ctx,mode:int=1,page:int=1):
        """Shows the streak currentscores"""
        i=(page-1)*10
        msg = ""
        if mode == 1:
            counter_cursor = og_collection.find(
                {},
                {'name':1,'streak':1,'_id':0}
            ).sort("streak",-1).skip(i).limit(10)
            title_msg = "Current streaks for og counting"
        elif mode == 2:
            counter_cursor = classic_collection.find(
                {},
                {'name':1,'streak':1,'_id':0}
            ).sort("streak",-1).skip(i).limit(10)
            title_msg = "Current streaks for classic counting"
        # elif mode == 3:
        #     counter_cursor = abc_collection.find(
        #         {},
        #         {'name':1,'streak':1,'_id':0}
        #     ).sort("streak",-1).skip(i).limit(10)
        #     title_msg = "Current streaks for abc counting"
        else:
            return
        for counter in counter_cursor:
            i+=1
            msg += f"{i}. {counter['name']} - {counter['streak']}\n"
        if msg!="":
            embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
            await ctx.send(embed=embedVar)
        else:
            return

    @commands.command(aliases=["lb"])
    async def leaderboard(self,ctx,mode:int=1,page:int=1):
        """Shows the streak highscores"""
        i=(page-1)*10
        msg = ""
        if mode == 1:
            counter_cursor = og_collection.find(
                {},
                {'name':1,'high':1,'_id':0}
            ).sort("high",-1).skip(i).limit(10)
            title_msg = "Highest streaks for og counting"
        elif mode == 2:
            counter_cursor = classic_collection.find(
                {},
                {'name':1,'high':1,'_id':0}
            ).sort("high",-1).skip(i).limit(10)
            title_msg = "Highest streaks for classic counting"
        # elif mode == 3:
        #     counter_cursor = abc_collection.find(
        #         {},
        #         {'name':1,'high':1,'_id':0}
        #     ).sort("high",-1).skip(i).limit(10)
        #     title_msg = "Highest streaks for abc counting"
        else:
            return
        for counter in counter_cursor:
            i+=1
            msg += f"{i}. {counter['name']} - {counter['high']}\n"
        if msg!="":
            embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
            await ctx.send(embed=embedVar)
        else:
            return

    @commands.command(aliases=["ru"])
    async def rankup(self,ctx,member:Member=None):
        """Shows the number of counts required to increase stats"""
        user = member or ctx.author
        msg = ""
        
        user_post = og_collection.find_one(
            {"_id":user.id},
            {"correct":1,"wrong":1}
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post['wrong']
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
            {"_id":user.id},
            {"correct":1,"wrong":1}
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post['wrong']
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
        # user_post = abc_collection.find_one(
        #     {"_id":user.id},
        #     {"correct":1,"wrong":1}
        # )
        # if user_post:
        #     correct = user_post['correct']
        #     wrong = user_post['wrong']
        #     total = correct + wrong
        #     rate = round(float(correct/total),4)
        #     if rate >= 0.9998:
        #         msg += "`abc`: The bot can't calculate the number of counts "
        #         msg += "you need to rank up\n"
        #     else:
        #         new_rate = rate + 0.00005
        #         x = math.ceil((new_rate * total - correct)/(1 - new_rate))
        #         new_cor = correct + x
        #         new_rate = str(round((rate + 0.0001)*100,2))[:5]
        #         msg += f"`abc`: Rank up to {new_rate}% at **{new_cor}**. "
        #         msg += f"You need ~**{x}** more numbers.\n"
        user_post = beta_collection.find_one(
            {"_id":user.id},
            {"correct":1,"wrong":1}
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post['wrong']
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
            {"_id":user.id},
            {"correct":1,"wrong":1}
        )
        if user_post:
            correct = user_post['correct']
            wrong = user_post['wrong']
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

    @commands.command()
    async def run(self,ctx):
        """Gives the time when the run started"""
        run_time = time_collection.find_one({"_id":"run"})
        time_now = datetime.utcnow().replace(microsecond=0)
        time_diff = time_now - run_time["time_last"]
        if time_diff >= timedelta(minutes=10):
            await ctx.send("It's been a while since a run")
        else:
            total_seconds = int((run_time["time_start"]-epoch_time).total_seconds())
            await ctx.send(f"Run started at <t:{total_seconds}:T>")


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def ogregister(self,ctx):
        """Register for c!vote reminders"""
        register_list = misc.find_one({"_id":"ogregister"})
        userID = ctx.author.id
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

    @ogregister.command(name="set")
    @admin_perms()
    async def ogreg_set(self,ctx,user:Member):
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
    async def reminders(self,ctx,member:Member=None):
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
        embedVar = Embed(title=f"Reminders for {user}",description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)

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


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vote(self, ctx):
        """Vote for the bot"""
        msg = "Thanks for caring about the bot enough to vote for it, "
        msg += "but unfortunately since the bot is private, there is no use "
        msg += "voting for it. Thanks all the same. 🤗 😍"
        await ctx.send(msg)


@bot.event
async def on_message(message):
    if message.author == bot.user: #ignores if message from bot
        return

    content:str = message.content
    author:Member = message.author
    channel:int = message.channel.id
    guild:discord.Guild = message.guild

    """To update user streak if correct and milestone update"""
    if track_list.count(channel)>0 and \
            len(content.split()) > 0 and \
            re.match("\w", content) and author.bot == False:
        number_str = content.split()[0]
        number_str = number_str.upper()
        user_id = author.id
        msg_s = ""
        if channel == og_channel and re.match("\d", number_str):
            try:
                number = int(number_str)
                if number == 0:
                    pass
                user_post = og_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1
                    }
                )
                if user_post:
                    if user_post['streak'] == user_post['high']:
                        og_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "streak":1,
                                    "high":1,
                                    "correct":1
                                }
                            }
                        )
                        if (user_post['streak']+1)%500==0:
                            msg_s = f"n{(user_post['streak']+1)}"
                    else:
                        og_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "streak":1,
                                    "correct":1
                                }
                            }
                        )
                        if (user_post['streak']+1)%500==0:
                            msg_s = f"{(user_post['streak']+1)}"
                    mode = "1"
            except Exception:
                return
            run_time = time_collection.find_one({"_id":"run"})
            time_now = message.created_at.replace(tzinfo=None,microsecond=0)
            time_diff = time_now - run_time["time_last"]
            if abs(time_diff) >= timedelta(minutes=10) \
                    or run_time['time_start']==epoch_time:
                time_collection.update_one(
                    {
                        "_id":"run"
                    }, {
                        "$set":
                        {
                            "time_last":time_now,
                            "time_start":time_now
                        }
                    }
                )
            else:
                time_collection.update_one(
                    {
                        "_id":"run"
                    }, {
                        "$set":
                        {
                            "time_last":time_now
                        }
                    }
                )
        elif channel == classic_channel and re.match("\d", number_str):
            try:
                number = int(number_str)
                if number == 0:
                    pass
                user_post = classic_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1
                    }
                )
                if user_post:
                    if user_post['streak'] == user_post['high']:
                        classic_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "streak":1,
                                    "high":1,
                                    "correct":1
                                }
                            }
                        )
                        if (user_post['streak']+1)%500==0:
                            msg_s = f"n{(user_post['streak']+1)}"
                    else:
                        classic_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "streak":1,
                                    "correct":1
                                }
                            }
                        )
                        if (user['streak']+1)%500==0:
                            msg_s = f"{(user_post['streak']+1)}"
                    mode = "2"
                else:
                    classic_collection.insert_one(
                        {
                            "_id":user_id,
                            "name":f"{author}",
                            "correct":1,
                            "wrong":0,
                            "streak":1,
                            "high":1
                        }
                    )
            except Exception:
                return
        # elif channel == abc_channel and re.match("[a-zA-Z]", number_str):
        #     number = letter_calc(number_str)
        #     if abc_collection.find_one({"_id":user_id}):
        #         user_post = abc_collection.find_one(
        #             {"_id":user_id},
        #             {"streak":1,"high":1}
        #         )
        #         if user_post['streak'] == user_post['high']:
        #             abc_collection.update_one(
        #                 {"_id":user_id},
        #                 {
        #                     "$inc":{"streak":1,"high":1,"correct":1}
        #                 }
        #             )
        #             if (user_post['streak']+1)%500==0:
        #                 msg_s = f"n{(user['streak']+1)}"
        #         else:
        #             abc_collection.update_one(
        #                 {"_id":user_id},
        #                 {
        #                     "$inc":{"streak":1,"correct":1}
        #                 }
        #             )
        #             if (user_post['streak']+1)%500==0:
        #                 msg_s = f"{(user['streak']+1)}"
        #         mode = "3"
        #     elif author.id == 789949322032316416:
        #         pass
        #     else:
        #         abc_collection.insert_one(
        #             {
        #                 "_id":user_id,
        #                 "name":f"{author}",
        #                 "correct":1,
        #                 "wrong":0,
        #                 "current_saves":1,
        #                 "total_saves":5,
        #                 "streak":1,
        #                 "high":1,
        #                 "counter":False
        #             }
        #         )
        elif channel == beta_channel and re.match("[a-zA-Z]",number_str):
            try:
                number = letter_calc(number_str)
            except Exception:
                return
            if beta_collection.find_one({"_id":user_id}):
                beta_collection.update_one(
                    {
                        "_id":user_id
                    }, {
                       "$inc":
                        {
                           "correct":1
                        }
                    }
                )
        elif channel == numselli_channels['binary'] and \
                re.match("[01]",number_str) :
            try:
                number = int(number_str, 2)
            except Exception:
                return
        elif channel == numselli_channels['hex'] and \
                re.match("[0-9a-fA-F]",number_str):
            try:
                number = int(number_str, 16)
            except Exception:
                return
        elif channel == numselli_channels["letters"] and \
                re.match("[a-zA-Z]",number_str):
            try:
                number = letter_calc(number_str)
            except Exception:
                return
        else: 
            return
        if number%100 == 0 and number!=0:
            if number%500 == 0:
                if number%1000 == 0 and channel != classic_channel:
                    await message.add_reaction("❤️‍🔥")
                    milestone = bot.get_channel(mile_channel)
                    if channel == og_channel:
                        sen = ""
                        while(len(number_str)>0):
                            sen = number_str[-3:] + sen
                            number_str = number_str[:-3]
                            if len(number_str)>0:
                                sen = "," + sen
                        time_now = message.created_at.replace(tzinfo=None,microsecond=0)
                        time_diff = time_now - epoch_time
                        total_seconds = int(time_diff.total_seconds())
                        msg = f"Reached **{sen}** in <#{channel}> - "
                        msg += f"<t:{total_seconds}:F>"
                        await milestone.send(msg)
                    else:
                        num_str = str(number)
                        sen = ""
                        while(len(num_str)>0):
                            sen = num_str[-3:] + sen
                            num_str = num_str[:-3]
                            if len(num_str)>0:
                                sen = "," + sen
                        time_now = message.created_at.replace(tzinfo=None,microsecond=0)
                        time_diff = time_now - epoch_time
                        total_seconds = int(time_diff.total_seconds())
                        msg = f"Reached **{number_str}** ({sen}) in "
                        msg += f"<#{channel}> - <t:{total_seconds}:F>"
                        await milestone.send(msg)
                else:
                    await message.add_reaction("🔥")
            else:
                await message.add_reaction("💯")
        elif number%100 == 69:
            await message.add_reaction("<:emoji69:915053989895221248>")
        elif number%1000 == 404:
            await message.add_reaction("🤖") 
        elif number%1000 == 420:
            await message.add_reaction("🌿")
        elif number%1000 == 666:
            await message.add_reaction("<:blobdevil:915054491227795477>")
        if re.match("n", msg_s):
            scores = bot.get_channel(bot_channel)
            msg = f"**{author.display_name}** has reached a new streak of "
            msg += f"**{str(msg_s)[1:]}** with {mode_list[mode]}"
            embedVar = Embed(description=msg,color=color_lamuse)
            await scores.send(embed=embedVar)
            await message.add_reaction("<:blobyes:915054339796639745>")
        elif re.match("\d", msg_s):
            scores = bot.get_channel(bot_channel)
            msg = f"**{author.display_name}** has reached a streak of "
            msg += f"**{msg_s}** with {mode_list[mode]}"
            embedVar = Embed(description=msg,color=color_lamuse)
            await scores.send(embed=embedVar)
            await message.add_reaction("<:blobyes:915054339796639745>")

    """To reset streak if error is made"""
    if (re.findall("You have used", content) or \
            re.findall("RUINED", content, re.I) or \
            re.search("Wrong number!", content)) and author.bot == True : 
        if message.mentions:
            user_id = message.mentions[0].id
            if channel == og_channel and author.id == og_bot:
                user_post = og_collection.find_one(
                    {"_id":user_id},
                    {"streak":1,"high":1}
                )
                final_streak = user_post['streak'] - 1
                if user_post['streak'] == user_post['high']:
                    og_collection.update_one(
                        {
                            "_id":user_id
                        }, {
                            "$inc":
                            {
                                "high":-1,
                                "wrong":1,
                                "correct":-1,
                                "current_saves":-1
                            },
                            "$set":
                            {
                                "streak":0
                            }
                        }
                    )
                else:
                    og_collection.update_one(
                        {
                            "_id":user_id
                        }, {
                            "$inc":
                            {
                                "wrong":1,
                                "correct":-1,
                                "current_saves":-1
                            },
                            "$set":
                            {
                                "streak":0
                            }
                        }
                    )
                mode="1" 
            elif channel == classic_channel and author.id == classic_bot:
                user_post = classic_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1
                    }
                )
                final_streak = user_post['streak'] - 1
                if user_post['streak'] == user_post['high']:
                    classic_collection.update_one(
                        {
                            "_id":user_id
                        }, {
                            "$inc":
                            {
                                "high":-1,
                                "wrong":1,
                                "correct":-1
                            },
                            "$set":
                            {
                                "streak":0
                            }
                        }
                    )
                else:
                    classic_collection.update_one(
                        {"_id":user_id},
                        {
                            "$inc":
                            {
                                "wrong":1,
                                "correct":-1
                            },
                            "$set":
                            {
                                "streak":1
                            }
                        }
                    )
                mode="2"
            # elif channel == abc_channel and author.id == abc_bot:
            #     user_post = abc_collection.find_one(
            #         {"_id":user_id},
            #         {"streak":1,"high":1}
            #     )
            #     final_streak = user_post['streak'] - 1
            #     if user_post['streak'] == user_post['high']:
            #         abc_collection.update_one(
            #             {
            #                 "_id":user_id
            #             }, {
            #                 "$inc":
            #                 {
            #                     "high":-1,
            #                     "wrong":1,
            #                     "correct":-1,
            #                     "current_saves":-1
            #                 },
            #                 "$set":
            #                 {
            #                     "streak":0
            #                 }
            #             }
            #         )
            #     else:
            #         abc_collection.update_one(
            #             {
            #                 "_id":user_id
            #             }, {
            #                 "$inc":
            #                 {
            #                     "wrong":1,
            #                     "correct":-1,
            #                     "current_saves":-1
            #                 },
            #                 "$set":
            #                 {
            #                     "streak":0
            #                 }
            #             }
            #         )
            #     mode="3"
            elif channel == beta_channel and author.id == beta_bot:
                beta_collection.update_one(
                    {
                        "_id":user_id
                    },
                    {
                        "$inc":
                        {
                            "wrong":1,
                            "correct":-1,
                            "current_saves":-1
                        }
                    }
                )
                return
            else:
                return
            final_streak = user_post['streak']-1
            scores = bot.get_channel(bot_channel)
            msg = f"**{message.mentions[0].display_name}**'s streak with "
            msg += f"{mode_list[mode]} has been reset from **{final_streak}** to 0"
            embedVar = Embed(title="Streak Ruined",description=msg,color=color_lamuse)
            await scores.send(embed=embedVar)

    """All functions related to og bot"""
    if author.id == og_bot:
        if message.embeds:
            embed_content = message.embeds[0].to_dict()
            if 'description' in embed_content.keys() and \
                    'fields' in embed_content.keys():
                descript = embed_content['description']
                if re.findall("You currently have",descript):
                    saves = descript.split("**")[1]
                    current_saves = float(saves.split("/")[0])
                    total_saves = int(saves.split("/")[1])
                    ogsave:dRole = guild.get_role(og_save_id)
                    dishonorable:dRole = guild.get_role(dishonorable_id)
                    user_post = misc.find_one({"_id":"c!vote"})
                    user = guild.get_member(user_post['user'])
                    if user:
                        if og_collection.find_one({"_id":user.id}):
                            og_collection.update_one(
                                {
                                    "_id":user.id
                                }, {
                                    "$set":
                                    {
                                        "current_saves":current_saves,
                                        "total_saves":total_saves
                                    }
                                }
                            )
                        else:
                            msg = "Run `c!user` first"
                            await message.reply(msg)
                            return
                        if dishonorable in user.roles:
                            await user.remove_roles(ogsave)
                            await message.add_reaction("❌")
                        elif current_saves >= 1:
                            if ogsave not in user.roles:
                                await user.add_roles(ogsave)
                                msg = f"<@{user.id}> can now count in <#{og_channel}>"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("✅")
                        else:
                            if ogsave in user.roles:
                                await user.remove_roles(ogsave)
                                msg = f"<@{user.id}> does not have enough saves "
                                msg += f"to count in <#{og_channel}>"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("❌")
                    register_list = misc.find_one({"_id":"ogregister"})
                    if f"{user.id}" in register_list:
                        if register_list[f"{user.id}"] == True:
                            field1 = embed_content['fields'][0]['value']
                            field2 = embed_content['fields'][1]['value']
                            if re.search("You have already",field1):
                                time1 = re.findall("[\d\.]+",field1)
                                hour1 = float(time1[1]) + 0.05
                                time_now = datetime.utcnow().replace(microsecond=0)
                                time_new = time_now + timedelta(hours=hour1)
                                if time_collection.find_one(
                                    {
                                        "user":user.id,
                                        "command":"vote in Discords.com"
                                    }
                                ):
                                    time_collection.update_one(
                                        {
                                            "user":user.id,
                                            "command":"vote in Discords.com"
                                        }, {
                                            "$set":
                                            {
                                                "time":time_new
                                            }
                                        }
                                    )
                                else:
                                    time_collection.insert_one(
                                        {
                                            "time":time_new,
                                            "user":user.id,
                                            "command":"vote in Discords.com"
                                        }
                                    )
                            if re.search("You have already", field2):
                                time2 = re.findall("[\d\.]+",field2)
                                hour2 = float(time2[1]) + 0.05
                                time_now = datetime.utcnow().replace(microsecond=0)
                                time_new = time_now + timedelta(hours=hour2)
                                if time_collection.find_one(
                                    {
                                        "user":user.id,
                                        "command":"vote in top.gg"
                                    }
                                ):
                                    time_collection.update_one(
                                        {
                                            "user":user.id,
                                            "command":"vote in top.gg"
                                        }, {
                                            "$set":
                                            {
                                                "time":time_new
                                            }
                                        }
                                    )
                                else:
                                    time_collection.insert_one(
                                        {
                                            "time":time_new,
                                            "user":user.id,
                                            "command":"vote in top.gg"
                                        }
                                    )
            elif 'fields' in embed_content.keys():
                if embed_content['fields'][0]['name'] == "Global Stats":
                    user_test = misc.find_one({"_id":"c!user"})
                    user = guild.get_member(user_test['user'])
                    if user:
                        desc = embed_content['fields'][0]['value']
                        correct = desc.split("**")[3]
                        wrong = desc.split("**")[5]
                        saves = desc.split("**")[9]
                        current_saves = float(saves.split("/")[0])
                        total_saves = int(saves.split("/")[1])
                        cor = wro = 0
                        for i in correct.split(","):
                            cor = cor * 1000 + int(i)
                        for i in wrong.split(","):
                            wro = wro * 1000 + int(i)
                        if og_collection.find_one({"_id":user.id}):
                            og_collection.update_one(
                                {
                                    "_id":user.id
                                },
                                {
                                    "$set":
                                    {
                                        "name":f"{user}",
                                        "correct":cor,
                                        "wrong":wro,
                                        "current_saves":current_saves,
                                        "total_saves":total_saves
                                    }
                                }
                        )
                        else:
                            og_collection.insert_one(
                                {
                                    "_id":user.id,
                                    "name":f"{user}",
                                    "correct":cor,
                                    "wrong":wro,
                                    "current_saves":current_saves,
                                    "total_saves":total_saves,
                                    "streak":0,
                                    "high":0,
                                    "counter":False
                                }
                            )
                        og_save:dRole = guild.get_role(og_save_id)
                        dishonorable:dRole = guild.get_role(dishonorable_id)
                        if dishonorable in user.roles:
                            await user.remove_roles(og_save)
                            await message.add_reaction("❌")
                        elif current_saves >= 1:
                            if og_save in user.roles:
                                await message.add_reaction("✅")
                            else:
                                await user.add_roles(og_save)
                                msg = f"<@{user.id}> can now "
                                msg += f"count in <#{og_channel}>"
                                await message.channel.send(msg)
                        else:
                            if og_save in user.roles:
                                await user.remove_roles(og_save)
                                msg = f"<@{user.id}> doesn't have enough saves "
                                msg += f"and cannot count in <#{og_channel}>"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("❌")
            elif 'description' in embed_content.keys():
                descript = embed_content['description']
                if re.findall("saves have been deducted",descript):
                    user_post = misc.find_one({"_id":"c!transfersave"})
                    user:Member = guild.get_member(user_post['user'])
                    current_saves = float(descript.split("`")[5])
                    og_collection.update_one(
                        {
                            "_id":user.id
                        }, {
                            "$set":
                            {
                                "current_saves":current_saves
                            }
                        }
                    )
                    if current_saves < 1:
                        ogsave:dRole = guild.get_role(og_save_id)
                        if ogsave in user.roles:
                            await user.remove_roles(ogsave)
                            msg = f"You can no longer count in <#{og_channel}>"
                            msg += f"till you have 1 save <@{user.id}>"
                            await message.channel.send(msg)
                    else:
                        await message.add_reaction("💾")
                    int_list = re.findall("\d+" ,descript)
                    user2_id = int(int_list[2])
                    og_collection.update_one(
                        {
                            "_id":user2_id
                        }, {
                            "$inc":
                            {
                                "current_saves":1
                            }
                        }
                    )

    """All functions related to classic counting"""
    if author.id == classic_bot:
        if message.embeds:
            embed_content = message.embeds[0].to_dict()
            if 'author' in embed_content.keys():
                name = embed_content['author']['name']
                user = guild.get_member_named(name)
                desc = embed_content['description']
                if user:
                    if re.findall("Correct numbers",desc):
                        correct = desc.split("**")[3]
                        wrong = desc.split("**")[5]
                        cor = wro = 0
                        for i in correct.split(","):
                            cor = cor * 1000 + int(i)
                        for i in wrong.split(","):
                            wro = wro * 1000 + int(i)
                        if classic_collection.find_one({"_id":user.id}):
                            classic_collection.update_one(
                                {"_id":user.id},
                                {
                                    "$set":
                                    {
                                        "name":f"{user}",
                                        "correct":cor,
                                        "wrong":wro
                                    }
                                }
                            )
                        else:
                            classic_collection.insert_one(
                                {
                                    "_id":user.id,
                                    "name":f"{user}",
                                    "correct":cor,
                                    "wrong":wro,
                                    "streak":0,
                                    "high":0
                                }
                            )

    """All function related to ABC Counting"""
    # if author.id == abc_bot:
    #     if message.embeds:
    #         embed_content = message.embeds[0].to_dict()
    #         title = embed_content['title']
    #         if re.findall('stats',title):
    #             if embed_content['fields'][3]['name']=="Saves":
    #                 name = title[:-8]
    #                 user = guild.get_member_named(name)
    #                 if user:
    #                     field_content = embed_content['fields'][3]
    #                     current_saves = float(field_content['value'].split("/")[0][1:])
    #                     if current_saves == int(current_saves):
    #                         current_saves = int(current_saves)
    #                     total_saves = int(field_content['value'].split("/")[1][:-1])
    #                     correct = int(re.split(" ",embed_content['fields'][0]['value'])[0][1:])
    #                     wrong = int(embed_content['fields'][1]['value'][1:-1])
    #                     if abc_collection.find_one({"_id":user.id}):
    #                         abc_collection.update_one(
    #                             {"_id":user.id},
    #                             {
    #                                 "$set":
    #                                 {
    #                                     "name":f"{user}",
    #                                     "correct":correct,
    #                                     "wrong":wrong,
    #                                     "current_saves":current_saves,
    #                                     "total_saves":total_saves
    #                                 }
    #                             }
    #                         )
    #                     else:
    #                         abc_collection.insert_one(
    #                             {
    #                                 "_id":user.id,
    #                                 "name":f"{user}",
    #                                 "correct":correct,
    #                                 "wrong":wrong,
    #                                 "current_saves":current_saves,
    #                                 "total_saves":total_saves,
    #                                 "streak":0,
    #                                 "high":0,
    #                                 "counter":False
    #                             }
    #                         )
    #     elif re.match("You bought that item recently.",content):
    #         time = re.findall("\d+",content)
    #         user = misc.find_one({"_id":"abc!shop"})
    #         time_now = datetime.utcnow()
    #         time_new = time_now + timedelta(hours=int(time[0]),minutes=int(time[1]))
    #         time_new= time_new.replace(tzinfo=None,microsecond=0)
    #         if time_collection.find_one({"user":user['user'],"command":"use abc!shop"}):
    #             time_collection.update_one(
    #                 {
    #                     "user":user['user'],
    #                     "command":"use abc!shop"
    #                 }, {
    #                     "$set":
    #                     {
    #                         "time":time_new
    #                     }
    #                 }
    #             )
    #         else:
    #             time_collection.insert_one(
    #                 {
    #                     "time":time_new,
    #                     "user":user['user'],
    #                     "command":"use abc!shop"
    #                 }
    #             )

    """All functions related to Beta Counting"""
    if author.id == beta_bot:
        if message.embeds:
            embed_content = message.embeds[0].to_dict()
            title = embed_content['title']
            if re.findall('stats',title):
                if embed_content['fields'][3]['name']=="Saves":
                    user_test = misc.find_one({"_id":"abc?u"})
                    user = guild.get_member(user_test['user'])
                    if user:
                        field_content = embed_content['fields'][3]
                        current_saves = float(field_content['value'].split("/")[0][1:])
                        if current_saves == int(current_saves):
                            current_saves = int(current_saves)
                        total_saves = int(field_content['value'].split("/")[1][:-1])
                        correct = int(re.split(" ",embed_content['fields'][0]['value'])[0][1:])
                        wrong = int(embed_content['fields'][1]['value'][1:-1])
                        if beta_collection.find_one({"_id":user_test['user']}):
                            beta_collection.update_one(
                                {
                                    "_id":user.id
                                }, {
                                    "$set":
                                    {
                                        "name":f"{user}",
                                        "correct":correct,
                                        "wrong":wrong,
                                        "current_saves":current_saves,
                                        "total_saves":total_saves
                                    }
                                }
                            )
                        else:
                            beta_collection.insert_one(
                                {
                                    "_id":user.id,
                                    "name":f"{user}",
                                    "correct":correct,
                                    "wrong":wrong,
                                    "current_saves":current_saves,
                                    "total_saves":total_saves,
                                    "counter":False
                                }
                            )
                        beta_save:dRole = guild.get_role(beta_save_id)
                        dishonorable:dRole = guild.get_role(dishonorable_id)
                        if dishonorable in user.roles:
                            await user.remove_roles(beta_save)
                            await message.add_reaction("❌")
                        elif current_saves >= 1:
                            if beta_save in user.roles:
                                await message.add_reaction("✅")
                            else:
                                await user.add_roles(beta_save)
                                msg = f"<@{user.id}> can now "
                                msg += f"count in <#{beta_channel}>"
                                await message.channel.send(msg)
                        else:
                            if beta_save in user.roles:
                                await user.remove_roles(beta_save)
                                msg = f"<@{user.id} doesn't have enough saves "
                                msg += f"and cannot count in <#{beta_channel}"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("❌")
        elif re.findall("Try again" ,content):
            time = re.findall("\d+",content)
            user = misc.find_one({"_id":"abc?d"})
            time_now = datetime.utcnow().replace(microsecond=0)
            hour, min = int(time[0]), int(time[1])
            if hour == 0 and min == 0:
                min = 1
            time_new = time_now + timedelta(hours=hour,minutes=min)
            if time_collection.find_one({"user":user['user'],"command":"use abc?d"}):
                time_collection.update_one(
                    {
                        "user":user['user'],
                        "command":"use abc?d"
                    }, {
                        "$set":
                        {
                            "time":time_new
                        }
                    }
                )
            else:
                time_collection.insert_one(
                    {
                        "time":time_new,
                        "user":user['user'],
                        "command":"use abc?d"
                    }
                )
        elif re.findall("You have been given",content):
            user = misc.find_one({"_id":"abc?d"})
            time_now = datetime.utcnow().replace(microsecond=0)
            time_new = time_now + timedelta(days=1)
            if time_collection.find_one({"user":user['user'],"command":"use abc?d"}):
                time_collection.update_one(
                    {
                        "user":user['user'],
                        "command":"use abc?d"
                    }, {
                        "$set":
                        {
                            "time":time_new
                        }
                    }
                )
            else:
                time_collection.insert_one(
                    {
                        "time":time_new,
                        "user":user['user'],
                        "command":"use abc?d"
                    }
                )
        elif re.match("Sent the gift",content):
            user_test = misc.find_one({"_id":"abc?gift"})
            userID = user_test['user']
            user_post = beta_collection.find_one({"_id":userID})
            if user_post:
                user = guild.get_member(user_test['user'])
                beta_save:dRole = guild.get_role(beta_save_id)
                dishonorable:dRole = guild.get_role(dishonorable_id)
                actual_saves = user_post['current_saves'] + 1
                if dishonorable in user.roles:
                    await user.remove_roles(beta_save)
                    await message.add_reaction("❌")
                elif actual_saves >= 1:
                    if beta_save in user.roles:
                        await message.add_reaction("✅")
                    else:
                        await user.add_roles(beta_save)
                        msg = f"<@{user.id}> can now "
                        msg += f"count in <#{beta_channel}>"
                        await message.channel.send(msg)
                beta_collection.update_one(
                    {
                        "_id":userID
                    }, {
                        "$inc":
                        {
                            "current_saves":1
                        }
                    }
                )

    """For reading numselli embeds"""
    if author.id == numselli_bot:
        if message.embeds:
            embed_content = message.embeds[0].to_dict()
            if 'fields' in embed_content:
                field1 = embed_content['fields'][0]
                if re.match('Global Stats',field1['name']):
                    name = embed_content['title'].split(" ",2)[2]
                    nums = re.findall('[\d\.,]+',field1['value'])
                    correct = int(re.sub(',','',nums[1]))
                    wrong = int(re.sub(',','',nums[2]))
                    current_saves = float(nums[4])
                    total_saves = int(nums[5])
                    user = guild.get_member_named(name)
                    if user:
                        if numselli_collection.find_one({"_id":user.id}):
                            numselli_collection.update_one(
                                {
                                    "_id":user.id
                                }, {
                                    "$set":
                                    {
                                        "name":f"{user}",
                                        "correct":correct,
                                        "wrong":wrong,
                                        "current_saves":current_saves,
                                        "total_saves":total_saves
                                    }
                                }
                            )
                        else:
                            numselli_collection.insert_one(
                                {
                                    "_id":user.id,
                                    "name":f"{user}",
                                    "correct":correct,
                                    "wrong":wrong,
                                    "current_saves":current_saves,
                                    "total_saves":total_saves,
                                    "streak":0,
                                    "high":0,
                                    "counter":False
                                }
                            )
                        have_save:dRole = guild.get_role(have_save_id)
                        dishonorable:dRole = guild.get_role(dishonorable_id)
                        if dishonorable in user.roles:
                            await user.remove_roles(have_save)
                            await message.add_reaction("❌")
                        elif current_saves >= 1:
                            if have_save in user.roles:
                                await message.add_reaction("✅")
                            else:
                                await user.add_roles(have_save)
                                msg = f"<@{user.id}> can now "
                                msg += f"count with <@{numselli_bot}>"
                                await message.channel.send(msg)
                        else:
                            if have_save in user.roles:
                                await user.remove_roles(have_save)
                                msg = f"<@{user.id}> doesn't have enough saves "
                                msg += f"and cannot count with <@{numselli_bot}>"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("❌")
            if re.match('Sent',embed_content['title']):
                nums = re.findall('[\d\.,]+',embed_content['description'])
                sent_saves = float(nums[0])
                rec_id = int(nums[1])
                user_post = numselli_collection.find_one({"_id":rec_id})
                if user_post:
                    user = guild.get_member(rec_id)
                    actual_saves = user_post['current_saves'] + sent_saves
                    have_save:dRole = guild.get_role(have_save_id)
                    dishonorable:dRole = guild.get_role(dishonorable_id)
                    if dishonorable in user.roles:
                        await user.remove_roles(have_save)
                        await message.add_reaction("❌")
                    elif actual_saves >= 1:
                        if have_save in user.roles:
                            await message.add_reaction("✅")
                        else:
                            await user.add_roles(have_save)
                            msg = f"<@{user.id}> can now "
                            msg += f"count with <@{numselli_bot}>"
                            await message.channel.send(msg)
                    # else:
                    #     if have_save in user.roles:
                    #         await user.remove_roles(have_save)
                    #         msg = f"<@{user.id}> doesn't have enough saves "
                    #         msg += f"and cannot count with <@{numselli_bot}>"
                    #         await message.channel.send(msg)
                    #     else:
                    #         await message.add_reaction("❌")

    """For generating the next prime number"""
    if channel == prime_channel and re.match("\d", content):
        try:
            num = int(content.split()[0])
        except Exception:
            return

        def prime(num:int):
            f = False
            for i in range(3,int(math.sqrt(num))+1,2):
                if num % i ==0:
                    f = True
            return f

        def next_prime(num:int):
            f = True
            while(f):
                if num > 2:
                    num += 2
                else:
                    num += 1
                f = prime(num)
            return num

        if num == 2 or (num % 2 == 1 and num > 2):
            next_num = next_prime(num)
            await message.channel.send(f"`Next is {next_num}`")

    """Functions for dank memer"""
    if channel == dank_channel:
        if author.id == dank_bot:
            if message.mentions:
                if re.search("Better take care of your pet", content):
                    return
                userID = message.mentions[0].id
                register_list = dank_collection.find_one({"_id":"register"})
                if f"{userID}" in register_list:
                    if register_list[f"{userID}"] == True:
                        time_now = message.created_at.replace(tzinfo=None,microsecond=0)
                        if re.search("You need to wait",content):
                            nums = re.findall("\d+",content)
                            min, sec = int(nums[1]), int(nums[2])
                            time_new = time_now + timedelta(minutes=min,seconds=sec)
                            if dank_collection.find_one(
                                {
                                    "user":userID,
                                    "command":"go to work"
                                }
                            ):
                                dank_collection.update_one(
                                    {
                                        "user":userID,
                                        "command":"go to work"
                                    }, {
                                        "$set":
                                        {
                                            "time":time_new
                                        }
                                    }
                                )
                            else:
                                dank_collection.insert_one(
                                    {
                                        "time":time_new,
                                        "user":userID,
                                        "command":"go to work"
                                    }
                                )
                        else:
                            time_new = time_now + timedelta(hours=1)
                            if dank_collection.find_one(
                                {
                                    "user":userID,
                                    "command":"go to work"
                                }
                            ):
                                dank_collection.update_one(
                                    {
                                        "user":userID,
                                        "command":"go to work"
                                    }, {
                                        "$set":
                                        {
                                            "time":time_new
                                        }
                                    }
                                )
                            else:
                                dank_collection.insert_one(
                                    {
                                        "time":time_new,
                                        "user":userID,
                                        "command":"go to work"
                                    }
                                )
            # print(dir(message.reference))
            # ID = message.reference.message_id
            # print(ID)
            # print(guild.get_message(ID))

    """Functions related to user input"""
    if re.match("c!user",content,re.I):
        user = re.search("\d+",content)
        if user:
            userID = int(user.group())
        else:
            userID = int(author.id)
        if misc.find_one({"_id":"c!user"}):
            misc.update_one({"_id":"c!user"}, {"$set":{"user":userID}})
        else:
            misc.insert_one({"_id":"c!user","user":userID})
    if re.match("c!vote",content,re.I):
        if misc.find_one({"_id":"c!vote"}):
            misc.update_one({"_id":"c!vote"}, {"$set":{"user":author.id}})
        else:
            misc.insert_one({"_id":"c!vote","user":author.id})
    if re.match("c!transfersave",content,re.I):
        if misc.find_one({"_id":"c!transfersave"}):
            misc.update_one({"_id":"c!transfersave"}, {"$set":{"user":author.id}})
        else:
            misc.insert_one({"_id":"c!transfersave","user":author.id})
    if re.match("abc\?u",content):
        user = re.search("\d+",content)
        if user:
            userID = int(user.group())
        else:
            userID = int(author.id)
        if misc.find_one({"_id":"abc?u"}):
            misc.update_one({"_id":"abc?u"}, {"$set":{"user":userID}})
        else:
            misc.insert_one({"_id":"abc?u","user":userID})
    if re.match("abc\?d",content,re.I):
        if misc.find_one({"_id":"abc?d"}):
            misc.update_one({"_id":"abc?d"}, {"$set":{"user":author.id}})
        else:
            misc.insert_one({"_id":"abc?d","user":author.id})
    if re.match("abc\?gift",content):
        user = re.search("\d+",content)
        if user:
            userID = int(user.group())
            if misc.find_one({"_id":"abc?gift"}):
                misc.update_one({"_id":"abc?gift"}, {"$set":{"user":userID}})
            else:
                misc.insert_one({"_id":"abc?gift","user":userID})
    # if re.match("abc!shop",content,re.I):
    #     if misc.find_one({"_id":"abc!shop"}):
    #         misc.update_one({"_id":"abc!shop"}, {"$set":{"user":author.id}})
    #     else:
    #         misc.insert_one({"_id":"abc!shop","user":author.id})
    if len(content) > 0 and content[0] == ":" and content[-1] == ":":
        emoji_name:str = content[1:-1]
        for emoji in guild.emojis:
            if emoji_name == emoji.name:
                await message.reply(str(emoji))
                break

    # if message.channel.id == 931498728760672276:
    #     time = message.created_at.replace(tzinfo=None,microsecond=0)
    #     print(time)
    #     time_post = misc.find_one({"_id":"trial"})
    #     print(time_post)
    #     t1 = time - time_post["timetrial"]
    #     print(t1.total_seconds())

    await bot.process_commands(message)

@bot.event
async def on_presence_update(member_old:Member, member_new:Member):
    if member_new.bot == False:
        return
    if member_new.raw_status == member_old.raw_status:
        return
    overrides = misc.find_one({"_id":"override"})
    if member_new.id == classic_bot:
        if overrides['classic'] == True:
            return
        channel = bot.get_channel(classic_channel)
        role:dRole = member_new.guild.get_role(countaholic_id)
    elif member_new.id == og_bot:
        if overrides['og'] == True:
            return
        channel = bot.get_channel(og_channel)
        role:dRole = member_new.guild.get_role(og_save_id)
    elif member_new.id == abc_bot:
        if overrides['abc'] == True:
            return
        channel = bot.get_channel(abc_channel)
        role:dRole = member_new.guild.get_role(abc_save_id)
    elif member_new.id == prime_bot:
        if overrides['prime'] == True:
            return
        channel = bot.get_channel(prime_channel)
        role:dRole = member_new.guild.get_role(countaholic_id)
    # elif member_new.id == sasha_bot:
    #     channel = bot.get_channel(sasha_channel)
        role:dRole = member_new.guild.get_role(countaholic_id)
    elif member_new.id == numselli_bot :
        role:dRole = member_new.guild.get_role(have_save_id)
    else:
        return
    if member_old.raw_status=="online" and member_new.raw_status=="offline":
        if member_new.id == numselli_bot:
            for channel_name in numselli_channels:
                channel_id = numselli_channels[channel_name]
                channel = bot.get_channel(channel_id)
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=False)
                await channel.set_permissions(role,overwrite=overwrites)
                embedVar = Embed(description="Channel locked as bot is offline",color=color_lamuse)
                await channel.send(embed=embedVar)
        else:
            overwrites = channel.overwrites_for(role)
            overwrites.update(send_messages=False)
            embedVar = Embed(description="Channel locked as bot is offline",color=color_lamuse)
            await channel.set_permissions(role,overwrite=overwrites)
            await channel.send(embed=embedVar)
    elif member_old.raw_status=="offline" and member_new.raw_status=="online":
        if member_new.id == numselli_bot:
            for channel_name in numselli_channels:
                channel_id = numselli_channels[channel_name]
                channel = bot.get_channel(channel_id)
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=True)
                await channel.set_permissions(role,overwrite=overwrites)
                embedVar = Embed(description="Channel unlocked as bot is online",color=color_lamuse)
                await channel.send(embed=embedVar)
        else:
            overwrites = channel.overwrites_for(role)
            overwrites.update(send_messages=True)
            embedVar = Embed(description="Channel unlocked as bot is online",color=color_lamuse)
            await channel.set_permissions(role,overwrite=overwrites)
            await channel.send(embed=embedVar)
    else:
        return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You do not have the required permissions to use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Command is missing an argument")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("You don't have the required permissions. ")
    elif isinstance(error, commands.BadLiteralArgument):
        await ctx.reply("Not a valid choice")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        raise error

@tasks.loop(seconds=0.9)
async def check_time():
    time_now = datetime.utcnow().replace(tzinfo=None,microsecond=0)
    if time_collection.find_one({"time":time_now}):
        time_cursor = time_collection.find({"time":time_now})
        scores = bot.get_channel(scores_channel)
        for cursor in time_cursor:
            user = cursor['user']
            command = cursor['command']
            await scores.send(f"<@{user}> time to {command}")
            time_collection.delete_one(cursor)
    if dank_collection.find_one({"time":time_now}):
        time_cursor = dank_collection.find({"time":time_now})
        dank_chnl = bot.get_channel(dank_channel)
        for cursor in time_cursor:
            user = cursor['user']
            command = cursor['command']
            await dank_chnl.send(f"<@{user}> time to {command}")
            dank_collection.delete_one(cursor)

r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

bot.add_cog(List(bot))
bot.add_cog(Stats(bot))
bot.add_cog(AdminCommands(bot))
bot.add_cog(Reminders(bot))
bot.add_cog(Vote(bot))
bot.run(secrets.BOT_TOKEN)