import discord
from discord.ext import commands
import asyncio
import datetime
import re

def check_permission(ctx):
    return ctx.author.top_role.position < ctx.guild.me.top_role.position and ctx.author is not ctx.guild.owner


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

class mod(TimeConverter):

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


class utils(mod):
    def __init__(self):
        pass

    async def error(self, ctx, error):
        await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=error), allowed_mentions=discord.AllowedMentions.none())
        
    async def blue(self, ctx, description):
        await ctx.send(embed=discord.Embed(color=discord.Color.blue(), description=description, allowed_mentions=discord.AllowedMentions.none()))
    
    def emptycheck(self, row):
        if row:
            if row[0]:
                return True
        return False

    async def profansetpunish(self, context, member):
        if type(context) == commands.context:
            guildid = context.guild.id
            channel = context
        else:
            guildid = context.guild.id
            channel = context.channel
        cursor = await self.bot.db.fetchrow("SELECT level FROM profanity_punish WHERE userid = $1 AND guildid = $2", member.id, guildid)
        if self.emptycheck(cursor):
            cursor = cursor[0]
            cursor += 1
            await self.bot.db.execute("UPDATE profanity_punish SET level = $1, cooldown = $2 WHERE userid = $3 AND guildid = $4", cursor, 86400, member.id, guildid)
        else:
            await self.bot.db.execute("INSERT INTO profanity_punish (guildid, userid, level, cooldown) VALUES ($1, $2, $3, $4)", guildid, member.id, 0, 86400)
    
    async def oncooldown(self, context, member):
        guild = context.guild
        guildid = context.guild.id
        if type(context) == commands.context:
            channel = context
        else:
            channel = context.channel   
        row = await self.bot.db.execute("SELECT cooldown FROM profanity_punish WHERE userid = $1 AND guildid = $2", member.id, guildid)
        if row:
            if row[0]:
                return False
        return True



    async def profanpunish(self, context, member, reason):
        guild = context.guild
        guildid = context.guild.id
        if type(context) == commands.context:
            channel = context
        else:
            channel = context.channel
        
        usercursor = await self.bot.db.fetchrow("SELECT level FROM profanity_punish WHERE guildid = $1 AND userid = $2", guildid, member.id)
        if self.emptycheck(usercursor):
            tblcursor = await self.bot.db.fetch("SELECT punishments FROM profanity WHERE guildid = $1 ORDER BY index", guildid)
            if self.emptycheck(tblcursor):
                punishment = tblcursor[usercursor[0]][0]
                await self.punishuser(punishment, guild, member, reason)
                return punishment
            else:
                await self.bot.db.execute("DELETE FROM profanity_punish WHERE guildid = $1", guildid)
                return None
        else:
            return None

    async def setpunishuser(self, context, table, member):
        if type(context) == commands.context:
            guildid = context.guild.id
            channel = context
        else:
            guildid = context.guild.id
            channel = context.channel
        cursor = await self.bot.db.fetchrow(f"SELECT level FROM {table} WHERE userid = $1 AND guildid = $2", member.id, guildid)
        if self.emptycheck(cursor):
            cursor = cursor[0]
            cursor += 1
            await self.bot.db.execute(f"UPDATE {table} SET level = $1 WHERE userid = $2 AND guildid = $3", cursor, member.id, guildid)
        else:
            await self.bot.db.execute(f"INSERT INTO {table} (guildid, userid, level) VALUES ($1, $2, $3)", guildid, member.id, 0)
    
    async def punish(self, context, table, member, reason):
        punishtbl = table # Stores the punishments for to supply punishusers
        punishusers = "%s_punish" % (table) # stores the users punishment level
        guild = context.guild
        guildid = context.guild.id
        if type(context) == commands.context:
            channel = context
        else:
            channel = context.channel
        
        usercursor = await self.bot.db.fetchrow(f"SELECT level FROM {punishusers} WHERE guildid = $1 AND userid = $2", guildid, member.id)
        if self.emptycheck(usercursor):
            tblcursor = await self.bot.db.fetch(f"SELECT punishments FROM {punishtbl} WHERE guildid = $1 ORDER BY index", guildid)
            if tblcursor:
                punishment = tblcursor[usercursor[0]][0]
                await self.punishuser(punishment, guild, member, reason)
                return punishment
            else:
                await self.bot.db.execute(f"DELETE FROM {punishusers} WHERE guildid = $1", guildid)
                return None
        else:
            return None

    async def punishuser(self, punishment, guild, member, reason):
        try:
            punishment = int(punishment)
            await self.mute(guild, member, punishment, reason)
        except ValueError:
            if punishment == "kick":
                await member.kick(reason=reason)
            elif punishment == "ban":
                await member.ban(reason=reason)
            elif punishment == "mute":
                await self.givemute(guild, member.id, reason)
            else:
                print("Error with punishuser")
                return None
            
    