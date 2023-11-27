import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import string
import io
import asyncio
import math


class WaveDeformer():

            def transform(self, x, y):
                y = y + 12*math.sin(x/35)
                return x, y

            def transform_rectangle(self, x0, y0, x1, y1):
                return (*self.transform(x0, y0),
                        *self.transform(x0, y1),
                        *self.transform(x1, y1),
                        *self.transform(x1, y0),
                        )

            def getmesh(self, img):
                self.w, self.h = img.size
                gridspace = 20
                target_grid = []
                for x in range(0, self.w, gridspace):
                    for y in range(0, self.h, gridspace):
                        target_grid.append((x, y, 
                                            x + gridspace, y + gridspace))

                source_grid = [self.transform_rectangle(*rect)
                                        for rect in target_grid]

                return [t for t in zip(target_grid, source_grid)]


class captcha(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def getcaptcha(self):
        img = Image.new(size=(350, 100), color=255, mode="L")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font= "Tools/arial.ttf", size= 60)
        randomsix = [random.choice(string.ascii_letters + string.digiits) for i in range(6)]
        code = "".join(randomsix)
        screentext = ' '.join(randomsix)
        W, H = (350, 100)
        w, h = draw.textsize(screentext, font= font)
        draw.text(((W-w)/2,(H-h)/2), screentext, font= font, fill=0)
        img=ImageOps.deform(img, WaveDeformer())

        img.paste(255, [109, 0, 220, 13])
        img.paste(255, [0, 85, 109, 100])
        img.paste(255, [328, 0, 350, 7])
        img.paste(255, [216, 85, 331, 100])

        width = random.randrange(5, 10)
        co1 = random.randrange(25, 88)
        co2 = random.randrange(20, 80)
        co3 = random.randrange(268, 334)
        co4 = random.randrange(38, 60)
        draw = ImageDraw.Draw(img)
        draw.line([(co1, co2), (co3, co4)], width= width, fill=90)


        randomization = .30

        xsize, ysize = img.size
        pix = img.load()
        for x in range(xsize):
            for y in range(ysize):
                perc = random.random()
                if perc < randomization:
                    pix[x, y] = 90
        bytes_array = io.BytesIO()
        img.save(bytes_array, format="png")
        return bytes_array.getvalue(), code
        
    async def captchacheck(self, member, title):
        bytes_array, code = await self.bot.loop.run_in_executor(None, self.getcaptcha)
        file = discord.File(fp=io.BytesIO(bytes_array), filename="captcha.png")
        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.set_image(url="attachment://captcha.png")
        await member.send(embed=embed, file=file)
        def check(message):
            return member.id == message.author.id
        for i in range(3):
            message = await self.bot.wait_for('message', check=check)
            if message.content == code:
                await member.send("Captcha complete, server channels have been unlocked")
                return True
            else:
                await member.send(f"Captcha incomplete, you have {i*-1+2} attempts left")
        await member.send(f"\U0000274c You have run out of attempts. Please try again in 5 seconds")
        return False

    """@commands.command(aliases = ["verify"])
    @commands.dm_only()
    async def captcha(self, ctx):
        while True:
            check = await self.captchacheck(ctx.guild, f"Hello, before you can access the channel to {ctx.guild.name}. We ask you to complete this captcha. Type in the letters shown above.")
            if check:
                verifiedrole = discord.utils.get(ctx.guild.roles, name="Verified")
                if not verifiedrole:
                    overwrites = {
                            ctx.guild.default_role: discord.PermissionOverwrite(
                                view_channel=False,
                                administrator=False,
                                manage_channels=False,
                                connect=False,
                                send_messages=False,
                                read_message_history=False,
                                read_messages=False
                            ),
                            verifiedrole: discord.PermissionOverwrite.from_pair(ctx.guild.default_role.permissions, discord.Permissions.none())
                        }
                    verifiedrole = await ctx.member.guild.create_role(name="Verified", colour=0x2eb918, reason="Captcha - Verified Role", overwrites=overwrites)
                    for channel in member.guild.channels:
                        await channel.edit(overwrites=overwrites, reason="Captcha - Setup")
                    for member in ctx.guild.members:
                        await member.add_roles(verifiedrole, reason="Captcha - Setup")
                else:
                    await ctx.author.add_roles(verifiedrole)
                break
            else:
                await asyncio.sleep(3)
                    """



    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        verifiedrole = discord.utils.get(guild.roles, name="Verified")
        if not verifiedrole:
            overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        view_channel=False,
                        administrator=False,
                        manage_channels=False,
                        connect=False,
                        send_messages=False,
                        read_message_history=False,
                        read_messages=False
                    ),
                    verifiedrole: discord.PermissionOverwrite.from_pair(guild.default_role.permissions, discord.Permissions.none())
                }
            verifiedrole = await guild.create_role(name="Verified", colour=0x2eb918, reason="Captcha - Verified Role", overwrites=overwrites)
            """for channel in guild.channels:
                await channel.edit(overwrites=overwrites, reason="Captcha - Setup")"""
            for member in guild.members:
                await member.add_roles(verifiedrole, reason="Captcha - Setup")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        while True:
            check = await self.captchacheck(member, f"Hello, before you can access the channel to {member.guild.name}. We ask you to complete this captcha. Type in the letters shown above.")
            if check:
                verifiedrole = discord.utils.get(member.guild.roles, name="Verified")
                if not verifiedrole:
                    overwrites = {
                            member.guild.default_role: discord.PermissionOverwrite(
                                view_channel=False,
                                administrator=False,
                                manage_channels=False,
                                connect=False,
                                send_messages=False,
                                read_message_history=False,
                                read_messages=False
                            ),
                            verifiedrole: discord.PermissionOverwrite.from_pair(member.guild.default_role.permissions, discord.Permissions.none())
                        }
                    verifiedrole = await member.guild.create_role(name="Verified", colour=0x2eb918, reason="Captcha - Verified Role", overwrites=overwrites)
                    """for channel in member.guild.channels:
                        await channel.edit(overwrites=overwrites, reason="Captcha - Setup")"""
                    for member in member.guild.members:
                        await member.add_roles(verifiedrole, reason="Captcha - Setup")
                else:
                    await member.add_roles(verifiedrole)
                break
            else:
                await asyncio.sleep(5)
                    
def setup(bot):
    bot.add_cog(captcha(bot))
