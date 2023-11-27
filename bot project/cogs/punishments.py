import discord
from discord.ext import commands, tasks
import datetime
from cogs.mod import TimeConverter
from cogs.utils import utils
import asyncio

class punishments(commands.Cog, TimeConverter, utils):
    def __init__(self, bot):
        self.bot = bot
        self.orange = 0xe48c21
        self.x = "\U0000274c"
        self.check = "\U00002705"
        def badwords():
            with open("badwords.txt", "r") as txt:
                return [i.replace("\n", "") for i in txt.readlines()]
        self.badwords = badwords()

    @tasks.loop(minutes=5)
    async def cooldown(self):
        users = await self.bot.db.fetch("SELECT cooldown FROM profanity_punish")
        for member in users:
            if member['cooldown']:
                user = member["userid"]
                time = member["cooldown"]
                guild = member["guildid"]
                if not time:
                    now = datetime.datetime.utcnow()
                    time = datetime.datetime.fromtimestamp(time)
                    td = (now - time).total_seconds()
                    if td < -5*60:
                        pass
                    else:
                        await self.bot.loop.create_task(self.belowfivetimer(td, guild, user))

    async def belowfivetimer(self, time, guildid, userid):
        if time < 0:
            await asyncio.sleep(time*-1)  # Convert the time left from a negative to postive time
        await self.bot.db.execute("DELETE FROM profanity_punish WHERE userid = $1 AND guildid = $2", userid, guildid)
                
    @commands.Cog.listener()
    async def on_message(self, message):
        badwords = await self.bot.db.fetch("SELECT words FROM blockedwords WHERE guildid = $1", message.guild.id)
        profanity_words = self.badwords
        if badwords: profanity_words = badwords + self.badwords
        punishments = await self.bot.db.fetch("SELECT punishments FROM profanity WHERE guildid = $1 ORDER BY index", message.guild.id)
        if punishments: # dont use empty check
            [i[index] = i[0] for index, i in enumerate(punishments)]
            print(punishments)

            




    async def convert(self, args):
        converted = list()
        fields = list()
        for index, arg in enumerate(args):
            if arg in ["ban", "mute", "kick", "warn"]:
                converted.append(arg)
                fields.append(f"{index+1}: `{arg}` was added as a punishment")
            elif arg == "default":
                return False
            else:
                seconds = await super().convert(arg)
                if seconds:
                    converted.append(str(seconds))
                    fields.append(f"{index+1}: `{arg}` mute was added as a punishment")
                else:
                    fields.append(f"{index+1}: `{arg}` is an invalid arguement")

        return converted, fields

    async def executesql(self, ctx, table, args):
        args, fields = await self.convert(args)
        if args:
            overwriteembed = discord.Embed(title=f"{table.capitalize()}'s overwrites", description="\n".join(fields), color=discord.Color.blue())
            punishments = await self.bot.db.fetch(f"SELECT punishments FROM {table} WHERE guildid = $1", ctx.guild.id)
            if self.emptycheck(punishments):
                embed = discord.Embed(description=f"Are you sure you want to overwrite permissions for `{table}`", color=self.orange)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction(self.check)
                await msg.add_reaction(self.x)
                def check(reaction, user):
                    return user.id == ctx.author.id and reaction.message == msg
                try:
                    cancelembed = discord.Embed(description=f"Cancelled `{table}` overwrite", color=discord.Color.red())
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                    if str(reaction.emoji) == self.check:
                        await self.bot.db.execute(f"DELETE FROM {table} WHERE guildid = $1", ctx.guild.id)
                        for index, arg in enumerate(args):
                            await self.bot.db.execute(f"INSERT INTO {table} (guildid, punishments, index) VALUES ($1, $2, $3)", ctx.guild.id, arg, index)
                        await ctx.send(embed=overwriteembed)
                    elif str(reaction.emoji) == self.x:
                        await ctx.send(embed=cancelembed)
                except asyncio.TimeoutError:
                    await ctx.send(embed=cancelembed)
            else:
                for index, arg in enumerate(args):
                    await self.bot.db.execute(f"INSERT INTO {table} (guildid, punishments, index) VALUES ($1, $2, $3)", ctx.guild.id, arg, index)
                await ctx.send(embed=overwriteembed)
                
        else:
            embed = discord.Embed(description=f"Are you sure you would like to set `{table}` to default punishments?", color=self.orange)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(self.check)
            await msg.add_reaction(self.x)
            def check(reaction, user):
                return user.id == ctx.author.id and reaction.message == msg
            cancelembed = discord.Embed(description="Cancelled default overwrite", color=discord.Color.red())
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                if str(reaction.emoji) == self.check:
                    await self.bot.db.execute(f"DELETE FROM {table} WHERE guildid = $1", ctx.guild.id)
                    embed = self.blue(ctx, f"Overwrited `{table}` to default punishments")
                    await ctx.send(embed=embed)
                elif str(reaction.emoji) == self.x:
                    await ctx.send(embed=cancelembed)
            except asyncio.TimeoutError:
                await ctx.send(embed=cancelembed)

    @commands.group(invoke_without_command=True)
    async def punish(self, ctx):
        pass

    @punish.command()
    async def userpunish(self, ctx, member: discord.Member):
        await self.punishuser(ctx, "profanity_punish", member)

    @punish.command()
    async def getpun(self, ctx, member: discord.Member):
        e = await self.getpunish(ctx, "profanity", member, "reason")
        print(e)
        em = discord.Embed(title=e, description="desc")
        await ctx.send(embed=em)


    @punish.group(help="Sets a punishments list for auto-mod to ban")
    async def set(self, ctx):
        pass


    @set.command(help="Sets punishments for when auto-mod detects spam")
    async def spam(self, ctx, *punishments):
        await self.executesql(ctx, "spam", punishments)
    
    @set.command(help="Sets punishments for when auto-mod detects self-advertising")
    async def advertising(self, ctx, *punishments):
        await self.executesql(ctx, "advertising", punishments)
    
    @set.command(help="Sets punishments for when auto-mod detects profanity")
    async def profanity(self, ctx, *punishments):
        await self.executesql(ctx, "profanity", punishments)

    @set.command(help="Sets punishments for when auto-mod detects mass-pings")
    async def massping(self, ctx, *punishments):
        await self.executesql(ctx, "massping", punishments)

def setup(bot):
    bot.add_cog(punishments(bot))