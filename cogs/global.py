from __future__ import annotations

import asyncio
import os
import platform
import traceback
from typing import TYPE_CHECKING

import discord
import psutil
from discord.ext import commands

import utils
from utils import Censorship

if TYPE_CHECKING:
    from main import GlobalChatBot


class LoggedMessages:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.queue: list[discord.Message] = []

    def enqueue(self, item: discord.Message):
        self.queue.append(item)
        if len(self.queue) > self.max_size:
            self.dequeue()

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            raise IndexError("Queue is empty")

    def get(self, message_id: int) -> discord.Message | None:
        item = [m for m in self.queue if m.id == message_id]

        if not item:
            return None

        return item[-1]

    def __len__(self):
        return len(self.queue)


class GlobalChat(commands.Cog):
    def __init__(self, bot: GlobalChatBot):
        self.bot: GlobalChatBot = bot
        self._cd = commands.CooldownMapping.from_cooldown(5.0, 7.0, commands.BucketType.user)

    async def cog_command_error(self, ctx, error: Exception):
        if ctx.command and not ctx.command.has_error_handler():
            await ctx.send("".join(traceback.format_exception(type(error), error, error.__traceback__)))

            traceback.print_exc()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        if not self.is_valid_message(message, ctx):
            return

        if self.bot.shutdown[0]:
            return await ctx.send(
                f"Sorry, Global Chat is paused temporarily. Reason given: {self.bot.shutdown[-1]}\nWe will be back as soon as possible."
            )

        args = await self.message_converter(message)

        if len(args) >= 6000:
            args = "TooBig: the content specified is too large to send."
            await self.handle_large_message(ctx)

        is_banned = await self.bot.get_global_blacklist(message.author.id)
        if is_banned:
            return await self.handle_user_banned(ctx, is_banned)  # type: ignore

        guild_banned = await self.bot.get_guild_blacklist(ctx.guild.id, ctx.author.id)
        if guild_banned:
            return await ctx.send(
                "You have been forbidden to use Global Chat in this guild. If you believe this to be a mistake, contact administrators."
            )

        for webhook_url in self.bot.linked_webhooks:
            for row in self.bot.linked_data:
                if row["webhook_url"] == webhook_url and row["guild_id"] != ctx.guild.id:
                    await self.forward_message(ctx, message, args, webhook_url)

    def is_valid_message(self, message: discord.Message, ctx: commands.Context):
        return not message.author.bot and not ctx.valid and not ctx.prefix

    async def refresh_linked_data(self):
        self.bot.linked_data = await self.bot.db.fetchall("SELECT * FROM linked_chat")

    async def message_converter(self, message: discord.Message):
        args = message.content or "No content specified."
        args = discord.utils.escape_markdown(args)

        rights_to_freedom = Censorship(args)
        no_rights = rights_to_freedom.censor()

        return no_rights

    async def handle_large_message(self, ctx: commands.Context):
        await ctx.send(
            "Hey! Please use content less than 6000 characters, either using pastebin or github gists, thanks"
        )

    async def handle_user_banned(self, ctx: commands.Context, is_banned: dict):
        embed = discord.Embed(
            title="Blacklisted",
            description=f"You were globally blacklisted for {is_banned['reason']}. Please appeal by contacting the developers.",
        )
        await ctx.reply(embed=embed)

    async def forward_message(self, ctx: commands.Context, message: discord.Message, args: str, webhook_url: str):
        bucket = self.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            await asyncio.sleep(7)

        name = f"{ctx.author.name}#{ctx.author.discriminator}" if ctx.author.discriminator != "0" else ctx.author.name
        username = name
        avatar_url = ctx.author.display_avatar.url
        files = [await a.to_file() for a in message.attachments]

        if await self.bot.is_owner(ctx.author):
            name += " | Administrator"

        await self.send_to_channel(webhook_url, args, username, avatar_url, files)

    def get_bucket(self, message: discord.Message):
        return self._cd.get_bucket(message)

    async def send_to_channel(
        self, webhook_url: str, args: str, username: str, avatar_url: str, files: list[discord.File]
    ):
        channel = discord.Webhook.from_url(webhook_url, session=self.bot.session, bot_token=self.bot.http.token)

        await channel.send(
            args,
            username=username,
            avatar_url=avatar_url,
            files=files,
            allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=False),
        )

    @commands.has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.group(brief="Global chat linking.", invoke_without_command=True)
    async def link(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @commands.has_guild_permissions(manage_messages=True, manage_webhooks=True)
    @link.command("add", brief="Add your server to the developer global chat system.")
    async def add_link(self, ctx: commands.Context):
        if not self.is_valid_guild_and_channel(ctx):
            return

        view = utils.BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This adds a link to the current channel. Do you want to do this?", view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit(content="Too slow, be quicker!")

        if not view.value:
            return await msg.edit(content="Not linking your channel to the global chat.")

        await msg.edit(content="I am now linking your channel. Linking....")

        row = await self.get_linked_channel_row(ctx.guild.id)

        if row:
            await self.update_linked_channel(ctx, row)
        else:
            await self.create_linked_channel(ctx)

        await msg.edit(content="The channel has been linked.")

    def is_valid_guild_and_channel(self, ctx: commands.Context):
        return ctx.guild and isinstance(ctx.channel, discord.TextChannel)

    async def get_linked_channel_row(self, guild_id):
        return await self.bot.db.fetchone("SELECT * FROM linked_chat WHERE guild_id = ?", guild_id)

    async def update_linked_channel(self, ctx: commands.Context, row):
        webhooks = await ctx.channel.webhooks()  # type: ignore
        for webhook in webhooks:
            await webhook.delete()
        new_webhook = await ctx.channel.create_webhook(name="Global Chat")  # type: ignore
        await self.bot.db.execute(
            "UPDATE linked_chat SET webhook_url = ? WHERE guild_id = ?", new_webhook.url, ctx.guild.id
        )
        self.bot.linked_webhooks.remove(row["webhook_url"])
        self.bot.linked_webhooks.append(new_webhook.url)
        await self.refresh_linked_data()

    async def create_linked_channel(self, ctx: commands.Context):
        new_webhook = await ctx.channel.create_webhook(name="Global Chat")  # type: ignore
        await self.bot.db.execute("INSERT INTO linked_chat VALUES (?, ?)", ctx.guild.id, new_webhook.url)
        self.bot.linked_webhooks.append(new_webhook.url)
        await self.refresh_linked_data()

    @commands.has_permissions(manage_messages=True)
    @link.command(brief="Removes the current channel's link.")
    async def remove(self, ctx: commands.Context):
        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.send("Must be in a text channel.")

        view = utils.BasicButtons(ctx, timeout=30.0)

        msg = await ctx.send("This remove a link to the current channel. Do you want to do this?", view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit(content="Too slow! Be quicker!")

        if not view.value:
            return await msg.edit(content="Not unlinking your channel to the global chat.")

        await msg.edit(content="I can now unlink your channel, unlinking....")

        row = await self.get_linked_channel_row(ctx.guild.id)

        if not row:
            return await ctx.send("Can't unlink from a channel that doesn't exist.")

        self.bot.linked_webhooks.remove(row["webhook_url"])
        await self.bot.db.execute("DELETE FROM linked_chat WHERE guild_id = ?", ctx.guild.id)

        await msg.edit(content="The link has been removed.")

    @commands.command(brief="Invite the bot!", aliases=["inv"])
    async def invite(self, ctx: commands.Context):
        minimal_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(70635073))
        moderate_invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8))

        embed = discord.Embed(title="Invite link:")
        embed.add_field(name="Minimal Permissions Invite", value=f"{minimal_invite}")
        embed.add_field(name="Moderate Invite", value=moderate_invite)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Not all features may work if you invite with minimal permissions.")

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Minimal Permissions Invite",
                url=minimal_invite,
                style=discord.ButtonStyle.link,
            )
        )
        view.add_item(
            discord.ui.Button(
                label=f"{self.bot.user.name}'s Moderate Permissions Invite",
                url=moderate_invite,
                style=discord.ButtonStyle.link,
            )
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(brief="Rules")
    async def rules(self, ctx: commands.Context):
        rules = ["No swearing. Keep it family-friendly.", "No NSFW - Keep it family-friendly."]
        content = "\n".join([f"{index}: {value}" for index, value in enumerate(rules)])
        await ctx.reply(content)

    @commands.command()
    async def credits(self, ctx: commands.Context):
        crediting = [
            "Hosting provided by frxstingz - They also provided the current profile picture.",
            "jdjg for founding the project and the basis of the bot.",
        ]
        content = "\n".join([f"{index}: {value}" for index, value in enumerate(crediting)])
        await ctx.reply(content)

    @commands.command(brief="Gives information about the bot.")
    async def about(self, ctx: commands.Context):
        embed = discord.Embed(title="About Bot:")
        embed.add_field(
            name="Author Information",
            value="This bot is made by a couple of developers, check credits to learn more.",
            inline=False,
        )
        embed.add_field(name="Bot Version", value="1.0.0")
        embed.add_field(name="Python Version:", value=f"{platform.python_version()}")
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(
            name="RAM Usage", value=f"{(psutil.Process(os.getpid()).memory_full_info().rss / 1024**2):.2f} MB"
        )
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.set_author(name=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(brief="Source code.")
    async def source(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Project at:",
            description="We have the MIT License for the project, you may not steal code. Just make it yourself or ask how we do it. Thank you!",
        )
        embed.set_author(name=f"{self.bot.user}'s source code:", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(brief="Suggest something.")
    async def suggest(self, ctx: commands.Context, *, content: str):
        embed = discord.Embed(title="Suggestion")
        embed.description = content
        embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Ran by {str(ctx.author)}")
        await (await self.bot.try_channel(947604940774309889)).send(embed=embed)  # type: ignore
        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GlobalChat(bot))
