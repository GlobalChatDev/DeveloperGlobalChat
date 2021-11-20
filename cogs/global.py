from discord.ext import commands
import utils

class GlobalChat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error

  @commands.Cog.listener()
  async def on_message(self, message):
    return message

  @commands.has_permissions(manage_messages = True)
  @commands.command(brief = "Adds yourself to the global chat with other developers", aliases = ["addlink"])
  async def add_link(self, ctx):

    view = utils.BasicButtons(ctx, timeout = 30.0)

    msg = await ctx.send("This adds a link to the current channel. Do you want to do this?", view = view)

    await view.wait()

    if view.value is None:
      return await msg.edit("you didn't respond quickly enough")

    if not view.value:
      return await msg.edit("Not linking your channel to the global chat.")

    await msg.edit("I can now link your channel.")

  @commands.has_permissions(manage_messages = True)
  @commands.command(brief = "Adds yourself to the global chat with other developers", aliases = ["removelink"])
  async def remove_link(self, ctx):

    view = utils.BasicButtons(ctx, timeout = 30.0)

    msg = await ctx.send("This remove a link to the current channel. Do you want to do this?", view = view)

    await view.wait()

    if view.value is None:
      return await msg.edit("you didn't respond quickly enough")

    if not view.value:
      return await msg.edit("Not unlinking your channel to the global chat.")

    await msg.edit("I can now unlink your channel.")


def setup(bot):
  bot.add_cog(GlobalChat(bot))