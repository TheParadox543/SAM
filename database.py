from pymongo import MongoClient
import certifi

from bot_secrets import *

ca = certifi.where()

CLUSTER = MongoClient(MONGO_DB_CONNECTION_STRING, tlsCAFile=ca)

db = CLUSTER['lamuse']
og_collection = db['ogcollection']
classic_collection = db['classiccollection']
abc_collection = db['abccollection']
beta_collection = db['betacollection']
numselli_collection = db['numsellicollection']
misc = db['misc']
time_collection = db['time']
dank_collection = db['dank']

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
    "5": "**Numselli**"
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