import discord, asyncpg
from discord.ext import commands
import asyncio, os, traceback, dotenv

dotenv.load_dotenv()

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

bot = GlobalChatBot(command_prefix = commands.when_mentioned_or("d!"), intents = discord.Intents.all(), owner_ids = [168422909482762240, 529499034495483926, 745058406083198994, 746807014658801704], activity = discord.Activity(type = discord.ActivityType.listening, name = f"I am making developer help across guilds possible."))

@bot.event
async def on_error(event, *args, **kwargs):
  more_information = os.sys.exc_info()
  error_wanted=traceback.format_exc()
  traceback.print_exc()

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.NoEntryPointError:
      traceback.print_exc()

bot.run(os.environ["TOKEN"])

