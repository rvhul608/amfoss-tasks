import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import aiohttp
import os

load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

GUILD_ID = discord.Object(id=929380631002112071)

class musicAPI(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = {}
        self.session = None

    async def setup_hook(self): 
        self.session = aiohttp.ClientSession()
        await self.tree.sync(guild=GUILD_ID)
    
    async def close(self):
        await self.session.close()
        await super().close()

    async def on_ready(self):
        print(f"logged on as {self.user}")
        await self.tree.sync(guild=GUILD_ID)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('hello'):
            await message.channel.send("Hello")
        await self.process_commands(message)
    
    async def track_info(self, track: str, artist: str):
        url = f"https://musicbrainz.org/ws/2/recording/?query=recording:{track} AND artist:{artist}&fmt=json"
        headers = {"User-Agent": "lyric_lounge/1.0 (rahulrohitnair@gmail.com)"}
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

    async def lyrics(self, track: str, artist: str):
        url = "https://lrclib.net/api/get"
        params = {"track_name": track, "artist_name": artist}
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return None

    def manage_playlist(self, user_id: int, action: str, song: str):
        if user_id not in self.playlists:
            self.playlists[user_id] = []
        if action == "add" and song:
            self.playlists[user_id].append(song)
            return f"Added {song} to your playlist."
        elif action == "remove" and song:
            if song in self.playlists[user_id]:
                self.playlists[user_id].remove(song)
                return f"Removed {song} from your playlist."
            else:
                return f"{song} not found in your playlist."
        elif action == "view":
            if self.playlists[user_id]:
                return self.playlists[user_id]
            return []
        elif action == "clear":
            self.playlists[user_id].clear()
            return "Your playlist has been cleared."
        return "Invalid action. Please use add, remove, view, or clear."

    async def trending(self):
        url = "https://api.deezer.com/chart/0/tracks"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def mood(self, tag: str):
        url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&api_key={os.getenv('LASTFM_KEY')}&format=json"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None


intents = discord.Intents.all()
intents.message_content = True 
bot = musicAPI(command_prefix='!', intents=intents)


@bot.tree.command(name="helloo", description="Says Hello!", guild=GUILD_ID)
async def sayhello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there!")


@bot.tree.command(name="printer", description="prints the user input !", guild=GUILD_ID)
async def printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)


@bot.tree.command(name="track", description="get track info", guild=GUILD_ID)
async def track(interaction: discord.Interaction, song: str, artist: str):
    await interaction.response.defer()
    data = await bot.track_info(song, artist)
    if data and data.get("recordings"):
        recording = data['recordings'][0]
        title = recording.get('title', 'N/A')
        duration = int(recording.get('length', 0)) // 1000 if recording.get("length") else 'N/A'
        embed = discord.Embed(title="Track Info", color=discord.Color.blue())
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Artist", value=artist, inline=False)
        embed.add_field(name="Duration", value=f"{duration} sec", inline=True)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("No data found for the given track/artist.")


@bot.tree.command(name="lyrics", description="get lyrics of a song", guild=GUILD_ID)
async def get_lyrics(interaction: discord.Interaction, track: str, artist: str):
    result = await bot.lyrics(track, artist)
    if result:
        lyrics = result.get("syncedLyrics") or result.get("plainLyrics") or "Lyrics not found."
        if len(lyrics) > 1900:  # Discord has a 2000 character limit
            await interaction.response.send_message("Lyrics too long, sending as file...")
            with open("lyrics.txt", "w", encoding="utf-8") as f:
                f.write(lyrics)
            await interaction.followup.send(file=discord.File("lyrics.txt"))
        else:
            await interaction.response.send_message(f"Lyrics for **{track}** by **{artist}**:\n{lyrics}")
    else:
        await interaction.response.send_message("Lyrics not found.")


@bot.tree.command(name="playlist", description="manage your playlist", guild=GUILD_ID)
async def playlist(interaction: discord.Interaction, action: str, song: str = None):
    user_id = interaction.user.id
    result = bot.manage_playlist(user_id, action, song)
    if isinstance(result, list):
        if not result:
            await interaction.response.send_message("Your playlist is empty.")
        else:
            embed = discord.Embed(title="Your Playlist", color=discord.Color.green())
            for i, track in enumerate(result, start=1):
                embed.add_field(name=f"{i}.", value=track, inline=False)
            await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(result)


@bot.tree.command(name="trending", description="get trending songs", guild=GUILD_ID)
async def trending(interaction: discord.Interaction):
    data = await bot.trending()
    if data and data.get("data"):
        embed = discord.Embed(title="Trending Songs", color=discord.Color.purple())
        for i, track in enumerate(data['data'][:10], start=1):
            embed.add_field(name=f"{i}. {track['title']}", value=f"Artist: {track['artist']['name']}", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("No trending songs found.")


@bot.tree.command(name="mood", description="get songs by mood", guild=GUILD_ID)
async def mood(interaction: discord.Interaction, tag: str):
    data = await bot.mood(tag)
    if data and data.get("tracks", {}).get("track"):
        embed = discord.Embed(title=f"Top Tracks for Mood: {tag}", color=discord.Color.orange())
        for i, track in enumerate(data['tracks']['track'][:10], start=1):
            embed.add_field(name=f"{i}. {track['name']}", value=f"Artist: {track['artist']['name']}", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"No tracks found for mood: {tag}.")
@bot.tree.command(name="help", description="get a list of commands", guild=GUILD_ID)
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Music Bot Commands", color=discord.Color.gold())
    embed.add_field(name="/lyrics <song> <artist>", value="Fetches and displays song lyrics.", inline=False)
    embed.add_field(name="/track <song> <artist>", value="Gets detailed track information including album, duration, and tags.", inline=False)
    embed.add_field(name="/playlist [add/remove/view/clear] [song]", value="Manage your personal playlist.", inline=False)
    embed.add_field(name="/trending", value="Shows the top 10 trending songs from Deezer.", inline=False)
    embed.add_field(name="/mood <tag>", value="Suggests songs based on mood/genre using Last.fm.", inline=False)
    embed.add_field(name="/help", value="Displays this help message.", inline=False)

    await interaction.response.send_message(embed=embed)


bot.run(os.getenv('DISCORD_TOKEN'))
