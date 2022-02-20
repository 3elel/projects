import discord
from discord.ext import commands
import logging
import pymongo
import certifi
import random
import db_testing

ca = certifi.where()

#Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Read in Key
key = open("key.txt", "r").read()
dbkey = open("dbkey.txt", "r").read()

#Init connecting to DB
client = pymongo.MongoClient("mongodb+srv://dbAdmin:{0}@cluster0.yvzo4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(dbkey), tlsCAFile=ca)
db = client.cnfbot

#Initiate Bot, set prefix
print("Initiating Jahy!")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["j!","J!"], intents=intents)

@bot.command()
async def pat(ctx):
    await ctx.reply('https://tenor.com/view/jahy-jahy-sama-petthejahy-gif-19036434')

#cogs and whatnot
bot.add_cog(db_testing.dbTesting(bot, db))
bot.run(key)