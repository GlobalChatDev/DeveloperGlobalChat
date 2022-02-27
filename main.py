from pyexpat.errors import messages
import asyncpg, sys, os, traceback, dotenv

import discord
from discord.ext import commands

dotenv.load_dotenv()


class GlobalChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start(self, *args, **kwargs):
        self.db = await asyncpg.create_pool(os.getenv("DB_key"))

        self.linked_data = await self.db.fetch("SELECT * FROM linked_chat")
        self.linked_channels = [c.get("channel_id") for c in self.linked_data]

        # grab from guild_bans - guild bans
        # bans - user bans (blacklist)

        await super().start(*args, **kwargs)

    async def close(self):
        await self.db.close()
        await super().close()


bot = GlobalChatBot(
    command_prefix=commands.when_mentioned_or("d!"),
    intents=discord.Intents(messages=True, guilds=True, members=True, webhooks=True, emojis=True),
    owner_ids=[168422909482762240, 529499034495483926, 745058406083198994, 746807014658801704],
    activity=discord.Activity(
        type=discord.ActivityType.listening, name=f"I am making developer help across guilds possible."
    ),
)

# if intents break, then re-apply them there and such, a.k.a make sure to add new intents to fix upcoming issues etc.


@bot.event
async def on_error(event, *args, **kwargs):
    more_information = sys.exc_info()
    error_wanted = traceback.format_exc()
    traceback.print_exc()


extensions = [ext.rstrip(".py") for ext in os.listdir("./cogs") if os.path.isfile(f"cogs/{ext}")]
for cog in extensions:
    bot.load_extension(f"cogs.{cog}")

bot.run(os.environ["TOKEN"])
