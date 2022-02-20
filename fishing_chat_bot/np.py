from discord.ext import commands
from discord.ext.commands import context
from discord.ext.commands.bot import Bot
from discord.ext.commands import context
from pprint import pprint
import pymongo
import time
import random
import asyncio

class notepad(commands.Cog):
    def __init__(self, bot: Bot, client: pymongo.MongoClient):
        self.bot = bot
        self.db = client