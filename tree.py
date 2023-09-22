import logging
from datetime import UTC, datetime, timedelta
from re import findall
from typing import cast

from nextcord import (
    ActionRow,
    Embed,
    Guild,
    Interaction,
    Member,
    Message,
    RawMessageUpdateEvent,
    TextChannel,
    slash_command,
)
from nextcord.ext.commands import Bot, Cog
from nextcord.ext.tasks import loop
from nextcord.ui import Button, View, button
from nextcord.utils import utcnow

# Using the logs.
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.FileHandler("sam.log")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


TREE_CHANNEL = 1083861644955881512
TREE_BOT_ID = 972637072991068220
TREE_WEBHOOK_ID = 1087087210261655562

WATER_ID = 1154787340007514262
FRUIT_ID = 1154787473721917602
INSECT_ID = 1154787645243789446


class RegisterReminderView(View):
    """Store data of users who opt in for reminders"""

    def __init__(self, *, auto_defer: bool = True) -> None:
        super().__init__(timeout=None, auto_defer=auto_defer)

    async def control_role(self, interaction: Interaction, role_id: int):
        """Control assigning and removing roles for a user"""

        if not isinstance(interaction.user, Member):
            return
        if not isinstance(interaction.guild, Guild):
            return
        member = interaction.user
        role = interaction.guild.get_role(role_id)
        if role is None:
            raise ValueError("Could not find role")
        if role in member.roles:
            try:
                await member.remove_roles(
                    role, reason=f"Does not want reminder for {role.name}"
                )
            except Exception as e:
                logger.exception(f"Could not remove role {role.name}")
            else:
                await interaction.send(
                    f"You have removed reminder {role.name}", ephemeral=True
                )
        else:
            try:
                await member.add_roles(role, reason=f"Wants reminder for {role.name}")
            except Exception as e:
                logger.exception(f"Could not add role {role.name}")
            else:
                await interaction.send(
                    f"You have added reminder {role.name}", ephemeral=True
                )

    @button(emoji="💧", custom_id="apb:register_water")
    async def register_water(self, button: Button, interaction: Interaction):
        """Register for water reminders"""

        await self.control_role(interaction, WATER_ID)

    @button(emoji="🍎", custom_id="apb:register_fruit")
    async def register_fruit(self, button, interaction: Interaction):
        """Register for fruit reminders"""

        await self.control_role(interaction, FRUIT_ID)

    @button(emoji="🐛", custom_id="apb:register_insect")
    async def register_insect(self, button, interaction: Interaction):
        """Register for insect reminders"""

        await self.control_role(interaction, INSECT_ID)


class Tree(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        self.next_time = None
        self.check_time.start()
        self.tree_channel = None
        self.water_message = None
        self.insect_message: list[Message] = list()

    @Cog.listener()
    async def on_ready(self):
        """Register view on getting ready"""
        self.bot.add_view(RegisterReminderView())

    @Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        """"""

        if payload.channel_id != TREE_CHANNEL:
            return
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
        except Exception as e:
            logger.exception("Could not find channel")
            return
        if isinstance(channel, TextChannel):
            if self.tree_channel is None:
                self.tree_channel = channel
            msg = await channel.fetch_message(payload.message_id)
            if msg.author.id != TREE_BOT_ID:
                return

            # * Check if it is the correct message
            if len(msg.embeds) < 0:
                return
            embed_content = msg.embeds[0].to_dict()
            if "description" not in embed_content:
                return
            if "Your tree" not in embed_content["description"]:
                return

            if "Thanks" in embed_content["description"]:
                try:
                    user_id_str, time_str = findall(
                        r"\d+", embed_content["description"].split("Thanks")[1]
                    )
                except ValueError:
                    return
                except IndexError:
                    return
                try:
                    next_time = datetime.utcfromtimestamp(float(time_str))
                except ValueError:
                    return
                else:
                    self.next_time = next_time.replace(tzinfo=UTC)
                member = channel.guild.get_member(int(user_id_str))
                if member is None:
                    return
                role = member.get_role(WATER_ID)
                if role is not None:
                    await member.remove_roles(role)
                    with open("water.txt", "w") as water_file:
                        water_file.write(f"{member.id}")
                if self.water_message is not None:
                    try:
                        await self.water_message.delete()
                    except Exception as e:
                        pass
                    finally:
                        self.water_message = None
            elif "Last" in embed_content["description"]:
                try:
                    user_id_str = findall(
                        r"\d+", embed_content["description"].split("Last")[1]
                    )[0]
                except ValueError:
                    return
                else:
                    try:
                        with open("water.txt", "r") as water_file:
                            user_id_stored = water_file.read()
                    except FileNotFoundError:
                        return
                    else:
                        if int(user_id_str) != int(user_id_stored):
                            return
                        member = channel.guild.get_member(int(user_id_str))
                        role = channel.guild.get_role(WATER_ID)
                        if role is None:
                            logger.error("Could not find role")
                            return
                        if member is None:
                            logger.error("Could not find user")
                            return
                        await member.add_roles(role)

            for row in msg.components:
                if isinstance(row, ActionRow):
                    button_count = len(row.children)
                    if button_count == 3 and len(self.insect_message) < 1:
                        try:
                            self.insect_message.append(
                                await channel.send(f"<@&{INSECT_ID}>", delete_after=20)
                            )
                            logger.debug(f"Insect: {self.insect_message}")
                        except Exception as e:
                            logger.exception("Insect msg not sent")
                    elif button_count != 3 and len(self.insect_message) > 1:
                        print(self.insect_message)
                        while len(self.insect_message) > 1:
                            try:
                                await self.insect_message[0].delete()
                            except:
                                pass
                            finally:
                                self.insect_message.pop(0)

    @Cog.listener()
    async def on_message(self, message: Message):
        """Find when fruit is ready"""

        if self.tree_channel is None:
            return
        if message.author.id != TREE_WEBHOOK_ID:
            return
        if len(message.embeds) != 1:
            return
        embed_content = message.embeds[0].to_dict()
        description = cast(str, embed_content.get("description"))
        if "Fruit" in description:
            try:
                await self.tree_channel.send(f"<@&{FRUIT_ID}>", delete_after=15)
            except Exception as e:
                logger.exception("Fruit msg not sent")

    @slash_command(
        guild_ids=[892553570208088064],
        default_member_permissions=8,
    )
    async def send_tree_role_view(self, interaction: Interaction):
        """Provide a few for users to get roles for tree reminders"""

        view = RegisterReminderView()
        embedVar = Embed(
            title="Tree Pings",
            description=(
                "Collect these roles to get pings from SAM"
                "\n💧 - The tree is ready to be watered again"
                "\n🍎 - Fruit is appearing"
                "\n🐛 - Insect is appearing"
            ),
        )
        await interaction.send("Sending view", ephemeral=True)
        if isinstance(interaction.channel, TextChannel):
            await interaction.channel.send(embed=embedVar, view=view)

    @loop(seconds=0.5)
    async def check_time(self):
        """"""

        time_now = utcnow()
        if self.next_time is not None and self.next_time < time_now:
            if self.tree_channel is not None:
                try:
                    self.water_message = await self.tree_channel.send(f"<@&{WATER_ID}>")
                except Exception as e:
                    logger.exception("Water msg not sent")
            self.next_time = None


def setup(bot: Bot):
    """Set up command for cog"""

    bot.add_cog(Tree(bot))
