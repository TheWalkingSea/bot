import discord
from discord.ext import commands
import aiosqlite as sql
import datetime

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="-", intents=intents)

async def var():
    #await bot.wait_until_ready()
    return await sql.connect("presence.db")
@bot.event
async def on_ready():
    print(f"{bot.user} is ready")

@bot.command()
async def hi(ctx):
    print("i")
    print(ctx.author.activities)

@bot.event
async def on_member_update(before, after):
    print(after.activity)
    activity = after.activity
    if activity.type == discord.ActivityType.playing:
        try:
            if activity.application_id == 867111922549784597:
                return
            else:
                raise AttributeError
        except AttributeError:
            game = activity.name
            query = datetime.datetime.utcnow()
            #time = datetime.datetime.utcnow() - activity.start #Time playing the game
            #print(time)
            await bot.db.execute("DELETE FROM game")
            await bot.db.execute("INSERT INTO game(game, time) VALUES(?, ?)", (game, query))
            await bot.db.commit()
            


bot.db = bot.loop.run_until_complete(var())
bot.run("ODY3MTExOTIyNTQ5Nzg0NTk3.YPcW6A.xXQUuB53_A8zb0S1rw5897ksWQk")