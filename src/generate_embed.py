import discord

'''
EMBED COLORS
'''
EMBED_BLUE = 0x2c76dd
EMBED_RED = 0xdf1141
EMBED_GREEN = 0x0eaa51
EMBED_PURPLE = 0xc200c2

def now_playing(interaction: discord.Interaction, song):
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

def add_to_queue(interaction: discord.Interaction, song):
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

def skip(interaction: discord.Interaction, song):
    title = song['title']
    link = song['link']
    thumbnail = song['thumbnail']
    author = interaction.user
    avatar = author.avatar.url

    embed = discord.Embed(
        title='Skipped Song',
        description=f'[{title}]({link})\n\nSkipped by: {author.mention}',
        colour=EMBED_RED
    )
    embed.set_thumbnail(url=thumbnail)
    return embed

def embed(interaciton: discord.Interaction):
    return discord.Embed(
        title='You asked for help!\nHere are all the functions:',
        description='''
                    **/help** - Displays all the functions
                    **/play** - Play a song from Spotify, Youtube or URL (supports any YT-DLP url)
                    　　*args*:
                    　　　　**\'Source\'** - Source of audio
                    　　　　**\'Query\'** - Song/Audio you want to search for
                    **/pause** - Pauses the audio
                    **/resume** - Resumes the audio
                    **/sync** - (For Dylan) Syncs the command tree across all servers
                    **/skip** - Skips song
                    **/join** - Bot joins the channel you are in
                    **/leave** - Bot leaves the channel it is in
                    ''',
        color=EMBED_PURPLE
    )