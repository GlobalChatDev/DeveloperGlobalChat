from discord.ext import commands
import utils
import discord, re, random, asyncio
from better_profanity import profanity
import traceback

class GlobalChat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._cd = commands.CooldownMapping.from_cooldown(3.0, 15.0, commands.BucketType.user)

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error

  async def message_converter(self, message : discord.Message):
    args = message.content
    args = args or "Test Content"
    
    try:
      for x in re.findall(r'<@!?([0-9]{15,20})>', args):
        user = await self.bot.try_user(int(x))
        
        print(f"{re.match(rf'<@!?({x})>', args).group()}")

        args = args.replace(f"{re.match(rf'<@!?({x})>', args).group()}", f"@{user}")
        #fix issue

    except Exception as e:
      traceback.print_exc()
      print(f"error occured as {e}.")

    ctx = await self.bot.get_context(message)
    args = await commands.clean_content().convert(ctx, args)
    args = profanity.censor(args, censor_char = "#")
    return args

  @commands.Cog.listener()
  async def on_message(self, message):
    
    #find out how to edit edited messages or who deleted them to enable syncing.

    ctx = await self.bot.get_context(message)
    if message.channel.id in self.bot.linked_channels and not message.author.bot and not ctx.valid and not ctx.prefix:

      bucket = self._cd.get_bucket(message)
      retry_after = bucket.update_rate_limit()

      if retry_after: 
        await asyncio.sleep(15.0)

      #slows down spam, now it just well wait 15 seconds if cooldown is triggered.
      
      args = await self.message_converter(message)

      if len(args) >= 6000:
        args = "Message Too Big, Author will be notifited"
        
        await ctx.send(f"{ctx.author.mention}, please use content less than 6000, either using a pastebin or something else, thanks")

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
    collection = self.bot.db['link']

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

    query = {
      "server_id": ctx.guild.id
    }

    if collection.count_documents(query) != 0:
      for data in collection.find(query):
        if ctx.channel.id == data["linked_chat"]:
          return await ctx.send("This channel is already linked.")
          
      await ctx.send("you already linked a channel, we'll update it right now.")

      payload = {
        "set": {
          "server_id": ctx.guild.id,
          "linked_chat": ctx.channel.id
        }
      }

      collection.update_one(query, payload)

    else:
      payload = {
        "server_id": ctx.guild.id,
        "linked_chat": ctx.channel.id
      }
      
      collection.insert_one(payload)
    self.bot.linked_channels.append(ctx.channel.id)
    await msg.edit("Linked channel :D")
    

  @commands.has_permissions(manage_messages = True)
  @commands.command(brief = "Adds yourself to the global chat with other developers", aliases = ["removelink"])
  async def remove_link(self, ctx):
    collection = self.bot.db['link']

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

    query = {
      "server_id": ctx.guild.id
    }

    if collection.count_documents(query) == 0:
      return await ctx.send("Can't unlink from a channel that doesn't exist.")
    
    for data in collection.find(query):
      self.bot.linked_channels.remove(data['linked_chat'])

      collection.deletekno_one(query)

      await msg.edit("Unlinked channel....")

  
  @commands.command(brief = "gives you an invite to invite the bot", aliases = ["inv"])
  async def invite(self, ctx):

    minimial_invite = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 70635073))

    embed = discord.Embed(title = "Invite link:", color = random.randint(0, 16777215))
    embed.add_field(name = "Minimial permisions", value = f"{ minimial_invite}")

    embed.set_thumbnail(url = self.bot.user.display_avatar.url)
    embed.set_footer(text = f"not all features may work if you invite with minimal perms, if you invite with 0 make sure these permissions are in a Bots/Bot role.")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = f"{self.bot.user.name}'s Minimial Permisions Invite", url = minimial_invite, style = discord.ButtonStyle.link))

    await ctx.send(embed = embed, view = view)


  @commands.command(brief = "rules")
  async def rules(self, ctx):
    await ctx.send("Please ask JDJG what the rules are.")

    #move the rules into here.

  @commands.command()
  async def credits(self, ctx):
    await ctx.send("DB provided by and ran by FrostiiWeeb#0400 \nAJTHATKID#0001 for his PFP \nJDJG Inc. Official#3493 as the owner and manager and programmer of the bot as well as FrostiiWeeb#0400 for also programming the bot. \nEndlessVortex#4547 and BenitzCoding#1317 Thank You!")

def setup(bot):
  bot.add_cog(GlobalChat(bot))