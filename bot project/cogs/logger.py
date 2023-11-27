import discord
from discord.ext import commands
import datetime

class logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logcolor = 0x19a4ac
        self.convert = {True: "\U00002705", None: "\U00002b1c", False: "\U0000274c"}
        self.permissions = ["add_reactions", "administrator", "attach_files", "ban_members", "change_nickname", "connect", "create_instant_invite", "deafen_members", "embed_links", "external_emojis", "kick_members", "manage_channels", "manage_emojis", "manage_guild", "manage_messages", "manage_nicknames", "manage_permissions", "manage_roles", "manage_webhooks", "mention_everyone", "move_members", "mute_members", "priority_speaker", "read_message_history", "request_to_speak", "send_messages", "send_tts_messages", "speak", "stream", "use_slash_commands", "use_voice_activation", "view_audit_log", "view_channel", "view_guild_insights"]        
    """
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = None
        for channels in guild.text_channels:
            for name in ["announcements", "general", "rules", "updates", "polls", "off-topic"]:
                for channelupper in [name, name.capitalize()]:
                    if channels.name in channelupper:
                        channel = channels
                        break
        if not channel:
            channel = guild.text_channels[0]
        if channel:
            await channel.send("Thank you for adding me to your server")
"""

    async def log(self, embed):
        chan = self.bot.get_channel(873314770785288192)
        await chan.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        print(after)
        if before.name != after.name: # Name of channel changed
            embed = discord.Embed(title="Role updated", color=0xce9a16)
            embed.add_field(name="**Before**", value=f"**Name**: {before.name}", inline=True)
            embed.add_field(name="**After**", value=f"**Name**: {after.name}", inline=True)
            await self.log(embed)
        elif before.permissions != after.permissions:
            if len(before.roles) > len(after.roles): # Deleted role
                for befrole in before.permissions:
                    try:
                        after.overwrites[befrole] # Try to grab the role
                    except KeyError: # Excepts the added role
                        embed = discord.Embed(title="Text channel updated", description=f"Role {befrole.mention} in {after.mention} added", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
                        await self.log(embed)
            elif len(before.overwrites) < len(after.overwrites): # Added role
                for aftrole in after.overwrites:
                    try:
                        before.overwrites[aftrole] # Try to grab the role
                    except KeyError: # Excepts the deleted role
                        embed = discord.Embed(title="Text channel updated", description=f"Role {aftrole.mention} in {after.mention} deleted", color=discord.Color.red(), timestamp = datetime.datetime.utcnow())
                        await self.log(embed)
            else: # Overwrites were changed
                def permissionsconvert(perm):
                    print(perm)
                    if perm == "create_instant_invite":
                        return "Create invite"
                    else:
                        perm = perm.replace("_", " ")
                        return perm.capitalize()
                role = str()
                perms = str()
                for aftrole in after.overwrites:
                    print(aftrole)
                    brole = before.overwrites[[i for i in before.overwrites if i == aftrole][0]]
                    arole = after.overwrites[aftrole]
                    for permission in self.permissions:
                        aroleperms = getattr(arole, permission)
                        broleperms = getattr(brole, permission)
                        if aroleperms != broleperms:
                            role = aftrole
                            perms += f"{permissionsconvert(permission)}: {self.convert[broleperms]}<:white_arrow_right:873529520529997845>{self.convert[aroleperms]}\n"
                print(role)
                perms = f"Permissions for {role} in {after.mention} updated\n {perms}"
                embed = discord.Embed(title="Text channel updated", description=perms, colour=self.logcolor, timestamp=datetime.datetime.utcnow())
                await self.log(embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name: # Name of channel changed
            embed = discord.Embed(title="Text channel updated", color=0xce9a16)
            embed.add_field(name="**Before**", value=f"**Name**: {before.name}", inline=True)
            embed.add_field(name="**After**", value=f"**Name**: {after.name}", inline=True)
            await self.log(embed)
        elif before.overwrites != after.overwrites:
            if len(before.overwrites) > len(after.overwrites): # Deleted role
                for befrole in before.overwrites:
                    try:
                        after.overwrites[befrole] # Try to grab the role
                    except KeyError: # Excepts the added role
                        embed = discord.Embed(title="Text channel updated", description=f"Role {befrole.mention} in {after.mention} added", color=self.logcolor, timestamp=datetime.datetime.utcnow())
                        await self.log(embed)
            elif len(before.overwrites) < len(after.overwrites): # Added role
                for aftrole in after.overwrites:
                    try:
                        before.overwrites[aftrole] # Try to grab the role
                    except KeyError: # Excepts the added role
                        embed = discord.Embed(title="Text channel updated", description=f"Role {aftrole.mention} in {after.mention} deleted", color=self.logcolor, timestamp = datetime.datetime.utcnow())
                        await self.log(embed)
            else: # Overwrites were changed
                def permissionsconvert(perm):
                    print(perm)
                    if perm == "create_instant_invite":
                        return "Create invite"
                    else:
                        perm = perm.replace("_", " ")
                        return perm.capitalize()
                role = str()
                perms = str()
                for aftrole in after.overwrites:
                    print(aftrole)
                    brole = before.overwrites[[i for i in before.overwrites if i == aftrole][0]]
                    arole = after.overwrites[aftrole]
                    for permission in self.permissions:
                        aroleperms = getattr(arole, permission)
                        broleperms = getattr(brole, permission)
                        if aroleperms != broleperms:
                            role = aftrole
                            perms += f"{permissionsconvert(permission)}: {self.convert[broleperms]}<:white_arrow_right:873529520529997845>{self.convert[aroleperms]}\n"
                print(role)
                perms = f"Permissions for {role} in {after.mention} updated\n {perms}"
                embed = discord.Embed(title="Text channel updated", description=perms, colour=self.logcolor, timestamp=datetime.datetime.utcnow())
                await self.log(embed)
                        


def setup(bot):
    bot.add_cog(logger(bot))