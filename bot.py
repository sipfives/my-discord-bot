import discord
from discord.ext import commands
import os

# Permissions setup
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# Change "general" to the name of the channel you want to watch
TARGET_CHANNEL_NAME = "general" 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "mods":
        await message.channel.send("Meow! I'm watching this channel! 🐾")

    await bot.process_commands(message)

# Put your secret token between the quotes below
bot.run(os.environ.get('DMTQ5OTkxMDMyMzcyNDA5MTQ1Mw.GSnXul.79n6l8j7BmqermaHZlJRGVSTeUjJMtL5X8Qt3cN'))
