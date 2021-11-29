import discord, asyncpg
from pymongo import MongoClient
from cool_utils import Mongo
from discord.ext import commands
import asyncio, os, traceback
import B

class GlobalChatBot(commands.AutoShardedBot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def start(self, *args, **kwargs):
    Mongo.connect(os.getenv("DB_url"), "GlobalChat")
    Mongo.set_collection("all_links")
    for data in await Mongo.find_one({"_id": "all"}):
      for channel in data["links"]:
        self.bot.linked_channels.append(channel)
    await super().start(*args, **kwargs)

  async def close(self):
    await super().close()

bot = GlobalChatBot(command_prefix = commands.when_mentioned_or("d!"), intents = discord.Intents.all(), owner_ids = [168422909482762240, 529499034495483926, 745058406083198994], activity = discord.Activity(type = discord.ActivityType.listening, name = f"I am making developer help across guilds possible."))

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.NoEntryPointError:
      traceback.print_exc()

B.b()
bot.run(os.environ["TOKEN"])

