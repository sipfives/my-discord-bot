import discord
from discord.ext import commands, tasks
import os

# 1. Permissions Setup
intents = discord.Intents.default()
intents.message_content = True  # Needed for the "watching" feature
intents.members = True          # Needed to see everyone in the server
intents.presences = True        # Needed to see custom statuses

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. Configuration
TARGET_CHANNEL_NAME = "mods"  # The channel for the "Watching" message
STATUS_ROLE_NAME = "pic" # The role name for the /pinkie status
STATUS_TRIGGER = "/pinkie"    # The text people need in their status

# 3. Background Task: Status Checker
@tasks.loop(seconds=30)
async def check_pinkie_status():
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=STATUS_ROLE_NAME)
        if not role:
            continue
            
        for member in guild.members:
            if member.bot:
                continue
            
            # Check if user has the trigger in their custom status
            has_status = False
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    if activity.name and STATUS_TRIGGER in activity.name.lower():
                        has_status = True
            
            # Logic to Add or Remove the role
            if has_status and role not in member.roles:
                try:
                    await member.add_roles(role)
                    print(f"Added role to {member.name}")
                except:
                    print(f"Failed to add role (Check bot permissions/hierarchy)")
            elif not has_status and role in member.roles:
                try:
                    await member.remove_roles(role)
                    print(f"Removed role from {member.name}")
                except:
                    print(f"Failed to remove role")

# 4. Event: Bot is Ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Start the background status checker loop
    if not check_pinkie_status.is_running():
        check_pinkie_status.start()

# 5. Event: Message Listener (The "Watching" Feature)
@bot.event
async def on_message(message):
    # Don't let the bot reply to itself
    if message.author == bot.user:
        return

    # Check if the message is in the target channel
    if message.channel.name == TARGET_CHANNEL_NAME:
        await message.channel.send("Meow! I'm watching this channel! 🐾")

    # This allows other commands (if you add any) to work
    await bot.process_commands(message)

# 6. Start the Bot
bot.run(os.environ.get('DISCORD_TOKEN'))