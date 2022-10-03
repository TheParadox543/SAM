import certifi
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

from bot_secrets import *

ca = certifi.where()

CLUSTER = MongoClient(MONGO_DB_CONNECTION_STRING, tlsCAFile=ca)

db = CLUSTER["lamuse"]
og_collection = db["ogcollection"]
classic_collection = db["classiccollection"]
abc_collection = db["abccollection"]
beta_collection = db["betacollection"]
numselli_collection = db["numsellicollection"]
yoda_collection = db["yodacollection"]
misc = db["misc"]
time_collection = db["time"]
dank_collection = db["dank"]

track_list = [
    og_channel,
    classic_channel, 
    abc_channel, 
    beta_channel, 
    numselli_channels["whole"],
    numselli_channels["letters"],
    numselli_channels['binary'],
    numselli_channels["decimal"],
    numselli_channels["hex"],
    numselli_channels["roman"],
    numselli_channels["two"],
    numselli_channels["five"],
    numselli_channels["ten"],
    numselli_channels["hundred"],
    yoda_channel,
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

mode_list = {
    "1": "**counting**",
    "2": "**classic**",
    "3": "**ABC Counting**",
    "4": "**AlphaBeta**",
    "5": "**Numselli**",
    "6": "**yoda**",
}

roman = {
    'I':1,
    'V':5,
    'X':10,
    'L':50,
    'C':100,
    'D':500,
    'M':1000,
    'IV':4,
    'IX':9,
    'XL':40,
    'XC':90,
    'CD':400,
    'CM':900
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