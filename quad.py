from replit import db
import codes

def start(chnl):
  channel = "chnl" + str(chnl)
  db[channel] = {
    "factor": 64,
    "curr": 0,
    "high": 0,
    "count":0,
    "last":935408554997874798
  }
  return db[channel]["curr"] + 1

def move(number, auth_id: int, channel):
  curr = convert(db[channel]["curr"])
  num = convert(db[channel]["curr"]+1 ) 
  if number == num:
    if auth_id != db[channel]["last"]:
      db[channel]["last"] = auth_id
      db[channel]["count"] = 0
      msg = correct(auth_id, channel,"n")
    else:
      c = db[channel]["count"]
      c = c + 1
      name = "user"+str(auth_id)
      uc = db[name]["count"]
      if c < uc:
        db[channel]["count"] = c
        if c == uc-1:
          msg = correct(auth_id,channel,"y")
        else:
          msg = correct(auth_id, channel,"n")
      else:
        msg = wrong(auth_id, channel, 3)+"w"+str(curr)
  else:
    msg = wrong(auth_id,channel,1)+"w"+str(curr)
  return msg


def correct(auth_id:int, channel, flag):
  codes.user_correct(auth_id)
  current = db[channel]["curr"]
  current = current + 1 
  db[channel]["curr"] = current
  if current > db[channel]["high"]:
    db[channel]["high"] = current
  if flag == "y":
    return "s"
  if db[channel]["high"]==current:
    return "h"
  else:
    return "c"


def wrong(auth_id,channel,reason):
  signal = codes.user_wrong(auth_id)
  if signal.startswith("w"):
    return signal
  else:
    db[channel]["curr"] = 0
    db[channel]["last"] = 935408554997874798
    db[channel]["count"] = 0
    msg = f"{reason}w<@{auth_id}>"
    return msg 

def details(channel):
  curr = db[channel]["curr"]
  high = db[channel]["high"]
  temp1 = convert(curr)
  temp2 = convert(high)
  return db[channel]["curr"], temp1, db[channel]["high"], temp2, db[channel]["last"], db[channel]["count"]

def convert(number):
  temp = ""
  if number == 0:
    temp = "0"
  while number >0:
    rem = number % 64
    if rem >= 0 and rem <= 9:
      temp = str(rem) + temp
    elif rem >= 10 and rem <= 35:
      temp = chr(rem+87) + temp
    elif rem >= 36 and rem <= 61:
      temp = chr(rem+29) + temp
    elif rem == 62:
	    temp = "+" + temp
    elif rem == 63:
      temp = "/" + temp
    number = int(number / 64)
  return temp