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
# These will DELETE previous messages
CLEAN_CHANNELS = {
    "﹒s﹒scαmmers": "only post real scammers. youll be warned if you send any nsfw messages.",
    "﹒╭✿，selfie﹒୭": "catfishing = ban <3"
}

# These will STACK messages (GIFs/Photos)
# Added the Forum name "୨୧ . persona" here so she works in those posts!
LOG_CHANNELS = {
    "✿︵vanity﹒﹒୧﹒": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif",
    "୨୧ . persona": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"
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

    # LOGIC: Check if we are in a channel or a thread/forum post
    channel_name = message.channel.name
    parent_name = ""
    if isinstance(message.channel, discord.Thread) and message.channel.parent:
        parent_name = message.channel.parent.name

    # Check CLEAN group (Channel name or Parent name)
    if channel_name in CLEAN_CHANNELS or parent_name in CLEAN_CHANNELS:
        target_key = channel_name if channel_name in CLEAN_CHANNELS else parent_name
        custom_msg = CLEAN_CHANNELS[target_key]
        async for old_msg in message.channel.history(limit=50):
            if old_msg.author == bot.user and old_msg.content == custom_msg:
                try:
                    await old_msg.delete()
                    break 
                except: pass 
        await message.channel.send(custom_msg)

    # Check LOG group (Channel name or Parent name)
    elif channel_name in LOG_CHANNELS or parent_name in LOG_CHANNELS:
        target_key = channel_name if channel_name in LOG_CHANNELS else parent_name
        custom_msg = LOG_CHANNELS[target_key]
        await message.channel.send(custom_msg)
    
    await bot.process_commands(message)

# 6. Start the Bot
bot.run(os.environ.get('DISCORD_TOKEN'))