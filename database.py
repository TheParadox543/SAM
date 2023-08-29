import certifi
from os import getenv
from datetime import datetime, timedelta, timezone, UTC

from pymongo import MongoClient, ReturnDocument
from dotenv import load_dotenv
from nextcord import TextChannel
from pydantic import BaseModel

from bot_secrets import *

ca = certifi.where()
load_dotenv()

# CLUSTER = MongoClient(getenv("DB_LOCAL_TOKEN"), tlsCAFile=ca)
CLUSTER = MongoClient(getenv("DB_US_TOKEN"), tlsCAFile=ca)

db = CLUSTER["lamuse"]
og_collection = db["og_collection"]
classic_collection = db["classic_collection"]
abc_collection = db["abc_collection"]
beta_collection = db["beta_collection"]
numselli_collection = db["numselli_collection"]
crazy_collection = db["crazy_collection"]
misc = db["misc"]
time_collection = db["time"]
dank_collection = db["dank"]
track_collection = db["tracklist"]
run_collection = db["run"]

db_cc = CLUSTER["cc_main"]
lottery_collection = db_cc["lottery_collection"]

track_list = [
    OG_CHANNEL_ID,
    CLASSIC_CHANNEL_ID,
    BETA_CHANNEL_ID,
    NUMSELLI_CHANNEL_ID["whole"],
    NUMSELLI_CHANNEL_ID["letters"],
    NUMSELLI_CHANNEL_ID["binary"],
    NUMSELLI_CHANNEL_ID["decimal"],
    NUMSELLI_CHANNEL_ID["hex"],
    NUMSELLI_CHANNEL_ID["roman"],
    NUMSELLI_CHANNEL_ID["two"],
    NUMSELLI_CHANNEL_ID["five"],
    NUMSELLI_CHANNEL_ID["ten"],
    NUMSELLI_CHANNEL_ID["hundred"],
]

emoji_list = [
    "<a:confetti:914965969661751309>",
    "<a:catjump:915069990951059467>",
    # "<a:pepeflame:914966371752882217",
    # "<a:pepelaugh:924117672550105089>",
    # "<a:rainbowboy:930683298710159360>",
    "<a:hypeboy:914966295592710194>",
    "<a:blobproud:953107361470496849>",
    "<a:emoji_rainbow_eyes:953064880066416713>",
    "<a:runningmanyellow:915054034589732894>",
    "<a:wiggle:915069970289946654>",
    "<a:cat_with_heart:953064613392576542>"
    # "<a:rainbowglowstickvibeslow:915069470198865961>"
]
check_emoji = "✅"
wrong_emoji = "❌"
warning_emoji = "⚠️"
clock_emoji = "⏰"

roman = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
    "IV": 4,
    "IX": 9,
    "XL": 40,
    "XC": 90,
    "CD": 400,
    "CM": 900,
}

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

ogreg_help = "Toggle for c!vote reminders. If you write DM as an option, bot will toggle reminders sent to your DM."

dank_work_time = {
    "Discord Mod": timedelta(minutes=40),
    "Babysitter": timedelta(minutes=40),
    "Fast Food Cook": timedelta(minutes=43),
    "House Wife": timedelta(minutes=43),
    "Twitch Streamer": timedelta(minutes=46),
    "Youtuber": timedelta(minutes=46),
    "Proffesional Hunter": timedelta(minutes=49),
    "Professional Fisherman": timedelta(minutes=49),
    "Bartender": timedelta(minutes=49),
    "Robber": timedelta(minutes=49),
    "Police Officer": timedelta(minutes=49),
    "Teacher": timedelta(minutes=49),
    "Musician": timedelta(minutes=49),
    "Pro Gamer": timedelta(minutes=52),
    "Manager": timedelta(minutes=52),
    "Developer": timedelta(minutes=52),
    "Day Trader": timedelta(minutes=55),
    "Santa Claus": timedelta(minutes=55),
    "Poltician": timedelta(minutes=55),
    "Veterinarian": timedelta(minutes=55),
    "Pharmacist": timedelta(minutes=55),
    "Dank Memer Shopkeeper": timedelta(minutes=55),
    "Lawyer": timedelta(minutes=58),
    "Doctor": timedelta(minutes=58),
    "Scientist": timedelta(minutes=58),
    "Ghost": timedelta(minutes=58),
}

bot_role = {
    OG_BOT_ID: OG_SAVE_ID,
    CLASSIC_BOT_ID: COUNTAHOLIC_ID,
    NUMSELLI_BOT_ID: NUMSELLI_SAVE_ID,
    BETA_BOT_ID: BETA_SAVE_ID,
    CRAZY_BOT_ID: CRAZY_SAVE_ID,
}

bot_collection = {
    OG_BOT_ID: og_collection,
    CLASSIC_BOT_ID: classic_collection,
    NUMSELLI_BOT_ID: numselli_collection,
    BETA_BOT_ID: beta_collection,
    CRAZY_BOT_ID: crazy_collection,
}

bot_channels = {
    OG_BOT_ID: [OG_CHANNEL_ID],
    CLASSIC_BOT_ID: [CLASSIC_CHANNEL_ID],
    NUMSELLI_BOT_ID: [
        NUMSELLI_CHANNEL_ID["whole"],
        NUMSELLI_CHANNEL_ID["letters"],
        NUMSELLI_CHANNEL_ID["binary"],
        NUMSELLI_CHANNEL_ID["decimal"],
        NUMSELLI_CHANNEL_ID["hex"],
        NUMSELLI_CHANNEL_ID["roman"],
        NUMSELLI_CHANNEL_ID["two"],
        NUMSELLI_CHANNEL_ID["five"],
        NUMSELLI_CHANNEL_ID["ten"],
        NUMSELLI_CHANNEL_ID["hundred"],
    ],
    BETA_BOT_ID: [BETA_CHANNEL_ID],
}


class UserData(BaseModel):
    id: str
    name: str
    correct: int = 0
    wrong: int = 0
    rate: float = 0
    streak: int | str = 0
    high: int | str = 0
    daily: int = 0

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = kwargs.pop("_id")
        if "streak" in kwargs and isinstance(kwargs["streak"], str):
            kwargs["streak"] = 0
            kwargs["high"] = 0
        super().__init__(**kwargs)

    def dict(self):
        data = super().dict()
        data["_id"] = data.pop("id")
        return data


class UserRunData(BaseModel):
    id: str
    count: int = 1


class RunData(BaseModel):
    id: str
    name: str
    time_start: datetime
    time_last: datetime
    count: int = 1
    contributors: list[UserRunData] = list()

    def __init__(self, **kwargs):
        if "_id" in kwargs:
            kwargs["id"] = kwargs.pop("_id")
        super().__init__(**kwargs)
        self.time_last = self.time_last.replace(tzinfo=UTC)
        self.time_start = self.time_start.replace(tzinfo=UTC)

    def dict(self):
        data = super().dict()
        data["_id"] = data.pop("id")
        return data


def update_user_stats(
    user: Member,
    rate: float,
    correct: int,
    wrong: int,
    bot_id: int,
):
    """Update the stats data of a user

    Args:
        user (Member): _description_
        rate (float): _description_
        correct (int): _description_
        wrong (int): _description_
        bot (int): _description_
    """
    result = bot_collection[bot_id].update_one(
        {"_id": f"{user.id}"},
        {
            "$set": {
                "name": f"{user.display_name}",
                "correct": correct,
                "wrong": wrong,
                "rate": rate,
            },
        },
        True,
    )
    return result.modified_count


def find_user_stats(user_id: int, bot_id: int):
    """Find user data

    Parameters
    ----------
        user_id (int): The ID of the user
        bot (int | str): The bot who gave the stats

    Returns
    -------
    """

    data = bot_collection[bot_id].find_one({"_id": f"{user_id}"})
    if isinstance(data, dict):
        user_data = UserData(**data)
        return user_data


def update_user_count_correct(user_id: int, bot_id: int):
    """Increase the count and streak if counter got it right"""
    counter_data = bot_collection[bot_id].find_one(
        {"_id": f"{user_id}"},
        {"streak": 1, "high": 1, "alt": 1},
    )
    if not isinstance(counter_data, dict):
        return None
    if "alt" in counter_data:
        original_id = f"{counter_data['alt']}"
        original_data = bot_collection[bot_id].find_one(
            {"_id": f"{original_id}"},
            {"streak": 1, "high": 1},
        )
        if not isinstance(original_data, dict):
            return None
        original_update = {"$inc": {"streak": 1, "daily": 1}}
        if original_data.get("streak", 0) >= original_data.get("high", 0):
            original_update["$set"] = {"high": original_data.get("streak", 0) + 1}
        try:
            result = bot_collection[bot_id].find_one_and_update(
                {"_id": f"{original_id}"},
                original_update,
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            bot_collection[bot_id].update_one(
                {"_id": f"{user_id}"},
                {"$inc": {"correct": 1}},
            )
        except:
            return None
    else:
        update_dict = {"$inc": {"correct": 1, "streak": 1, "daily": 1}}
        if counter_data.get("streak", 0) >= counter_data.get("high", 0):
            update_dict["$set"] = {"high": counter_data.get("streak", 0) + 1}
        try:
            result = bot_collection[bot_id].find_one_and_update(
                {"_id": f"{user_id}"},
                update_dict,
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except:
            return None
    return result


def update_user_count_incorrect(user_id: int, bot_id: int):
    """Decrease the count and reset streak if counter got it wrong"""
    counter_data = bot_collection[bot_id].find_one(
        {"_id": f"{user_id}"},
        {"streak": 1, "high": 1, "alt": 1},
    )
    if not isinstance(counter_data, dict):
        return None
    if "alt" in counter_data:
        original_id = f"{counter_data['alt']}"
        original_data = bot_collection[bot_id].find_one(
            {"_id": f"{original_id}"},
            {"streak": 1, "high": 1},
        )
        if not isinstance(original_data, dict):
            return None
        original_update = {"$set": {"streak": 0}}
        try:
            result = bot_collection[bot_id].find_one_and_update(
                {"_id": f"{original_id}"},
                original_update,
                upsert=True,
                return_document=ReturnDocument.BEFORE,
            )
            bot_collection[bot_id].update_one(
                {"_id": f"{user_id}"},
                {"$inc": {"wrong": 1}},
            )
        except:
            return None
    else:
        update_dict = {"$inc": {"wrong": 1}, "$set": {"streak": 0}}
        try:
            result = bot_collection[bot_id].find_one_and_update(
                {"_id": f"{user_id}"},
                update_dict,
                upsert=True,
                return_document=ReturnDocument.BEFORE,
            )
        except:
            return None
    return result


def update_run(channel: TextChannel, time_now: datetime, user_id: int):
    """_summary_

    Args:
        channel (TextChannel): _description_
        time_now (datetime): _description_
        user_id (int): _description_
    """
    data = run_collection.find_one({"_id": f"{channel.id}"})

    if data is None:
        run_data = RunData(
            id=f"{channel.id}",
            name=channel.name,
            time_start=time_now,
            time_last=time_now,
            contributors=[
                {
                    "id": f"{user_id}",
                    "count": 1,
                },
            ],
        )
    else:
        run_data = RunData(**data)
        run_data.name = channel.name
        time_last = run_data.time_last.replace(tzinfo=UTC)
        if (
            time_now - time_last < timedelta(minutes=10) and channel.id == OG_CHANNEL_ID
        ) or (
            time_now - time_last < timedelta(minutes=5) and channel.id != OG_CHANNEL_ID
        ):
            run_data.count += 1
            for item in run_data.contributors:
                if item.id == f"{user_id}":
                    item.count += 1
                    break
            else:
                run_data.contributors.append(
                    UserRunData(
                        id=f"{user_id}",
                        count=1,
                    ),
                )
        else:
            run_data.time_start = time_now
            run_data.count = 1
            run_data.contributors = [
                UserRunData(
                    id=f"{user_id}",
                    count=1,
                ),
            ]
        run_data.time_last = time_now
    run_collection.update_one(
        {"_id": f"{channel.id}"},
        {"$set": run_data.dict()},
        upsert=True,
    )
    return run_data


def sort_contributors(channel_id: str):
    """Sort the contributors of a channel by the number of counts

    Args:
        data (_type_): _description_
    """
    user_data = run_collection.aggregate(
        [
            {"$match": {"_id": f"{channel_id}"}},
            {
                "$unwind": {
                    "path": "$contributors",
                    "includeArrayIndex": "position",
                    "preserveNullAndEmptyArrays": False,
                }
            },
            {"$sort": {"contributors.count": -1}},
            {
                "$project": {
                    "id": "$contributors.id",
                    "count": "$contributors.count",
                    "_id": 0,
                }
            },
        ]
    )
    return [UserRunData(**user) for user in user_data]


def find_run_data(channel_id: int):
    """Find the run data of a channel

    Parameters
    ----------
        channel_id (int): The channel ID
    """

    data = run_collection.find_one({"_id": f"{channel_id}"})
    if data is not None:
        run_data = RunData(**data)
        run_data.contributors = sort_contributors(f"{channel_id}")
        return run_data


def time_up_channels(time_now: datetime):
    """Find the channels that have timed out their runs

    Args:
        time_now (datetime): _description_
    """
    data = run_collection.find_one(
        {
            "$or": [
                {
                    "_id": f"{OG_CHANNEL_ID}",
                    "time_last": {
                        "$lte": time_now - timedelta(minutes=10),
                    },
                },
                {
                    "_id": {
                        "$ne": f"{OG_CHANNEL_ID}",
                    },
                    "time_last": {
                        "$lte": time_now - timedelta(minutes=5),
                    },
                },
            ],
            "count": {"$gt": 0},
        },
    )
    if data is not None:
        run_data = RunData(**data)
        run_data.contributors = sort_contributors(f"{data.get('_id')}")
        run_collection.update_one(
            {"_id": run_data.id},
            {
                "$set": {
                    "count": 0,
                    "contributors": [],
                },
            },
        )
        return run_data
