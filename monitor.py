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
from nextcord.ext import commands

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

    @commands.Cog.listener()
    async def on_message(self, message:nextcord.Message):
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
                if user_post:
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
                        if user_post2['streak'] == user_post2['high']:
                            og_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "high":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"n{(user_post2['streak']+1)}"
                        else:
                            og_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"{(user_post2['streak']+1)}"
                        og_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        if user_post['streak'] == user_post['high']:
                            og_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "high":1,
                                        "correct":1,
                                        "daily":1
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
                                        "correct":1,
                                        "daily":1
                                    }
                                }
                            )
                            if (user_post['streak']+1)%500==0:
                                msg_s = f"{(user_post['streak']+1)}"
                    mode = "1"
                time_now = message.created_at
                time_diff = time_now - self.og_last_count
                self.og_last_count = time_now
                if abs(time_diff) >= timedelta(minutes=10) \
                        or self.og_start_count == EPOCH:
                    if self.og_count >= 50:
                        scores_chnl:TextChannel = guild.get_channel(sam_channel)
                        msg = f"Last run in <#{og_channel}> had "
                        msg += f"**{self.og_count}** numbers."
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
                else:
                    self.og_count += 1
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
                if user_post:
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
                        if user_post2['streak'] == user_post2['high']:
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "high":1,
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"n{(user_post2['streak']+1)}"
                        else:
                            classic_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"{(user_post2['streak']+1)}"
                        classic_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "correct":1
                                }
                            }
                        )
                    else:
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
                            if (user_post['streak']+1)%500==0:
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
                    number = self.letter_calc(number_str)
                except:
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
                if user_post:
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
                        if user_post2['streak'] == user_post2['high']:
                            numselli_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1,
                                        "high":1,
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"n{(user_post2['streak']+1)}"
                        else:
                            numselli_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$inc":
                                    {
                                        "streak":1
                                    }
                                }
                            )
                            if (user_post2['streak']+1)%500==0:
                                msg_s = f"{(user_post2['streak']+1)}"
                        numselli_collection.update_one(
                            {
                                "_id":user_id
                            }, {
                                "$inc":
                                {
                                    "correct":1
                                }
                            }
                        )
                    else:
                        if user_post['streak'] == user_post['high']:
                            numselli_collection.update_one(
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
                            numselli_collection.update_one(
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
                            await self.mile_chnl.send(msg)
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
        if (re.findall("You have used", content) or \
                re.findall("RUINED", content, re.I) or \
                re.search("Wrong number!", content)) and author.bot == True : 
            if message.mentions:
                user = message.mentions[0]
                user_id = message.mentions[0].id
                if channel == og_channel and author.id == og_bot:
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
                                    "current_saves":-1
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
                                        "current_saves":-1,
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
                                    "_id":user_id
                                }, {
                                    "$inc":
                                    {
                                        "wrong":1,
                                        "correct":-1,
                                        "current_saves":-1,
                                        "daily":-1
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
        """If mistake is made in numselli bot"""

        """All functions related to og bot"""
        if author.id == og_bot:
            if message.embeds:
                embed_content = message.embeds[0].to_dict()
                if 'fields' in embed_content:
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
                            og_save:Role = guild.get_role(og_save_id)
                            dishonorable:Role = guild.get_role(dishonorable_id)
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
                            ogsave = guild.get_role(og_save_id)
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
                if "author" in embed_content and "fields" in embed_content:
                    name = embed_content["author"]["name"]
                    user = guild.get_member_named(name)
                    desc = embed_content["fields"][0]["value"]
                    if user:
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
                            beta_save:Role = guild.get_role(beta_save_id)
                            dishonorable:Role = guild.get_role(dishonorable_id)
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
                try:
                    hour, min = int(time[0]), int(time[1])
                except:
                    return
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
                if re.match('Sent',embed_content['title']):
                    nums = re.findall('[\d\.,]+',embed_content['description'])
                    sent_saves = float(nums[0])
                    rec_id = int(nums[1])
                    user_post = numselli_collection.find_one({"_id":rec_id})
                    if user_post:
                        user = guild.get_member(rec_id)
                        actual_saves = user_post['current_saves'] + sent_saves
                        have_save:Role = guild.get_role(have_save_id)
                        dishonorable:Role = guild.get_role(dishonorable_id)
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
                if re.match("Save Used", embed_content['title']):
                    nums = re.findall("[\d.]+", embed_content['description'])
                    user_id = int(nums[0])
                    current_saves = float(nums[2])
                    user = guild.get_member(user_id)
                    user_post = numselli_collection.find_one(
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
                        user_post2 = numselli_collection.find_one(
                            {
                                "_id":user_main
                            }, {
                                "streak":1,
                                "high":1
                            }
                        )
                        final_streak = user_post2["streak"] - 1
                        if user_post2['streak'] == user_post2['high']:
                            numselli_collection.update_one(
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
                            numselli_collection.update_one(
                                {
                                    "_id":user_main
                                }, {
                                    "$set":
                                    {
                                        "streak":0
                                    }
                                }
                            )
                        numselli_collection.update_one(
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
                            numselli_collection.update_one(
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
                            numselli_collection.update_one(
                                {
                                    "_id":user_id
                                }, {
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
                    mode="5"
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

        """For generating the next prime number"""
        if channel == prime_channel and re.match("\d", content):
            try:
                num = int(content.split()[0])
            except:
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
        if re.match("c!vote", content, re.I):
            def check(message:Message):
                return message.author.id == og_bot and message.embeds
            try:
                msg:Message = await self.bot.wait_for("message", 
                    check=check, timeout=5)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read vote embed.")
            else:
                await self.vote_update(message, msg)
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
        if content.startswith("y!userstats"):
            def check(m:Message):
                return m.author.id==yoda_bot and m.embeds
            try:
                yoda_message:Message = await self.bot.wait_for("message", 
                    check=check, timeout=5)
            except asyncio.TimeoutError:
                await message.channel.send("Failed to read yoda embed.")
            else:
                self.yoda_update(yoda_message, author)
        # if re.match("abc!shop",content,re.I):
        #     if misc.find_one({"_id":"abc!shop"}):
        #         misc.update_one({"_id":"abc!shop"}, {"$set":{"user":author.id}})
        #     else:
        #         misc.insert_one({"_id":"abc!shop","user":author.id})
        if len(content) > 0 and content[0] == ":" and content[-1] == ":":
            emoji_name = content[1:-1]
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
        # elif member_new.id == sasha_bot:
        #     channel = bot.get_channel(sasha_channel)
        #     role = member_new.guild.get_role(countaholic_id)
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
        """Gives the time when the run started"""
        await self.run(ctx)

    @nextcord.slash_command(name="run", guild_ids=servers)
    async def slash_run(self, ctx:Interaction):
        """Gives the time when the run started"""
        await self.run(ctx)

    async def run(self, ctx:Union[commands.Context, Interaction]):
        """
        The method used to run both slash and prefix command of run.
        """
        time_now = utils.utcnow()
        if self.og_last_count == EPOCH:
            msg = "Can't tell run time."

        # If its been a while since a run.
        elif time_now - self.og_last_count >= timedelta(minutes=10):
            msg = "Its been a while since a run."

        else:
            # Calculate the time when run started in int.
            time_str = nextcord.utils.format_dt(self.og_start_count, "T")
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

    async def vote_update(self, message:Message, msg:Message):
        """Update vote stats after using c!vote."""
        embed_content = msg.embeds[0].to_dict()
        descript = embed_content["description"]
        saves = descript.split("**")[1]
        current_saves = float(saves.split("/")[0])
        total_saves = int(saves.split("/")[1])
        ogsave = msg.guild.get_role(og_save_id)
        dishonorable = msg.guild.get_role(dishonorable_id)
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
            await msg.add_reaction("❌")
        elif current_saves >= 1:
            if ogsave not in user.roles:
                await user.add_roles(ogsave)
                msg = f"<@{user.id}> can "
                msg += f"now count in <#{og_channel}>"
                await message.channel.send(msg)
            else:
                await msg.add_reaction("✅")
        else:
            if ogsave in user.roles:
                await user.remove_roles(ogsave)
                msg = f"<@{user.id}> does not have enough saves "
                msg += f"to count in <#{og_channel}>"
                await message.channel.send(msg)
            else:
                await msg.add_reaction("❌")
        rem = counter_post.get("reminder", False)
        dm = counter_post.get("dm", False)
        if rem:
            field1 = embed_content["fields"][0]["value"]
            field2 = embed_content["fields"][1]["value"]
            channel_id = message.channel.id
            if re.search("You have already", field1):
                time1 = re.findall("[\d\.]+", field1)
                hour1 = float(time1[1]) + 0.05
                time_now = datetime.utcnow().replace(microsecond=0)
                time_new = time_now + timedelta(hours=hour1)
                if time_collection.find_one(
                    {
                        "user": user.id,
                        "command": "vote in Discords.com"
                    }
                ):
                    time_collection.update_one(
                        {
                            "user": user.id,
                            "command": "vote in Discords.com"
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
                            "command": "vote in Discords.com",
                            "dm": dm,
                            "channel": channel_id,
                        }
                    )
            if re.search("You have already", field2):
                time2 = re.findall("[\d\.]+", field2)
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

    def yoda_update(self, yoda_message:Message, author:Member):
        """Input yoda details after reading the embed."""
        embed_content = yoda_message.embeds[0].to_dict()
        descr = embed_content["description"]
        correct = int(descr.split("**")[3])
        wrong = int(descr.split("**")[5])
        tokens = float(descr.split("**")[9].split("/")[0])
        if yoda_collection.find_one(
            {
                "_id": author.id
            }
        ):
            yoda_collection.update_one(
                {
                    "_id": author.id
                }, {
                    "$set": {
                        "correct": correct,
                        "wrong": wrong,
                        "tokens": tokens,
                    }
                }
            )
        else:
            yoda_collection.insert_one(
                {
                    "_id": author.id,
                    "name": f"{author}",
                    "correct": correct,
                    "wrong": wrong,
                    "tokens": tokens,
                    "streak": 0,
                    "high": 0,
                }
            )

def setup(bot):
    bot.add_cog(Monitor(bot))