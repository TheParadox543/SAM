import asyncio
import logging
from math import sqrt
from datetime import UTC, datetime, timedelta, timezone, time
from re import I, findall, match, search, split
from typing import Union, cast

import nextcord
from nextcord import (
    ButtonStyle,
    Embed,
    Guild,
    Interaction,
    Member,
    Message,
    Role,
    SlashOption,
    TextChannel,
    slash_command,
    utils,
)
from nextcord.abc import GuildChannel
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
from nextcord.ui import Button, View
from nextcord.utils import format_dt, get, utcnow

from bot_secrets import *
from database import (
    RunData,
    beta_collection,
    bot_role,
    check_emoji,
    classic_collection,
    clock_emoji,
    find_run_data,
    find_user_stats,
    misc,
    numselli_collection,
    og_collection,
    roman,
    time_collection,
    time_up_channels,
    track_list,
    update_run,
    update_user_count_correct,
    update_user_count_incorrect,
    update_user_stats,
    warning_emoji,
    wrong_emoji,
)

# Using the logs.
logger_monitor = logging.getLogger(__name__)
logger_monitor.setLevel(logging.ERROR)
handler = logging.FileHandler("SAM.log")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger_monitor.addHandler(handler)


async def control_permission(saves: int | float, counter: Member, message: Message):
    """Control letting users to count in channels

    Parameters
    ----------
        saves (int): _description_
        counter (Member): _description_
        message (Message): _description_
        bot (int | str): _description_
    """

    bot_id = message.author.id
    guild = message.guild
    if guild is None:
        return
    dishonorable = cast(Role, guild.get_role(DISHONORABLE_ID))
    role_id = bot_role[bot_id]
    role = guild.get_role(role_id)
    if role is None:
        await message.channel.send("Could not find the role")
        return
    if dishonorable in counter.roles:
        reaction = get(guild.emojis, name="Incorrect")
        if reaction is not None:
            await message.add_reaction(reaction)
        return
    if saves >= 1:
        if role in counter.roles:
            reaction = get(guild.emojis, name="Correct")
            if reaction is not None:
                await message.add_reaction(reaction)
        else:
            await counter.add_roles(role, reason="Has enough saves")
            await message.channel.send(
                f"{counter.mention} can now count with <@{bot_id}>."
            )
    else:
        if role in counter.roles:

            async def button_callback(interaction: Interaction):
                await counter.remove_roles(role, reason="Not enough saves")
                await interaction.response.edit_message(
                    content=f"{counter.mention} role has been removed",
                    view=None,
                )

            button = Button(style=ButtonStyle.red)
            button.callback = button_callback
            view = View()
            view.add_item(button)
            await message.channel.send(
                f"{counter.mention} doesn't have enough saves to count with <@{bot_id}>.",
                view=view,
            )
        else:
            reaction = get(guild.emojis, name="Incorrect")
            if reaction is not None:
                await message.add_reaction(reaction)


def name_extractor(title: str):
    """Extract the user name from the title"""

    if "Stats" in title:
        title = title.split("Stats for ")[1]
        # return title.split("#")[0]
    # else:
    return title.split("#")[0]


def stats_embed_extractor(embed: Embed):
    """Extract the numbers from an embed"""

    embed_content = embed.to_dict()
    if "fields" not in embed_content:
        return None, None
    if "Stats" not in embed_content["fields"][0]["name"]:
        return None, None

    user_name = None
    if "title" in embed_content:
        user_name = name_extractor(embed_content["title"])
    elif "author" in embed_content:
        if "name" in embed_content["author"]:
            user_name = embed_content["author"]["name"]

    field_content = embed_content["fields"][0]["value"].replace(",", "")
    numbers_list: list[str] = findall("[\d\.]+", field_content)  # type: ignore
    numbers_return = (
        float(numbers_list[0]),
        int(numbers_list[1]),
        int(numbers_list[2]),
    )
    if "Saves" in field_content:
        saves_str = field_content.split("Saves")[1]
        saves = int(findall("[0-9]+", saves_str)[0])  # type: ignore
        numbers_return = numbers_return + (saves,)
    return user_name, numbers_return


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
        num += lett * 26**pos
        pos = pos - 1
    return num


def prime(num: int):
    f = False
    for i in range(3, int(sqrt(num)) + 1, 2):
        if num % i == 0:
            f = True
    return f


def next_prime(num: int):
    f = True
    while f:
        if num % 2 == 1:
            num += 2
        else:
            num += 1
        f = prime(num)
    return num


def create_run_embed(run_data: RunData):
    time_start = run_data.time_start.replace(tzinfo=UTC)
    time_last = run_data.time_last.replace(tzinfo=UTC)
    start_str = format_dt(time_start, "T")
    last_str = format_dt(time_last, "T")

    # Run time in words.
    time_diff = time_last - time_start
    time_diff_str = str(time_diff).split(":")
    time_diff_hour = int(time_diff_str[0])
    time_diff_min = int(time_diff_str[1])
    time_diff_sec = int(time_diff_str[2][:2])
    run_time = ""
    if time_diff_hour > 1:
        run_time += f"{time_diff_hour} hrs "
    elif time_diff_hour == 1:
        run_time += f"{time_diff_hour} hr "
    if time_diff_min > 1:
        run_time += f"{time_diff_min} mins "
    elif time_diff_min == 1:
        run_time += f"{time_diff_min} min "
    if time_diff_sec > 1:
        run_time += f"{time_diff_sec} secs "
    elif time_diff_sec == 1:
        run_time += f"{time_diff_sec} sec "
    run_time = run_time.rstrip()

    msg = (
        f"Run time: {run_time}"
        f"\nRun start: {start_str}"
        f"\nRun last: {last_str}"
        f"\nRun counts: **{run_data.count}**"
    )
    embedVar = Embed(title=run_data.name, description=msg, color=color_lamuse)
    field = ""
    for item in run_data.contributors:
        field += f"\n<@{item.id}> - {item.count}"
    embedVar.add_field(name="Contributors", value=field)
    return embedVar


async def streak_reset(
    streak_data: dict,
    user: Member,
    mode: str,
    sam_channel: TextChannel,
):
    """Send a message to sam channel on streak getting reset

    Parameters
    ----------
    - streak_data `dict`: The streak data of the user
    - user `Member`: The counter who made the mistake
    """

    final_streak = streak_data.get("streak", 0)
    if final_streak < 3:
        return
    final_streak -= 1
    msg = f"**{user.display_name}**'s streak with "
    msg += f"{mode_list[mode]} has been reset from "
    msg += f"**{final_streak}** to 0"
    embedVar = Embed(title="Streak Ruined", description=msg, color=color_lamuse)
    await sam_channel.send(embed=embedVar)


class Monitor(Cog):
    """Monitor the channels and control permissions to count in channels."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.check_time.start()
        self.daily.start()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return

        if not isinstance(message.author, Member):
            return
        if not isinstance(message.guild, Guild):
            return

        content = message.content
        author = message.author
        channel_id = message.channel.id
        channel = message.channel
        guild = message.guild

        # * To update user streak if correct and milestone update
        if (
            track_list.count(channel_id) > 0
            and len(content.split()) > 0
            and match("\w", content)  # type: ignore
            and author.bot == False
        ):
            number_str = content.split()[0]
            number_str = number_str.upper()
            user = author
            user_id = author.id
            msg_s = ""
            time_now = message.created_at
            channel = cast(TextChannel, channel)
            if channel_id == OG_CHANNEL_ID and match("[0-9]", number_str):  # type: ignore
                try:
                    number = int(number_str)
                except:
                    return
                if number == 0:
                    pass
                update_user_count_correct(user_id, OG_BOT_ID)
                run_data = update_run(channel, time_now, user_id)
                if run_data.time_start == time_now:
                    minutes = run_data.time_start.minute
                    seconds = run_data.time_start.second
                    await channel.edit(name=f"og-counting-{minutes}-{seconds}")
                # elif (
                #     time_now - run_data.time_start.replace(tzinfo=UTC)
                #     > timedelta(minutes=55)
                #     and channel.name != f"og-counting-{warning_emoji}"
                # ):
                #     await channel.edit(name=f"og-counting-{warning_emoji}")
                elif (
                    time_now - run_data.time_start.replace(tzinfo=UTC)
                    > timedelta(hours=1)
                    and channel.name != f"og-counting-{clock_emoji}"
                ):
                    await channel.edit(name=f"og-counting-{clock_emoji}")
                bot_id = OG_BOT_ID
            elif channel_id == CLASSIC_CHANNEL_ID and match("[0-9]", number_str):
                try:
                    number = int(number_str)
                except:
                    return
                if number == 0:
                    pass
                update_run(channel, time_now, user_id)
                update_user_count_correct(user_id, CLASSIC_BOT_ID)
                bot_id = CLASSIC_BOT_ID
            elif channel_id == BETA_CHANNEL_ID and match("[a-zA-Z]", number_str):
                try:
                    number = letter_calc(number_str)
                except:
                    return
                update_run(channel, time_now, user_id)
                update_user_count_correct(user_id, BETA_BOT_ID)
                bot_id = BETA_BOT_ID
            elif channel_id in NUMSELLI_CHANNEL_ID.values():
                if channel_id == NUMSELLI_CHANNEL_ID["whole"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(number_str)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["letters"] and match(
                    "[a-zA-Z]", number_str
                ):
                    try:
                        number = letter_calc(number_str)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["binary"] and match(
                    "[01]", number_str
                ):
                    try:
                        number = int(number_str, 2)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["decimal"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(float(number_str) * 10)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["hex"] and match(
                    "[0-9a-fA-F]", number_str
                ):
                    try:
                        number = int(number_str, 16)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["roman"] and match(
                    "[IVXLCDM]", number_str
                ):
                    try:
                        i = 0
                        number = 0
                        while i < len(number_str):
                            if (
                                i + 1 < len(number_str)
                                and number_str[i : i + 2] in roman
                            ):
                                number += roman[number_str[i : i + 2]]
                                i += 2
                            else:
                                # print(i)
                                number += roman[number_str[i]]
                                i += 1
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["two"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(int(number_str) / 2)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["five"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(int(number_str) / 5)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["ten"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(int(number_str) / 10)
                    except:
                        return
                elif channel_id == NUMSELLI_CHANNEL_ID["hundred"] and match(
                    "[0-9]", number_str
                ):
                    try:
                        number = int(int(number_str) / 100)
                    except:
                        return
                else:
                    return
                update_run(channel, time_now, user_id)
                update_user_count_correct(user_id, NUMSELLI_BOT_ID)
                bot_id = NUMSELLI_BOT_ID
            else:
                return
            rev_num = number_str[::-1]
            if rev_num == number_str and len(rev_num) > 1:
                await message.add_reaction("↔️")
            if number % 100 == 0 and number != 0:
                if number % 500 == 0:
                    if number % 1000 == 0 and channel_id != CLASSIC_CHANNEL_ID:
                        await message.add_reaction("❤️‍🔥")
                        milestone = cast(
                            TextChannel, self.bot.get_channel(MILE_CHANNEL_ID)
                        )
                        time = int(message.created_at.timestamp())
                        if number == 5_000_000:
                            msg = f"**WE HIT __FIVE MILLION__** at <t:{time}:F>. "
                            msg += "**THIS IS AMAZING. LET'S KEEP GOING.**"
                            await milestone.send(msg)
                        else:
                            if (
                                channel_id == OG_CHANNEL_ID
                                or channel_id == NUMSELLI_CHANNEL_ID["whole"]
                            ):
                                sen = ""
                                while len(number_str) > 0:
                                    sen = number_str[-3:] + sen
                                    number_str = number_str[:-3]
                                    if len(number_str) > 0:
                                        sen = "," + sen
                                msg = f"Reached **{sen}** in <#{channel_id}> - "
                                msg += f"<t:{time}:F>"
                            else:
                                num_str = str(number)
                                sen = ""
                                while len(num_str) > 0:
                                    sen = num_str[-3:] + sen
                                    num_str = num_str[:-3]
                                    if len(num_str) > 0:
                                        sen = "," + sen
                                msg = f"Reached **{number_str}** ({sen}) in "
                                msg += f"<#{channel_id}> - <t:{time}:F>"
                            await milestone.send(msg)
                    else:
                        await message.add_reaction("🔥")
                    pass
                else:
                    await message.add_reaction("💯")
            elif number % 100 == 69:
                await message.add_reaction("<:emoji69:915053989895221248>")
            elif number % 1000 == 161:
                await message.add_reaction("🌀")
            elif number % 1000 == 271:
                await message.add_reaction("🇪")
            elif number % 1000 == 314:
                await message.add_reaction("🥧")
            elif number % 1000 == 404:
                await message.add_reaction("🤖")
            elif number % 1000 == 420:
                await message.add_reaction("🌿")
            elif number % 1000 == 666:
                await message.add_reaction("<:blobdevil:915054491227795477>")
            elif number % 1000 == 711:
                await message.add_reaction("<:7eleven:1029416348671016980>")
            elif number % 1000 == 747:
                await message.add_reaction("✈️")
            elif number % 1000 == 777:
                await message.add_reaction("🎰")
            elif number % 1000 == 911:
                await message.add_reaction("💥")
            elif number % 10_000 == 3108:
                await message.add_reaction("💡")
            user = cast(Member, user)
            if match("n", msg_s):
                scores = cast(TextChannel, self.bot.get_channel(SAM_CHANNEL_ID))
                msg = f"**{user.display_name}** has reached a new streak of "
                msg += f"**{str(msg_s)[1:]}** with {mode_list[f'{bot_id}']}"
                embedVar = Embed(description=msg, color=color_lamuse)
                await scores.send(embed=embedVar)
                await message.add_reaction("<:blobyes:915054339796639745>")
            elif match("[0-9]", msg_s):
                scores = cast(TextChannel, self.bot.get_channel(SAM_CHANNEL_ID))
                msg = f"**{user.display_name}** has reached a streak of "
                msg += f"**{msg_s}** with {mode_list[f'{bot_id}']}"
                embedVar = Embed(description=msg, color=color_lamuse)
                await scores.send(embed=embedVar)
                await message.add_reaction("<:blobyes:915054339796639745>")

        # * Deal with messages from users
        if author.bot is not True:
            if match("c!user", content, I):
                number_str = search("[0-9]+", content)
                if number_str is not None:
                    user_id = int(number_str.group())
                    user_find = guild.get_member(user_id)
                    if user_find is not None:
                        user = user_find
                    else:
                        await channel.send("Could not identify the user in the server")
                        return
                else:
                    user = message.author

                def og_user_check(msg: Message):
                    bool_var = False
                    if msg.embeds and msg.author.id == OG_BOT_ID:
                        embed_content = msg.embeds[0].to_dict()
                        if (
                            "fields" in embed_content
                            and embed_content["fields"][0]["name"] == "Global Stats"
                        ):
                            bool_var = True
                    return bool_var

                try:
                    og_msg = await self.bot.wait_for(
                        "message", check=og_user_check, timeout=15
                    )
                except asyncio.TimeoutError:
                    await message.channel.send("Failed to read `counting` embed.")
                else:
                    await self.og_user_update(og_msg, user)

            if match("c!vote", content, I):

                def og_vote_check(message: Message):
                    return message.author.id == OG_BOT_ID and len(message.embeds) == 1

                try:
                    og_msg: Message = await self.bot.wait_for(
                        "message", check=og_vote_check, timeout=5
                    )
                except asyncio.TimeoutError:
                    await message.channel.send("Failed to read vote embed.")
                else:
                    await self.vote_update(og_msg, message.author)

            if match("c!transfersave", content, I):

                def og_transfer_check(message: Message):
                    return message.author.id == OG_BOT_ID and len(message.embeds) == 1

                try:
                    og_msg: Message = await self.bot.wait_for(
                        "message", check=og_transfer_check, timeout=10
                    )
                except asyncio.TimeoutError:
                    await message.channel.send("Failed to read og transfer embed.")
                else:
                    await self.og_transfer(author, og_msg)

            if "abc?u" in content:
                user = search("[0-9]+", content)
                if user:
                    user_id = int(user.group())
                else:
                    user_id = int(author.id)

                def beta_check(msg: Message):
                    return msg.author.id == BETA_BOT_ID and len(msg.embeds) == 1

                try:
                    beta_msg = await self.bot.wait_for(
                        "message", check=beta_check, timeout=3
                    )
                except asyncio.TimeoutError:
                    await message.channel.send("Failed to read `beta` embed.")
                else:
                    await self.beta_update(beta_msg, user_id)

            if "abc?d" in content:
                if misc.find_one({"_id": "abc?d"}):
                    misc.update_one({"_id": "abc?d"}, {"$set": {"user": author.id}})
                else:
                    misc.insert_one({"_id": "abc?d", "user": author.id})

            if "abc?gift" in content:
                user = search("[0-9]+", content)
                if user:
                    userID = int(user.group())
                    if misc.find_one({"_id": "abc?gift"}):
                        misc.update_one({"_id": "abc?gift"}, {"$set": {"user": userID}})
                    else:
                        misc.insert_one({"_id": "abc?gift", "user": userID})

            if len(content) > 0 and content[0] == ":" and content[-1] == ":":
                emoji_name = content[1:-1]
                for emoji in guild.emojis:
                    if emoji_name == emoji.name:
                        await message.channel.send(f"{emoji.id}")
                        await message.reply(str(emoji))
                        break

            if message.channel.id == 988454528632373250:
                number = int(content.split()[0])
                num = next_prime(number)
                await message.channel.send(f"`Next: {num}`")

            return

        """Deal with bot messages"""

        # * Messages from og counting bot
        if author.id == OG_BOT_ID:
            if len(message.embeds) == 0:
                if len(message.mentions) != 1:
                    return
                user = cast(Member, message.mentions[0])
                user_id = user.id
                if "guild" in content:

                    async def button_callback(interaction: Interaction):
                        await self.ruin_ban(user)
                        channel = message.channel
                        if not isinstance(channel, TextChannel):
                            return
                        role = user.get_role(OG_SAVE_ID)
                        if not isinstance(role, Role):
                            return
                        overwrites = channel.overwrites_for(role)
                        overwrites.update(send_messages=False)
                        await channel.set_permissions(role, overwrite=overwrites)
                        await interaction.response.edit_message(
                            content="Channel Locked", view=None
                        )

                    msg_send = "@everyone Guild save got used. LOCK THE CHANNEL"
                    button = Button(label="LOCK", style=nextcord.ButtonStyle.red)
                    button.callback = button_callback
                    view = View()
                    view.add_item(button)
                    await message.channel.send(msg_send, view=view)
                    return

                elif "of your saves" in content:
                    numbers_list = findall("[0-9]+", content)
                    saves_left = int(numbers_list[2])
                    await control_permission(saves_left, user, message)
                else:
                    return
                counter_data = update_user_count_incorrect(user_id, OG_BOT_ID)
                if counter_data is None:
                    return
                sam_channel = self.bot.get_channel(SAM_CHANNEL_ID)
                if isinstance(sam_channel, TextChannel):
                    await streak_reset(
                        counter_data,
                        user,
                        f"{OG_BOT_ID}",
                        sam_channel,
                    )

        # * All functions related to classic counting
        elif author.id == CLASSIC_BOT_ID:
            if message.embeds:
                embed_content = message.embeds[0].to_dict()
                if "author" in embed_content and "fields" in embed_content:
                    if "name" not in embed_content["author"]:
                        return
                    name = embed_content["author"]["name"]
                    user = guild.get_member_named(name)
                    desc = embed_content["fields"][0]["value"]
                    if user:
                        correct = int(desc.split("**")[3].replace(",", ""))
                        wrong = int(desc.split("**")[5].replace(",", ""))
                        classic_collection.update_one(
                            {"_id": f"{user.id}"},
                            {
                                "$set": {
                                    "name": f"{user}",
                                    "correct": correct,
                                    "wrong": wrong,
                                }
                            },
                            True,
                        )
            elif len(message.embeds) == 0:
                if "RUINED IT AT" in content:
                    user = message.mentions[0]
                    if not isinstance(user, Member):
                        return
                    counter_data = update_user_count_incorrect(user.id, CLASSIC_BOT_ID)
                    if counter_data is None:
                        return
                    sam_channel = self.bot.get_channel(SAM_CHANNEL_ID)
                    if isinstance(sam_channel, TextChannel):
                        await streak_reset(
                            counter_data,
                            user,
                            f"{CLASSIC_BOT_ID}",
                            sam_channel,
                        )

        # * All messages by beta bot
        elif author.id == BETA_BOT_ID:
            if len(message.embeds) != 0:
                return
            if "Wrong word!" in content:
                user = message.mentions[0]
                if not isinstance(user, Member):
                    return
                saves_left = int(findall("[0-9]+", content)[1])
                await control_permission(saves_left, user, message)
                counter_data = update_user_count_incorrect(user.id, BETA_BOT_ID)
                if counter_data is None:
                    return
                sam_channel = self.bot.get_channel(SAM_CHANNEL_ID)
                if isinstance(sam_channel, TextChannel):
                    await streak_reset(
                        counter_data,
                        user,
                        f"{BETA_BOT_ID}",
                        sam_channel,
                    )
            elif "Try again" in content:
                time = findall("[0-9]+", content)
                user = misc.find_one({"_id": "abc?d"})
                if user is None:
                    return
                time_now = datetime.utcnow().replace(microsecond=0)
                try:
                    hour, mins = int(time[0]), int(time[1])
                except:
                    return
                if hour == 0 and mins == 0:
                    mins = 1
                time_new = time_now + timedelta(hours=hour, minutes=mins)
                if time_collection.find_one(
                    {"user": user["user"], "command": "use abc?d"}
                ):
                    time_collection.update_one(
                        {"user": user["user"], "command": "use abc?d"},
                        {"$set": {"time": time_new}},
                    )
                else:
                    time_collection.insert_one(
                        {"time": time_new, "user": user["user"], "command": "use abc?d"}
                    )
            elif findall("You have been given", content):
                user = misc.find_one({"_id": "abc?d"})
                if user is None:
                    return
                time_now = datetime.utcnow().replace(microsecond=0)
                time_new = time_now + timedelta(days=1)
                if time_collection.find_one(
                    {"user": user["user"], "command": "use abc?d"}
                ):
                    time_collection.update_one(
                        {"user": user["user"], "command": "use abc?d"},
                        {"$set": {"time": time_new}},
                    )
                else:
                    time_collection.insert_one(
                        {"time": time_new, "user": user["user"], "command": "use abc?d"}
                    )
            elif match("Sent the gift", content):
                user_test = misc.find_one({"_id": "abc?gift"})
                if user_test is None:
                    return
                userID = user_test["user"]
                user_post = beta_collection.find_one({"_id": userID})
                if user_post:
                    user = guild.get_member(user_test["user"])
                    if user is None:
                        return
                    actual_saves = user_post["current_saves"] + 1
                    await control_permission(actual_saves, user, message)
                    beta_collection.update_one(
                        {"_id": f"{userID}"}, {"$inc": {"current_saves": 1}}
                    )
            elif match("Count reset", content):
                counter = cast(Member, message.mentions[0])
                await self.ruin_ban(counter)
                counter_data = update_user_count_incorrect(counter.id, BETA_BOT_ID)
                if counter_data is None:
                    return
                sam_channel = self.bot.get_channel(SAM_CHANNEL_ID)
                if isinstance(sam_channel, TextChannel):
                    await streak_reset(
                        counter_data,
                        counter,
                        f"{BETA_BOT_ID}",
                        sam_channel,
                    )

        """For reading numselli embeds"""
        if author.id == NUMSELLI_BOT_ID:
            if message.embeds:
                embed_content = message.embeds[0].to_dict()
                if message.interaction and message.interaction.name == "user":
                    await self.numselli_user_update(message)
                if "title" in embed_content and "Sent" in embed_content["title"]:
                    if "description" not in embed_content:
                        return
                    nums = findall("[0-9]+\.*[0-9]*", embed_content["description"])  # type: ignore
                    sent_saves = float(nums[0])
                    rec_id = int(nums[1])
                    saves_left = float(nums[3])
                    have_save = cast(Role, guild.get_role(NUMSELLI_SAVE_ID))
                    dishonorable: Role = cast(Role, guild.get_role(DISHONORABLE_ID))
                    user_post = numselli_collection.find_one({"_id": rec_id})
                    if user_post is None:
                        return
                    receiver = guild.get_member(rec_id)
                    if receiver is None:
                        logger_monitor.error(
                            f"Could not find {rec_id} in numselli error"
                        )
                        return
                    actual_saves = user_post.get("current_saves", 0) + sent_saves
                    numselli_collection.update_one(
                        {"_id": f"{rec_id}"},
                        {"$set": {"current_saves": actual_saves}},
                    )
                    await control_permission(actual_saves, receiver, message)
                    if message.interaction is None:
                        return
                    sender = message.interaction.user
                    numselli_collection.update_one(
                        {"_id": f"{sender.id}"},
                        {"$set": {"current_saves": saves_left}},
                        True,
                    )
                    if saves_left >= 1:
                        await message.add_reaction("💾")
                    else:
                        await message.add_reaction("❌")
                        msg = f"<@{sender.id}> doesn't have enough saves "
                        msg += f"and cannot count with <@{NUMSELLI_BOT_ID}>"

                if "title" in embed_content and match(
                    "Save Used", embed_content["title"]
                ):
                    if "description" not in embed_content:
                        return
                    if match("Channel save", embed_content["description"]):

                        async def button_callback(interaction: Interaction):
                            have_save = guild.get_role(NUMSELLI_SAVE_ID)
                            if have_save is None:
                                return
                            for user in have_save.members:
                                await user.remove_roles(
                                    have_save, reason="Channel save got used"
                                )
                            await interaction.response.edit_message(
                                content="Channel locked for all counters.",
                                view=None,
                            )

                        channel_send = guild.get_channel(SAM_CHANNEL_ID)
                        if not isinstance(channel_send, TextChannel):
                            return
                        msg_send = f"Channel save got used "
                        msg_send += "in {message.channel.mention}."
                        await channel_send.send(msg_send)
                        msg_send = "@everyone channel save got used. LOCK THE CHANNEL"
                        button = Button(label="LOCK", style=nextcord.ButtonStyle.red)
                        button.callback = button_callback
                        view = View()
                        view.add_item(button)
                        await channel.send(msg_send, view=view)
                    else:
                        nums = findall(
                            "[0-9]+\.*[0-9]*",  # type: ignore
                            embed_content["description"],  # type: ignore
                        )
                        user_id = int(nums[0])
                        current_saves = float(nums[1])
                        user = guild.get_member(user_id)
                        if user is None:
                            return
                        await control_permission(current_saves, user, message)
                        counter_data = update_user_count_incorrect(
                            user.id, NUMSELLI_BOT_ID
                        )
                        if counter_data is None:
                            return
                        sam_channel = self.bot.get_channel(SAM_CHANNEL_ID)
                        if isinstance(sam_channel, TextChannel):
                            await streak_reset(
                                counter_data,
                                user,
                                f"{NUMSELLI_BOT_ID}",
                                sam_channel,
                            )
                        update_user_count_incorrect(user.id, NUMSELLI_BOT_ID)

        # * CrazyCounting
        if author.id == CRAZY_BOT_ID:
            if len(message.embeds) == 1:
                embed_content = message.embeds[0].to_dict()
                if (
                    "fields" in embed_content
                    and "Stats" in embed_content["fields"][0]["name"]
                ):
                    user_name, numbers_list = stats_embed_extractor(message.embeds[0])
                    if user_name is None:
                        await channel.send("Could not find user name")
                        return
                    if numbers_list is None:
                        await channel.send("Could not read field values")
                        return
                    user = guild.get_member_named(user_name)
                    if user is None:
                        return
                    await control_permission(
                        numbers_list[-1],
                        user,
                        message,
                    )

        # """Functions for dank memer"""
        # if author.id == DANK_BOT_ID:
        #     if message.interaction and message.embeds:
        #         slash_data = message.interaction.data
        #         embed_content = message.embeds[0].to_dict()
        #         if "description" not in embed_content:
        #             return
        #         if embed_content["description"].startswith("Remember"):
        #             await message.channel.send(embed_content["description"])
        #             dank_collection.update_one(
        #                 {"_id": int(slash_data["user"]["id"])},
        #                 {"$set": {"data": embed_content["description"]}},
        #                 True,
        #             )
        #         if (
        #             slash_data["name"] == "work apply"
        #             or slash_data["name"] == "work shift"
        #         ):
        #             embed_content = message.embeds[0].to_dict()
        #             if "description" not in embed_content:
        #                 return
        #             if search("<t:", embed_content["description"]):
        #                 user_id = int(slash_data["user"]["id"])
        #                 if time_collection.find_one(
        #                     {
        #                         "user": user_id,
        #                         "command": "work shift",
        #                     }
        #                 ):
        #                     sec_str = findall("[0-9]+", embed_content["description"])[0]
        #                     time_next = EPOCH + timedelta(seconds=int(sec_str))
        #                     time_collection.update_one(
        #                         {
        #                             "user": user_id,
        #                             "command": "work shift",
        #                         },
        #                         {
        #                             "$set": {
        #                                 "time": time_next,
        #                                 "channel": message.channel.id,
        #                             }
        #                         },
        #                     )
        #                     time_str = utils.format_dt(time_next, "t")
        #                     await message.channel.send(f"Will remind you at {time_str}")
        #         # elif (slash_data["name"] == "daily"):
        #         #     embed_content = message.embeds[0].to_dict()
        #         #     if ("fields" in embed_content):
        #         #         try:
        #         #             sec_str = int(findall("[0-9]+",
        #         #                 embed_content["fields"][3]["value"])[0])
        #         #         except:
        #         #             logger_monitor.exception("Failed to find the time.")
        #         #         else:
        #         #             time_next = EPOCH + timedelta(seconds=int(sec_str))
        #         #             time_collection.update_one(
        #         #                 {
        #         #                     "user": user_id,
        #         #                     "command": "daily",
        #         #                 }, {
        #         #                     "$set": {
        #         #                         "time": time_next,
        #         #                         "channel": message.channel.id
        #         #                     }
        #         #                 }
        #         #             )
        #         #             time_str = utils.format_dt(time_next, "t")
        #         #             await message.channel.send(f"Will remind you at {time_str}")
        #         # else:
        #         #     embed_content = message.embeds[0].to_dict()
        #         #     await message.channel.send(embed_content)

        # if message.channel.id == 931498728760672276:
        #     time = message.created_at.replace(tzinfo=None,microsecond=0)
        #     print(time)
        #     time_post = misc.find_one({"_id":"trial"})
        #     print(time_post)
        #     t1 = time - time_post["timetrial"]
        #     print(t1.total_seconds())

    # @commands.Cog.listener()
    # async def on_message_edit(self, before: Message, after: Message):
    #     if after.interaction and after.author.id == DANK_BOT_ID:
    #         if before.interaction is None:
    #             return
    #         slash_data = before.interaction.data
    #         if slash_data["name"] == "work shift":
    #             embed_content = after.embeds[0].to_dict()
    #             if "description" not in embed_content:
    #                 return
    #             await after.channel.send(embed_content["description"])
    #             if after.components:
    #                 for component in after.components:
    #                     # if component.type == nextcord.ComponentType.action_row:
    #                     main_component = cast(nextcord.ActionRow, component)
    #                     msg = ""
    #                     for sub_component in main_component.children:
    #                         comp_content = sub_component.to_dict()
    #                         msg += (
    #                             comp_content.get(
    #                                 "emoji", comp_content.get("label", "Error")
    #                             )
    #                             + " "
    #                         )
    #                         msg += str(comp_content.get("disabled", False)) + " "
    #                         # await after.channel.send(comp_content)
    #                     await after.channel.send(msg)
    #             if "footer" in embed_content:
    #                 user_id = int(slash_data["user"]["id"])
    #                 if time_collection.find_one(
    #                     {"user": user_id, "command": "work shift"}
    #                 ):
    #                     job = embed_content["footer"]["text"].split(" as a ")[1]
    #                     if job != "":
    #                         time_delta = dank_work_time[job]
    #                     else:
    #                         time_delta = timedelta(hours=1)
    #                     time_next = utils.utcnow().replace(microsecond=0) + time_delta
    #                     time_collection.update_one(
    #                         {"user": user_id, "command": "work shift"},
    #                         {"$set": {"time": time_next, "channel": before.channel.id}},
    #                     )
    #                     time_str = utils.format_dt(time_next, "t")
    #                     await after.channel.send(f"Will remind at {time_str}")
    #             # else:
    #             #     await after.channel.send(embed_content)

    @commands.Cog.listener()
    async def on_presence_update(self, member_old: Member, member_new: Member):
        """Lock/Unlock channels if bots are offline/online."""
        if member_new.bot == False:
            return
        if member_new.raw_status == member_old.raw_status:
            return
        overrides = misc.find_one({"_id": "override"})
        if overrides is None:
            return
        if member_new.id == CLASSIC_BOT_ID:
            if overrides["classic"] == True:
                return
            channel = self.bot.get_channel(CLASSIC_CHANNEL_ID)
            role = member_new.guild.get_role(COUNTAHOLIC_ID)
        elif member_new.id == OG_BOT_ID:
            if overrides["og"] == True:
                return
            channel = self.bot.get_channel(OG_CHANNEL_ID)
            role = member_new.guild.get_role(OG_SAVE_ID)
        elif member_new.id == NUMSELLI_BOT_ID:
            role = member_new.guild.get_role(NUMSELLI_SAVE_ID)
            channel = ""
        else:
            return
        if role is None:
            return
        if member_old.raw_status == "online" and member_new.raw_status == "offline":
            if member_new.id == NUMSELLI_BOT_ID:
                for channel_name in NUMSELLI_CHANNEL_ID:
                    channel_id = NUMSELLI_CHANNEL_ID[channel_name]
                    channel = self.bot.get_channel(channel_id)
                    if not isinstance(channel, TextChannel):
                        continue
                    overwrites = channel.overwrites_for(role)
                    overwrites.update(send_messages=False)
                    await channel.set_permissions(role, overwrite=overwrites)
                    embedVar = Embed(
                        description="Channel locked as bot is offline",
                        color=color_lamuse,
                    )
                    await channel.send(embed=embedVar)
            else:
                if not isinstance(channel, TextChannel):
                    return
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=False)
                embedVar = Embed(
                    description="Channel locked as bot is offline", color=color_lamuse
                )
                await channel.set_permissions(role, overwrite=overwrites)
                await channel.send(embed=embedVar)
        elif member_old.raw_status == "offline" and member_new.raw_status == "online":
            if member_new.id == NUMSELLI_BOT_ID:
                for channel_name in NUMSELLI_CHANNEL_ID:
                    channel_id = NUMSELLI_CHANNEL_ID[channel_name]
                    channel = self.bot.get_channel(channel_id)
                    if not isinstance(channel, TextChannel):
                        return
                    overwrites = channel.overwrites_for(role)
                    overwrites.update(send_messages=True)
                    await channel.set_permissions(role, overwrite=overwrites)
                    embedVar = Embed(
                        description="Channel unlocked as bot is online",
                        color=color_lamuse,
                    )
                    await channel.send(embed=embedVar)
            else:
                if not isinstance(channel, TextChannel):
                    return
                overwrites = channel.overwrites_for(role)
                overwrites.update(send_messages=True)
                embedVar = Embed(
                    description="Channel unlocked as bot is online", color=color_lamuse
                )
                await channel.set_permissions(role, overwrite=overwrites)
                await channel.send(embed=embedVar)
        else:
            return

    @commands.command(name="run")
    async def command_run(self, ctx: Context, channel: TextChannel | None = None):
        """Gives the time when the run started."""
        if channel is None:
            channel_id = OG_CHANNEL_ID
        else:
            channel_id = channel.id
        await self.run(ctx, channel_id)

    @slash_command(name="run", guild_ids=servers)
    async def slash_run(
        self,
        ctx: Interaction,
        channel: GuildChannel,
        # = SlashOption(
        #     description="The channel you want to see run stats of",
        #     required=False,
        #     channel_types=[TextChannel],  # type: ignore
        #     default=None,
        # ),
    ):
        """Gives the time when the run started"""
        if channel is None:
            channel_id = OG_CHANNEL_ID
        else:
            channel_id = channel.id
        await self.run(ctx, channel_id)

    async def run(self, ctx: Union[commands.Context, Interaction], channel_id: int):
        """The method used to run both slash and prefix command of run."""
        time_now = utcnow()

        run_data = find_run_data(channel_id)
        if run_data is None:
            msg = f"No run data for <@{channel_id}>."
            await ctx.send(msg)
            return

        time_last = run_data.time_last.replace(tzinfo=UTC)

        # If its been a while since a run.
        if time_now - time_last >= timedelta(minutes=10):
            msg = "Its been a while since a run."
            await ctx.send(msg)
            return

        embedVar = create_run_embed(run_data)
        await ctx.send(embed=embedVar)

    async def og_user_update(self, message: Message, user: Member):
        """Update og stats of the user after seeing c!user."""

        _, numbers_list = stats_embed_extractor(message.embeds[0])
        if numbers_list is None:
            await message.channel.send("Failed to read field value")
            return
        update_user_stats(user, *numbers_list[:3], message.author.id)
        await control_permission(numbers_list[-1], user, message)

    async def vote_update(self, message: Message, user: Member):
        """Update vote stats after using c!vote."""
        embed_content = message.embeds[0].to_dict()
        if "description" not in embed_content:
            return
        description = embed_content["description"]
        saves = description.split("**")[1]
        current_saves = float(saves.split("/")[0])
        total_saves = int(saves.split("/")[1])
        guild = message.guild
        if guild is None:
            return
        counter_post = og_collection.find_one({"_id": f"{user.id}"})
        if not isinstance(counter_post, dict):
            msg = "Run `c!user` first."
            await message.reply(msg)
            return
        await control_permission(current_saves, user, message)
        rem = counter_post.get("reminder", False)
        dm = counter_post.get("dm", False)
        if rem:
            if "fields" not in embed_content:
                return
            field1 = embed_content["fields"][0]["value"]
            field2 = embed_content["fields"][1]["value"]
            channel_id = message.channel.id
            if search("You have already", field1):
                time1 = findall("[0-9]+", field1)
                time_new = datetime.fromtimestamp(int(time1[0]), timezone.utc)
                time_collection.update_one(
                    {"user": user.id, "command": "vote in top.gg"},
                    {
                        "$set": {
                            "time": time_new,
                            "dm": dm,
                            "channel": channel_id,
                        }
                    },
                    upsert=True,
                )
            if search("You have already", field2):
                time2 = findall("[0-9]+", field2)
                time_new = datetime.fromtimestamp(int(time2[0]), timezone.utc)
                time_collection.update_one(
                    {"user": user.id, "command": "vote in discordbotlist.com"},
                    {
                        "$set": {
                            "time": time_new,
                            "dm": dm,
                            "channel": channel_id,
                        }
                    },
                    upsert=True,
                )

    async def og_transfer(self, sender: Member, og_message: Message):
        embed_content = og_message.embeds[0].to_dict()
        title = embed_content.get("title")
        if title is None:
            return
        if not title.startswith("Save Transferred"):
            return

        guild = og_message.guild
        if guild is None:
            return
        dishonorable = cast(Role, guild.get_role(DISHONORABLE_ID))
        og_save = cast(Role, guild.get_role(OG_SAVE_ID))
        description = embed_content.get("description")
        if description is None:
            return
        num_list = findall("[0-9]+\.*[0-9]*", description)  # type: ignore
        rec_id = int(num_list[1])
        current_saves = float(num_list[3])

        if current_saves < 1:
            if og_save in sender.roles:
                await sender.remove_roles(og_save)
                msg = f"You can no longer count in <#{OG_CHANNEL_ID}>"
                msg += f"till you have 1 save <@{sender.id}>"
                await og_message.channel.send(msg)
        else:
            await og_message.add_reaction("💾")

        receiver = guild.get_member(rec_id)
        if receiver is None:
            return
        await control_permission(1, receiver, og_message)

        og_collection.update_one(
            {"_id": f"{sender.id}"}, {"$set": {"current_saves": current_saves}}, True
        )
        og_collection.update_one(
            {"_id": f"{rec_id}"}, {"$inc": {"current_saves": 1}}, True
        )

    async def numselli_user_update(self, message: Message):
        """Update numselli data from user embed."""
        embed_content = message.embeds[0].to_dict()
        guild = message.guild
        if guild is None:
            return
        if "title" not in embed_content:
            return
        if "fields" not in embed_content:
            return
        if "Stats for " not in embed_content["title"]:
            return
        field1 = embed_content["fields"][0]
        name = embed_content["title"].split(" ", 2)[2]
        number_list = field1["value"].split("**")
        rate = float(number_list[1][:-1])
        correct = int(number_list[3].replace(",", ""))
        wrong = int(number_list[5].replace(",", ""))
        saves = number_list[9]
        current_saves = float(saves.split("/")[0])
        user = guild.get_member_named(name)
        if user is None:
            return
        update_user_stats(user, rate, correct, wrong, NUMSELLI_BOT_ID)
        await control_permission(current_saves, user, message)

    async def beta_update(self, message: Message, user_id: int):
        """Update beta stats."""
        embed_content = message.embeds[0].to_dict()
        guild = message.guild
        if guild is None:
            return
        if "title" not in embed_content:
            return
        if "stats" not in embed_content["title"]:
            return
        if "fields" not in embed_content:
            return
        if "Saves" not in embed_content["fields"][3]["name"]:
            return

        user = guild.get_member(user_id)
        if user is None:
            return
        field_content = embed_content["fields"][3]["value"]
        current_saves = float(field_content.split("/")[0][1:])
        if current_saves == int(current_saves):
            current_saves = int(current_saves)
        total_saves = int(field_content.split("/")[1][:-1])
        field_content = embed_content["fields"][0]["value"]
        rate = float(embed_content["fields"][2]["value"][1:-2])
        correct = int(split(" ", field_content)[0][1:])
        wrong = int(embed_content["fields"][1]["value"][1:-1])
        update_user_stats(user, rate, correct, wrong, BETA_BOT_ID)
        await control_permission(current_saves, user, message)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """Do something when roles get changed."""
        if len(before.roles) != len(after.roles):
            dishonorable = before.guild.get_role(DISHONORABLE_ID)
            if dishonorable in after.roles and dishonorable not in before.roles:
                await self.ruin_ban(after)

    async def ruin_ban(self, user: Member):
        """Ban a user from counting channels if they ruin a count."""
        guild = user.guild
        dishonorable = cast(Role, guild.get_role(DISHONORABLE_ID))
        og_save = cast(Role, guild.get_role(OG_SAVE_ID))
        have_save = cast(Role, guild.get_role(NUMSELLI_SAVE_ID))
        beta_save = cast(Role, guild.get_role(BETA_SAVE_ID))
        crazy_save = cast(Role, guild.get_role(CRAZY_SAVE_ID))
        await user.add_roles(dishonorable)
        await user.remove_roles(og_save, have_save, beta_save, crazy_save)
        send_channel = guild.get_channel(SAM_CHANNEL_ID)
        if not isinstance(send_channel, TextChannel):
            return
        await send_channel.send(
            f"{user.mention} has been banned from counting channels."
        )

    @tasks.loop(seconds=1)
    async def check_time(self):
        time_now = utcnow()

        run_data = time_up_channels(time_now)
        if run_data is None:
            return

        if run_data.count > 50:
            embedVar = create_run_embed(run_data)
            send_channel = self.bot.get_channel(SAM_CHANNEL_ID)
            if not isinstance(send_channel, TextChannel):
                return
            try:
                task = await send_channel.send(embed=embedVar)
                # print(task.id)
            except nextcord.errors.Forbidden:
                logger_monitor.error(
                    f"Couldn't send run end msg in {send_channel.name}"
                )

        if run_data.id == f"{OG_CHANNEL_ID}":
            og_send_channel = self.bot.get_channel(OG_CHANNEL_ID)
            if not isinstance(og_send_channel, TextChannel):
                return
            if og_send_channel.name != "og-counting":
                try:
                    await og_send_channel.edit(name="og-counting")
                except nextcord.Forbidden:
                    await og_send_channel.send("Editing channel name failed.")
                    logger_monitor.exception("Editing channel name failed.")

    @tasks.loop(time=time(23, 59, 59, tzinfo=UTC))
    async def daily(self):
        time = datetime.utcnow().isoformat()[:10]
        cursor = og_collection.find(
            {"daily": {"$gte": 1}},
            {
                "name": 1,
                "daily": 1,
            },
        ).sort("daily", -1)
        msg = "Total numbers counted today: <!@#TOTALCOUNTED!@#>"
        total = 0
        i = 0
        for user in cursor:
            i += 1
            name = user.get("name", "Unknown")
            daily = user.get("daily", ">1")
            try:
                total += int(daily)
            except:
                pass
            msg += f"\n{i}. {name} - {daily}"
        msg = msg.replace("<!@#TOTALCOUNTED!@#>", str(total), 1)
        embedVar = Embed(title=f"{time}", description=msg, color=color_lamuse)
        scores = cast(TextChannel, self.bot.get_channel(SAM_CHANNEL_ID))
        if total > 1:
            await scores.send(embed=embedVar)
            og_collection.update_many({"daily": {"$gte": 1}}, {"$set": {"daily": 0}})


def setup(bot):
    """The setup command for the cog."""
    bot.add_cog(Monitor(bot))
