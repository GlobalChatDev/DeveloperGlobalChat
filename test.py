from discord.ext.customs import commands
import discord, asyncio

bot = commands.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
	while True:
		await (await bot.fetch_channel(939951130023182397)).send("L <@480773589411299328>")
		await asyncio.sleep(1)

bot.run("NzQ3MDE0MjQwNjMxNjUyMzgz.X0ItOQ.lIg96D4Ni2x6bZnELhDZt8zmZvI")