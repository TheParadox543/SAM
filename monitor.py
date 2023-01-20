import asyncio
from datetime import timedelta, timezone
import json
import logging
import math
import re
from typing import Union

import nextcord
from nextcord import Interaction, Embed, Member, Message, Role, TextChannel
from nextcord import utils
from nextcord.ext import commands, tasks

from bot_secrets import *
from database import *

# Using the logs.
logger_monitor = logging.getLogger(__name__)
logger_monitor.setLevel(logging.DEBUG)
handler = logging.FileHandler("SAM.log")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger_monitor.addHandler(handler)

class Monitor(commands.Cog):
    """Monitor the channels and control permissions to count in channels."""

    def __init__(self, bot:commands.Bot):
        """Initialize the cog."""
        self.bot = bot
        try: 
            with open("run_time.txt", "r") as file:
                time_str:str = json.load(file)
        except FileNotFoundError:
            time_str = EPOCH.isoformat()
        except:
            time_str = EPOCH.isoformt()
        finally:
            self.og_start_count = datetime.fromisoformat(time_str).replace(
                tzinfo=timezone.utc
            )
            if utils.utcnow() - self.og_start_count >= timedelta(hours=1):
                self.og_last_count = EPOCH
            else:
                self.og_last_count = self.og_start_count
        self.og_count = 0
        self.check_time_og.start()

    @commands.Cog.listener()
    async def on_message(self, message:Message):
        if message.author == self.bot.user: #ignores if message from bot
            return

        content = message.content
        author:Member = message.author
        channel = message.channel.id
        guild:nextcord.Guild = message.guild

        """To update user streak if correct and milestone update"""
        if track_list.count(channel) > 0 and \
                len(content.split()) > 0 and \
                re.match("\w", content) and author.bot == False:
            number_str = content.split()[0]
            number_str = number_str.upper()
            user = author
            user_id = author.id
            msg_s = ""
            if channel == og_channel and re.match("\d", number_str):
                try:
                    number = int(number_str)
                except:
                    return
                if number == 0:
                    pass
                user_post:dict = og_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1,
                        "alt":1
                    }
                )
                if user_post is not None:
                    if "alt" in user_post:
                        user_main = user_post.get("alt")
                        user = guild.get_member(user_main)
                        user_post2:dict = og_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        streak = user_post2.get("streak", 0)
                        if streak == user_post2.get("high", 0):
                            og_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (streak + 1)%500 == 0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            og_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (streak + 1)%500 == 0:
                                msg_s = f"{(streak+1)}"
                        og_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc": {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        streak = user_post.get("streak", 0)
                        if streak == user_post.get("high", 0):
                            og_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                        "correct":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (streak + 1)%500 == 0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            og_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "correct":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (streak + 1)%500 == 0:
                                msg_s = f"{(streak+1)}"
                    mode = "1"
                time_now = message.created_at
                time_diff = time_now - self.og_last_count
                if abs(time_diff) >= timedelta(minutes=10) \
                        or self.og_start_count == EPOCH:
                    if self.og_count >= 50:
                        start = utils.format_dt(self.og_start_count, "T")
                        stop = utils.format_dt(self.og_last_count, "T")
                        scores_chnl:TextChannel = guild.get_channel(sam_channel)
                        msg = f"Last run in <#{og_channel}> had "
                        msg += f"**{self.og_count}** numbers."
                        msg += f"\nRun started from {start} to {stop}."
                        try:
                            await scores_chnl.send(msg)
                        except nextcord.errors.Forbidden:
                            logger_monitor.error(f"Couldn't send message in {scores_chnl}")
                    self.og_start_count = time_now
                    self.og_count = 1
                    try:
                        with open("run_time.txt", "w") as file:
                            json.dump(self.og_start_count.isoformat(), file)
                    except:
                        logger_monitor.error("Couldn't save run start.")
                    try:
                        chnl_name = f"og-counting-{time_now.minute}-{time_now.second}"
                        await message.channel.edit(name=chnl_name)
                    except nextcord.Forbidden:
                        await message.channel.send("Editing channel name failed.")
                        logger_monitor.exception("Editing channel name failed.")
                else:
                    self.og_count += 1
                self.og_last_count = time_now
            elif channel == classic_channel and re.match("\d", number_str):
                try:
                    number = int(number_str)
                except:
                    return
                if number == 0:
                    pass
                user_post = classic_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1,
                        "alt":1
                    }
                )
                if user_post is not None:
                    if "alt" in user_post:
                        user_main = user_post.get("alt")
                        user = guild.get_member(user_main)
                        user_post2:dict = classic_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        streak = user_post2.get("streak", 0)
                        if streak == user_post2.get("high", 0):
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
                        classic_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc": {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        streak = user_post.get("streak", 0)
                        if streak == user_post.get("high", 0):
                            classic_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            classic_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
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
            elif channel == beta_channel and re.match("[a-zA-Z]", number_str):
                try:
                    number = self.letter_calc(number_str)
                except:
                    return
                user_post =  beta_collection.find_one({"_id":user_id})
                if user_post is not None:
                    if "alt" in user_post:
                        user_main = user_post.get("alt")
                        user = guild.get_member(user_main)
                        user_post2:dict = beta_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        streak = user_post2.get("streak", 0)
                        if streak == user_post2.get("high", 0):
                            beta_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            beta_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
                        beta_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc": {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        streak = user_post.get("streak", 0)
                        if streak == user_post.get("high", 0):
                            beta_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            beta_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
                    mode = "4"
            elif channel in numselli_channels.values():
                if channel == numselli_channels["whole"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(number_str)
                    except:
                        return
                elif channel == numselli_channels["letters"] and \
                        re.match("[a-zA-Z]",number_str):
                    try:
                        number = self.letter_calc(number_str)
                    except:
                        return
                elif channel == numselli_channels['binary'] and \
                        re.match("[01]",number_str) :
                    try:
                        number = int(number_str, 2)
                    except:
                        return
                elif channel == numselli_channels["decimal"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(float(number_str)*10)
                    except:
                        return
                elif channel == numselli_channels['hex'] and \
                        re.match("[0-9a-fA-F]",number_str):
                    try:
                        number = int(number_str, 16)
                    except:
                        return
                elif channel == numselli_channels["roman"] and \
                        re.match("[IVXLCDM]", number_str):
                    try:
                        i = 0
                        number = 0
                        while i < len(number_str):
                            if i+1<len(number_str) and number_str[i:i+2] in roman:
                                number+=roman[number_str[i:i+2]]
                                i+=2
                            else:
                                #print(i)
                                number+=roman[number_str[i]]
                                i+=1
                    except:
                        return
                elif channel == numselli_channels["two"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(int(number_str)/2)
                    except:
                        return
                elif channel == numselli_channels["five"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(int(number_str)/5)
                    except:
                        return
                elif channel == numselli_channels["ten"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(int(number_str)/10)
                    except:
                        return
                elif channel == numselli_channels["hundred"] and \
                        re.match("\d", number_str):
                    try:
                        number = int(int(number_str)/100)
                    except:
                        return
                else:
                    return
                user_post:dict = numselli_collection.find_one(
                    {
                        "_id":user_id
                    }, {
                        "streak":1,
                        "high":1,
                        "alt":1
                    }
                )
                if user_post is not None:
                    if "alt" in user_post:
                        user_main = user_post.get("alt")
                        user = guild.get_member(user_main)
                        user_post2:dict = numselli_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        streak = user_post2.get("streak", 0)
                        if streak == user_post2.get("high", 0):
                            numselli_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            numselli_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "streak":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
                        numselli_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc": {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        streak = user_post.get("streak", 0)
                        if streak == user_post.get("high", 0):
                            numselli_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "high":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"n{(streak+1)}"
                        else:
                            numselli_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "streak":1,
                                        "correct":1
                                    }
                                }
                            )
                            if (streak+1)%500==0:
                                msg_s = f"{(streak+1)}"
                    mode = "5"
            else: 
                return
            rev_num = number_str[::-1]
            if rev_num == number_str and len(rev_num) > 1:
                await message.add_reaction("↔️")
            if number%100 == 0 and number!=0:
                if number%500 == 0:
                    if number%1000 == 0 and channel != classic_channel:
                        await message.add_reaction("❤️‍🔥")
                        milestone = self.bot.get_channel(mile_channel)
                        time = int(message.created_at.timestamp())
                        if number==3_000_000:
                            msg = f"**WE HIT __THREE MILLION__** at <t:{time}:F>. "
                            msg += "**THIS IS AMAZING. LET'S KEEP GOING.**"
                            await milestone.send(msg)
                        else:
                            if channel == og_channel \
                                    or channel == numselli_channels["whole"]:
                                sen = ""
                                while(len(number_str)>0):
                                    sen = number_str[-3:] + sen
                                    number_str = number_str[:-3]
                                    if len(number_str)>0:
                                        sen = "," + sen
                                msg = f"Reached **{sen}** in <#{channel}> - "
                                msg += f"<t:{time}:F>"
                            else:
                                num_str = str(number)
                                sen = ""
                                while(len(num_str)>0):
                                    sen = num_str[-3:] + sen
                                    num_str = num_str[:-3]
                                    if len(num_str)>0:
                                        sen = "," + sen
                                msg = f"Reached **{number_str}** ({sen}) in "
                                msg += f"<#{channel}> - <t:{time}:F>"
                            await milestone.send(msg)
                    else:
                        await message.add_reaction("🔥")
                else:
                    await message.add_reaction("💯")
            elif number%100 == 69:
                await message.add_reaction("<:emoji69:915053989895221248>")
            elif number%1000 == 161:
                await message.add_reaction("🌀")
            elif number%1000 == 271:
                await message.add_reaction("🇪")
            elif number%1000 == 314:
                await message.add_reaction("🥧")
            elif number%1000 == 404:
                await message.add_reaction("🤖") 
            elif number%1000 == 420:
                await message.add_reaction("🌿")
            elif number%1000 == 666:
                await message.add_reaction("<:blobdevil:915054491227795477>")
            elif number%1000 == 711:
                await message.add_reaction("<:7eleven:1029416348671016980>")
            elif number%1000 == 747:
                await message.add_reaction("✈️")
            elif number%1000 == 777:
                await message.add_reaction("🎰")
            elif number%1000 == 911:
                await message.add_reaction("💥")
            elif number%10_000 == 3108:
                await message.add_reaction("💡")
            if re.match("n", msg_s):
                scores = self.bot.get_channel(sam_channel)
                msg = f"**{user.display_name}** has reached a new streak of "
                msg += f"**{str(msg_s)[1:]}** with {mode_list[mode]}"
                embedVar = Embed(description=msg,color=color_lamuse)
                await scores.send(embed=embedVar)
                await message.add_reaction("<:blobyes:915054339796639745>")
            elif re.match("\d", msg_s):
                scores = self.bot.get_channel(sam_channel)
                msg = f"**{user.display_name}** has reached a streak of "
                msg += f"**{msg_s}** with {mode_list[mode]}"
                embedVar = Embed(description=msg,color=color_lamuse)
                await scores.send(embed=embedVar)
                await message.add_reaction("<:blobyes:915054339796639745>")

        """To reset streak if error is made"""
        if ((re.findall("You have used", content) or # for og and beta
                re.findall("RUINED", content, re.I) or # for classic
                re.search("Wrong number!", content)) # for beta?
                and author.bot == True) : 
            if message.mentions:
                user = message.mentions[0]
                user_id = message.mentions[0].id
                if channel == og_channel and author.id == og_bot:
                    if re.findall("guild save", content):
                        await self.ruin_ban(user)
                        msg_send = "Why did you count without a save "
                        msg_send += f"{user.mention}!!!"
                        await message.channel.send(msg_send)
                        return
                    saves_left = float(re.findall("\d+\.*\d*", content)[2])
                    og_save:Role = guild.get_role(og_save_id)
                    dishonorable:Role = guild.get_role(dishonorable_id)
                    if dishonorable in user.roles:
                        await user.remove_roles(og_save)
                        await message.add_reaction("❌")
                    elif saves_left >= 1:
                        await message.add_reaction("✅")
                    else:
                        await user.remove_roles(og_save)
                        msg = f"No more saves left for <@{user.id}>!"
                        await message.channel.send(msg)
                        await message.add_reaction("❌")
                    user_post = og_collection.find_one(
                        {
                            "_id":user_id
                        }, {
                            "streak":1,
                            "high":1,
                            "alt":1
                        }
                    )
                    if "alt" in user_post:
                        user_main = user_post["alt"]
                        user = guild.get_member(user_main)
                        user_post2 = og_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        final_streak = user_post2["streak"] - 1
                        if user_post2['streak'] == user_post2['high']:
                            og_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "high":-1,
                                        "daily":-1
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
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "daily":-1
                                    },
                                    "$set":
                                    {
                                        "streak":0
                                    }
                                }
                            )
                        og_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "correct":-1,
                                    "wrong":1,
                                }, 
                                "$set": {
                                    "current_saves": saves_left,
                                }
                            }
                        )
                    else:
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
                                        "daily":-1
                                    },
                                    "$set":
                                    {
                                        "current_saves": saves_left,
                                        "streak":0,
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
                                        "daily":-1
                                    },
                                    "$set":
                                    {
                                        "current_saves": saves_left,
                                        "streak":0,
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
                            "high":1,
                            "alt":1
                        }
                    )
                    if "alt" in user_post:
                        user_main = user_post["alt"]
                        user = guild.get_member(user_main)
                        user_post2 = classic_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        final_streak = user_post2["streak"] - 1
                        if user_post2['streak'] == user_post2['high']:
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "high":-1
                                    },
                                    "$set":
                                    {
                                        "streak":0
                                    }
                                }
                            )
                        else:
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$set":
                                    {
                                        "streak":0
                                    }
                                }
                            )
                        classic_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "correct":-1,
                                    "wrong":1
                                }
                            }
                        )
                    else:
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
                elif channel == beta_channel and author.id == beta_bot:
                    saves_left = int(re.findall("\d+", content)[1])
                    beta_save:Role = guild.get_role(beta_save_id)
                    dishonorable:Role = guild.get_role(dishonorable_id)
                    if dishonorable in user.roles:
                        await user.remove_roles(beta_save)
                        await message.add_reaction("❌")
                    elif saves_left >= 1:
                        await message.add_reaction("✅")
                    else:
                        await user.remove_roles(beta_save)
                        msg = f"No saves left for <@{user.id}!"
                        await message.channel.send(msg)
                        await message.add_reaction("❌")
                    user_post = beta_collection.find_one(
                        {
                            "_id":user_id
                        }, {
                            "streak":1,
                            "high":1,
                            "alt":1
                        }
                    )
                    if "alt" in user_post:
                        user_main = user_post["alt"]
                        user = guild.get_member(user_main)
                        user_post2 = beta_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        final_streak = user_post2["streak"] - 1
                        if user_post2['streak'] == user_post2['high']:
                            beta_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc": {
                                        "high":-1
                                    },
                                    "$set": {
                                        "streak":0
                                    }
                                }
                            )
                        else:
                            beta_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$set": {
                                        "streak":0
                                    }
                                }
                            )
                        beta_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc": {
                                    "correct":-1,
                                    "wrong":1
                                }, 
                                "$set": {
                                    "current_saves": saves_left,
                                }
                            }
                        )
                    else:
                        final_streak = user_post['streak'] - 1
                        if user_post['streak'] == user_post['high']:
                            beta_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc": {
                                        "high":-1,
                                        "wrong":1,
                                        "correct":-1
                                    },
                                    "$set": {
                                        "streak": 0,
                                        "current_saves": saves_left,
                                    }
                                }
                            )
                        else:
                            beta_collection.update_one(
                                {"_id":user_id},
                                {
                                    "$inc": {
                                        "wrong":1,
                                        "correct":-1
                                    },
                                    "$set": {
                                        "streak": 0,
                                        "current_saves": saves_left,
                                    }
                                }
                            )
                    mode="4"
                else:
                    return
                scores = self.bot.get_channel(sam_channel)
                msg = f"**{user.display_name}**'s streak with "
                msg += f"{mode_list[mode]} has been reset from "
                msg += f"**{final_streak}** to 0"
                embedVar = Embed(
                    title="Streak Ruined",
                    description=msg,
                    color=color_lamuse
                )
                await scores.send(embed=embedVar)
        """If mistake is made in numselli bot, handled by numselli embed handler."""

        """All functions related to og bot"""

        """All functions related to classic counting"""
        if author.id == classic_bot:
            if message.embeds:
                embed_content = message.embeds[0].to_dict()
                if ("author" in embed_content and "fields" in embed_content):
                    name = embed_content["author"]["name"]
                    user = guild.get_member_named(name)
                    desc = embed_content["fields"][0]["value"]
                    if user:
                        correct = int(desc.split("**")[3].replace(",", ""))
                        wrong = int(desc.split("**")[5].replace(",", ""))
                        classic_collection.update_one(
                            {"_id":user.id},
                            {
                                "$set":
                                {
                                    "name":f"{user}",
                                    "correct":correct,
                                    "wrong":wrong,
                                }
                            }, True
                        )

        """All functions related to Beta Counting"""
        if author.id == beta_bot:
            if re.findall("Try again" ,content):
                time = re.findall("\d+",content)
                user = misc.find_one({"_id":"abc?d"})
                time_now = datetime.utcnow().replace(microsecond=0)
                try:
                    hour, mins = int(time[0]), int(time[1])
                except:
                    return
                if hour == 0 and mins == 0:
                    mins = 1
                time_new = time_now + timedelta(hours=hour,minutes=mins)
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
                    beta_save = guild.get_role(beta_save_id)
                    dishonorable = guild.get_role(dishonorable_id)
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
            elif re.match("Count reset", content):
                counter = message.mentions[0]
                await self.ruin_ban(counter)
                beta_collection.update_one(
                    {"_id": counter.id}, 
                    {
                        "$inc": {
                            "correct": -1,
                            "wrong": 1,
                            "streak": -1,
                        }
                    }
                )

        """For reading numselli embeds"""
        if author.id == numselli_bot:
            if message.embeds:
                if (message.interaction and 
                        message.interaction.name == "user"):
                    await self.numselli_user_update(message)
                embed_content = message.embeds[0].to_dict()
                if ("title" in embed_content 
                        and re.match("Sent", embed_content["title"])):
                    nums = re.findall("\d+\.*\d*", embed_content["description"])
                    sent_saves = float(nums[0])
                    rec_id = int(nums[1])
                    saves_left = float(nums[3])
                    have_save:Role = guild.get_role(have_save_id)
                    dishonorable:Role = guild.get_role(dishonorable_id)
                    user_post = numselli_collection.find_one({"_id": rec_id})
                    if user_post:
                        user = guild.get_member(rec_id)
                        actual_saves = user_post.get("current_saves") + sent_saves
                        numselli_collection.update_one(
                            {"_id": rec_id}, 
                            {
                                "$set": {
                                    "current_saves": actual_saves
                                }
                            }
                        )
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
                        else:
                            if have_save in user.roles:
                                await user.remove_roles(have_save)
                                msg = f"<@{user.id}> doesn't have enough saves "
                                msg += f"and cannot count with <@{numselli_bot}>"
                                await message.channel.send(msg)
                            else:
                                await message.add_reaction("❌")
                    sender:Member = message.interaction.user
                    numselli_collection.update_one(
                        {"_id": sender.id}, 
                        {
                            "$set": {
                                "current_saves": saves_left,
                            }
                        }, True
                    )
                    if saves_left >= 1:
                        await message.add_reaction("💾")
                    else:
                        await message.add_reaction("❌")
                        msg = f"<@{user.id}> doesn't have enough saves "
                        msg += f"and cannot count with <@{numselli_bot}>"

                if re.match("Save Used", embed_content["title"]):
                    if re.match("Channel save", embed_content["description"]):
                        have_save = guild.get_role(have_save_id)
                        for user in have_save.members:
                            user.remove_roles(have_save, 
                                reason="Channel save got used")
                        channel_send = guild.get_channel(sam_channel)
                        msg_send = f"Channel save got used "
                        msg_send += "in {message.channel.mention}."
                        await channel_send.send(msg_send)
                        await message.channel.send("Channel locked for all counters.")
                    else:
                        nums = re.findall("\d+\.*\d*", embed_content["description"])
                        user_id = int(nums[0])
                        current_saves = float(nums[1])
                        user = guild.get_member(user_id)

                        have_save = guild.get_role(have_save_id)
                        dishonorable = guild.get_role(dishonorable_id)
                        if dishonorable in user.roles:
                            await user.remove_roles(have_save)
                            await message.add_reaction("❌")
                        elif current_saves >= 1:
                            await message.add_reaction("✅")
                        else:
                            await user.remove_roles(have_save)
                            msg = f"No saves left for <@{user.id}>!"
                            await message.channel.send(msg)
                            await message.add_reaction("❌")

                        user_post = numselli_collection.find_one(
                            {
                                "_id": user_id
                            }, {
                                "streak": 1,
                                "high": 1,
                                "alt": 1,
                            }
                        )
                        if "alt" in user_post:
                            user_main = user_post["alt"]
                            user = guild.get_member(user_main)
                            user_post2 = numselli_collection.find_one(
                                {
                                    "_id": user_main
                                }, {
                                    "streak": 1,
                                    "high": 1,
                                }
                            )
                            final_streak = user_post2.get("streak") - 1
                            if user_post2.get("streak") == user_post2.get("high"):
                                numselli_collection.update_one(
                                    {"_id": user_main}, 
                                    {
                                        "$inc": {
                                            "high": -1,
                                        },
                                        "$set": {
                                            "streak": 0,

                                        }
                                    }
                                )
                            else:
                                numselli_collection.update_one(
                                    {"_id": user_main}, 
                                    {
                                        "$set": {
                                            "streak": 0,
                                        }
                                    }
                                )
                            numselli_collection.update_one(
                                {"_id": user_id}, 
                                {
                                    "$inc":{
                                        "correct": -1,
                                        "wrong": 1,
                                        "current_saves": current_saves,
                                    }
                                }
                            )
                        else:
                            final_streak = user_post.get("streak") - 1
                            if user_post.get("streak") == user_post.get("high"):
                                numselli_collection.update_one(
                                    {"_id": user_id}, 
                                    {
                                        "$inc": {
                                            "high": -1,
                                            "wrong": 1,
                                            "correct": -1,
                                        },
                                        "$set":{
                                            "streak": 0,
                                            "current_saves": current_saves,
                                        }
                                    }
                                )
                            else:
                                numselli_collection.update_one(
                                    {"_id": user_id}, 
                                    {
                                        "$inc": {
                                            "wrong": 1,
                                            "correct": -1,
                                        },
                                        "$set": {
                                            "streak": 1,
                                            "current_saves": current_saves,
                                        }
                                    }
                                )
                        mode="5"
                        scores = self.bot.get_channel(sam_channel)
                        msg = f"**{user.display_name}**'s streak with "
                        msg += f"{mode_list[mode]} has been reset from "
                        msg += f"**{final_streak}** to 0"
                        embedVar = Embed(title="Streak Ruined", description=msg,
                            color=color_lamuse)
                        await scores.send(embed=embedVar)

        """Functions for dank memer"""
        if author.id == dank_bot:
            if message.interaction and message.embeds:
                slash_data = message.interaction.data
                if (slash_data["name"] == "work apply"
                        or slash_data["name"] == "work shift"):
                    embed_content = message.embeds[0].to_dict()
                    if re.search("<t:", embed_content["description"]):
                        user_id = int(slash_data["user"]["id"])
                        if time_collection.find_one(
                            {
                                "user": user_id,
                                "command": "work shift",
                            }
                        ):
                            sec_str = re.findall("\d+", embed_content["description"])[0]
                            time_next = EPOCH + timedelta(seconds=int(sec_str))
                            time_collection.update_one(
                                {
                                    "user": user_id,
                                    "command": "work shift",
                                }, {
                                    "$set": {
                                        "time": time_next,
                                        "channel": message.channel.id
                                    }
                                }
                            )
                            time_str = utils.format_dt(time_next, "t")
                            await message.channel.send(f"Will remind you at {time_str}")

        """Functions related to user input"""
        if re.match("c!user", content, re.I):
            user = re.search("\d+",content)
            if user:
                user_id = int(user.group())
            else:
                user_id = int(author.id)

            def og_user_check(msg:Message):
                bool = False
                if msg.embeds and msg.author.id == og_bot:
                    embed_content = msg.embeds[0].to_dict()
                    if ("fields" in embed_content and 
                            embed_content["fields"][0]["name"]=="Global Stats"):
                        bool = True
                return bool
            try:
                og_msg:Message = await self.bot.wait_for("message", 
                    check=og_user_check, timeout=15)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read `counting` embed.")
            else:
                await self.og_user_update(message, og_msg)

        if re.match("c!vote", content, re.I):
            def og_vote_check(message:Message):
                return message.author.id == og_bot and message.embeds
            try:
                og_msg:Message = await self.bot.wait_for("message", 
                    check=og_vote_check, timeout=5)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read vote embed.")
            else:
                await self.vote_update(message, og_msg)

        if re.match("c!transfersave",content,re.I):
            def og_transfer_check(message:Message):
                return message.author.id == og_bot and message.embeds
            try:
                og_msg:Message = await self.bot.wait_for("message", 
                    check=og_transfer_check, timeout=10)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read og transfer embed.")
            else:
                await self.og_transfer(author, og_msg)

        if re.match("abc\?u",content):
            user = re.search("\d+",content)
            if user:
                user_id = int(user.group())
            else:
                user_id = int(author.id)

            def beta_check(msg:Message):
                return msg.author.id == beta_bot and msg.embeds
            try:
                beta_msg = await self.bot.wait_for("message", 
                    check=beta_check, timeout=3)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read `beta` embed.")
            else:
                await self.beta_update(message, beta_msg, user_id)

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

        if len(content) > 0 and content[0] == ":" and content[-1] == ":":
            emoji_name = content[1:-1]
            for emoji in guild.emojis:
                if emoji_name == emoji.name:
                    await message.reply(str(emoji))
                    break

    @commands.Cog.listener()
    async def on_message_edit(self, before:Message, after:Message):
        if after.interaction and after.author.id == dank_bot:
            slash_data = before.interaction.data
            if slash_data["name"] == "work shift":
                embed_content = after.embeds[0].to_dict()
                if "footer" in embed_content:
                    user_id = int(slash_data["user"]["id"])
                    if time_collection.find_one({
                        "user": user_id,
                        "command": "work shift"
                    }):
                        job = embed_content["footer"]["text"].split(" as a ")[1]
                        if job != "":
                            time_delta = dank_work_time[job]
                        else:
                            time_delta = timedelta(hours=1)
                        time_next = (utils.utcnow().replace(microsecond=0) 
                            + time_delta)
                        time_collection.update_one(
                            {
                                "user": user_id,
                                "command": "work shift"
                            }, {
                                "$set": {
                                    "time": time_next,
                                    "channel": before.channel.id
                                }
                            }
                        )
                        time_str = utils.format_dt(time_next, "t")
                        await after.channel.send(f"Will remind at {time_str}")

    def letter_calc(self, word: str):
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

    @commands.Cog.listener()
    async def on_presence_update(self, member_old:Member, member_new:Member):
        if member_new.bot == False:
            return
        if member_new.raw_status == member_old.raw_status:
            return
        overrides = misc.find_one({"_id":"override"})
        if member_new.id == classic_bot:
            if overrides['classic'] == True:
                return
            channel = self.bot.get_channel(classic_channel)
            role = member_new.guild.get_role(countaholic_id)
        elif member_new.id == og_bot:
            if overrides['og'] == True:
                return
            channel = self.bot.get_channel(og_channel)
            role = member_new.guild.get_role(og_save_id)
        elif member_new.id == abc_bot:
            if overrides['abc'] == True:
                return
            channel = self.bot.get_channel(abc_channel)
            role = member_new.guild.get_role(abc_save_id)
        elif member_new.id == prime_bot:
            if overrides['prime'] == True:
                return
            channel = self.bot.get_channel(prime_channel)
            role = member_new.guild.get_role(countaholic_id)
        elif member_new.id == numselli_bot :
            role = member_new.guild.get_role(have_save_id)
        else:
            return
        if member_old.raw_status=="online" and member_new.raw_status=="offline":
            if member_new.id == numselli_bot:
                for channel_name in numselli_channels:
                    channel_id = numselli_channels[channel_name]
                    channel:TextChannel = self.bot.get_channel(channel_id)
                    overwrites = channel.overwrites_for(role)
                    overwrites.update(send_messages=False)
                    await channel.set_permissions(role,overwrite=overwrites)
                    embedVar = Embed(
                        description="Channel locked as bot is offline",
                        color=color_lamuse
                    )
                    await channel.send(embed=embedVar)
            else:
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=False)
                embedVar = Embed(
                    description="Channel locked as bot is offline",
                    color=color_lamuse
                )
                await channel.set_permissions(role,overwrite=overwrites)
                await channel.send(embed=embedVar)
        elif member_old.raw_status=="offline" and member_new.raw_status=="online":
            if member_new.id == numselli_bot:
                for channel_name in numselli_channels:
                    channel_id = numselli_channels[channel_name]
                    channel = self.bot.get_channel(channel_id)
                    overwrites = channel.overwrites_for(role)
                    overwrites.update(send_messages=True)
                    await channel.set_permissions(role,overwrite=overwrites)
                    embedVar = Embed(
                        description="Channel unlocked as bot is online",
                        color=color_lamuse
                    )
                    await channel.send(embed=embedVar)
            else:
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=True)
                embedVar = Embed(
                    description="Channel unlocked as bot is online",
                    color=color_lamuse
                )
                await channel.set_permissions(role,overwrite=overwrites)
                await channel.send(embed=embedVar)
        else:
            return

    @commands.command(name="run")
    async def command_run(self, ctx:commands.Context):
        """Gives the time when the run started."""
        await self.run(ctx)

    @nextcord.slash_command(name="run", guild_ids=servers)
    async def slash_run(self, ctx:Interaction):
        """Gives the time when the run started"""
        await self.run(ctx)

    async def run(self, ctx:Union[commands.Context, Interaction]):
        """The method used to run both slash and prefix command of run."""
        time_now = utils.utcnow()
        if self.og_last_count == EPOCH:
            msg = "Can't tell run time."

        # If its been a while since a run.
        elif time_now - self.og_last_count >= timedelta(minutes=10):
            msg = "Its been a while since a run."

        else:
            # Calculate the time when run started in int.
            time_str = utils.format_dt(self.og_start_count, "T")
            msg = f"Run started at {time_str}.\n"

            # Run time in words.
            time_diff = time_now - self.og_start_count 
            time_diff_str = str(time_diff).split(":")
            time_diff_hour = int(time_diff_str[0])
            time_diff_min = int(time_diff_str[1])
            time_diff_sec = int(time_diff_str[2][:2])
            msg += "Run has been going on for "
            if time_diff_hour > 1:
                msg += f"{time_diff_hour} hrs "
            elif time_diff_hour == 1:
                msg += f"{time_diff_hour} hr "
            if time_diff_min > 1:
                msg += f"{time_diff_min} mins "
            elif time_diff_min == 1:
                msg += f"{time_diff_min} min "
            if time_diff_sec > 1:
                msg += f"{time_diff_sec} secs "
            elif time_diff_sec == 1:
                msg += f"{time_diff_sec} sec "
            msg = msg.rstrip() + ".\n"

            msg += f"**{self.og_count}** numbers have been counted."

        await ctx.send(msg)

    async def og_user_update(self, message:Message, og_message:Message):
        """Update og stats of the user after seeing c!user."""
        embed_content = og_message.embeds[0].to_dict()
        guild = og_message.guild
        user = guild.get_member_named(embed_content["title"])
        if user:
            desc = embed_content["fields"][0]["value"]
            correct = desc.split("**")[3].replace(",", "")
            wrong = desc.split("**")[5].replace(",", "")
            saves = desc.split("**")[9]
            current_saves = float(saves.split("/")[0])
            total_saves = int(saves.split("/")[1])
            og_collection.update_one(
                {
                    "_id":user.id
                }, {
                    "$set": {
                        "name":f"{user}",
                        "correct":int(correct),
                        "wrong":int(wrong),
                        "current_saves":current_saves,
                        "total_saves":total_saves
                    }
                }, True
            )
            og_save:Role = guild.get_role(og_save_id)
            dishonorable:Role = guild.get_role(dishonorable_id)
            if dishonorable in user.roles:
                await user.remove_roles(og_save)
                await og_message.add_reaction("❌")
            elif current_saves >= 1:
                if og_save in user.roles:
                    await og_message.add_reaction("✅")
                else:
                    await user.add_roles(og_save)
                    msg = f"<@{user.id}> can now count in <#{og_channel}>"
                    await message.channel.send(msg)
            else:
                if og_save in user.roles:
                    await user.remove_roles(og_save)
                    msg = f"<@{user.id}> doesn't have enough saves "
                    msg += f"and cannot count in <#{og_channel}>"
                    await message.channel.send(msg)
                else:
                    await og_message.add_reaction("❌")

    async def vote_update(self, message:Message, og_msg:Message):
        """Update vote stats after using c!vote."""
        embed_content = og_msg.embeds[0].to_dict()
        descript = embed_content["description"]
        saves = descript.split("**")[1]
        current_saves = float(saves.split("/")[0])
        total_saves = int(saves.split("/")[1])
        ogsave = og_msg.guild.get_role(og_save_id)
        dishonorable = og_msg.guild.get_role(dishonorable_id)
        user = message.author
        counter_post = og_collection.find_one({"_id": user.id})
        if counter_post is not None:
            og_collection.update_one(
                {
                    "_id":user.id
                }, {
                    "$set":
                    {
                        "current_saves": current_saves,
                        "total_saves": total_saves
                    }
                }
            )
        else:
            msg = "Run `c!user` first."
            await message.reply(msg)
            return
        if dishonorable in user.roles:
            await user.remove_roles(ogsave)
            await og_msg.add_reaction("❌")
        elif current_saves >= 1:
            if ogsave not in user.roles:
                await user.add_roles(ogsave)
                msg = f"<@{user.id}> can "
                msg += f"now count in <#{og_channel}>"
                await message.channel.send(msg)
            else:
                await og_msg.add_reaction("✅")
        else:
            if ogsave in user.roles:
                await user.remove_roles(ogsave)
                msg = f"<@{user.id}> does not have enough saves "
                msg += f"to count in <#{og_channel}>"
                await message.channel.send(msg)
            else:
                await og_msg.add_reaction("❌")
        rem = counter_post.get("reminder", False)
        dm = counter_post.get("dm", False)
        if rem:
            field1 = embed_content["fields"][0]["value"]
            # field2 = embed_content["fields"][1]["value"]
            channel_id = message.channel.id
            if re.search("You have already", field1):
            #     time1 = re.findall("[\d\.]+", field1)
            #     hour1 = float(time1[1]) + 0.05
            #     time_now = datetime.utcnow().replace(microsecond=0)
            #     time_new = time_now + timedelta(hours=hour1)
            #     if time_collection.find_one(
            #         {
            #             "user": user.id,
            #             "command": "vote in Discords.com"
            #         }
            #     ):
            #         time_collection.update_one(
            #             {
            #                 "user": user.id,
            #                 "command": "vote in Discords.com"
            #             }, {
            #                 "$set":
            #                 {
            #                     "time": time_new,
            #                     "dm": dm,
            #                     "channel": channel_id,
            #                 }
            #             }
            #         )
            #     else:
            #         time_collection.insert_one(
            #             {
            #                 "time": time_new,
            #                 "user": user.id,
            #                 "command": "vote in Discords.com",
            #                 "dm": dm,
            #                 "channel": channel_id,
            #             }
            #         )
            # if re.search("You have already", field2):
                time2 = re.findall("[\d\.]+", field1)
                hour2 = float(time2[1]) + 0.05
                time_now = datetime.utcnow().replace(microsecond=0)
                time_new = time_now + timedelta(hours=hour2)
                if time_collection.find_one(
                    {
                        "user": user.id,
                        "command": "vote in top.gg"
                    }
                ):
                    time_collection.update_one(
                        {
                            "user": user.id,
                            "command": "vote in top.gg"
                        }, {
                            "$set":
                            {
                                "time": time_new,
                                "dm": dm,
                                "channel": channel_id,
                            }
                        }
                    )
                else:
                    time_collection.insert_one(
                        {
                            "time": time_new,
                            "user": user.id,
                            "command": "vote in top.gg", 
                            "dm": dm,
                            "channel": channel_id,
                        }
                    )

    async def og_transfer(self, sender:Member, og_message:Message):
        embed_content = og_message.embeds[0].to_dict()
        if re.match("Save transferred!", embed_content["title"]) is None:
            return

        guild = og_message.guild
        dishonorable:Role = guild.get_role(dishonorable_id)
        og_save:Role = guild.get_role(og_save_id)
        descript = embed_content["description"]
        num_list = re.findall("\d+\.*\d*", descript)
        rec_id = int(num_list[1])
        current_saves = float(num_list[3])

        if current_saves < 1:
            if og_save in sender.roles:
                await sender.remove_roles(og_save)
                msg = f"You can no longer count in <#{og_channel}>"
                msg += f"till you have 1 save <@{sender.id}>"
                await og_message.channel.send(msg)
        else:
            await og_message.add_reaction("💾")

        receiver = guild.get_member(rec_id)
        if dishonorable in receiver.roles:
            await og_message.add_reaction("❌")
            await receiver.remove_roles(og_save)
        elif og_save in receiver.roles:
            await og_message.add_reaction("✅")
        else:
            await receiver.add_roles(og_save)
            msg = f"<@{receiver.id}> can "
            msg += f"now count in <#{og_channel}>"
            await og_message.channel.send(msg)

        og_collection.update_one(
            {
                "_id":sender.id
            }, {
                "$set": {
                    "current_saves":current_saves
                }
            }, True
        )
        og_collection.update_one(
            {
                "_id":rec_id
            }, {
                "$inc": {
                    "current_saves":1
                }
            }, True
        )

    async def numselli_user_update(self, message:Message):
        """Update numselli data from user embed."""
        embed_content = message.embeds[0].to_dict()
        guild = message.guild
        if ("fields" in embed_content and 
                embed_content["fields"][0]["name"]=="Global Stats"):
            field1 = embed_content["fields"][0]
            name = embed_content["title"].split(" ", 2)[2]
            list = field1["value"].split("**")
            correct = int(list[3].replace(",",""))
            wrong = int(list[5].replace(",",""))
            saves = list[9]
            current_saves = float(saves.split("/")[0])
            total_saves = int(saves.split("/")[1])
            user = guild.get_member_named(name)
            if user:
                numselli_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set": {
                            "name":f"{user}",
                            "correct":correct,
                            "wrong":wrong,
                            "current_saves":current_saves,
                            "total_saves":total_saves
                        }
                    }, True
                )
                have_save:Role = guild.get_role(have_save_id)
                dishonorable:Role = guild.get_role(dishonorable_id)
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

    async def beta_update(self, message:Message, beta_message:Message, 
            user_id:int):
        """Update beta stats."""
        embed_content = beta_message.embeds[0].to_dict()
        guild = message.guild
        if (re.findall("stats", embed_content["title"]) and
                embed_content["fields"][3]["name"] == "Saves"):
            user = guild.get_member(user_id)
            if user:
                field_content = embed_content["fields"][3]["value"]
                current_saves = float(field_content.split("/")[0][1:])
                if current_saves == int(current_saves):
                    current_saves = int(current_saves)
                total_saves = int(field_content.split("/")[1][:-1])
                field_content = embed_content["fields"][0]["value"]
                correct = int(re.split(" ", field_content)[0][1:])
                wrong = int(embed_content["fields"][1]["value"][1:-1])
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
                    }, True
                )
                beta_save:Role = guild.get_role(beta_save_id)
                dishonorable:Role = guild.get_role(dishonorable_id)
                if dishonorable in user.roles:
                    await user.remove_roles(beta_save)
                    await beta_message.add_reaction("❌")
                elif current_saves >= 1:
                    if beta_save in user.roles:
                        await beta_message.add_reaction("✅")
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
                        await beta_message.add_reaction("❌")

    @commands.Cog.listener()
    async def on_member_update(self, before:Member, after:Member):
        """Do something when roles get changed."""
        if len(before.roles) != len(after.roles):
            dishonorable = before.guild.get_role(dishonorable_id)
            if dishonorable in after.roles and dishonorable not in before.roles:
                await self.ruin_ban(after)

    async def ruin_ban(self, user:Member):
        """Ban a user from counting channels if they ruin a count."""
        guild = user.guild
        dishonorable = guild.get_role(dishonorable_id)
        og_save = guild.get_role(og_save_id)
        have_save = guild.get_role(have_save_id)
        beta_save = guild.get_role(beta_save_id)
        # hermanos = guild.get_role(hermanos_id)
        await user.add_roles(dishonorable)
        await user.remove_roles(og_save, have_save, beta_save)#, hermanos)
        send_channel = guild.get_channel(sam_channel)
        await send_channel.send(f"{user.mention} has been banned from counting channels.")

    @tasks.loop(seconds=1)
    async def check_time_og(self):
        time_now = utils.utcnow()
        if time_now - self.og_last_count >= timedelta(minutes=10):
            if self.og_count >= 50:
                start = utils.format_dt(self.og_start_count, "T")
                stop = utils.format_dt(self.og_last_count, "T")
                scores_chnl:TextChannel = self.bot.get_channel(sam_channel)
                msg = f"Last run in <#{og_channel}> had "
                msg += f"**{self.og_count}** numbers."
                msg += f"\nRun started from {start} to {stop}."
                try:
                    await scores_chnl.send(msg)
                except nextcord.errors.Forbidden:
                    logger_monitor.error(f"Couldn't send run end msg in {scores_chnl}")
                self.og_count = 0

            og_send_channel = self.bot.get_channel(og_channel)
            if og_send_channel is None:
                return
            if og_send_channel.name != "og-counting":
                try:
                    await og_send_channel.edit(name="og-counting")
                except nextcord.Forbidden:
                    await og_send_channel.send("Editing channel name failed.")
                    logger_monitor.exception("Editing channel name failed.")

def setup(bot):
    """The setup command for the cog."""
    bot.add_cog(Monitor(bot))