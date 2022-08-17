import discord, asyncpg
from discord.ext import commands
import asyncio, os, traceback, dotenv

dotenv.load_dotenv()


class GlobalChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_global_blacklist(self, user_id: int):
        return await self.db.fetchrow("SELECT * FROM global_ban WHERE user_id = $1", user_id)

    async def get_guild_blacklist(self, guild_id: int, user_id: int):
        return await self.db.fetchrow("SELECT * FROM guild_ban WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)

    async def start(self, *args, **kwargs):
        self.db = await asyncpg.create_pool(os.getenv("DB_key"))

        self.linked_data = await self.db.fetch("SELECT * FROM linked_chat")
        self.linked_channels = [c.get("channel_id") for c in self.linked_data]

        await super().start(*args, **kwargs)

    async def try_user(self, id: int, /):
        maybe_user = self.get_user(id)
import discord, asyncpg
from discord.ext import commands
import asyncio, os, traceback, dotenv

dotenv.load_dotenv()


class GlobalChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_global_blacklist(self, user_id: int):
        return await self.db.fetchrow(
            "SELECT * FROM global_ban WHERE user_id = $1", user_id
        )

    async def get_guild_blacklist(self, guild_id: int, user_id: int):
        return await self.db.fetchrow(
            "SELECT * FROM guild_ban WHERE user_id = $1 AND guild_id = $2",
            user_id,
            guild_id,
        )

    async def start(self, *args, **kwargs):
        self.db = await asyncpg.create_pool(os.getenv("DB_key"))

        self.linked_data = await self.db.fetch("SELECT * FROM linked_chat")
        self.linked_channels = [c.get("channel_id") for c in self.linked_data]

        await super().start(*args, **kwargs)

    async def try_user(self, id: int, /):
        maybe_user = self.get_user(id)

        if maybe_user is not None:
            return maybe_user

        try:
            return await self.fetch_user(id)
        except discord.errors.NotFound:
            return None

    async def try_channel(self, id: int, /):
        maybe_channel = self.get_channel(id)

        if maybe_channel is not None:
            return maybe_channel

        try:
            return await self.fetch_channel(id)
        except (discord.errors.NotFound, discord.errors.Forbidden):
            return None

    async def close(self):
        await self.db.close()
        await super().close()

    async def setup_hook(self):
        extensions = [
            ext.rstrip(".py")
            for ext in os.listdir("./cogs")
            if os.path.isfile(f"cogs/{ext}")
        ]
        for cog in extensions:
            await bot.load_extension(f"cogs.{cog}")


bot = GlobalChatBot(
    command_prefix=commands.when_mentioned_or("d!"),
    intents=discord.Intents.all(),
    owner_ids=[
        168422909482762240,
        529499034495483926,
        745058406083198994,
        746807014658801704,
    ],
    activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=f"I am making developer help across guilds possible.",
    ),
)

# if intents break, then re-apply them there and such, a.k.a make sure to add new intents to fix upcoming issues etc.


class Help(commands.MinimalHelpCommand):  # Better help command
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(
                description=page,
                color=discord.Colour.burple,
                timestamp=discord.utils.utcnow(),
            )
            emby.set_footer(
                text=f"Requested by: {self.context.author}",
                icon_url=self.context.author.avatar,
            )
            await destination.send(embed=emby)


bot.help_command = Help()


@bot.event
async def on_error(event, *args, **kwargs):
    more_information = os.sys.exc_info()
    error_wanted = traceback.format_exc()
    traceback.print_exc()


bot.run(os.environ["TOKEN"])
