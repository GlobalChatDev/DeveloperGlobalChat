from discord.ext import commands
import discord
from main import GlobalChatBot
import typing


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: GlobalChatBot) -> None:
        self.bot: GlobalChatBot = bot
        self.log_channel = discord.TextChannel(
            state=bot._connection,
            data={
                "id": "947882907068956682",
                "last_message_id": None,
                "type": 0,
                "name": "logs",
                "position": 13,
                "parent_id": "947604752886300774",
                "topic": None,
                "guild_id": "928371409317670931",
                "permission_overwrites": [
                    {"id": "842025753993805834", "type": 1, "allow": "3072", "deny": "0"},
                    {"id": "929704300777717841", "type": 0, "allow": "3072", "deny": "0"},
                    {"id": "928371409317670931", "type": 0, "allow": "0", "deny": "377957125120"},
                    {"id": "928372768653864982", "type": 0, "allow": "3072", "deny": "0"},
                ],
                "nsfw": False,
                "rate_limit_per_user": 0,
            },
            guild=discord.Guild(
                state=bot._connection,
                data={
                    "id": "928371409317670931",
                    "name": "The Database Club Server",
                    "icon": "c410e7452f921ac55b3510f39811b7f8",
                    "description": None,
                    "splash": None,
                    "discovery_splash": None,
                    "features": ["NEWS", "COMMUNITY"],
                    "approximate_member_count": 21,
                    "approximate_presence_count": 12,
                    "emojis": [
                        {
                            "name": "848402357863710762",
                            "roles": [],
                            "id": "928388722972565534",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "Ban",
                            "roles": [],
                            "id": "928388724180545648",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "badgeStaff",
                            "roles": [],
                            "id": "928388724193112066",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "channelLocked",
                            "roles": [],
                            "id": "928388724214079509",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "channel",
                            "roles": [],
                            "id": "928388724293763112",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "channelNSFW",
                            "roles": [],
                            "id": "928388724302168124",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostedUpload",
                            "roles": [],
                            "id": "928388724318941205",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostLvl3",
                            "roles": [],
                            "id": "928388724327321672",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "Copy",
                            "roles": [],
                            "id": "928388724386058240",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostLvl9",
                            "roles": [],
                            "id": "928388724457373696",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "badgePartner",
                            "roles": [],
                            "id": "928388724503486465",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "booster4",
                            "roles": [],
                            "id": "928388724549640232",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "createEmoji",
                            "roles": [],
                            "id": "928388724587393044",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostLvl6",
                            "roles": [],
                            "id": "928388724595777537",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostLvl1",
                            "roles": [],
                            "id": "928388724709023815",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "CreateInvite",
                            "roles": [],
                            "id": "928388724746780723",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "boostLvl2",
                            "roles": [],
                            "id": "928388724750975087",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                        {
                            "name": "903710583126376530",
                            "roles": [],
                            "id": "928632456700129320",
                            "require_colons": True,
                            "managed": False,
                            "animated": False,
                            "available": True,
                        },
                    ],
                    "stickers": [],
                    "banner": None,
                    "owner_id": "746807014658801704",
                    "application_id": None,
                    "region": "southafrica",
                    "afk_channel_id": None,
                    "afk_timeout": 300,
                    "system_channel_id": "928371409317670934",
                    "widget_enabled": False,
                    "widget_channel_id": None,
                    "verification_level": 2,
                    "roles": [
                        {
                            "id": "928371409317670931",
                            "name": "@everyone",
                            "permissions": "1073309273793",
                            "position": 0,
                            "color": 0,
                            "hoist": False,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "928372141542482011",
                            "name": "Snoopy",
                            "permissions": "8",
                            "position": 8,
                            "color": 0,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "870098659453329478"},
                        },
                        {
                            "id": "928372768653864982",
                            "name": "Bot Adder",
                            "permissions": "1071698661089",
                            "position": 12,
                            "color": 3447003,
                            "hoist": True,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "928373698094858240",
                            "name": "epic pink user",
                            "permissions": "1071698660929",
                            "position": 10,
                            "color": 15277667,
                            "hoist": True,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "928373928894791690",
                            "name": "Helper/Creator",
                            "permissions": "1071698660937",
                            "position": 14,
                            "color": 15158332,
                            "hoist": False,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "928374155760500816",
                            "name": "epic user",
                            "permissions": "1071698660929",
                            "position": 11,
                            "color": 3926505,
                            "hoist": True,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "928374922886148137",
                            "name": "Oahx",
                            "permissions": "549755813887",
                            "position": 15,
                            "color": 1752220,
                            "hoist": True,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "844213992955707452"},
                        },
                        {
                            "id": "928384283792523285",
                            "name": "Developer Global Chat",
                            "permissions": "70635073",
                            "position": 7,
                            "color": 7419530,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "842025753993805834"},
                        },
                        {
                            "id": "928384636286029844",
                            "name": "JDBot",
                            "permissions": "8",
                            "position": 6,
                            "color": 12745742,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "347265035971854337"},
                        },
                        {
                            "id": "928387082701918229",
                            "name": "My Games",
                            "permissions": "388160",
                            "position": 5,
                            "color": 0,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "747984555352260750"},
                        },
                        {
                            "id": "928401052796072038",
                            "name": "DuckBot",
                            "permissions": "523553459937",
                            "position": 4,
                            "color": 0,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "788278464474120202"},
                        },
                        {
                            "id": "929704300777717841",
                            "name": "Staff",
                            "permissions": "2181574414071",
                            "position": 13,
                            "color": 15277667,
                            "hoist": True,
                            "managed": False,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                        },
                        {
                            "id": "933445547774324787",
                            "name": "kriX",
                            "permissions": "8",
                            "position": 1,
                            "color": 0,
                            "hoist": False,
                            "managed": True,
                            "mentionable": False,
                            "icon": None,
                            "unicode_emoji": None,
                            "tags": {"bot_id": "325857819888713730"},
                        },
                    ],
                    "default_message_notifications": 1,
                    "mfa_level": 0,
                    "explicit_content_filter": 2,
                    "max_presences": None,
                    "max_members": 500000,
                    "max_video_channel_users": 25,
                    "vanity_url_code": None,
                    "premium_tier": 0,
                    "premium_subscription_count": 0,
                    "system_channel_flags": 0,
                    "preferred_locale": "en-US",
                    "rules_channel_id": "929416811957604402",
                    "public_updates_channel_id": "928607469276643378",
                    "hub_type": None,
                    "premium_progress_bar_enabled": False,
                    "nsfw": False,
                    "nsfw_level": 0,
                },
            ),
        )

    @commands.group(brief="Group for blacklist commands.Chat", hidden=True)
    async def blacklist(self, ctx: commands.Context):
        return await ctx.send_help(ctx.command)

    @blacklist.command(brief="Add someone to the global blacklist.", name="global")
    @commands.is_owner()
    async def global_(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member, int], reason: str):
        if await self.bot.get_global_blacklist(user.id):
            return await ctx.send("That user is already globally blacklisted.")
        await self.bot.db.execute("INSERT INTO global_ban(user_id, reason) VALUES ($1, $2)", user.id, reason)
        return await ctx.send(f"Blacklisted user `{user}`."), await self.log_channel.send(f"Blacklisted user `{user}`.")

    @blacklist.command(brief="Add someone to the guild blacklist.", name="guild", hidden=False)
    @commands.has_permissions(manage_server=True)
    async def guild_(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member, int], reason: str):
        if await self.bot.get_guild_blacklist(ctx.guild.id, user.id):
            return await ctx.send("That user is already blacklisted in this guild.")
        await self.bot.db.execute(
            "INSERT INTO guild_ban(guild_id, user_id, reason) VALUES ($1, $2, $3)", ctx.guild.id, user.id, reason
        )
        return await ctx.send(f"Blacklisted user `{user}`."), await self.log_channel.send(f"Blacklisted user `{user}`.")


def setup(bot: GlobalChatBot):
    bot.add_cog(Owner(bot))
