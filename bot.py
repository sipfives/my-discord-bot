import discord
from discord.ext import commands, tasks
import os

# 1. Permissions Setup
intents = discord.Intents.default() # Fixed the typo from before!
intents.message_content = True  
intents.members = True          
intents.presences = True        

# Set your prefix here (e.g., "!")
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. Configuration
TARGET_CHANNEL_NAME = "mods"
STATUS_ROLE_NAME = "pic"
STATUS_TRIGGER = "/pinkie"

# 3. BACKGROUND TASK: Status Checker
@tasks.loop(seconds=30)
async def check_pinkie_status():
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=STATUS_ROLE_NAME)
        if not role: continue
        for member in guild.members:
            if member.bot: continue
            has_status = False
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    if activity.name and STATUS_TRIGGER in activity.name.lower():
                        has_status = True
            if has_status and role not in member.roles:
                try: await member.add_roles(role)
                except: pass
            elif not has_status and role in member.roles:
                try: await member.remove_roles(role)
                except: pass

# 4. COMMAND: In Role (Bleed style)
@bot.command()
async def inrole(ctx, *, role: discord.Role):
    """Lists all members that have a specific role."""
    members = role.members
    if not members:
        await ctx.send(f"No one has the **{role.name}** role yet!")
        return

    # Create a list of names
    member_list = "\n".join([f"• {m.name}" for m in members])
    
    # Send it in a nice format
    embed = discord.Embed(
        title=f"Members with {role.name}",
        description=member_list,
        color=role.color # This makes the side of the message match the role color!
    )
    embed.set_footer(text=f"Total: {len(members)}")
    await ctx.send(embed=embed)

# 5. EVENTS
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if not check_pinkie_status.is_running():
        check_pinkie_status.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.name == TARGET_CHANNEL_NAME:
        await message.channel.send("Meow! I'm watching this channel! 🐾")
    
    # CRUCIAL: This line allows the !inrole command to work!
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN'))