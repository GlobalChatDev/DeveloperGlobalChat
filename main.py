from __future__ import annotations

import asyncio
import os

import discord
from aiohttp import ClientSession
from asqlite import create_pool
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class GlobalChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shutdown = (False, "")

    async def get_global_blacklist(self, user_id: int):
        return await self.db.fetchone("SELECT * FROM global_ban WHERE user_id = ?", user_id)

    async def get_guild_blacklist(self, guild_id: int, user_id: int):
        return await self.db.fetchone("SELECT * FROM guild_ban WHERE guild_id = ? AND user_id = ?", guild_id, user_id)

    async def create_tables(self) -> None:
        await self.db.execute(
            """
        CREATE TABLE IF NOT EXISTS global_ban (
            user_id INTEGER PRIMARY KEY,
            reason TEXT
        );
        """
        )

        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS guild_ban (guild_id BIGINT, user_id INTEGER, reason TEXT, PRIMARY KEY (guild_id, user_id));"
        )

        await self.db.execute("CREATE TABLE IF NOT EXISTS linked_chat (guild_id BIGINT PRIMARY KEY, webhook_url TEXT);")

        print("Created tables.")

    async def start(self, *args, **kwargs):
        self.db = await (await create_pool("chat.db")).acquire()  # type: ignore

        await self.create_tables()

        self.linked_data = await self.db.fetchall("SELECT * FROM linked_chat")

        print([dict(i) for i in self.linked_data])

        self.linked_webhooks = [c["webhook_url"] for c in self.linked_data]  # type: ignore

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
        extensions = [ext.rstrip(".py") for ext in os.listdir("./cogs") if os.path.isfile(f"cogs/{ext}")]
        for cog in extensions:
            await bot.load_extension(f"cogs.{cog}")

        self.session = ClientSession()


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
        name=f"cross-server messages!",
    ),
)

# if intents break, then re-apply them there and such, a.k.a make sure to add new intents to fix upcoming issues etc.


class Help(commands.MinimalHelpCommand):  # Better help command
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(
                description=page,
                color=discord.Colour.blurple(),
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
    print(event, *args, **kwargs)


async def run_bot():
    await bot.start(os.getenv("TOKEN"))


asyncio.run(run_bot())
