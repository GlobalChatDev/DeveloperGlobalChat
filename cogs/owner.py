from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = None

    def cog_load(self):
        self.bot.loop.create_task(self.task())

    async def task(self):
        await self.bot.wait_until_ready()
        self.log_channel = await self.bot.try_channel(947882907068956682)

    @commands.command(brief="Shutdown the Global Chat.")
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context, *, reason: str):
        if self.bot.shutdown[0]:
            self.bot.shutdown = (False, "")
            await ctx.send("Global chat is back.")
        else:
            self.bot.shutdown = (True, reason) # type: ignore
            await ctx.send("Global chat has paused.")

    @commands.group(brief="Group for blacklist commands.", invoke_without_command=True)
    async def blacklist(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @blacklist.command(brief="Add someone to the global blacklist.", name="global")
    @commands.is_owner()
    async def global_(self, ctx: commands.Context, user: commands.UserConverter, *, reason: str):
        if await self.bot.get_global_blacklist(user.id): # type: ignore
            return await ctx.send("That user is already globally blacklisted.")
        await self.bot.db.execute("INSERT INTO global_ban VALUES (?, ?)", user.id, reason) # type: ignore
        await ctx.send(f"Blacklisted user `{user}`.")
        await self.log_channel.send(f"Blacklisted user `{user}`.") # type: ignore

    @blacklist.group(brief="Add someone to the guild blacklist.", name="guild", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def guild_(self, ctx: commands.Context, user: commands.UserConverter, *, reason: str):
        if await self.bot.get_guild_blacklist(ctx.guild.id, user.id): # type: ignore
            return await ctx.send("That user is already blacklisted in this guild.")
        await self.bot.db.execute("INSERT INTO guild_ban VALUES (?, ?, ?)", ctx.guild.id, user.id, reason) # type: ignore
        await ctx.send(f"Blacklisted user `{user}` from guild.")
        await self.log_channel.send(f"Blacklisted user `{user}` from guild.") # type: ignore

    @guild_.command(brief="Remove someone from the guild blacklist.", name="remove")
    @commands.has_permissions(administrator=True)
    async def guild_remove_(self, ctx: commands.Context, user: commands.UserConverter):
        if not await self.bot.get_guild_blacklist(ctx.guild.id, user.id): # type: ignore
            return await ctx.send("That user is not blacklisted in this guild.")
        await self.bot.db.execute("DELETE FROM guild_ban WHERE guild_id = ? AND user_id = ?", ctx.guild.id, user.id) # type: ignore
        await ctx.send(f"Unblacklisted user `{user}` from a guild.")
        await self.log_channel.send(f"Unblacklisted user `{user}` from a guild.") # type: ignore

    @blacklist.command(brief="Remove someone from the global blacklist.", name="remove")
    @commands.is_owner()
    async def global_remove_(self, ctx: commands.Context, user: commands.UserConverter):
        if not await self.bot.get_global_blacklist(user.id): # type: ignore
            return await ctx.send("That user is not globally blacklisted.")
        await self.bot.db.execute("DELETE FROM global_ban WHERE user_id = ?", user.id) # type: ignore
        await ctx.send(f"Unblacklisted user `{user}`.")
        await self.log_channel.send(f"Unblacklisted user `{user}`.") # type: ignore

async def setup(bot: commands.Bot):
    await bot.add_cog(Owner(bot)) # type: ignore
