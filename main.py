import discord, asyncpg
from discord.ext import commands
import asyncio, os, traceback
import B

class GlobalChatBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def start(self, *args, **kwargs):
    self.db = await asyncpg.create_pool(os.getenv("DB_key"))

    self.linked_data = await self.db.fetch("SELECT * FROM linked_chat")
    self.linked_channels = [c.get("channel_id") for c in self.linked_data]

    #grab from guild_bans - guild bans
    #bans - user bans (blacklist)

    await super().start(*args, **kwargs)

  async def close(self):
    await self.db.close()
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

