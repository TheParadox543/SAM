import discord


def guide():
  embedVar = discord.Embed(title = "Guide for crazy counting channels", description = "Prefix: `>` \nThe crazy counting channels are still under development, so the bot may go offline frequently. If you notice any issues or have any doubts, please feel free to contact the developer.", color = 0x0a53c7)
  embedVar.add_field(name = "__General Rules (All channels)__", value = "1. No skipping numbers\n2. No going back in numbers.\n3. No counting more than your count limit (You start with 3 and get more as you count).\n4. You can count like other channels where you count one number at a time and alternately with another user", inline = True)
  embedVar.add_field(name = "__Commands__", value = "**user (<user>/<userID>)** - gives user stats with crazy counting\n**channel (<channel>/<channelID>)** - gives the channel stats for crazy counting channels\n**allchannels** - gives the stats of channels in a single message\n**lb** - gives the leaderboard of counters", inline = True)
  embedVar.add_field(name = "Backward Counting", value= "You have to count backwards from the given base and go to 0. On reaching 0 the base value is increased",inline=False)
  embedVar.add_field(name = "Maths Counting", value= "You have to count by evaluating the given expressions.\n `+` - evaluate for sum\n`-` - evaluate for difference\n`*` - evaluate for product\n`/` - evaluate for quotient\n`%` - evaluate the remainder on dividing by the divisor",inline=False)
  embedVar.add_field(name = "Ternary Channel", value = "There are 3 digits - 0, 1, 2. Order goes as :\n1, 2, 10, 11, 12, 20, 21, 22, 100,...\n..., 212, 220, 221, 222, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Quarternary Channel", value = "There are 4 digits - 0, 1, 2, 3. Order goes as :\n1, 2, 3, 10, 11, 12,...\n..., 30, 31, 32, 33, 100, 101,...\n..., 331, 332, 333, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Quinary Channel", value = "There are 5 digits - 0 to 4. Order goes as :\n1, 2, 3, 4, 10, 11, 12,...\n...40, 41, 42, 43, 44, 100, 101,...\n..., 442, 443, 444, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Senary Channel", value = "There are 6 digits - 0 to 5. Order goes as :\n1, 2, 3, 4, 5, 10, 11, 12,...\n..., 51, 52, 53, 54, 55, 100, 101,...\n...,553, 554, 555, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Septenary Channel", value = "There are 7 digits - 0 to 6. Order goes as :\n1, 2, 3, 4, 5, 6, 10, 11, 12,...\n..., 62, 63, 64, 65, 66, 100, 101,...\n...,664, 665, 666, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Octal Channel", value = "There are 8 digits - 0 to 7. Order goes as :\n1, 2, 3, 4, 5, 6, 7, 10, 11, 12,...\n..., 73, 74, 75, 76, 77, 100, 101,...\n...,775, 776, 777, 1000, 1001,...", inline = True)
  embedVar.add_field(name = "Nonary Channel", value = "There are 9 digits - 0 to 8. Order goes as :\n1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12,...\n..., 84, 85, 86, 87, 88, 100, 101,...\n...,886, 887, 888, 1000, 1001,...", inline = False)
  embedVar.add_field(name = "Hexatridecimal Channel", value = "Details available in `>guide hexatridecimal`")
  embedVar.add_field(name = "Quadrahexcimal Channel", value = "Details available in `>guide quadrahexdecimal`")
  embedVar.add_field(name = "Mayan Channel", value = "Details available in `>guide mayan`")
  embedVar.add_field(name = "__Count Limit__", value = "The current formula for count limit goes as such: \n__Correct Counts  - Limit__ \n0 to 249                -     3 \n250 to 499           -     4 \n500 to 999          -     5 \n1000 to 1499      -     6 \n1500 to 1999       -     7 \n2000 to 2999     -     8 \n3000 to 4999     -     9 \n5000 +                 -     10 \nThe formula is subject to change so do check it once in a while", inline = True)
  embedVar.add_field(name = "__Saves Formula__", value = "Every count has a 10% chance of giving you 0.05 saves", inline = True)
  return embedVar
  

def mayan():
  embedVar = discord.Embed(title = "Mayan Counting", description = "Mayan counting uses the symbols **. - ;**\n`.` is worth 1 unit and you can have a max of 4 per group. `-` is worth 5 and you can have a max of 3 per group. `;` is used to split the groups. You can then use a combination of -s and .s to count\n1 = .\n2 = ..\n3 = ...\n4 = ....\n5 = -\n6 = -.\n17 = ---..\n19 = ---....\n19 is the largest number we can make in one group. This means we have to go to the next group to the left using ;.\n\nEach ; after a group multiplies that group by 20.\n20 = .; (`.` * 20 = 20)\n21 = .;.\n24 = .;....\n25 = .;-\n40 = ..; (`..` * 20 = 40)\n100 = -;\n399 = ---....;---....\n399 = ---....;---....\n400 = .;; (`.` * 20 * 20 = 400)\n401 = .;;.", color = 0x0a53c7)
  return embedVar

def hexa():
  embedVar = discord.Embed(title = "Hexatridecimal Counting", description = "Hexatridecimal uses 0 - 9 and A - Z as 36 characters. Order goes as :\n1,2,3,4,5,6,7,8,9,A,B,C,....,X,Y,Z,10,11, and so on", color = 0x0a53c7)
  return embedVar

def quad():
  embedVar = discord.Embed(title = "Quadrahexdecimal Counting", description = "Quadrahexdecimal uses 0 - 9, a - z, A - Z, +, / as its 64 symbols. Order goes as :\n1,2,3,4,5,6,7,8,9,a,b,c,....,x,y,z,A,B,C,....X,Y,Z,+,/,10,11,12,....,18,19,1a,1b,1c,....,1x,1y,1z,1A,1B,1C,....,1X,1Y,1Z,1+,1/,20,21,22, and so on" , color = 0x0a53c7)
  return embedVar