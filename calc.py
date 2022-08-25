from replit import db
import codes
import random

symbol_list = ["+","-","*","/","%"]

def start():
  db["math"] = {
    "curr":0,
    "high":0,
    "next": random.randint(1,9),
    "expression": "",
    "count": 0,
    "last":935408554997874798
  }
  db["weight"] = [ 5 , 0 , 0 , 0 , 0 ]
  return db["math"]["next"]


def move(num, auth_id: int):
  name = "user"+str(auth_id)
  if num == db["math"]["next"]:
    if auth_id != db["math"]["last"]:
      db["math"]["last"] = auth_id
      db["math"]["count"] = 0
      msg = correct(auth_id, "n")
    else:
      c = db["math"]["count"]
      c = c + 1
      uc = db[name]["count"]
      if c < uc:
        db["math"]["count"] = c
        if c == uc-1:
          msg = correct(auth_id,"y")
        else:
          msg = correct(auth_id,"n")
      else:
        msg = wrong(auth_id, 2)+f"w{db['math']['next']}"
  else:
    msg = wrong(auth_id, 1)+f"w{db['math']['next']}"
  return msg


def correct(auth_id,flag):
  codes.user_correct(auth_id)
  next_number()
  current = db["math"]["curr"]
  current = current + 1 
  db["math"]["curr"] = current
  if current > db["math"]["high"]:
    db["math"]["high"] = current
  if flag == "y":
    return f"s{db['math']['expression']}"
  return f"c{db['math']['expression']}"


def wrong(auth_id,reason):
  signal = codes.user_wrong(auth_id)
  if signal.startswith("w") :
    msg = f"{signal}w{db['math']['expression']}"
    return msg
  else:
    score = db["math"]["curr"]
    db["math"]["curr"] = 0
    db["math"]["last"] = 935408554997874798
    db["math"]["count"] = 0
    curr = db["math"]["next"]
    db["math"]["next"] = random.randint(1,9)
    db["math"]["expression"] = ""
    msg = f"{reason}w<@{auth_id}>w{curr}w{score}"
    return msg 

def next_number():
  curr = db["math"]["next"]
  factor = factors(curr)
  if len(factor)<3:
    db["weight"][3] = 0
  if curr < 10:
    db["weight"][1] = 0
  if curr < 15:
    db["weight"][3] = 0
  if curr > 2000:
    db["weight"][0] = 1
    db["weight"][2] = 0
    db["weight"][4] = 4
  
  symbol = random.choices(symbol_list, weights = db["weight"],k = 1)[0]
  if symbol == "+":
    operand = random.randint(1,10)
    db["math"]["next"] = int(curr + operand)
    db["weight"] = [2,4,4,4,1]
  elif symbol == "-":
    operand = random.randint(1,10)
    db["math"]["next"] = int(curr - operand)
    db["weight"] = [4,2,4,4,1]
  elif symbol == "*":
    operand = random.randint(2,9)
    db["math"]["next"] = int(curr * operand)
    db["weight"] = [4,4,2,4,1]
  elif symbol == "/":
    operands = factors(curr)
    operand = random.choice(operands)
    db["math"]["next"] = int(curr / operand)
    db["weight"] = [4,4,4,2,1]
  elif symbol == "%":
    operands = factors(curr)
    while True:
      operand = random.randint(2,9)
      if operand not in operands:
        break
    db["math"]["next"] = int(curr % operand)
    db["weight"] = [4,4,4,4,0]
  db["math"]["expression"] = f"{curr} {symbol} {operand}"
    
def factors(num):
  factor = []
  for i in range(2,11):
    if num %i==0:
      factor.append(i)
  return factor
  
def details():
  return db["math"]["curr"],db["math"]["high"],db["math"]["last"], db["math"]["count"], db["math"]["expression"]
