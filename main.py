import discord, asyncpg
from discord.ext import commands
import asyncio, os
import B

class GlobalChatBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def start(self,*args, **kwargs):
    self.db = await asyncpg.create_pool(os.getenv("DB_key"))

    await super().start(*args, **kwargs)

  async def close(self):
    await self.db.close()
    await super().close()

bot = GlobalChatBot(command_prefix = commands.when_mentioned_or("d!"), intents = discord.Intents.all())

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.NoEntryPointError as e:
      print(e)

B.b()
bot.run(os.environ["TOKEN"])

