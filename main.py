import discord
import os
#import time
import re
import multi
import hexa
import quad
import mayan_calc
import back
import calc
import codes
import guide_file
import discord.ext
import requests
import sys
from keep_alive import keep_alive
from discord.ext import commands
from replit import db
#from discord.ext.commands import has_permissions
#^ basic imports for other features of discord.py and python ^


intents = discord.Intents.none()
intents.guild_messages = True
intents.guilds = True


class CustomHelpCommand(commands.HelpCommand):
  
  def __init__(self):
    super().__init__

  async def send_bot_help(self, mapping):
    return await super().send_bot_help(mapping)


bot = commands.Bot(command_prefix = ">", intents = intents, owner_id = 717240803789111345)

channel_list = {
  "937575518616829962": [3,"Ternary"],
  "937575590175838259": [4,"Quaternary"],
  "937575695993946162": [5,"Quinary"],
  "937575754546446366": [6,"Senary"],
  "937575791733125120": [7,"Septenary"],
  "937575817591009290": [8,"Octal"],
  "937575838306693140": [9,"Nonary"]
}
chnl_back = 937386296765202453
reason = ["You can't skip numbers.", "You can't go back in numbers.", "You can't count more than your count limit.", "You have to count count backwards, not forwards.", "You can't count the same number twice.","That's not a valid number in this channel"]
chnl_math = 938855717044097146
chnl_hexatridecimal = 939844401851695104
chnl_quadrahexdecimal = 939844467580612609
chnl_mayan = 939844515852865539


#this code is to send channel stats to all channels when the bot is rebooted  
def ready_bot():
  chnl_send = bot.get_channel(937577453075976262) #crazybot commands channel
  embedVar = discord.Embed(description = "Bot has restarted.", color = 0x2ecc71) # Reactions have been disabled")
  return chnl_send, embedVar
def ready_multi(channel):
  chnl = int(channel)
  chnl_send = bot.get_channel(chnl)
  curr_chnl = "chnl"+channel
  factor = channel_list[str(channel)][0]
  curr, cur, high, hig, last, c = multi.details(curr_chnl, factor)
  embedVar=discord.Embed(title = f"Stats for {channel_list[channel][1]}", description = f"Current Number: **{cur}** ({curr})\nLast Counter: <@{last}> (counted {c+1} times)", color = 0x2ecc71)
  return chnl_send, embedVar
def ready_back():
  chnl_send = bot.get_channel(chnl_back)
  base, curr, high, last, c = back.details()
  embedVar = discord.Embed(title = f"Stats for Backwards", description = f"Current Base: {base}\nCurrent Number: {curr}\nLast Counter: <@{last}> (counted {c+1} times)",color = 0x2ecc71)
  return chnl_send, embedVar
def ready_math():
  chnl_send = bot.get_channel(chnl_math)
  curr, high, last, c, expression = calc.details()
  embedVar = discord.Embed(title = f"Stats for Math", description = f"Next number: {expression}\nLast Counter: <@{last}> (counted {c+1} times)",color = 0x2ecc71)
  return chnl_send, embedVar
def ready_hexa():
  chnl_send = bot.get_channel(chnl_hexatridecimal)
  channel = "chnl" + str(chnl_hexatridecimal)
  curr, cur, high, hig, last, c = hexa.details(channel)
  embedVar=discord.Embed(title = f"Stats for Hexatridecimal", description = f"Current Number: **{cur}** ({curr})\nLast Counter: <@{last}> (counted {c+1} times)", color = 0x2ecc71)
  return chnl_send, embedVar
def ready_quad():
  chnl_send = bot.get_channel(chnl_quadrahexdecimal)
  channel = "chnl" + str(chnl_quadrahexdecimal)
  curr, cur, high, hig, last, c = quad.details(channel)
  embedVar=discord.Embed(title = f"Stats for Quadrahexdecimal", description = f"Current Number: **{cur}** ({curr})\nLast Counter: <@{last}> (counted {c+1} times)", color = 0x2ecc71)
  return chnl_send, embedVar
def ready_mayan():
  chnl_send = bot.get_channel(chnl_mayan)
  channel = "chnl" + str(chnl_mayan)
  curr, cur, high, hig, last, c = mayan_calc.details(channel)
  embedVar=discord.Embed(title = f"Stats for Mayan", description = f"Current Number: **{cur}** ({curr})\nLast Counter: <@{last}> (counted {c+1} times)", color = 0x2ecc71)
  return chnl_send, embedVar
    

@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(">guide"))
  print('We have logged in as {0.user}'.format(bot))
  """chnl_send, embed = ready_bot()
  await chnl_send.send(embed=embed)
  chnl_send, embed = ready_back()
  await chnl_send.send(embed = embed)
  for channel in channel_list:
    chnl_send, embed = ready_multi(channel)
    await chnl_send.send(embed = embed)
  chnl_send, embed = ready_math()
  await chnl_send.send(embed = embed)
  chnl_send, embed = ready_hexa()
  await chnl_send.send(embed = embed)
  chnl_send, embed = ready_quad()
  await chnl_send.send(embed = embed)
  chnl_send, embed = ready_mayan()
  await chnl_send.send(embed = embed)
  """

@bot.group(invoke_without_command = True)
async def guide(ctx):
  embedVar = guide_file.guide()
  await ctx.send(embed = embedVar)


@guide.command()
async def mayan(ctx):
  embedVar = guide_file.mayan()
  await ctx.send(embed = embedVar)

@guide.command()
async def hexatridecimal(ctx):
  embedVar = guide_file.hexa()
  await ctx.send(embed = embedVar)

@guide.command()
async def quadrahexdecimal(ctx):
  embedVar = guide_file.quad()
  await ctx.send(embed = embedVar)


@bot.command(aliases = ["c","chnl"])
async def channel(ctx, chnl:discord.TextChannel = ""):
  if chnl == "":
    chnl =  ctx.channel
  if chnl.id ==  chnl_back:
    base, curr, high, last, c = back.details()
    embedVar = discord.Embed(title = f"Stats for {chnl.name}", description = f"Current Base: {base}\nCurrent Number: {curr}\nHigh score: {high}\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  elif str(chnl.id) in channel_list.keys():
    num = channel_list[str(chnl.id)][0]
    curr_chnl = "chnl" + str(chnl.id)
    curr, cur, high, hig, last, c = multi.details(curr_chnl, num)
    embedVar = discord.Embed(title = f"Stats for {chnl.name}", description = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  elif chnl.id == chnl_math:
    curr, high, last, c, expression = calc.details()
    embedVar = discord.Embed(title = f"Stats for {chnl.name}", description = f"Current Calc: {curr}\nHighest Calc: {high}\nNext number: {expression}\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  elif chnl.id == chnl_hexatridecimal:
    chnl = "chnl" + str(chnl.id)
    curr, cur, high, hig, last, c = hexa.details(chnl)
    embedVar = discord.Embed(title = f"Stats for hexatridecimal", description = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  elif chnl.id == chnl_quadrahexdecimal:
    chnl = "chnl" + str(chnl.id)
    curr, cur, high, hig, last, c = quad.details(chnl)
    embedVar = discord.Embed(title = f"Stats for quadrahexadecimal", description = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  elif chnl.id == chnl_mayan:
    chnl = "chnl" + str(chnl.id)
    curr, cur, high, hig, last, c = mayan_calc.details(chnl)
    embedVar = discord.Embed(title = f"Stats for mayan", description = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)",color=0x0a53c7)
  else:
    embedVar = discord.Embed(description = "INVALID CHANNEL")
  try:
    await ctx.send(embed=embedVar)
  except:
    os.system("kill 1")
    bot.run(os.getenv("TOKEN"))


@bot.command(aliases = ["ac","allchannels","channels"])
async def allchannel(ctx):
  #channel = bot.get_channel(937577453075976262)
  embedVar = discord.Embed(title = f"Stats for {ctx.guild.name}",color=0x0a53c7)
  base, curr, high, last, c = back.details()
  embedVar.add_field(name = "Stats for Backwards", value = f"Current Base: {base}\nCurrent Number: **{curr}**\nHigh score: {high}\nLast Counter: <@{last}> (counted {c+1} times)")
  for channel in channel_list.keys():
    num = channel_list[str(channel)][0]
    curr_chnl = "chnl" + str(channel)
    curr, cur, high, hig, last, c = multi.details(curr_chnl, num)
    embedVar.add_field(name = f"Stats for {channel_list[channel][1]}", value = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)")
  curr, high, last, c, expression = calc.details()
  embedVar.add_field(name = f"Stats for Math", value = f"Current Calc: {curr}\nHighest Calc: {high}\nNext number: **{expression}**\nLast Counter: <@{last}> (counted {c+1} times)")
  curr, cur, high, hig, last, c = hexa.details("chnl"+str(chnl_hexatridecimal))
  embedVar.add_field(name = f"Stats for Hexatridecimal", value = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)")
  curr, cur, high, hig, last, c = quad.details("chnl"+str(chnl_quadrahexdecimal))
  embedVar.add_field(name = f"Stats forQuadraHexdecimal", value = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)")
  curr, cur, high, hig, last, c = mayan_calc.details("chnl"+str(chnl_mayan))
  embedVar.add_field(name = f"Stats for Mayan", value = f"Current Number: **{cur}** ({curr})\nHigh score: **{hig}** ({high})\nLast Counter: <@{last}> (counted {c+1} times)")
  
  try:
    await ctx.send(embed=embedVar)
  except:
    os.system("kill 1")
    bot.run(os.getenv("TOKEN"))


@bot.command(aliases = ["u"])
async def user(ctx, member: discord.Member = ""):
  if member == "":
    user = ctx.author.id
    name = ctx.author.display_name
    link = ctx.author.avatar_url
  else:
    user = member.id
    name = member.display_name
    link = member.avatar_url
  codes.user(name, user)
  corr, wrong, score, save, used, count = codes.stats(user)
  tot = corr + wrong
  if tot != 0:
    rate = round((corr / tot)*100, 2)
  else:
    rate = 0
  if save > 0:
    save = round(save,2)
  embedVar = discord.Embed(title = f"Stats for {name}", description = f"Rate: **{rate}%**\nCorrect: **{corr}**\nWrong: **{wrong}**\nScore: **{score}** \nSaves: **{save}**\nSaves used: **{used}** \nCount Limit: **{count}**",color=0x0a53c7)
  embedVar.set_thumbnail(url = link)
  try:
    await ctx.send(embed=embedVar)
  except:
    os.system("kill 1")
    bot.run(os.getenv("TOKEN"))


@bot.command()
async def lb(ctx):
  msg = codes.rank()
  embedVar = discord.Embed(title = f"Scores of {ctx.guild.name}", description = msg, color = 0x0a53c7)
  try:
    await ctx.send(embed=embedVar)
  except:
    os.system("kill 1")
    bot.run(os.getenv("TOKEN"))


@bot.event
async def on_message(message):
  
  cont = message.content
  auth = message.author
  chnl = message.channel.id
  str_chnl = str(chnl)

  if message.author == bot.user:
    return
  
  if chnl == 937386296765202453:#backward channel
    if re.match("\d", cont):
      num = int(cont.split()[0])
      msg = back.move(num, auth.id)
      try:
        if re.match("s",msg):
          await message.add_reaction("🛑")
        elif re.match("h", msg):
          await message.add_reaction("🏆")
        elif re.match("c", msg):
          await message.add_reaction("✅")
        if re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Last number was **{curr}**.")
        elif re.match("[1234]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          base = msg.split("w")[2]
          curr = msg.split("w")[3]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[0]} Start from **{base}**")
          elif re.match("2", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[3]} Start from **{base}**")
          elif re.match("3", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[2]} Start from **{base}**")
          elif re.match("4", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[4]} Start from **{base}**")
        elif re.match("n", msg):
          #await message.add_reaction("🏆")
          n_base = msg.split("n")[1]
          base = msg.split("n")[2]
          await message.channel.send("<a:rainbowglowstickvibeslow:915069470198865961>")
          await message.channel.send(f"You have counted from **{base}** to 0. Time to start from **{n_base}**")
      except:
        os.system("kill 1")
        print("Error during back")
        bot.run(os.getenv("TOKEN"))


  elif str_chnl in channel_list.keys() :
    if re.match("\d", cont):
      number = cont.split()[0]
      channel = "chnl"+str_chnl
      msg = multi.move(number, auth.id,channel,channel_list[str_chnl][0])
      try:
        if re.match("s",msg):
          await message.add_reaction("🛑")
        elif re.match("h", msg):
          await message.add_reaction("🏆")
        elif re.match("c", msg):
          await message.add_reaction("✅")
        elif re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Last number was **{curr}**.")
        elif re.match("[12345]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          curr = msg.split("w")[2]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[0]} Start from 1")
          elif re.match("2", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[1]} Start from 1")
          elif re.match("3", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[2]} Start from 1")
          elif re.match("4", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[4]} Start from **{base}**")
          elif re.match("5", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[5]} Start from **{base}**")
      except:
        os.system("kill 1")
        print("Error during multi")
        bot.run(os.getenv("TOKEN"))


  elif chnl == chnl_hexatridecimal :# insert hexatridecimal channel id
    if re.match("\w", cont):
      number = cont.split()[0]
      channel = "chnl"+str_chnl
      msg = hexa.move(number, auth.id,channel)
      try:
        if re.match("s",msg):
          await message.add_reaction("🛑")
        elif re.match("h", msg):
          await message.add_reaction("🏆")
        elif re.match("c", msg):
          await message.add_reaction("✅")
        elif re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Last number was **{curr}**.")
        elif re.match("[12345]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          curr = msg.split("w")[2]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. That's not the next number. Start from 1")
          elif re.match("3", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[2]} Start from 1")
      except:
        os.system("kill 1")
        print("Error during multi")
        bot.run(os.getenv("TOKEN"))


  elif chnl == chnl_quadrahexdecimal :# insert quadrahexdecimal channel id
    if re.match("[\w+/]", cont):
      number = cont.split()[0]
      channel = "chnl"+str_chnl
      msg = quad.move(number, auth.id,channel)
      try:
        if re.match("s",msg):
          await message.add_reaction("🛑")
        elif re.match("h", msg):
          await message.add_reaction("🏆")
        elif re.match("c", msg):
          await message.add_reaction("✅")
        elif re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Last number was **{curr}**.")
        elif re.match("[12345]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          curr = msg.split("w")[2]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. That's not the next number. Start from 1")
          elif re.match("3", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[2]} Start from 1")
      except:
        os.system("kill 1")
        print("Error during multi")
        bot.run(os.getenv("TOKEN"))
  

  elif chnl == 939844515852865539 :# insert mayan channel id
    if re.match("[.\-;]", cont):
      number = cont.split()[0]
      channel = "chnl"+str_chnl
      msg = mayan_calc.move(number, auth.id,channel)
      try:
        if re.match("s",msg):
          await message.add_reaction("🛑")
        elif re.match("h", msg):
          await message.add_reaction("🏆")
        elif re.match("c", msg):
          await message.add_reaction("✅")
        elif re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Last number was **{curr}**")
        elif re.match("[12345]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          curr = msg.split("w")[2]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. That's not the next number. Start from 1")
          elif re.match("3", msg):
            await message.channel.send(f"{name} ruined the count at {curr}. {reason[2]} Start from 1")
      except:
        os.system("kill 1")
        print("Error during multi")
        bot.run(os.getenv("TOKEN"))
  

  elif chnl == chnl_math:
    if re.match("\d", cont):
      num = int(cont.split()[0])
      msg = calc.move(num, auth.id)
      try:
        #if re.match("h", msg):
          #await message.add_reaction("🏆")
        if re.match("s",msg):
          await message.add_reaction("🛑")
          expression = msg.split("s")[1]
          await message.channel.send(f"The next number is {expression}")
        elif re.match("c", msg):
          #await message.add_reaction("✅")
          expression = msg.split("c")[1]
          await message.channel.send(f"The next number is {expression}")
        elif re.match("w", msg):
          #await message.add_reaction("⚠")
          name = msg.split("w")[1]
          save = msg.split("w")[2]
          curr = msg.split("w")[3]
          await message.channel.send(f"{name} has used 1 save. {save} saves left. Next number is **{curr}**.")
        elif re.match("[12]", msg):
          #await message.add_reaction("❌")
          name = msg.split("w")[1]
          curr = msg.split("w")[2]
          next_number = msg.split("w")[4]
          score = msg.split("w")[3]
          if re.match("1", msg):
            await message.channel.send(f"{name} ruined the count at {score} calculations. The correct number was {curr}. Start from **{next_number}**")
          elif re.match("2", msg):
            await message.channel.send(f"{name} ruined the count at {score} calculation. {reason[2]} Start from **{next_number}**")
        
      except:
        os.system("kill 1")
        print("Error during calc")
        bot.run(os.getenv("TOKEN"))


  codes.user(auth.display_name,auth.id)


  if auth.id == 717240803789111345:
    
    if cont.startswith("#startmulti"):
      multi.start(str_chnl, int(cont.split()[1]))
      await message.channel.send(f"Start counting from **1**")

    if cont.startswith("#startback"):
      base= back.start()
      await message.channel.send(f"Start counting from **{base}**")

    if cont.startswith("#startmath"):
      start = calc.start()
      await message.channel.send(f"Start counting from **{start}**")
    
    if cont.startswith("#starthexatridecimal"):
      start = hexa.start(str_chnl)
      await message.channel.send(f"Start counting from **{start}**")

    if cont.startswith("#startquadrahexdecimal"):
      start = quad.start(str_chnl)
      await message.channel.send(f"Start counting from **{start}**")
    
    if cont.startswith("#startmayan"):
      start = mayan_calc.start(str_chnl)
      await message.channel.send(f"Start counting from **{start}**")

    if cont.startswith("#prelist"):
      #try:
      pre = cont.split()[1]
      msg = codes.prelist(pre)
      #except:
        #await message.channel.send("Invalid command")
      await message.channel.send(msg)

    if cont.startswith("#keys"):
      msg = ""
      for key in db:
        msg+=f"{key}\n"
      print(msg)
    
    if cont.startswith("#list"):
      msg = codes.list()
      await message.channel.send(msg)

    if cont.startswith("#delete"):
      key = cont.split()[1]
      codes.delete(key)
    
    if cont.startswith("#update"):
      name = cont.split()[1]
      if name in db:
        del db[name]
      db[name] = {
        "correct": int(cont.split()[2]),
        "wrong": int(cont.split()[3]),
        "score": int(cont.split()[4]),
        "save": float(cont.split()[5]),
        "used": int(cont.split()[6]),
        "count": int(cont.split()[7]),
        "name": cont.split()[8]
      }
    
    if cont.startswith("#restart"):
      sys.exit(1)
  
  await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.reply("Not a valid command")
  elif isinstance(error, commands.MemberNotFound): #if invalid data given
    await ctx.send("User not found")
  #elif isinstance(error, commands.CommandInvokeError): #if user has not counted before
    #await ctx.reply("User data not available")
  elif isinstance(error, discord.errors.HTTPException):
    os.system("kill 1")
    bot.run(os.getenv("TOKEN"))
  else:
    raise error


@bot.command
@commands.has_permissions(administrator = True)
async def restart():
  sys.exit(1)

r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")


keep_alive()
try:
  bot.run(os.getenv("TOKEN")) 
except:
  os.system("kill 1")
  bot.run(os.getenv("TOKEN"))
