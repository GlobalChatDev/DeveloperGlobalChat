from discord.ext import commands
import discord, random

class Events(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_error(event,*args,**kwargs):
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

def setup(bot):
  bot.add_cog(Events(bot))