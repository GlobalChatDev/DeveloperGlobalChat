from discord.ext import commands
import discord, random

class Events(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_error(event, *args, **kwargs):
    import traceback
    more_information=os.sys.exc_info()
    error_wanted=traceback.format_exc()
    traceback.print_exc()
    
    #print(more_information[0])

  @commands.Cog.listener()
  async def on_ready(self):
    print("Bot is Ready")
    print(f"Logged in as {self.bot.user}")
    print(f"Id: {self.bot.user.id}")

  @commands.command()
  async def credits(self, ctx):
    await ctx.send("DB provided by and ran by FrostiiWeeb#0400 \nAJTHATKID#0001 for his PFP \nJDJG Inc. Official#3493 as the owner and manager and programmer of the bot as well as FrostiiWeeb#0400 for also programming the bot.")

def setup(bot):
  bot.add_cog(Events(bot))