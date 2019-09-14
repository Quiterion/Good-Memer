#!/home/quiterion/discord-bots/Good-Memer/venv/bin/python

## Good Memer, a personal discord bot made by Quiterion
## TODOs: ~~video chat link generator~~
##          ~~chatbot integration,~~
##          ~~minecraft server status~~
##          ~~text game integration~~
##          ~~quote trigger storage and retrieval~~

import discord
import sqlite3
import subprocess
import re
import pexpect
import configparser
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from discord.ext import commands

# Initialise connections and processes
bot = commands.Bot(command_prefix='$',
        description="A Good Memer.")

chatbot = ChatBot('Good Memer')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")

config = configparser.ConfigParser()
config.read("/home/quiterion/discord-bots/Good-Memer/config.ini")
TOKEN = config.get("Discord", "TOKEN")
EMBED_COLOUR = int(config.get("Discord", "Embed Colour"), 16)
TRUSTED_SERVER_ID = config.getint("Discord", "Trusted Server ID")
DAD_SHUTUP_CHIDING = config.get("Discord", "Dad Chiding")
MC_URL = config.get("Minecraft", "URL")
MC_IPV4_PORT = config.get("Minecraft", "IPv4 Port")
MC_IPV6_PORT = config.get("Minecraft", "IPv6 Port")
MC_THUMBNAIL_URL = config.get("Minecraft", "Thumbnail URL")
TEXTGAME_PATH = config.get('Text Game', "Text Game Path")
TEXTGAME_WORLD_PATH = config.get('Text Game', "World Path")

# Dictionary storing server ID's and their text game objects
TEXT_GAMES = {}

@bot.event
async def on_ready():
    # Runs upon bot loading
    print(f"Logged in as:\n{bot.user.name}\n{bot.user.id}\n-----------")

@bot.command()
async def vid(ctx, channel: discord.VoiceChannel):
    # Command that generates a link for screensharing in a specified voice channel
    embd = discord.Embed(title="Channel-Specific Screenshare Link", 
            description=f"https://discordapp.com/channels/{ctx.guild.id}/{channel.id}",
            type="rich", colour=EMBED_COLOUR)
    await ctx.send(embed=embd)

@bot.command()
async def mcstat(ctx):
    # Command that sends an embed with information about a locally running minecraft server. Only outputs information in trusted server

    if ctx.guild.id != TRUSTED_SERVER_ID:
        print(f"Information access request denied!\nServer ID: {ctx.guild.id}\nExpected ID: {TRUSTED_SERVER_ID}\n")
        await ctx.send(embed=discord.Embed(title="Hypernet Server Information", description="Information access denied!", type="rich", colour=EMBED_COLOUR))
        return

    hypernet_status = not ("inactive" in subprocess.run('/bin/systemctl status mc-hypernet', shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8'))
    embd = discord.Embed(title="Hypernet Server Information", type="rich", colour=EMBED_COLOUR)
    embd.set_thumbnail(url=MC_THUMBNAIL_URL)
    embd.add_field(name="Domain Name", value=MC_URL)
    embd.add_field(name="Level Name", value="Good Memes")
    embd.add_field(name="IPv4 Network Port", value=MC_IPV4_PORT)
    embd.add_field(name="IPv6 Network Port", value=MC_IPV6_PORT)
    embd.add_field(name="Server Status", value=("Running :)" if hypernet_status == True else "Not Running :("))
    await ctx.send(embed=embd)

@bot.command()
async def add(ctx, trigger, content):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS quotes_{ctx.guild.id} (quote_id INTEGER PRIMARY KEY autoincrement, 
                                                             trigger TEXT, 
                                                             content TEXT)''')
        cursor.execute(f'INSERT INTO quotes_{ctx.guild.id} (trigger, content) VALUES(?, ?)', (trigger, content))
        quotes_db.commit()
        cursor.execute(f'SELECT * FROM quotes_{ctx.guild.id}')
        records = cursor.fetchall()
        embd = discord.Embed(title="Quote transaction", description="Success!", type="rich", colour=EMBED_COLOUR)
        embd.add_field(name="Number of quotes", value=str(len(records)))
        await ctx.send(embed=embd)
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=EMBED_COLOUR, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()


@bot.command()
async def delete(ctx, given_id):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute(f'DELETE FROM quotes_{ctx.guild.id} WHERE quote_id = ?', (given_id,))
        quotes_db.commit()
        await ctx.send(embed=discord.Embed(title="Quote transaction", description="Success!",
            type="rich", colour=EMBED_COLOUR))
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=EMBED_COLOUR, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()

@bot.command()
async def list(ctx):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute(f'SELECT quote_id, trigger, content FROM quotes_{ctx.guild.id}')
        result = cursor.fetchall()
        out_table = "```Quote List\nID | Trigger | Content"
        for res in result:
            out_table += "\n" + str(res[0]) + "  | " + str(res[1]) + " | " + str(res[2]).replace("`", "").replace("\n", "")[:18]
        out_table += "```"
        await ctx.send(out_table)
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=EMBED_COLOUR, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()

@bot.command()
async def s(ctx, *, message):
    response = str(chatbot.get_response(message))
    embd = discord.Embed(title="Chatterbot Output", description=response, type="rich", colour=EMBED_COLOUR)
    await ctx.send(embed=embd)

@bot.command()
async def game(ctx):
    textgame = pexpect.spawn('python3 ' + TEXTGAME_PATH + ' ' + TEXTGAME_WORLD_PATH)
    TEXT_GAMES[ctx.channel.id] = textgame
    textgame.expect('> ')
    desc = "Adventure Quest instance succesfully opened for this channel! Send commands to it with \"$z <text>\" and end the game with \"$end\""
    embd = discord.Embed(title="Text Game Creation", description=desc, type="rich", colour=EMBED_COLOUR)
    await ctx.send("```" + textgame.before.decode('utf-8') + "```", embed=embd)

@bot.command()
async def z(ctx, *, message):
    textgame = TEXT_GAMES.get(ctx.channel.id, 0)
    if textgame == 0:
        embd = discord.Embed(title="Text Game Output", description="Error! No text game for this channel found. Create one with \"$game\"", colour=EMBED_COLOUR)
        await ctx.send(embed=embd)
        return
    textgame.sendline(message)
    textgame.expect('> ')
    await ctx.send("```> " + textgame.before.decode('utf-8') + "```")

@bot.command()
async def end(ctx):
    textgame = TEXT_GAMES.get(ctx.channel.id, 0)
    if textgame == 0:
        embd = discord.Embed(title="Text Game Output", description="Error! No text game for this channel found. Create one with \"$game\"", colour=EMBED_COLOUR)
    else:
        textgame.terminate()
        del TEXT_GAMES[ctx.channel.id]
        embd = discord.Embed(title="Text Game Output", description="Text game terminated succesfully.", colour=EMBED_COLOUR)
    await ctx.send(embed=embd)




@bot.event
async def on_message(message):
    # Coroutine that runs upon each message, main purpose
    # is to catch quote triggers and provide Dad-Bot-like functions.

    if message.author == bot.user:
        await bot.process_commands(message)
        return
    
    if 'stfu' in message.content.lower() or re.findall(r'shut.*up', message.content.lower()) != []:
        chide = DAD_SHUTUP_CHIDING.replace("{user}", message.author.mention)
        await message.channel.send(chide)
        return

    # Lord forgive me for I have sinned
    # This monstrosity takes a list of tuples of find() indexes and the offset
    # required to correctly parse the message. The hope is that one of the find()
    # values will return something other than -1 and we can use the offset value
    # to parse the message.

    dad_list = [(message.content.find("I'm"), 4), (message.content.find("I‘m"), 4), (message.content.find("I am"), 5)]
    if any([x[0] != -1 for x in dad_list]):
        start_index = min([x[0] + x[1] for x in dad_list if x[0] != -1]) 
        await message.channel.send(f"Hi {message.content[start_index:]}, I'm Dad!")
        await bot.process_commands(message)
        return

    if not message.content.startswith("$"):
        try:
            quotes_db = sqlite3.connect("quotes-db")
            cursor = quotes_db.cursor()
            cursor.execute(f'SELECT content FROM quotes_{message.guild.id} WHERE trigger = ?', (message.content,))
            result = cursor.fetchone()
            if result:
                await message.channel.send(str(result[0]))
        except sqlite3.Error as error:
            quotes_db.rollback()
            # Don't send a message to chat given this coroutine runs for every single message
            raise error
        finally:
            cursor.close()
            quotes_db.close()
    
    # Allows bot.command() coroutines to run
    await bot.process_commands(message)

bot.run(TOKEN)
