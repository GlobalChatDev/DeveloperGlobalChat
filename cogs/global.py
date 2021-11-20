from discord.ext import commands
import utils
import discord, re
from better_profanity import profanity

class GlobalChat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error

  async def message_converter(self, message : discord.Message):
    args = message.content
    args = args or "Test Content"
    for x in re.findall(r'<@!?([0-9]{15,20})>', args):
      user = await self.bot.try_user(int(x))
      args = args.replace(f"{re.match(rf'<@!?({x})>', args).group()}", f"@{user}")

    ctx = await self.bot.get_context(message)
    args = await commands.clean_content().convert(ctx, args)
    args = profanity.censor(args, censor_char = "#")
    return args

  @commands.Cog.listener()
  async def on_message(self, message):

    ctx = await self.bot.get_context(message)
    if message.channel.id in self.bot.linked_channels and not message.author.bot and not ctx.valid and not ctx.prefix:
      
      args = await self.message_converter(message)

      embed = discord.Embed(title = f"{message.guild}",
      description = f"{args}", color = 15428885, timestamp = message.created_at)

      embed.set_author(name=f"{message.author}", icon_url = message.author.display_avatar.url)

      if message.guild: embed.set_thumbnail(url = message.guild.icon.url if message.guild.icon else "https://i.imgur.com/3ZUrjUP.png")

      for c in self.bot.linked_channels:
        channel = self.bot.get_channel(c)
        if c == message.channel.id:
            continue
        await channel.send(embed = embed)

  @commands.has_permissions(manage_messages = True)
  @commands.command(brief = "Adds yourself to the global chat with other developers", aliases = ["addlink"])
  async def add_link(self, ctx):

    if not ctx.guild:
      return await ctx.send("this is not a guild appreantly, if it is report the problem to the developer thanks :D at JDJG Inc. Official#3493")

    if not isinstance(ctx.channel, discord.TextChannel):
      return await ctx.send("you must use in a textchannel")

    view = utils.BasicButtons(ctx, timeout = 30.0)

    msg = await ctx.send("This adds a link to the current channel. Do you want to do this?", view = view)

    await view.wait()

    if view.value is None:
      return await msg.edit("you didn't respond quickly enough")

    if not view.value:
      return await msg.edit("Not linking your channel to the global chat.")

    await msg.edit("I can now link your channel. Linking....")

    row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE server_id = $1", ctx.guild.id)

    if row:
      await ctx.send("you already linked a channel, we'll update it right now.")

      await self.bot.db.execute("UPDATE linked_chat SET channel_id WHERE server_id = $2", ctx.guild.id)

      self.bot.linked.channels.remove(row.get("channel_id"))

    self.bot.linked_channels.append(ctx.channel.id)
    await msg.edit("Linked channel :D")
    

  @commands.has_permissions(manage_messages = True)
  @commands.command(brief = "Adds yourself to the global chat with other developers", aliases = ["removelink"])
  async def remove_link(self, ctx):

    if not isinstance(ctx.channel, discord.TextChannel):
      return await ctx.send("you must use in a text channel")

    view = utils.BasicButtons(ctx, timeout = 30.0)

    msg = await ctx.send("This remove a link to the current channel. Do you want to do this?", view = view)

    await view.wait()

    if view.value is None:
      return await msg.edit("you didn't respond quickly enough")

    if not view.value:
      return await msg.edit("Not unlinking your channel to the global chat.")

    await msg.edit("I can now unlink your channel, unlinking....")

    row = await self.bot.db.fetchrow("SELECT * FROM linked_chat WHERE server_id = $1", ctx.guild.id)

    if not row:
      await ctx.send("Can't unlink from a channel that doesn't exist.")

    await self.bot.db.execute("DELETE FROM linked_chat WHERE server_id = $1", ctx.guild.id)

    await msg.edit("Unlinked channel....")

def setup(bot):
  bot.add_cog(GlobalChat(bot))