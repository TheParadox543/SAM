import discord
from discord.ext import commands, bridge


class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ol'])
    async def oglist(self, ctx):
        """Gives a list of users who want to receive saves for og counting"""
        saves_list = og_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':
                {
                    '_id':0,
                    'name':1,
                    'save_slot':{'$subtract':['$total_saves','$current_saves']}
                }
            },
            {
                '$sort':{'save_slot':-1}
            }
        ])
        msg = ""
        for counter in saves_list:
            if int(counter['save_slot']) > 0:
                msg += f"{counter['name']} - {counter['save_slot']}\n"
        title_msg = "Counters who could use a save in og-counting"
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)
    
    @commands.group(aliases=['ocounter','oc'],invoke_without_command=True)
    async def ogcounter(self, ctx):
        """
        Registers a counter as og-counters to receive saves from users who have extra saves
        """
        user = ctx.author
        user_post = og_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                msg = f"<@{user.id}> is an og-counter. "
                msg += "Your name will appear in `oglist`"
            elif user_post['counter'] == True:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                msg = f"<@{user.id}> is no longer an og-counter. "
                msg += "Your name will not appear in `oglist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @ogcounter.command(name="set")
    @admin_perms()
    async def og_set(self,ctx,user:discord.Member):
        """Used to set another counter as ogcounter by admin"""
        user_post = og_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                msg = f"<@{user.id}> is an og-counter. "
                msg += "Your name will appear in `oglist`"
            elif user_post['counter'] == True:
                og_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                msg = f"<@{user.id}> is no longer an og-counter. "
                msg += "Your name will not appear in `oglist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    # @commands.command()
    # async def alphacounter(self,ctx):
    #     """Registers a counter as abc counters who want gifts"""
    #     user = ctx.author
    #     alphacounter_role = ctx.guild.get_role(alphacounter_id)
    #     if abc_collection.find_one({"_id":user.id}):
    #         user_post = abc_collection.find_one({"_id":user.id}, {"counter":1})
    #         if 'counter' not in user_post or user_post['counter'] == False:
    #             abc_collection.update_one(
    #                 {
    #                     "_id":user.id
    #                 }, {
    #                     "$set":
    #                     {
    #                         "counter":True
    #                     }
    #                 }
    #             )
    #             await user.add_roles(alphacounter_role)
    #             msg = f"<@{user.id}> is an ABC counter. "
    #             msg += "Your name will appear in `alist`."
    #             await ctx.send(msg)
    #         elif user_post['counter'] == True:
    #             abc_collection.update_one(
    #                 {
    #                     "_id":user.id
    #                 }, {
    #                     "$set":
    #                     {
    #                         "counter":False
    #                     }
    #                 }
    #             )
    #             await user.remove_roles(alphacounter_role)
    #             msg = f"<@{user.id}> is no longer an ABC counter. "
    #             msg += "Your name will not appear in `alist`."
    #             await ctx.send(msg)
    #     else:
    #         abc_collection.insert_one(
    #             {
    #                 "_id":user.id,
    #                 "name":f"{user}",
    #                 "correct":0,
    #                 "wrong":0,
    #                 "current_saves":0,
    #                 "total_saves":5,
    #                 "streak":0,
    #                 "high":0,
    #                 "counter":True
    #             }
    #         )
    #         await user.add_roles(alphacounter_role)
    #         msg = f"<@{user.id}> is an ABC counter. "
    #         msg += "Your name will appear in `alist`."

    # @commands.command()
    # async def alist(self,ctx):
    #     """Gives the list of counters who can receive abc gifts"""
    #     saves_list = abc_collection.aggregate([
    #         {
    #             '$match':{'counter':True}
    #         },
    #         {
    #             '$project':
    #             {
    #                 '_id':0,
    #                 'name':1,
    #                 'save_slot':{'$subtract': ['$total_saves','$current_saves']}
    #             }
    #         },
    #         {
    #             '$sort': {'save_slot':-1}
    #         }
    #     ])
    #     msg = ""
    #     for counter in saves_list:
    #         if int(counter['save_slot']) > 0:
    #             msg += f"{counter['name']} - {counter['save_slot']}\n"
    #     title_msg = "ABC counters who could use a save"
    #     embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
    #     await ctx.send(embed=embedVar)

    @commands.command(aliases=['bl'])
    async def blist(self, ctx):
        """Gives the list of counters who can receive AlphaBeta gifts"""
        saves_list = beta_collection.aggregate([
            {
                '$match':{'counter':True}
            },
            {
                '$project':
                {
                    '_id':0,
                    'name':1,
                    'save_slot':{'$subtract': ['$total_saves','$current_saves']}
                }
            },
            {
                '$sort': {'save_slot':-1}
            }
        ])
        msg = ""
        for counter in saves_list:
            if int(counter['save_slot']) > 0:
                msg += f"{counter['name']} - {counter['save_slot']}\n"
        title_msg = "AlphaBeta counters who could use a save"
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)

    @commands.group(aliases=['bcounter','bc'],imvoke_without_command=True)
    async def betacounter(self, ctx):
        """Registers a counter as AlphaBeta counters"""
        user = ctx.author
        betacounter_role = ctx.guild.get_role(betacounter_id)
        user_post = beta_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                await user.add_roles(betacounter_role)
                msg = f"<@{user.id}> is an AlphaBeta counter. "
                msg += "Your name will appear in `blist`"
            elif user_post['counter'] == True:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                await user.remove_roles(betacounter_role)
                msg = f"<@{user.id}> is no longer an AlphaBeta counter. "
                msg += "Your name will not appear in `blist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @betacounter.command(name='set')
    @admin_perms()
    async def beta_set(self, ctx, user:discord.Member):
        """Used to set another counter as AlphaBeta counter by an admin"""
        betacounter_role = ctx.guild.get_role(betacounter_id)
        user_post = beta_collection.find_one({"_id":user.id}, {"counter":1})
        if user_post:
            if 'counter' not in user_post or user_post['counter'] == False:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":True
                        }
                    }
                )
                await user.add_roles(betacounter_role)
                msg = f"<@{user.id}> is an AlphaBeta counter. "
                msg += "Your name will appear in `blist`"
            elif user_post['counter'] == True:
                beta_collection.update_one(
                    {
                        "_id":user.id
                    }, {
                        "$set":
                        {
                            "counter":False
                        }
                    }
                )
                await user.remove_roles(betacounter_role)
                msg = f"<@{user.id}> is no longer an AlphaBeta counter. "
                msg += "Your name will not appear in `blist`"
        else:
            msg = "Run stat commands first"
        await ctx.send(msg)

    @commands.command()
    async def checklist(self,ctx,type_check:typing.Literal['og','b','vote']): #'a'
        """Displays the list of people registered to receive saves"""
        msg = ""
        if type_check == 'og':
            counter_list = og_collection.aggregate([
                {
                    '$match':{'counter':True}
                },
                {
                    '$project':{'name':1}
                }
            ])
            for counter in counter_list:
                msg += f"{counter['name']}\n"
            title_msg = "List of og counters registered by the bot"
        # elif type_check == "a":
        #     counter_list = abc_collection.aggregate([
        #         {
        #             '$match':{'counter':True}
        #         },
        #         {
        #             '$project':{'name':1}
        #         }
        #     ])
        #     for counter in counter_list:
        #         msg += f"{counter['name']}\n"
        #     title_msg = "List of ABC counters registered by the bot"
        elif type_check == "b":
            counter_list = beta_collection.aggregate([
                {
                    '$match':{'counter':True}
                },
                {
                    '$project':{'name':1}
                }
            ])
            for counter in counter_list:
                msg += f"{counter['name']}\n"
            title_msg = "List of AlphaBeta counters registered by the bot"
        elif type_check == "vote":
            counter_list = misc.find_one({"_id":"ogregister"},{"_id":0})
            for user_id in counter_list:
                if counter_list[f"{user_id}"] == True:
                    user = ctx.guild.get_member(int(user_id))
                    msg += f"{user}\n"
            title_msg = "Counters who opted in for vote reminders"
        else:
            return
        embedVar = Embed(title=title_msg,description=msg,color=color_lamuse)
        await ctx.send(embed=embedVar)
