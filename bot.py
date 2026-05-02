import discord
from discord.ext import commands, tasks
import os

# 1. Permissions Setup
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.presences = True        

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. Configuration
# FORMAT: "channel-name": "Message you want"
# TIP: Copy the name exactly as it appears in the channel header!
WATCHED_CHANNELS = {
    "﹒s﹒scαmmers": "only post actual scammers. do not post nsfw messages here!",
    "﹒╭✿，selfie﹒୭": "catfishing is a ban <3"
}

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

# 4. COMMAND: In Role
@bot.command()
async def inrole(ctx, *, role: discord.Role):
    members = role.members
    if not members:
        await ctx.send(f"No one has the **{role.name}** role yet!")
        return
    member_pings = "\n".join([f"• <@{m.id}>" for m in members])
    embed = discord.Embed(title=f"Members with {role.name}", description=member_pings, color=0xFFB6C1)
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

    # Check if the channel name is one of our keys in WATCHED_CHANNELS
    if message.channel.name in WATCHED_CHANNELS:
        custom_msg = WATCHED_CHANNELS[message.channel.name]
        
        # CLEANUP: Delete the previous custom message for THIS channel
        async for old_msg in message.channel.history(limit=50):
            if old_msg.author == bot.user and old_msg.content == custom_msg:
                try:
                    await old_msg.delete()
                    break 
                except:
                    pass 
        
        # Send the fresh custom message
        await message.channel.send(custom_msg)
    
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN'))