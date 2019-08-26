## Good Memer, a personal discord bot made by Quiterion
## TODOs: ~~video chat link generator~~
##          chatbot integration,
##          minecraft server status,
##          ~~text game integration~~
##          quote trigger storage and retrieval

import discord
import sqlite3
import subprocess
from discord.ext import commands

# Initialise connections and processes
bot = discord.Bot(command_prefix='>',
        description="A good memer.")
quotes_db = sqlite3.connect("quotes-db")

@bot.event
async def on_ready():
    # Runs upon bot loading
    print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\n--------")

@bot.command()
async def vidlink(ctx, channel: discord.VoiceChannel):
    # Command that generates a link for screensharing in a specified voice channel
    embd = discord.Embed(title="Channel-Specific Screenshare Link", 
            description="https://canary.discordapp.com/channels/{ctx.guild.id}/{channel.id}")
    ctx.send(embed=embd)

@bot.command()
async def mc_status(ctx):
    # Command that sends an embed with information about a locally running  minecraft server.
    hyperion_status = not ("inactive" in subprocess.check_output('systemctl status mc-hyperion', shell=True))
    embd = discord.Embed(title="Hyperion Server Information")
    embd.add_field(name="Domain Name", value=URL)
    embd.add_field(name="Level Name", value="Good Memes")
    embd.add_field(name="Network Ports", value=PORTS)
    embd.add_field(name="Server Status", value=("Running :)" if hyperion_status = True else "Not Running :("))
    ctx.send(embed=embd)

@bot.command()
async def add_quote(ctx, trigger, content):
    #conn = quotes_db.cursor()
    pass

bot.run(TOKEN)
