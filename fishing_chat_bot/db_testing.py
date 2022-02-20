#from _typeshed import Self
from discord.ext import commands
from discord.ext.commands import context
from discord.ext.commands.bot import Bot
from discord.ext.commands import context
from pprint import pprint
import pymongo
import time
import random
import asyncio


class dbTesting(commands.Cog):
    def __init__(self, bot: Bot, client: pymongo.MongoClient):
        self.bot = bot
        self.db = client
        self.cnfFish = ["Trout","Catfish","Carp","Bass","Perch",
                        "Shad","Bluegill","Salmon","Pumpkinseed Sunfish","Brassy Minnow",  
                        "Goldfish","Koi","Pike","Jewel Cichlid", 
                        "Glassfish","Muskellunge","Rainbow Tetra"]

        self.cnfFish2 = ["Oscar","Clownfish","Swordfish","Grouper","Pufferfish",
                        "Flying Fish","Damselfish","Tuna","Jawfish","Dottyback",
                        "Snowflake Eel","Mahi-mahi","Boxfish","Lionfish",
                        "Frogfish","Oarfish","Bony-eared Assfish"]

        self.pools = ["fresh","salt"]

        self.cnfRarityWeight = [95,95,95,95,95, 20,20,20,20,20, 10,10,10,10, 5,5,5]

        self.fishprices1 = dict([('Trout', 1),('Catfish', 1),('Carp', 1),('Bass', 1),('Perch', 1),
                                ('Shad', 6),('Bluegill', 6),('Salmon', 6),('Pumpkinseed Sunfish', 6),('Brassy Minnow', 6),
                                ('Goldfish', 14),('Koi', 14),('Pike', 14),('Jewel Cichlid', 14),
                                ('Glassfish', 40),('Muskellunge', 45),('Rainbow Tetra', 45)])
                                
        self.fishprices2 = dict([('Oscar', 1),('Clownfish', 1),('Swordfish', 1),('Grouper', 1),('Pufferfish', 1),
                                ('Flying Fish', 6),('Damselfish', 6),('Tuna', 6),('Jawfish', 6),('Dottyback', 6),
                                ('Snowflake Eel', 14),('Mahi-mahi', 14),('Boxfish', 14),('Lionfish', 14),
                                ('Frogfish', 40),('Oarfish', 40),('Bony-eared Assfish', 50)])
                  
        self.price_dicts = [self.fishprices1, self.fishprices2]

        self.rods = ["Twig with String","Flimsy Rod","Ash Rod","Treated Ash Rod","Bamboo Rod",
                    "Treated Bamboo Rod","Fiberglass Rod","Dwarven Novice Rod","Dwarven Mastercraft Rod"]

        self.rodprices = dict([("Twig with String", 0),("Flimsy Rod", 1000),("Ash Rod", 1500),("Treated Ash Rod", 2250),
                                ("Bamboo Rod", 3375),("Treated Bamboo Rod", 5060),("Fiberglass Rod", 7590),("Dwarven Novice Rod", 11390),("Dwarven Mastercraft Rod", 17085)])

        self.rodtimes = dict([("Twig with String", 0),("Flimsy Rod", 30),("Ash Rod", 60),("Treated Ash Rod", 90),
                                ("Bamboo Rod", 120),("Treated Bamboo Rod", 150),("Fiberglass Rod", 180),("Dwarven Novice Rod", 210),("Dwarven Mastercraft Rod", 240)])

        self.boxes = ["Empty Spaghettio Can","Spare Boot","Small Froggy Bucket","Big Froggy Bucket","Boomer Beer Cooler","Bang's Rootbeer Cooler","Giant Fisher Barrel"]

        self.boxsizes = dict([("Empty Spaghettio Can", 16),("Spare Boot", 20),("Small Froggy Bucket", 24),("Big Froggy Bucket", 28),
                            ("Boomer Beer Cooler", 32),("Bang's Rootbeer Cooler", 36),("Giant Fisher Barrel", 40)])

        self.boxprices = dict([("Empty Spaghettio Can", 0),("Spare Boot", 800),("Small Froggy Bucket", 1360),("Big Froggy Bucket", 2310),
                            ("Boomer Beer Cooler", 3930),("Bang's Rootbeer Cooler", 6680),("Giant Fisher Barrel", 11360)])

        self.catch_time_min = 300
        self.catch_time_plus = 300

    def generateFish(self,pool_id):
            if pool_id == 0:
                fish_spawn = random.choices(self.cnfFish, weights=self.cnfRarityWeight, k=1)
                return fish_spawn[0]
            elif pool_id == 1:
                fish_spawn = random.choices(self.cnfFish2, weights=self.cnfRarityWeight, k=1)
                return fish_spawn[0]
    
    def generateRod(self,num):
            rod_spawn = self.rods[num]
            return rod_spawn

    def generateBox(self,num):
            box_spawn = self.boxes[num]
            return box_spawn

#DOCUMENT FOR NEW MONGERS
    async def initUserDocument(self, ctx: context):
        """
        Helper function that can be called whenever we check to see if user has document.
        If user doesn't have a document, generate one for them.
        """
        print("Generate new user document")
        #Create new user document
        user_info = {
            'user_id' : ctx.author.id,
            'fish' : 0,
            'gold' : 0,
            'current_box' : self.generateBox(0),
            'current_rod' : self.generateRod(0),
            'pool' : self.pools[0]
        }
        self.db.users.insert_one(user_info)
        updated = self.db.users.find_one({'user_id' : ctx.author.id})
        await ctx.reply("A new fishmonger! You may now start using commands.")

    #INVENTORY
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def inv(self, ctx: context):
        #Find user document
        print(type(self.db.users))
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document found
        if user_info is not None:
            print("Update user document")
            pprint(user_info)
            updated = self.db.users.find_one({'_id': user_info.get('_id')})

            #Respond with updated gold and fish(?) val
            await ctx.reply("```\nGold: {0}\nBox: {1} ({2})\nRod: {3} ({4} sec)```".format(updated.get('gold'),updated.get('current_box'),self.boxsizes[user_info.get('current_box')],updated.get('current_rod'),self.rodtimes[user_info.get('current_rod')]))
        else:
            await self.initUserDocument(ctx)

    def generateFishWaitTime(self):
        """
        Returns a wait time from catch_time_min + (0 - 10) seconds
        """
        ran_num = random.random()
        wait_time = self.catch_time_min + self.catch_time_plus*ran_num
        return wait_time

    def updateOneValue(self, user_info, operation: str, attribute: str, value):
        """
        Set One Value in Database
        """
        self.db.users.update_one({'_id' : user_info.get('_id')}, {operation: {attribute: value}})

    #CAST
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cast(self, ctx: context):
        #Find user document
        print(type(self.db.users))
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document found
        if user_info is not None:
            #Check if user document found
            if "box" in user_info:
                if user_info.get('rodcast') == 1:
                    await ctx.reply("```\nYou are already fishing. Calm down.\n```")
                if (len(user_info.get('box')) < self.boxsizes[user_info.get('current_box')]) and user_info.get('rodcast') == 0:
                    #Prepare timestamp and cast state
                    self.updateOneValue(user_info, '$set', 'cancel', 0)
                    self.updateOneValue(user_info, '$set', 'timestamp', time.time())
                    await ctx.reply("```\nRod cast!\n```")

                    while self.boxsizes[user_info.get('current_box')] > len(user_info.get('box')) + 1:
                        #Get current document state
                        user_info = self.db.users.find_one({'user_id': ctx.author.id})

                        #Check if cancel
                        if user_info.get('cancel') == 1:
                            break

                        #Cast rod
                        self.updateOneValue(user_info, '$set', 'rodcast', 1)
                        await ctx.send('{0} cast their rod.'.format(ctx.message.author))

                        #Wait for da fish
                        wait_time = self.generateFishWaitTime()

                        rod = user_info.get('current_rod')
                        if rod is not None:
                            cast_reduction = self.rodtimes[rod]
                        else:
                            cast_reduction = 0

                        total_wait = wait_time-cast_reduction
                        await asyncio.sleep(total_wait)

                        #Generate da fish
                        pool = user_info.get('pool')
                        pool_index = self.pools.index(pool)
                        fish = self.generateFish(pool_index)
                        #self.updateOneValue(self, user_info, '$push', 'box', fish) brokey atm!!!
                        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$push' : {'box': fish}})
                        await ctx.send('{0} caught: {1}! Added to box. Took {2} seconds.'.format(ctx.message.author,fish,round(total_wait, 1)))
                    
                    #Finish da fish
                    self.updateOneValue(user_info, '$set', 'rodcast', 0)
                    self.updateOneValue(user_info, '$set', 'cancel', 0)
                    await ctx.reply("```\nYou finished fishing.\n```")
                    
                if len(user_info.get('box')) >= self.boxsizes[user_info.get('current_box')]:
                    await ctx.reply("```\nNo space in box..\n```")
            else:
                self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'box' : []}})
        else:
            await self.initUserDocument(ctx)

    #LINE --- change to show elapsed time and size of box array
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def line(self, ctx: context):
        #Find user document
        print(type(self.db.users))
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document found
        if user_info is not None:
            print("Update user document")
            pprint(user_info)
            if user_info.get('rodcast') == 1:
                
                #paste cast time and fish on line
                timestamp = time.time()
                line_time = timestamp - user_info.get('timestamp')
                line_fish = len(user_info.get('box'))
                line_time = int(line_time)
                
                if line_fish >= self.boxsizes[user_info.get('current_box')]:
                    line_fish = self.boxsizes[user_info.get('current_box')]
                    await ctx.reply("```\nYou have been fishing for {0} seconds.\n{1} fish stored in box. Your box is full!!\n```".format(line_time,line_fish))
                else:
                    await ctx.reply("```\nYou have been fishing for {0} seconds.\n{1} fish stored in box.\n```".format(line_time,line_fish))
            else:
                await ctx.reply("```\nCast your line first.\n```")
        else:
            await self.initUserDocument(ctx)

    #BOX
    @commands.command(name="box")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def showBox(self, ctx: context):
        """
        Example code to show inventory
        """
        #Find user document
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if "box" not in user_info:
            #Create an empty list inventory for the user
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'box' : []}})
        
        await ctx.reply("Your box:\n{0}".format(user_info.get('box')))

    #WIPE BOX
    @commands.command(name="wipebox")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def wipeBox(self, ctx: context):
        """
        Example code to delete inventory
        """
        #Find user document
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if "box" not in user_info:
            await ctx.reply("You don't even have a box...")
        
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'box' : []}})
        await ctx.reply("Box purged.")

    #FIX
    @commands.command(name="fix")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def repair(self, ctx: context):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'deltaT' : ""}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'fish' : ""}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'box_size' : ""}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'box' : []}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'rodcast' : 0}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'pool' : self.pools[0]}})

        if user_info.get('current_rod') not in self.rods :
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_rod' : self.generateRod(0)}})
        if user_info.get('current_rod') is None:
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_rod' : self.generateRod(0)}})
        
        if user_info.get('current_box') not in self.boxes :
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_box' : self.generateBox(0)}})
        if user_info.get('current_box') is None:
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_box' : self.generateBox(0)}})

        await ctx.reply("Account data repaired!! (In theory).")

    #STOP_FISHING
    @commands.command(name="cancel")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def cancel(self, ctx: context):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'cancel' : 1}})

        await ctx.reply("Stopping fishing queue...")
        
    #SELL
    @commands.command(name="sell") #reworked sell
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def repairdata(self, ctx: context):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)
        
        sell_sum = 0
        for fishie in user_info.get('box'):
            for prices in self.price_dicts:
                if fishie in prices:
                    sell_sum += prices[fishie]
        
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$inc' : {'gold' : sell_sum}})
        self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'box' : [] }})

        await ctx.reply("Fish sold for a sum of {0} gold!".format(sell_sum))

    #PRICE PRINTING
    @commands.command(aliases=["value","values"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def value_print(self, ctx: context, *, page):
        
        index = -1

        if page == "fresh":
            index = 0
        elif page == "salt":
            index = 1
        else:
            await ctx.reply("fresh or salt")
            return

        message = "```\n"
        for k, v in self.price_dicts[int(index)].items():
            message += k + " value: " + str(v) + "\n"
        message += "\n```"

        await ctx.reply("{0}".format(message))

    #STORE
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def store(self, ctx: context):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        rod = user_info.get('current_rod')
        if rod is self.rods[8]:
            await ctx.reply("Rod is maxed.") ## WILL HAVE TO REWORK THESE REPLY COMMANDS NOW THAT I HAVE MULTIPLE ITEMS
        if rod is not None and rod is not self.rods[8]:
            rodindex = self.rods.index(rod)
            new_rod_index = rodindex + 1
            newrod = self.rods[new_rod_index] 
            rodprice = self.rodprices[newrod]

        box = user_info.get('current_box')
        if box is self.boxes[6]:
            await ctx.reply("Box is maxed.") ## WILL HAVE TO REWORK THESE REPLY COMMANDS NOW THAT I HAVE MULTIPLE ITEMS
        if box is not None and box is not self.boxes[6]:
            boxindex = self.boxes.index(box)
            new_box_index = boxindex + 1
            newbox = self.boxes[new_box_index] 
            boxprice = self.boxprices[newbox]

            await ctx.reply("```\nWelcome to The Salty Seamonkey.\n-------------------------------\n\nYour current rod: {0}\nUpgrade: {1}\nCost: {2} gold.\nTo purchase rod upgrade, use j!buy rod\n\nYour current box: {3}\nUpgrade: {4}\nCost: {5} gold.\nTo purchase box upgrade, use j!buy box```".format(rod,newrod,rodprice,box,newbox,boxprice))

    #BUY -- clean this up later with functions and whatnot
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def buy(self, ctx: context, *, item):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        rod = user_info.get('current_rod')
        box = user_info.get('current_box')

        if rod == self.rods[8]:
            await ctx.reply("Rod is maxed.")
        elif rod is not None and rod != self.rods[8]:
            rod_index = self.rods.index(rod)
            new_rod_index = rod_index + 1
            newrod = self.rods[new_rod_index] 
            rodprice = self.rodprices[newrod]
        
        if item == "rod" and user_info.get('gold') >= rodprice and rod is not None and rod != self.rods[8]:
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_rod' : self.generateRod(new_rod_index)}})
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$inc' : {'gold' : rodprice*(-1)}})
            await ctx.reply("Rod upgraded to {0}!".format(newrod))
        elif item == "rod" and user_info.get('gold') < rodprice and rod is not None and rod != self.rods[8]: 
            await ctx.reply("You don't have enough gold for this... get back to fishing!!")

        if box == self.boxes[6]:
            await ctx.reply("Box is maxed.")
        elif box is not None and box != self.boxes[6]:
            box_index = self.boxes.index(box)
            new_box_index = box_index + 1
            newbox = self.boxes[new_box_index] 
            boxprice = self.boxprices[newbox]

        if item == "box" and user_info.get('gold') >= boxprice and box is not None and box != self.boxes[6]:
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_box' : self.generateBox(new_box_index)}})
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$inc' : {'gold' : boxprice*(-1)}})
            await ctx.reply("Box upgraded to {0}!".format(newbox))
        elif item == "box" and user_info.get('gold') < boxprice and box is not None and box != self.boxes[6]:
            await ctx.reply("You don't have enough gold for this... get back to fishing!!")

        #change pool
    @commands.command(name="pool")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def pool_swap(self, ctx: context, *, pool):

        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if pool == "fresh":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'pool' : self.pools[0]}})
            await ctx.reply("pool: {0}.".format(self.pools[0]))
        elif pool == "salt":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'pool' : self.pools[1]}})
            await ctx.reply("pool: {0}.".format(self.pools[1]))
        else:
            await ctx.reply("fresh or salt.")


    #FIX2 -- TEMPORARY
    #@commands.command(name="boxfix")
    #@commands.cooldown(1, 1, commands.BucketType.user)
    #async def repair2(self, ctx: context):

    #    user_info = self.db.users.find_one({'user_id': ctx.author.id})

    #    if user_info is None:
    #        await self.initUserDocument(ctx)

    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'deltaT' : ""}})
    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'fish' : ""}})
    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$unset' : {'box_size' : ""}})
    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'box' : []}})
    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'rodcast' : 0}})

    #    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'current_box' : self.generateBox(1)}})

    #    await ctx.reply("xd")

    @commands.command(name="n")
    @commands.cooldown(0, 0, commands.BucketType.user)
    async def notepad(self, ctx, *, msg=""):
    
        #Find user document
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if "notepad" not in user_info:
            #Create an empty list inventory for the user
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'notepad' : ["","","","","","","","","","","","","","",""]}})

        if msg == "":
            notepad = user_info.get('notepad')
            text = "```\n"
            for line in notepad:
                text += str(line) + "\n"
            text += "\n```"
            await ctx.reply("{0}".format(text))

        elif msg == "wipe":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'notepad' : ["","","","","","","","","","","","","","",""]}})
            notepad = user_info.get('notepad')
            await ctx.reply("Wiped.")
            
        elif msg != "":
            line_num = msg.split()[0]
            entry = msg.split()
            if len(entry) > 1:
                deleted_line = entry[1]
                if deleted_line == "w":
                    notepad = user_info.get('notepad')
                    notepad[int(line_num)] = ""
                    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'notepad' : notepad}})

                elif deleted_line != "w":
                    notepad = user_info.get('notepad')
                    notepad[int(line_num)] = msg
                    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'notepad' : notepad}})


    @commands.command(name="f")
    @commands.cooldown(0, 0, commands.BucketType.user)
    async def funny(self, ctx, *, msg=""):
    
        #Find user document
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if "funny" not in user_info:
            #Create an empty list inventory for the user
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'funny' : ""}})

        if msg == "":
            funny = user_info.get('funny')
            await ctx.send("{0}".format(funny))

        elif msg == "wipe":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'funny' : ""}})
            await ctx.reply("Wiped.")
            
        elif msg != "":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'funny' : msg}})
    

    @commands.command(name="b")
    @commands.cooldown(0, 0, commands.BucketType.user)
    async def board(self, ctx, *, msg=""):
    
        #Find user document
        user_info = self.db.users.find_one({'user_id': ctx.author.id})

        #If user document not found
        if user_info is None:
            await self.initUserDocument(ctx)

        if "board" not in user_info:
            #Create an empty list inventory for the user
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'board' : ["","","","","","","","","","","","","","",""]}})

        if msg == "":
            board = user_info.get('board')
            text = "```\n"
            for line in board:
                text += str(line) + "\n"
            text += "\n```"
            await ctx.reply("{0}".format(text))

        elif msg == "wipe":
            self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'board' : ["","","","","","","","","","","","","","",""]}})
            board = user_info.get('board')
            await ctx.reply("Wiped.")
            
        elif msg != "":
            line_num = msg.split()[0]
            entry = msg.split()
            if len(entry) > 1:
                deleted_line = entry[1]
                if deleted_line == "w":
                    board = user_info.get('board')
                    board[int(line_num)] = ""
                    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'board' : board}})

                elif deleted_line != "w":
                    board = user_info.get('board')
                    board[int(line_num)] = msg
                    self.db.users.update_one({'_id' : user_info.get('_id')}, {'$set' : {'board' : board}})

            elif len(entry) == 1:
                board = user_info.get('board')
                post = msg.split()[0]
                message = board[int(post)]
                message = message.split(' ', 1)[1]

                await ctx.send("{0}".format(str(message)))
