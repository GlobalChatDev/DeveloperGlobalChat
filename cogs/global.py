from discord.ext import commands

class GlobalChat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.Cog.listener()
  async def on_message(self, message):
    return message


def setup(bot):
  bot.add_cog(GlobalChat(bot))