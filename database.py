from pymongo import MongoClient
import certifi

import bot_secrets

ca = certifi.where()

CLUSTER = MongoClient(bot_secrets.MONGO_DB_CONNECTION_STRING, tlsCAFile=ca)

db = CLUSTER['lamuse']
og_collection = db['ogcollection']
classic_collection = db['classiccollection']
abc_collection = db['abccollection']
beta_collection = db['betacollection']
numselli_collection = db['numsellicollection']
misc = db['misc']
time_collection = db['time']
dank_collection = db['dank']