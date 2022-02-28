from discord.ext import commands
import utils
import discord, re, random, asyncio
from utils import Censorship
import traceback
import cool_utils
from better_profanity import profanity


class GlobalChat(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(3.0, 15.0, commands.BucketType.user)

    async def cog_command_error(self, ctx, error):
        if ctx.command and not ctx.command.has_error_handler():
            await ctx.send(error)
            import traceback

            traceback.print_exc()

        # I need to fix all cog_command_error

    async def message_converter(self, message: discord.Message):
        args = message.content
        args = args or "Test Content"

        try:
            for x in re.findall(r"<@!?([0-9]{15,20})>", args):
                user = await self.bot.try_user(int(x))

                print(f"{re.match(rf'<@!?({x})>', args).group()}")

                args = args.replace(f"{re.match(rf'<@!?({x})>', args).group()}", f"@{user}")
                # fix issue

        except Exception as e:
            traceback.print_exc()
            print(f"error occured as {e}.")

        ctx = await self.bot.get_context(message)
        args = await commands.clean_content(remove_markdown=True).convert(ctx, args)
        censoring = Censorship(args)
        args_censored = censoring.censor()
        args = profanity.censor(args_censored, censor_char="#")
        args = cool_utils.Links.censor(content=args, censor="#")
        # using this as a backup, cool_utils and the old better_profanity :)
        return args_censored

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # find out how to edit edited messages or who deleted them to enable syncing.

        ctx = await self.bot.get_context(message)
        if (
            message.channel.id in self.bot.linked_channels
            and not message.author.bot
            and not ctx.valid
            and not ctx.prefix
        ):

            bucket = self._cd.get_bucket(message)
            retry_after = bucket.update_rate_limit()

            if retry_after:
                await asyncio.sleep(15.0)

            # slows down spam, now it just well wait 15 seconds if cooldown is triggered.

            args = await self.message_converter(message)

            if len(args) >= 6000:
                args = "TooBig: the content specified is too large to send."

                await ctx.send(
                    f"Hey! Please use content less than 6000 characters, either using a pastebin or something else, thanks"
                )

            embed = discord.Embed(
                title=f"{message.guild}", description=f"{args}", color=15428885, timestamp=message.created_at
            )

            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)

            if message.guild:
                embed.set_thumbnail(
                    url=message.guild.icon.url if message.guild.icon else "https://i.imgur.com/3ZUrjUP.png"
                )
            thing = await self.bot.get_global_blacklist(message.author.id)
            if thing:
                return await ctx.reply(
                    embed=discord.Embed(
                        title="Blacklisted",
                        description=f"You were globally blacklisted for {thing['reason']}. Please appeal by contacting the developers.",
                    )
                )

            for c in self.bot.linked_channels:
                channel = self.bot.get_channel(c)
                channel = channel if channel is not None else (await self.bot.fetch_channel(c))
                # frostii you can make your own method if you want for try_channel, maybe put it in a log or something, if the channel is None, so we can remove the link?
                if c == message.channel.id:
                    continue

                if channel is None:
                    print(c)

                if channel:
                    thing = await self.bot.get_guild_blacklist(channel.guild.id, message.author.id)
                    if thing:
                        dont_send = True
                    if not dont_send:
                        await channel.send(embed=embed)
                    else:
                        await ctx.reply("Blacklisted in some guild, can't send.")

    @commands.has_permissions(manage_messages=True)
    @commands.command(brief="Adds yourself to the global chat with other developers", aliases=["addlink"])
    async def add_link(self, ctx):

        if not ctx.guild:
            return await ctx.send(
                "There is no guild found, if this seems like an error, report the problem to the developer at `JDJG Inc. Official#3493`.  Thank you."
            )

        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.send("Must be in a text channel.")

        view = utils.BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This adds a link to the current channel. Do you want to do this?", view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit("Too slow, be quicker!")

        if not view.value:
            return await msg.edit("Not linking your channel to the global chat.")

        await msg.edit("I can now link your channel. Linking....")

        row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE guild_id = $1", ctx.guild.id)

        if row:
            await ctx.send("You already linked a channel, we'll update it right now.")

            await self.bot.db.execute(
                "UPDATE linked_chat SET channel_id = $1 WHERE guild_id = $2", ctx.channel.id, ctx.guild.id
            )

            self.bot.linked_channels.remove(row.get("channel_id"))

        if not row:
            await self.bot.db.execute("INSERT INTO linked_chat values ($1, $2)", ctx.guild.id, ctx.channel.id)

        self.bot.linked_channels.append(ctx.channel.id)
        await msg.edit("**`Locked and loaded`**. The channel has been linked.")

    @commands.has_permissions(manage_messages=True)
    @commands.command(brief="Removes the current channel's link.", aliases=["removelink"])
    async def remove_link(self, ctx):

        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.send("Must be in a text channel.")

        view = utils.BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This remove a link to the current channel. Do you want to do this?", view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit("Too slow! Be quicker!")

        if not view.value:
            return await msg.edit("Not unlinking your channel to the global chat.")

        await msg.edit("I can now unlink your channel, unlinking....")

        row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE guild_id = $1", ctx.guild.id)

        if not row:
            await ctx.send("Can't unlink from a channel that doesn't exist.")

        self.bot.linked_channels.remove(row.get("channel_id"))

        await self.bot.db.execute("DELETE FROM linked_chat WHERE guild_id = $1", ctx.guild.id)

        await msg.edit("**`Locked and loaded`** The link has been removed.")

    @commands.command(brief="Invite the bot!", aliases=["inv"])
    async def invite(self, ctx):

        minimial_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(70635073))
        moderate_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8))

        embed = discord.Embed(title="Invite link:", color=random.randint(0, 16777215))
        embed.add_field(name="Minimial permisions", value=f"{minimial_invite}")
        embed.add_field(name="Moderate Invite:", value=moderate_invite)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Not all features may work if you invite with minimal perms, if you invite with 0 make sure these permissions are in a Bots/Bot role."
        )

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Minimial Permisions Invite",
                url=minimial_invite,
                style=discord.ButtonStyle.link,
            )
        )
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Moderate Permisions Invite",
                url=moderate_invite,
                style=discord.ButtonStyle.link,
            )
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(brief="rules")
    async def rules(self, ctx):
        rules = ["No swearing. Keep it family friendly.", "No NSFW - Same thing, keep it family friendly."]
        content = """"""
        for index, value in enumerate(rules):
            content += f"{index}: {value}\n"
        return await ctx.reply(content)

    @commands.command()
    async def credits(self, ctx):
        crediting = [
            "Hosting provided by FrostiiWeeb#8373 - They also provided the current profile picture.",
            "AJTHATKID#0001 for providing the bot's old profile picture.",
            "JDJG Inc. Official#3943 for the creator of this project and programming the bot.",
            "Thank you for the support and endless help, EndlessVortex#4547 and BenitzCoding#1317.",
        ]
        content = """"""
        for index, value in enumerate(crediting):
            content += f"{index}: {value}\n"
        return await ctx.reply(content)

    @commands.command(brief="Source code.")
    async def source(self, ctx):
        embed = discord.Embed(
            title="Project at:\nhttps://github.com/GlobalChatDev/DeveloperGlobalChat !",
            description="We have the MIT License for the project, you may not steal code. Just make it yourself or ask how we do it. Thank you!",
            color=random.randint(0, 16777215),
        )
        embed.set_author(name=f"{self.bot.user}'s source code:", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(brief="Suggest something.")
    async def suggest(self, ctx: commands.Context, *, content: str):
        embed = discord.Embed(title="Suggestion")
        embed.description = content
        embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Ran by {str(ctx.author)}")
        await (await self.bot.fetch_channel(947604940774309889)).send(embed=embed)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GlobalChat(bot))
