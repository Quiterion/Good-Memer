## Good Memer, a personal discord bot made by Quiterion
## TODOs: ~~video chat link generator~~
##          chatbot integration,
##          ~~minecraft server status~~
##          text game integration,
##          ~~quote trigger storage and retrieval~~

import discord
import sqlite3
import subprocess
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from discord.ext import commands

# Initialise connections and processes
bot = commands.Bot(command_prefix='$',
        description="A Good Memer.")

chatbot = ChatBot('Good Memer')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")


@bot.event
async def on_ready():
    # Runs upon bot loading
    print(f"Logged in as:\n{bot.user.name}\n{bot.user.id}\n-----------")

@bot.command()
async def vidlink(ctx, channel: discord.VoiceChannel):
    # Command that generates a link for screensharing in a specified voice channel
    embd = discord.Embed(title="Channel-Specific Screenshare Link", 
            description=f"https://canary.discordapp.com/channels/{ctx.guild.id}/{channel.id}",
            type="rich", colour=0xea4cc0)
    await ctx.send(embed=embd)

@bot.command()
async def mcstatus(ctx):
    # Command that sends an embed with information about a locally running  minecraft server.
    #hypernet_status = not ("inactive" in subprocess.check_output('systemctl status mc-hypernet', shell=True))
    embd = discord.Embed(title="Hypernet Server Information",
            type="rich", colour=0xea4cc0)
    embd.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/977e8c4f-1c99-46cd-b070-10cd97086c08/d36qrs5-017c3744-8c94-4d47-9633-d85b991bf2f7.png")
    embd.add_field(name="Domain Name", value=URL)
    embd.add_field(name="Level Name", value="Good Memes")
    embd.add_field(name="IPv4 Network Port", value=IPV4_PORT)
    embd.add_field(name="IPv6 Network Port", value=IPV6_PORT)
    embd.add_field(name="Server Status", value=("Running :)" if hypernet_status == True else "Not Running :("))
    await ctx.send(embed=embd)

@bot.command()
async def add_quote(ctx, trigger, content):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS quotes (quote_id INTEGER PRIMARY KEY autoincrement, 
                                                             trigger TEXT, 
                                                             content TEXT)''')
        cursor.execute('INSERT INTO quotes (trigger, content) VALUES(?, ?)', (trigger, content))
        quotes_db.commit()
        cursor.execute('SELECT * FROM quotes')
        records = cursor.fetchall()
        embd = discord.Embed(title="Quote transaction", description="Success!", type="rich", colour=0xea4cc0)
        embd.add_field(name="Number of quotes", value=str(len(records)))
        await ctx.send(embed=embd)
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=0xea4cc0, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()


@bot.command()
async def del_quote(ctx, given_id):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute('DELETE FROM quotes WHERE quote_id = ?', (given_id,))
        quotes_db.commit()
        await ctx.send(embed=discord.Embed(title="Quote transaction", description="Success!",
            type="rich", colour=0xea4cc0))
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=0xea4cc0, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()

@bot.command()
async def quote(ctx, trig):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute('SELECT content FROM quotes WHERE trigger = ?', (trig,))
        result = cursor.fetchone()
        if result:
            await ctx.send(str(result[0]))
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=0xea4cc0, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()

@bot.command()
async def list_quotes(ctx):
    try:
        quotes_db = sqlite3.connect("quotes-db")
        cursor = quotes_db.cursor()
        cursor.execute('SELECT quote_id, trigger, content FROM quotes')
        result = cursor.fetchall()
        out_table = "```Quote List\nID | Trigger | Content"
        for res in result:
            out_table += "\n" + str(res[0]) + "  | " + str(res[1]) + " | " + str(res[2]).replace("`", "").replace("\n", "")[:18]
        out_table += "```"
        await ctx.send(out_table)
    except sqlite3.Error as error:
        quotes_db.rollback()
        await ctx.send(embed=discord.Embed(title="Oopsie, we did a fucky wucky",
            type="rich", colour=0xea4cc0, description=str(error)))
        raise error
    finally:
        cursor.close()
        quotes_db.close()

@bot.command()
async def say(ctx, message):
    await ctx.send(embed=discord.Embed(title="Chatterbot Response", description=str(chatbot.get_response(message)),
            type="rich", colour=0xea4cc0))

bot.run(TOKEN)
