import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final, Literal
import asyncio
import yt_dlp
from urllib import parse, request
from pathlib import Path
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).parent
join_gif_path = BASE_DIR / 'resources' / 'join.gif'

load_dotenv()
BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN")
USER_ID: Final[int] = int(os.getenv("USER_ID"))
TEST_GUILD: Final[discord.Object] = discord.Object(id=int(os.getenv("TEST_GUILD")))
GOOGLE_KEY: Final[str] = os.getenv("GOOGLE_KEY")
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
EMBED_BLUE = 0x2c76dd
EMBED_RED = 0xdf1141
EMBED_GREEN = 0x0eaa51

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=GOOGLE_KEY)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        
        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.disconnecting = {}
        self.vc = {}

    async def setup_hook(self):
        self.tree.clear_commands(guild=TEST_GUILD)
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)
        print('Bot synced.')

def search_YT(search: str):
    searchResponse = youtube.search().list(
        part = 'snippet',
        maxResults = 5,
        q = search,
        regionCode = 'us',
        relevanceLanguage = 'en',
        type = 'video'
    ).execute()

    videoIds = []

    for entry in searchResponse['items']:
        videoIds.append(entry['id'].get('videoId'))

    return videoIds


def get_YT_title(url):
    html_content = request.urlopen(url).read().decode()
    title = re.search(r'<title>(.*?) - YouTube</title>', html_content)
    return title.group(1) if title else "Title not found"

def generate_now_playing_embed(interaction: discord.Interaction, song):
    title = song['title']
    link = song['link']
    thumbnail = song['thumbnail']
    author = interaction.user
    avatar = author.avatar.url

    embed = discord.Embed(
        title='Now Playing',
        description=f'[{title}]({link})\n\nSong added by: {author.mention}',
        colour=EMBED_GREEN
    )
    embed.set_thumbnail(url=thumbnail)
    return embed

def generate_add_to_queue_embed(interaction: discord.Interaction, song):
    title = song['title']
    link = song['link']
    thumbnail = song['thumbnail']
    author = interaction.user
    avatar = author.avatar.url

    embed = discord.Embed(
        title='Added to Queue',
        description=f'[{title}]({link})\n\nSong added by: {author.mention}',
        colour=EMBED_BLUE
    )
    embed.set_thumbnail(url=thumbnail)
    return embed

def reset_music_variables(client: MyClient, id):
    client.is_playing[id] = client.is_paused[id] = False
    client.musicQueue[id] = []
    client.queueIndex[id] = 0


'''Beginning of bot'''
def run_bot():
    intents = discord.Intents.all()

    client = MyClient(intents=intents)

    ytdl_options: Final[dict] = {'format': 'bestaudio/best', 'noplaylist': 'True'}
    ffmpeg_options: Final[dict] = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ytdl = yt_dlp.YoutubeDL(ytdl_options)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        for guild in client.guilds:
            id = int(guild.id)
            client.musicQueue[id] = []
            client.queueIndex[id] = 0
            client.is_playing[id] = client.is_paused[id] = False
            client.vc[id] = None
        print('Bot is running...')

    @client.event
    async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        id = int(member.guild.id)
        if member.id != client.user.id and before.channel != None and after.channel != before.channel:
            await asyncio.sleep(5)
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == client.user.id and client.vc[id].is_connected():
                reset_music_variables(client)
                await client.vc[id].disconnect()

    
    async def join_voice(interaction: discord.Interaction, channel: discord.VoiceChannel):
        id = int(interaction.guild_id)
        if client.vc[id] == None or not client.vc[id].is_connected():
            client.vc[id] = await channel.connect()

            if client.vc[id] == None:
                await interaction.response.send_message('Could not connect to the voice channel.')
                return
        elif interaction.user.voice.channel == client.vc[id].channel:
            return
        else:
            await client.vc[id].move_to(channel)

    def extract_music_info(url):
        try:
            info = ytdl.extract_info(url, download=False)
        except:
            return False
        
        if ('YouTube' in url):
            return {
                'link': 'https://www.youtube.com/watch?v=' + url,
                'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
                'source': info.get('url'),
                'title': info['title']
            }
        else:
            return {
                'link': url,
                'thumbnail': info.get('thumbnail'),
                'source': info.get('url'),
                'title': info['title']
            }

    @client.event
    async def on_guild_join(guild):
        channel = discord.utils.find(lambda c: 'general' in c.name.lower(), guild.text_channels)
        try:
            await channel.send('The bot has joined.', file=discord.File(join_gif_path))
        except Exception as e:
            print(e)

    @client.tree.command(name='hello', description='Command that returns "Hello!"')
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message('Hello!')

    @client.tree.command(name='play', description='Play a song from YouTube or SoundCloud.')
    async def play(interaction: discord.Interaction, source: Literal['YouTube','SoundCloud','URL'], query: str):
        try:
            userChannel = interaction.user.voice.channel
        except:
            await interaction.response.send_message('You need to be connected to a voice channel.')
            return

        await interaction.response.defer()

        if source == 'YouTube':
            input = await resultsYT(interaction, query)
            if input == None:
                await interaction.channel.send('Action canceled or could not fetch results.')
                return
            song = extract_music_info(input)
            await play_song(interaction, song, userChannel)
        elif source == 'SoundCloud':
            await interaction.followup.send('Not Implemented.')
        elif source == 'URL':
            try:
                query_info = extract_music_info(query)
            except:
                await interaction.followup.send('Invalid URL.')
                return
            await play_song(interaction, query_info, userChannel)
        else:
            await interaction.followup.send('Invalid source. Select a valid source.')

    def play_next(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        if not client.is_playing[id] or client.disconnecting[id]:
            return
        if client.queueIndex[id] + 1 < len(client.musicQueue[id]):
            client.is_playing[id] = True
            client.queueIndex[id] += 1

            song = client.musicQueue[id][client.queueIndex[id]][0]
            message = generate_now_playing_embed(interaction, song)
            coro = interaction.channel.send(embed=message)
            fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
            try:
                fut.result()
            except:
                pass

            client.vc[id].play(discord.FFmpegPCMAudio(song['source'], **ffmpeg_options), after=lambda e: play_next(interaction))
        else:
            client.queueIndex[id] += 1
            client.is_playing[id] = False


    async def play_music(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        if client.queueIndex[id] < len(client.musicQueue[id]):
            client.is_playing[id] = True
            client.is_paused[id] = False

            await join_voice(interaction, client.musicQueue[id][client.queueIndex[id]][1])
            song = client.musicQueue[id][client.queueIndex[id]][0]

            message = generate_now_playing_embed(interaction, song)
            await interaction.followup.send(embed=message)

            client.vc[id].play(discord.FFmpegPCMAudio(song['source'], **ffmpeg_options), after=lambda e: play_next(interaction))
        else:
            await interaction.followup.send('There are no songs in the queue.')
            client.queueIndex[id] += 1
            client.is_playing[id] = False

    async def play_song(interaction: discord.Interaction, song, channel):
        id = int(interaction.guild_id)
        if type(song) == type(True):
            await interaction.followup.send('Could not fetch the song.')
            return
        else:
            client.musicQueue[id].append([song, channel])
            if not client.is_playing[id]:
                await play_music(interaction)
            else:
                message = generate_add_to_queue_embed(interaction, song)
                await interaction.followup.send(embed=message)

    async def resultsYT(interaction: discord.Interaction, keywords):
        results = search_YT(keywords)
        embedText = ''

        for i, token in enumerate(results):
            url = 'https://www.youtube.com/watch?v=' + token
            name = get_YT_title(url)
            embedText += f'{i+1} - [{name}]({url})\n\n'
        
        searchResultsEmbed = discord.Embed(
            title='First 5 Search Results',
            description=embedText + 'Use !play <number> to select or !cancel to cancel selection.',
            colour=EMBED_RED
            )

        await interaction.followup.send(embed=searchResultsEmbed)

        def check(message: discord.Message):
            return (message.author == interaction.user 
                    and message.channel == interaction.channel
                    and (message.content.startswith('!play ') or message.content == '!cancel'))

        try:
            message = await client.wait_for('message', check=check, timeout=30.0)
            tokens = message.content.split()
            if tokens[0] == '!cancel':
                return None
            if len(tokens) == 2 and 1 <= int(tokens[1]) <= 5:
                return results[int(tokens[1]) - 1]
            else:
                'Either invalid choice or format.'
        except asyncio.TimeoutError:
            await interaction.followup.send('You took too long to reply. Please search again.')
            return None

    @client.tree.command(name='sync', description='Updates the command list.')
    async def sync(interaction: discord.Interaction):
        if interaction.user.id == USER_ID:
            client.tree.copy_global_to(guild=TEST_GUILD)
            synced = await client.tree.sync(guild=TEST_GUILD)
            await interaction.response.send_message(f'Command Tree synced {len(synced)} commands: {[cmd.name for cmd in synced]}', ephemeral=True)
        else:
            await interaction.response.send_message('You are not dylan.')

    @client.tree.command(name='join', description='Nishinoya joins your voice chat channel.')
    async def join(interaction: discord.Interaction):
        if interaction.user.voice:
            await join_voice(interaction, interaction.user.voice.channel)
            await interaction.response.send_message(f'Nishinoya has joined {interaction.user.voice.channel}')
        else:
            await interaction.response.send_message('You need to be connected to a voice channel.')

    @client.tree.command(name='leave', description='Nishinoya leaves the voice chat.')
    async def leave(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        reset_music_variables(client, id)
        if client.vc[id] == None:
            await interaction.response.send_message('Nishinoya is not in a voice channel.')
        if client.vc[id] != None and interaction.user.voice.channel == client.vc[id].channel:
            client.disconnecting[id] = True
            await client.vc[id].disconnect()
            client.disconnecting[id] = False
            await interaction.response.send_message('Nishinoya has left the chat.')
            client.vc[id] == None
        else:
            await interaction.response.send_message('You are not in the same voice channel as Nishinoya.')

    @client.tree.command(name='pause', description='Pause the audio if playing.')
    async def pause(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        if not client.vc[id]:
            await interaction.response.send_message('There is no audio to be paused at the moment.')
        elif interaction.user.voice.channel != client.vc[id]:
            await interaction.response.send_message('You need to be connected to the same voice channel.')
        elif client.is_playing[id]:
            await interaction.response.send_message('Audio paused.')
            client.is_playing[id] = False
            client.is_paused[id] = True
            client.vc[id].pause()

    @client.tree.command(name='resume', description='Resume the audio if playing.')
    async def resume(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        if not client.vc[id]:
            await interaction.response.send_message('There is no audio to be resumed at the moment.')
        elif interaction.user.voice.channel != client.vc[id]:
            await interaction.response.send_message('You need to be connected to the same voice channel.')
        elif client.is_paused[id]:
            await interaction.response.send_message('Audio resumed.')
            client.is_playing[id] = True
            client.is_paused[id] = False
            client.vc[id].resume()

    @client.tree.command(name='skip', description='Skip the current audio if playing.')
    async def skip(interaction: discord.Interaction):
        id = int(interaction.guild_id)
        await interaction.response.defer()
        if not client.vc[id]:
            await interaction.followup.send('The bot is not in a voice channel.')
        elif interaction.user.voice.channel != client.vc[id].channel:
            await interaction.followup.send('You need to be connected to the same voice channel.')
        elif client.queueIndex[id] >= len(client.musicQueue) - 1:
            await interaction.followup.send('There are no more songs in the queue.')
            client.vc[id].pause()
            reset_music_variables(client)
        else:
            client.vc[id].pause()
            client.queueIndex[id] += 1
            await play_music(interaction)

    client.run(BOT_TOKEN)

    '''
    ALTERNATE WAY WHICH USES MESSAGE INSTEAD OF SLASH COMMAND
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        
        if message.content.startswith('$zimak'):
            await message.channel.send('Zimak has the sweet succulent smell of a man dowsed in beautiful cologne made from the greenest forests of Heaven.')
    '''