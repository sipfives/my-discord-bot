import discord
from discord.ext import commands

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

    if message.channel.name == TARGET_CHANNEL_NAME:
        await message.channel.send("Meow! I'm watching this channel! 🐾")

    await bot.process_commands(message)

# Put your secret token between the quotes below
bot.run('MTQ5OTkxMDMyMzcyNDA5MTQ1Mw.GxT2HV.nG59K91co2gPPIb8_8y17AM7Xx9e8_4DDck77o')
