import typing

import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def task(self):
        await self.bot.wait_until_ready()
        self.log_channel = await self.bot.try_channel(947882907068956682)

    async def cog_load(self):
        self.bot.loop.create_task(self.task())

    @commands.group(brief="Group for blacklist commands.", invoke_without_command=True)
    async def blacklist(self, ctx: commands.Context):
        return await ctx.send_help(ctx.command)

    @blacklist.command(brief="Add someone to the global blacklist.", name="global")
    @commands.is_owner()
    async def global_(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member, int], reason: str):
        if await self.bot.get_global_blacklist(user.id):
            return await ctx.send("That user is already globally blacklisted.")
        await self.bot.db.execute("INSERT INTO global_ban(user_id, reason) VALUES ($1, $2)", user.id, reason)
        return await ctx.send(f"Blacklisted user `{user}`."), await self.log_channel.send(f"Blacklisted user `{user}`.")

    @blacklist.command(brief="Add someone to the guild blacklist.", name="guild")
    @commands.has_permissions(administrator=True)
    async def guild_(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member, int], reason: str):
        if await self.bot.get_guild_blacklist(ctx.guild.id, user.id):
            return await ctx.send("That user is already blacklisted in this guild.")
        await self.bot.db.execute(
            "INSERT INTO guild_ban(guild_id, user_id, reason) VALUES ($1, $2, $3)", ctx.guild.id, user.id, reason
        )
        return await ctx.send(f"Blacklisted user `{user}`."), await self.log_channel.send(f"Blacklisted user `{user}`.")

    @blacklist.command(brief="Remove someone from the global blacklist.", name="remove")
    @commands.is_owner()
    async def global_remove_(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member, int]):
        if not await self.bot.get_global_blacklist(user.id):
            return await ctx.send("That user is not globally blacklisted.")
        await self.bot.db.execute("DELETE FROM global_ban WHERE user_id = $1", user.id)
        return await ctx.send(f"UNlacklisted user `{user}`."), await self.log_channel.send(
            f"Unblacklisted user `{user}`."
        )


async def setup(bot):
    await bot.add_cog(Owner(bot))
