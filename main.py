import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="-", case_insensitive=True, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"'{bot.user}' is ready")

@bot.command()
async def test(ctx):
    await ctx.send('test')

@bot.command()
async def load(ctx, cog: str):
    if cog.endswith(".py"):
        if cog in os.listdir("./cogs"):
            bot.load_extension(f"cogs.{cog[:-3]}")
        else:
            await ctx.send(f"Failed to find {cog}")

@bot.command()
async def dm(ctx):
    print("e")
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("dm")

@bot.command()
async def unload(ctx, cog: str):
    if cog.endswith(".py"):
        if cog in os.listdir("./cogs"):
            bot.unload_extension(f"cogs.{cog[:-3]}")
        else:
            await ctx.send(f"Failed to find {cog}")

@bot.command()
async def reload(ctx, cog: str):
    if cog.endswith(".py"):
        if cog in os.listdir("./cogs"):
            bot.unload_extension(f"cogs.{cog[:-3]}")
            bot.load_extension(f"cogs.{cog[:-3]}")
        else:
            await ctx.send(f"Failed to find {cog}")

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run("")