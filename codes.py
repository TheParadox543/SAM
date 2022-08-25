from replit import db
import random

def set(ID):
  db[ID] = {
    "correct":0,
    "wrong": 0,
    "score": 0,
    "save": 0,
    "used": 0,
    "count": 3,
    "name":""
  }

def user(name, id):
  profile = "user"+str(id)
  if profile not in db:
    set(profile)
  db[profile].update({"name":name})

def stats(user):
  user = "user" + str(user)
  if "score" not in db[user]:
    score = "0"
  else:
    score = db[user]["score"]
  return db[user]["correct"], db[user]["wrong"], score, db[user]["save"], db[user]["used"], db[user]["count"]

def rank():
  key_value = {}
  msg = ""
  c = 1
  for key in db.prefix("user"):
    if "score" in db[key].keys():
      if db[key]["score"] !=0:
        key_value[db[key]["score"]] = db[key]["name"] #initialising the dictionary
        #print(db[key]["name"])
        #print(db[key]["score"])
  for i in sorted(key_value, reverse = True):
    msg = msg + f"{c}. {key_value[i]} - **{i}**\n"
    c = c + 1
  return msg


def user_correct(auth_id):
  name = "user" + str(auth_id)
  if name not in db:
    set(name)
  correct = db[name]["correct"]
  correct = correct + 1
  db[name]["correct"] = correct
  score = db[name]["score"]
  db[name]["score"] = score+1
  save = db[name]["save"]
  if correct % 777==0:
    save = save + 1
  if save < 10:
    db[name]["save"] = saves(save)
  if correct % 250 == 0:
    db[name]["count"] = update_count(correct)

def user_wrong(auth_id):
  name = "user" + str(auth_id)
  if name not in db:
    set(name)
  wrong = db[name]["wrong"]
  db[name]["wrong"] = wrong + 1
  score = db[name]["score"]
  db[name]["score"] = score-1
  if db[name]["save"] > 1:
    save = db[name]["save"]
    save = round(save - 1, 2)
    db[name]["save"] = save
    used = db[name]["used"]
    db[name]["used"] = used + 1
    msg = f"w<@{auth_id}>w{save}"
    return msg
  else:
    return "nosave"


def update_count(correct):
  if correct < 250:
    return 3
  elif correct < 500:
    return 4
  elif correct < 1000:
    return 5
  elif correct < 1500:
    return 6
  elif correct < 2000:
    return 7
  elif correct < 3000:
    return 8
  elif correct < 5000:
    return 9
  else:
    return 10


def saves(curr):
  if random.random()<0.1:
    curr = curr + 0.05 
  return curr

def prelist(pre):
  msg = ""
  for key in db.prefix(pre):
    for subkey in db[key]:
      msg += f"{db[key][subkey]} -"
    msg += "\n"
    #if key!="back":
    #new_key = key[4:]
    #db[new_key]["correct"] = db[new_key]["correct"]+db[key]["correct"]
    #db[key].update({"wrong":0})
    #db[key].pop("factor")
    #db[new_key]["score"] = db[new_key]["correct"] - db[new_key]["wrong"]
    #db[new_key]["count"] = update_count(db[new_key]["correct"])
    print(f"{key} - {db[key]}")
    #print(f"{new_key} = {db[new_key]}")
    #del db[key]
  return msg

def list():
  msg = ""
  for key in db.keys():
    print(f"{key} - {db[key]}")
    msg = f"{msg}\n{key} - {db[key]}" 
  return msg
    
def delete (key):
  del db[key]
