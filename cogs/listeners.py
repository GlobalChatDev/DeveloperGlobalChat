from discord.ext import commands
import discord, random


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is Ready")
        print(f"Logged in as {self.bot.user}")
        print(f"Id: {self.bot.user.id}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channels = [channel for channel in guild.channels]
        roles = roles = [role for role in guild.roles]
        embed = discord.Embed(title=f"Bot just joined  {guild.name}", color=random.randint(0, 16777215))

        embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

        embed.add_field(name="Server Name:", value=f"{guild.name}")
        embed.add_field(name="Server ID:", value=f"{guild.id}")
        embed.add_field(name="Server region:", value=f"{guild.region}")
        embed.add_field(
            name="Server Creation Date:",
            value=f"{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}",
        )
        embed.add_field(name="Server Owner:", value=f"{guild.owner}")
        embed.add_field(name="Server Owner ID:", value=f"{guild.owner_id}")
        embed.add_field(name="Member Count:", value=f"{guild.member_count}")
        embed.add_field(name="Amount of Channels:", value=f"{len(channels)}")
        embed.add_field(name="Amount of Roles:", value=f"{len(roles)}")
        await self.bot.fetch_channel(947882907068956682).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        channels = [channel for channel in guild.channels]
        roles = roles = [role for role in guild.roles]
        embed = discord.Embed(title=f"Bot just left : {guild.name}", color=random.randint(0, 16777215))

        embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

        embed.add_field(name="Server Name:", value=f"{guild.name}")
        embed.add_field(name="Server ID:", value=f"{guild.id}")

        try:
            embed.add_field(name="Server region:", value=f"{guild.region}")

        except:
            pass

        embed.add_field(
            name="Server Creation Date:",
            value=f"{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}",
        )
        embed.add_field(name="Server Owner:", value=f"{guild.owner}")
        embed.add_field(name="Server Owner ID:", value=f"{guild.owner_id}")
        try:
            embed.add_field(name="Member Count:", value=f"{guild.member_count}")
        except:
            pass
        embed.add_field(name="Amount of Channels:", value=f"{len(channels)}")
        embed.add_field(name="Amount of Roles:", value=f"{len(roles)}")
        await self.bot.fetch_channel(947882907068956682).send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
