import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import re
from cogs.utils import utils

class TimeConverter:
    async def convert(self, time):
        try:
            timedic = {**{"s": 1, "seconds": 1, "second": 1}, **{"m": 60, "min": 60, "minutes": 60, "minute": 60}, **{"h": 3600, "hrs": 3600, "hr": 3600, "hour": 3600, "hours": 3600}, **{"d": 86400, "days": 86400, "day": 86400}}
            regexfind = re.findall("[a-zA-Z]+", time)[-1].lower()
            split = time.split(regexfind)[0]
            tempmute = int(split) * timedic[regexfind]
            return tempmute
        except TypeError:
            return int(time)
        except (KeyError, ValueError):
            return False
    
    async def convertback(self, time):
        if time <= 86400:
            minutes = f"{time // 60} minute{'s' if not time//60 == 1 else ''}"
        elif time <= 3600:
            hours = f"{time // 3600} hour{'s' if not time//3600 == 1 else ''}"
        elif time <= 60:
            days = f"time // 86400 {'s' if not time//86400 == 1 else ''}"


class mod(commands.Cog, utils):

    def __init__(self, bot):
        #super().__init__()
        self.bot = bot
        self.rate = 15
        self.per = 8
        self.cd = commands.CooldownMapping.from_cooldown(self.per, self.rate, commands.BucketType.user)
    
    @tasks.loop(minutes=5)
    async def timertask(self):
        users = await self.bot.db.fetch("SELECT * FROM mute")
        for member in users:
            user = member["userid"]
            time = member["time"]
            guild = member["guildid"]
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
        guild = self.bot.get_guild(guildid)
        member = guild.get_member(userid)
        muted = discord.utils.get(guild.roles, name="Muted")
        if not muted:
            permissions = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                connect=False,
                speak=False
            )
            muted = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.edit(overwrites={muted: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                connect=False,
                speak=False
            )})
        await member.remove_roles(muted)
        await self.bot.db.execute("DELETE FROM mute WHERE userid = $1 AND guildid = $2", userid, guildid)
        await member.send(f"You have been unmuted from {guild.name}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cursor = await self.bot.db.fetchrow("SELECT * FROM mute WHERE userid = $1 AND guildid = $2", member.id, member.guild.id)
        if cursor:
            await self.givemute(member.guild, member, "Joined while muted")

    async def givemute(self, guild, member, reason):
        muted = discord.utils.get(guild.roles, name="Muted")
        if not muted:
            permissions = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                connect=False,
                speak=False
            )
            muted = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.edit(overwrites={muted: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                connect=False,
                speak=False
            )})
        await member.add_roles(muted, reason=reason)
        return muted


    async def mute(self, guild, member, time, reason):
        await member.send(f"You have been muted from {guild.name} for {await TimeConverter().convertback(time)}{f': {reason}' if reason else ''}")
        muted = await self.givemute(guild, member, reason)
        if time <= (5*60):
            await asyncio.sleep(time)
            await member.remove_roles(muted)
            await member.send(f"You have been unmuted from {guild.name}")
        else:
            now = datetime.datetime.utcnow()
            time = datetime.timedelta(seconds=time)
            td = (now + time).timestamp()
            cursor = await self.bot.db.fetchrow("SELECT time FROM mute WHERE userid = $1 AND guildid = $2", member.id, guild.id)
            if cursor:
                await self.bot.db.execute("UPDATE mute SET time = $1 WHERE userid = $2 AND guildid = $3", td, member.id, guild.id)
            else:
                await self.bot.db.execute("INSERT INTO mute (userid, time, guildid) VALUES ($1, $2, $3)", member.id, td, guild.id)
                
    def check_permission(ctx):
        return ctx.author.top_role.position < ctx.guild.me.top_role.position and ctx.author is not ctx.guild.owner

    @commands.command(name="mute")
    @commands.has_permissions(manage_messages=True)
    @commands.check(check_permission)
    async def muteuser(self, ctx, member: discord.Member, time: TimeConverter(), reason=None):
        if time == None:
            self.givemute(ctx.guild, member, None)
            await ctx.send(f"{member.mention} has been muted{f': {reason}' if reason else ''}")
        else:
            await self.mute(ctx.guild, member, time, reason)

    @commands.Cog.listener()
    async def on_message(self, message):
        def haspermission(author, guild):
            return author.top_role.position < guild.me.top_role.position and author is not guild.owner
        if message.guild and haspermission(message.author, message.guild):
            # message ratelimit
            bucket = self.cd.get_bucket(message)
            limit = bucket.update_rate_limit()
            self.cd._cooldown.reset()
            def check(msg):
                return msg.author == message.author and (datetime.datetime.utcnow() - msg.created_at).total_seconds() < self.rate
            def cached():
                return len(list(filter(lambda msg: check(msg), self.bot.cached_messages)))
            if limit and cached() > self.per:
                await self.mute(message.guild, message.author, 30*60, f"Spamming in {message.channel.name}")
                await message.channel.send("Woah woah, enter the chill zone there buddy!")
                def check(msg):
                    return message.author.id == msg.author.id
                after = datetime.datetime.utcnow() - datetime.timedelta(seconds=self.rate)
                await message.channel.purge(check=check, limit=None, after=after)


        #await self.bot.process_commands(message) # No need to process commands in a cog

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        await member.send(f"You have been banned from **{ctx.guild.name}**{f': {reason}' if reason else ''}")
        await member.ban(reason=reason)
        await ctx.send(f"You have been banned from **{ctx.guild.name}**{f': {reason}' if reason else ''}")
    
    @commands.command()
    @commands.has_permissions(kick_members=False)
    async def kick(self, ctx, member: discord.Member, reason=None):
        if ctx.author.top_role.position > member.top_role.position:
            await member.send(f"You have been kicked from **{ctx.guild.name}**{f': {reason}' if reason else ''}")
            await member.kick(reason=reason)
            await ctx.send(f"You have been kicked from **{ctx.guild.name}**{f': {reason}' if reason else ''}")
        else:
            raise commands.MissingPermissions


def setup(bot):
    bot.add_cog(mod(bot))