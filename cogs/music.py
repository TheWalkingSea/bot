import discord
from discord.utils import _URL_REGEX
import wavelink
import asyncio
import re
import datetime
from discord.ext import commands



class AlrConnected(commands.CommandError):
    pass


class NoVC(commands.CommandError):
    pass

class QueneEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass


class Quene:
    def __init__(self):
        self._quene = []
        self.position = 0
    
    def add(self, *arg):
        self._quene.extend(arg)

    @property
    def first_track(self):
        if not self._quene:
            raise QueneEmpty
        
        return self._quene[0]
    
    def next_track(self):
        if not self._quene:
            raise QueneEmpty
        self.position += 1
        if self.position > len(self._quene) - 1:
            return None
        
        return self._quene[self.position]


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quene = Quene()
        self.reactions = {
            "\U00000031": 0,
            "\U00000032": 1,
            "\U00000033": 2,
            "\U00000034": 3,
            "\U00000035": 4

}
    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound
        
        if isinstance(tracks, wavelink.TrackPlaylist):
            self.quene.add(*tracks.tracks)

        elif len(tracks) == 1:
            self.quene.add(tracks[0])
            await ctx.send(f"Added {tracks[0].title} to quene.")
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.quene.add(track)
                await ctx.send(f"Added {track.title} to quene.")

        if not self.is_playing:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in self.reactions.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {'e'} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(self.reactions.keys()[:min(len(tracks), len(self.reactions))]):
            await msg.add_reaction(emoji)

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=_check, timeout=60)
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.delete()
            else:
                await msg.delete()
                return tracks[self.reactions[reaction.emoji]]
                

    async def start_playback(self):
        await self.play(self.quene.first_track)
    
    async def advance(self):
        try:
            if (track := self.quene.next_track()) is not None:
                await self.play(track)
        except QueneEmpty:
            pass
    


class music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await asyncio.sleep(5*60)
                player = self.get_player(member.guild.id)
                if player.is_connected and not [m for m in before.channel.members if not m.bot]:
                    await player.destroy()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node '{node.identifier}' ready")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        await payload.player.advance()

    async def is_dm(self, ctx):
        return isinstance(ctx.channel, discord.DMChannel) is False

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "Main Node",
                "region": "us_central"
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, ctx):
        if isinstance(ctx, commands.Context):
            return self.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)
        elif isinstance((ctx, discord.Guild)):
            return self.wavelink.get_player(ctx.guild.id, cls=Player)
    
    @commands.command(aliases=["join", "fuckon"])
    async def connect(self, ctx):
        player = self.get_player(ctx)
        try:
            await player.connect(ctx.author.voice.channel.id)
            msg = await ctx.send(f"Connected to {ctx.author.voice.channel.name}")
        except AttributeError:
            await ctx.send("You have to be connected to a voice channel to use this command")

    @connect.error
    async def on_connect_error(self, ctx, error):
        if isinstance(error, AlrConnected):
            await ctx.send("Already connected to a different voice channel")
        else:
            raise error

    @commands.command(aliases=["leave", "fuckoff"])
    async def disconnect(self, ctx):
        player = self.get_player(ctx)
        if player.is_connected:
            await player.destroy()
        else:
            msg = await ctx.send("I am not connected to a voice channel")

    @commands.command()
    async def play(self, ctx, query):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx.author.voice.channel.id)
        
        if query is None:
            pass
        else:
            query = query.strip("<>")
            if not re.match(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))


def setup(bot):
    bot.add_cog(music(bot))