from typing import TYPE_CHECKING
from asyncio import sleep
from re import findall, match

import traceback
import random

import discord
from discord.ext import commands
from discord.utils import escape_markdown

import cool_utils
from utils import Censorship, BasicButtons
from better_profanity import profanity


if TYPE_CHECKING:
    from discord import Message
    from discord.ext.commands import Context, CommandError

    from main import GlobalChatBot
else:
    GlobalChatBot = commands.Bot


class GlobalChat(commands.Cog):
    def __init__(self, bot: GlobalChatBot) -> None:
        self.bot: GlobalChatBot = bot
        self._cd = commands.CooldownMapping.from_cooldown(3.0, 15.0, commands.BucketType.user)

    async def cog_command_error(self, ctx: Context, error: CommandError) -> None:
        if ctx.command and not ctx.command.has_error_handler():
            await ctx.send(str(error))
            traceback.print_exc()

        # I need to fix all cog_command_error

    async def message_converter(self, message: Message) -> str:
        message_content = message.content
        message_content = message_content or "Test Content"

        try:
            for x in findall(r"<@!?([0-9]{15,20})>", message_content):
                user = await self.bot.try_user(int(x))

                print(f"{match(rf'<@!?({x})>', message_content).group()}")  # type: ignore

                message_content = message_content.replace(
                    f"{match(rf'<@!?({x})>', message_content).group()}", f"@{user}"  # type: ignore
                )
                # fix issue

        except Exception as e:
            traceback.print_exc()
            print(f"error occured as {e}.")

        message_content = escape_markdown(message_content)
        censoring = Censorship(message_content)
        message_content_censored = censoring.censor()
        message_content = profanity.censor(message_content_censored, censor_char="#")
        message_content = cool_utils.Links.censor(content=message_content, censor="#")
        # using this as a backup, cool_utils and the old better_profanity :)
        return message_content_censored

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        # find out how to edit edited messages or who deleted them to enable syncing.

        ctx = await self.bot.get_context(message)
        if message.channel.id not in self.bot.linked_channels or (message.author.bot or not ctx.valid):
            return

        bucket = self._cd.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            await sleep(15.0)

        # slows down spam, now it just well wait 15 seconds if cooldown is triggered.
        cleaned_message_content = await self.message_converter(message)

        if len(cleaned_message_content) >= 6000:
            cleaned_message_content = "TooBig: the content specified is too large to send."

            await ctx.send(
                f"Hey! Please use content less than 6000 characters, either using a pastebin or something else, thanks"
            )

        embed = discord.Embed(
            title=str(message.guild),
            description=str(cleaned_message_content),
            color=15428885,
            timestamp=message.created_at,
        )

        embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)

        if message.guild:
            embed.set_thumbnail(url=str(message.guild.icon or "https://i.imgur.com/3ZUrjUP.png"))

        for c in self.bot.linked_channels:
            channel = self.bot.get_channel(c)
            # frostii you can make your own method if you want for try_channel,
            # maybe put it in a log or something, if the channel is None, so we can remove the link?
            if c == message.channel.id:
                continue

            if channel:
                await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            else:
                print(f"Channel {c} is not found.")

    @commands.command(brief="Adds yourself to the global chat with other developers", aliases=["addlink"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def add_link(self, ctx: Context):

        if not ctx.guild:
            await ctx.send(
                "There is no guild found, if this seems like an error, "
                f"report the problem to the developer at `JDJG Inc. Official#3493`.  Thank you."
            )
            return

        if not isinstance(ctx.channel, discord.TextChannel):
            await ctx.send("Must be in a text channel.")
            return

        view = BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This adds a link to the current channel. Do you want to do this?", view=view)

        await view.wait()
        if view.value is None:
            await msg.edit(content="Too slow, be quicker!")
            return

        elif view.value is False:
            await msg.edit(content="Not linking your channel to the global chat.")
            return

        await msg.edit(content="I can now link your channel. Linking....")

        row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE server_id = $1", ctx.guild.id)

        if row:
            await ctx.send("You already linked a channel, we'll update it right now.")

            await self.bot.db.execute(
                "UPDATE linked_chat SET channel_id = $1 WHERE server_id = $2", ctx.channel.id, ctx.guild.id
            )

            self.bot.linked_channels.remove(row.get("channel_id"))

        if not row:
            await self.bot.db.execute("INSERT INTO linked_chat values ($1, $2)", ctx.guild.id, ctx.channel.id)

        self.bot.linked_channels.append(ctx.channel.id)
        await msg.edit(content="**`Locked and loaded`**. The channel has been linked.")

    @commands.command(brief="Removes the current channel's link.", aliases=["removelink"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def remove_link(self, ctx: Context):

        if not isinstance(ctx.channel, discord.TextChannel):
            await ctx.send("Must be in a text channel.")
            return

        view = BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This remove a link to the current channel. Do you want to do this?", view=view)

        await view.wait()
        if view.value is None:
            await msg.edit(content="Too slow! Be quicker!")
            return

        elif view.value is False:
            await msg.edit(content="Not unlinking your channel to the global chat.")
            return

        await msg.edit(content="I can now unlink your channel, unlinking....")

        row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE server_id = $1", ctx.guild.id)  # type: ignore

        if not row:
            await ctx.send("Can't unlink from a channel that doesn't exist.")

        self.bot.linked_channels.remove(row.get("channel_id"))

        await self.bot.db.execute("DELETE FROM linked_chat WHERE server_id = $1", ctx.guild.id)  # type: ignore

        await msg.edit(content="**`Locked and loaded`** The link has been removed.")

    @commands.command(brief="Invite the bot!", aliases=["inv"])
    async def invite(self, ctx: Context):

        minimial_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(70635073))
        moderate_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8))

        embed = discord.Embed(title="Invite link:", color=discord.Color.random())
        embed.add_field(name="Minimial permisions", value=minimial_invite)
        embed.add_field(name="Moderate Invite:", value=moderate_invite)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Not all features may work if you invite with minimal perms, "
            "if you invite with 0 make sure these permissions are in a Bots/Bot role."
        )

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Minimial Permisions Invite",
                url=minimial_invite,
            )
        )
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Moderate Permisions Invite",
                url=moderate_invite,
            )
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(brief="rules")
    async def rules(self, ctx: Context):
        rules = ["No swearing. Keep it family friendly.", "No NSFW - Same thing, keep it family friendly."]
        await ctx.reply("\n".join(f"{index}: {value}" for index, value in enumerate(rules)))

    @commands.command()
    async def credits(self, ctx: Context):
        crediting = [
            "Database provided by and ran by FrostiiWeeb#8373 - They also programmed the basis of the bot.",
            "AJTHATKID#0001 for providing the bot's profile picture.",
            "JDJG Inc. Official#3943 for the creator of this project and programming the bot.",
            "Thank you for the support and endless help, EndlessVortex#4547 and BenitzCoding#1317.",
        ]
        await ctx.reply("\n".join(f"{index}: {value}" for index, value in enumerate(crediting)))

    @commands.command(brief="Source code.")
    async def source(self, ctx):
        embed = discord.Embed(
            title="Project at:\nhttps://github.com/GlobalChatDev/DeveloperGlobalChat !",
            description="We have the MIT License for the project, you may not steal code. Just make it yourself or ask how we do it. Thank you!",
            color=discord.Color.random(),
        )
        embed.set_author(name=f"{self.bot.user}'s source code:", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(brief="Suggest something.")
    async def suggest(self, ctx: commands.Context, *, content: str):
        embed = discord.Embed(title="Suggestion")
        embed.description = content
        await (await self.bot.fetch_channel(947604940774309889)).send(embed=embed)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GlobalChat(bot))
