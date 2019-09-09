#!/home/quiterion/discord-bots/Good-Memer/venv/bin/python

## Good Memer, a personal discord bot made by Quiterion
## TODOs: ~~video chat link generator~~
##          chatbot integration,
##          ~~minecraft server status~~
##          text game integration,
##          ~~quote trigger storage and retrieval~~

import discord
import sqlite3
import subprocess
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
MC_URL = config.get("Minecraft", "URL")
MC_IPV4_PORT = config.get("Minecraft", "IPv4 Port")
MC_IPV6_PORT = config.get("Minecraft", "IPv6 Port")
MC_THUMBNAIL_URL = config.get("Minecraft", "Thumbnail URL")

@bot.event
async def on_ready():
    # Runs upon bot loading
    print(f"Logged in as:\n{bot.user.name}\n{bot.user.id}\n-----------")

@bot.command()
async def vidlink(ctx, channel: discord.VoiceChannel):
    # Command that generates a link for screensharing in a specified voice channel
    embd = discord.Embed(title="Channel-Specific Screenshare Link", 
            description=f"https://canary.discordapp.com/channels/{ctx.guild.id}/{channel.id}",
            type="rich", colour=EMBED_COLOUR)
    await ctx.send(embed=embd)

@bot.command()
async def mcstatus(ctx):
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
async def add_quote(ctx, trigger, content):
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
async def del_quote(ctx, given_id):
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
async def list_quotes(ctx):
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
async def s(ctx, message):
    response = str(chatbot.get_response(message))
    embd =discord.Embed(title="Chatterbot Output", type="rich", colour=EMBED_COLOUR)
    embd.add_field(name="Received Message", value=message)
    embd.add_field(name="Generated Response", value=response)
    await ctx.send(embed=embd)

@bot.event
async def on_message(message):
    
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    if message.content.startswith("I'm "):
        await message.channel.send(f"Hi {message.content[4:]}, I'm Dad!")

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

    await bot.process_commands(message)

bot.run(TOKEN)
