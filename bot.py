## Good Memer, a personal discord bot made by Quiterion
## TODOs: ~~video chat link generator~~
##          chatbot integration,
##          minecraft server status,
##          text game integration
##          quote trigger storage and retrieval

import discord
import sqlite3
from discord.ext import commands

bot = discord.Bot(command_prefix='>',
        description="A good memer.")

@bot.event
async def on_ready():
    print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\n--------")

@bot.command()
async def vidlink(ctx, channel: discord.VoiceChannel):
    embd = discord.Embed(title="Channel-Specific Screenshare Link", 
            description="https://canary.discordapp.com/channels/{ctx.guild.id}/{channel.id}")
    ctx.send(embed=embd)

#@bot.command()
#async def add_quote(ctx, trigger, content):
     

bot.run(TOKEN)
