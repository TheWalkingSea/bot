import discord
from discord.ext import commands
import cogs.utils
import datetime


class clsprofanity(commands.Cog, cogs.utils.utils):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.teal = 0x19a4ac
        def badwords():
            with open("badwords.txt", "r") as txt:
                return [i.replace("\n", "") for i in txt.readlines()]
        self.badwords = badwords()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        cursor = await self.bot.db.fetchrow("SELECT words FROM blockedwords WHERE guildid = $1", message.guild.id)
        if self.emptycheck(cursor):
            if message.content in self.badwords or message.content in cursor[0]:
                await message.delete()
                await message.channel.send("HEY! Don't say that")
        else:
            if message.content in self.badwords:
                await message.delete()
                await message.channel.send("HEY! Don't say that")


    @commands.group(invoke_without_command=True)
    async def profanity(self, ctx):
        cursor = await self.bot.db.fetchrow("SELECT words FROM blockedwords WHERE guildid = $1", ctx.guild.id)
        embed = discord.Embed(title="Profanity Information", color=self.teal)
        if self.emptycheck(cursor):
            embed.add_field(name="Added words", value=" | ".join(cursor[0]))
        await ctx.send(embed=embed)

    @profanity.command(help="Adds a word to the profanity list")
    async def add(self, ctx, *arg):
        output = list()
        for addedword in arg:
            if len(addedword) < 20:
                words = await self.bot.db.fetchrow("SELECT words FROM blockedwords WHERE guildid = $1", ctx.guild.id)
                if words:
                    words = words[0]
                    if words:
                        if addedword not in words:
                            if addedword in words or addedword in self.badwords:
                                output.append(f"{addedword}` is already in the profanity list")
                            else:
                                words.append(addedword)
                                await self.bot.db.execute("UPDATE blockedwords SET words = $1 WHERE guildid = $2", set(words), ctx.guild.id)
                                output.append(f"Added `{addedword}` to the profanity list")
                        else:
                            output.append(f"`{addedword}` is already in the profanity list")
                    else:
                        await self.bot.db.execute("UPDATE blockedwords SET words = $1 WHERE guildid = $2", {addedword}, ctx.guild.id)
                        output.append(f"Added `{addedword}` to the profanity list")
                else:
                    await self.bot.db.execute("INSERT INTO blockedwords (words, guildid) VALUES ($1, $2)", {addedword}, ctx.guild.id)
                    output.append(f"Added `{addedword}` to the profanity list")
            else:
                output.append("Cannot block words longer than 20 characters")
        embed = discord.Embed(title="Added words", description="\n".join(output), colour=self.teal)
        await ctx.send(embed=embed)
    
    @profanity.command(help="Removes word from the profanity list")
    async def remove(self, ctx, word):
        cursor = await self.bot.db.fetchrow("SELECT words FROM blockedwords WHERE guildid = $1", ctx.guild.id)
        if self.emptycheck(cursor):
            cursor = cursor[0]
            if word in cursor:
                cursor.remove(word)
                await self.bot.db.execute("UPDATE blockedwords SET words = $1 WHERE guildid = $2", cursor, ctx.guild.id)
                await self.blue(ctx, f"`{word}` was removed from the profanity list")
            else:
                await self.error(ctx, f"`{word}` is not in the profanity list")
        else:
            await self.error(ctx, f"`{word}` is not in the profanity list")


def setup(bot):
    bot.add_cog(clsprofanity(bot))