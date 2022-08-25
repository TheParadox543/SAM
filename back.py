from replit import db
import codes

def start():
  db["back"] = {
    "curr": 11,
    "high": 11,
    "last": 935408554997874798,
    "count": 0,
    "base": 10
  }
  base = db["back"]["base"]
  return base

def move(num: int, auth_id: int):
  curr = db["back"]["curr"]
  if num == (db["back"]["curr"] - 1):
    if auth_id != db["back"]["last"]:
      db["back"]["last"] = auth_id
      db["back"]["count"] = 0
      msg = correct(auth_id, "n")
    else:
      c = db["back"]["count"]
      c = c + 1
      name = "user" + str(auth_id)
      uc = db[name]["count"]
      if c < uc:
        db["back"]["count"] = c
        if c == uc - 1:
          msg = correct(auth_id, "y")
        else:
          msg = correct(auth_id, "n")
      else:
        msg = wrong(auth_id, 3) + "w" + str(curr)
    if num == 0:
      base = db["back"]["base"]
      if str(base)[0] == "1":
        n_base = base * 5
      else:
        n_base = base * 2
      db["back"]["base"] = n_base
      db["back"]["curr"] = n_base + 1
      db["back"]["high"] = n_base + 1
      msg = "n" + str(n_base) + "n" + str(base)
  elif num == (db["back"]["curr"]):
    msg = wrong(auth_id, 4) + "w" + str(curr)
  elif num > (db["back"]["curr"]):
    msg = wrong(auth_id, 2) + "w" + str(curr)
  else:
    msg = wrong(auth_id, 1) + "w" + str(curr)
  return msg

def correct(auth_id, flag):
  codes.user_correct(auth_id)
  current = db["back"]["curr"]
  current = current - 1
  db["back"]["curr"] = current
  if current < db["back"]["high"]:
    db["back"]["high"] = current
    if flag == "y":
      return "s"
    return "h"
  else:
    if flag == "y":
      return "s"
    return "c"

def wrong(auth_id, reason):
  signal = codes.user_wrong(auth_id)
  if signal.startswith("w") :
    return signal
  else:
    db["back"]["curr"] = db["back"]["base"] + 1
    db["back"]["last"] = 935408554997874798
    db["back"]["count"] = 0
    msg = f"{reason}w<@{auth_id}>w{db['back']['base']}"
    return msg

def details():
  return db["back"]["base"], db["back"]["curr"], db["back"]["high"], db["back"]["last"], db["back"]["count"]