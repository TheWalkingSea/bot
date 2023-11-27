import discord
from discord.ext import commands
import os
from asyncpg.pool import create_pool
from cogs.mod import mod
import datetime
from cogs.punishments import punishments

bot = commands.Bot(command_prefix="-", intents=discord.Intents().all())


async def db_pool():
    bot.db = await create_pool(database="bot", user="postgres", password="n3PbL#v%7tp!DF$t")

async def create_tables():
    await bot.db.execute("CREATE TABLE IF NOT EXISTS mute (userid BIGINT NOT NULL, time BIGINT NOT NULL, guildid BIGINT NOT NULL)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS profanity (exceptwords CHAR[], addwords CHAR[], exceptusers CHAR[], guildid BIGINT NOT NULL)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS spam (guildid BIGINT, punishments TEXT[])")



class HelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blue())
        for cog, commands in mapping.items():
            filter = await self.filter_commands(commands, sort=True)
            signatures = [self.get_command_signature(i) for i in filter]
            if signatures:
                cog = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=f"__{cog.capitalize()}__", value="\n".join(signatures), inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(title=f"{command.qualified_name.capitalize()} Help")
        embed.add_field(name=command.help, value=self.get_command_signature(command))
        aliases = command.aliases
        if aliases:
            embed.add_field(name=aliases, value=", ".join(aliases))
        destination = self.get_destination()
        await destination.send(embed=embed)
        
    async def send_group_help(self, group):
        embed = discord.Embed(title=f"{group.qualified_name.capitalize()} Help")
        for command in group.commands:
            embed.add_field(name=command.help, value=self.get_command_signature(command), inline=False)
        destination = self.get_destination()
        await destination.send(embed=embed)

bot.help_command = HelpCommand()
@bot.command()
@commands.is_owner()
async def close(ctx):
    await bot.close()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")
    mod.timertask.start(mod(bot))
    punishments.cooldown.start(punishments(bot))

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="Error", description=error, color=discord.Color.red())
    await ctx.send(embed=embed)
    raise error

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename not in ["utils.py"]:
        bot.load_extension(f"cogs.{filename[:-3]}")


bot.loop.run_until_complete(db_pool())
bot.loop.run_until_complete(create_tables())
bot.run("ODU1MTkwNDM0Mjc5MTk0NjM1.YMu4KA.OnNRqiY7irzeHO1VYxgOT4PqVIQ")