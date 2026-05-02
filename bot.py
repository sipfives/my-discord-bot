import discord
from discord.ext import commands, tasks
import os
import asyncio
import random

# 1. Permissions Setup
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.presences = True        
intents.moderation = True # Needed to read Audit Logs

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# 2. Configuration
CLEAN_CHANNEL_IDS = {
    1484730031048491049: "only post real scammers. youll be warned if you send any nsfw messages.",
    1483988599337783448: "catfishing = ban <3"
}

LOG_CHANNEL_IDS = {
    1499948539424411863: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"
}

STATUS_ROLE_NAME = "pic"
STATUS_TRIGGER = "/pinkie"
BABY_PINK = 0xFFB6C1

# 3. BACKGROUND TASK: Audit-Log Status Checker
@tasks.loop(seconds=30)
async def check_pinkie_status():
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=STATUS_ROLE_NAME)
        if not role: continue
        
        for member in guild.members:
            if member.bot: continue
            
            # Check current status
            has_status = False
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    if activity.name and STATUS_TRIGGER in activity.name.lower():
                        has_status = True
            
            # If they have the status but NOT the role -> Add it
            if has_status and role not in member.roles:
                try: await member.add_roles(role)
                except: pass
            
            # If they DON'T have the status but DO have the role -> CHECK AUDIT LOG
            elif not has_status and role in member.roles:
                try:
                    # Look at the most recent time this role was added to this specific member
                    async for entry in guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=10):
                        if entry.target.id == member.id:
                            # Check if the 'pic' role was added in this log entry
                            for r in entry.after.roles:
                                if r.id == role.id:
                                    # If the bot was the one who added it, the bot can remove it
                                    if entry.user.id == bot.user.id:
                                        await member.remove_roles(role)
                                        print(f"Removed role from {member.name} (Bot-given)")
                                    else:
                                        # A human or other bot gave it, so we leave it alone!
                                        print(f"Skipping {member.name} (Role was given by {entry.user.name})")
                                    break
                except Exception as e:
                    print(f"Audit log error: {e}")

# 4. COMMANDS
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 **chocolα's help menu** 🎀", description="Here are the commands available for you, kitties!", color=BABY_PINK)
    embed.add_field(name="🐾 **General**", value="`.help` - Shows this menu!\n`.inrole [role]` - Pings everyone with a role.", inline=False)
    embed.add_field(name="🎁 **Giveaways**", value="`.giveaway [time] [prize]` - Starts a giveaway!\n`.reroll [message_id]` - Picks a new winner.", inline=False)
    embed.set_footer(text="Prefix: .")
    await ctx.send(embed=embed)

@bot.command()
async def inrole(ctx, *, role: discord.Role):
    members = role.members
    if not members:
        await ctx.send(f"No one has the **{role.name}** role yet!")
        return
    member_pings = "\n".join([f"• <@{m.id}>" for m in members])
    embed = discord.Embed(title=f"Members with {role.name}", description=member_pings, color=BABY_PINK)
    embed.set_footer(text=f"Total: {len(members)}")
    await ctx.send(embed=embed)

def convert_time(time_str):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = time_str[-1]
    if unit not in time_dict: return -1
    try: return int(time_str[:-1]) * time_dict[unit]
    except: return -1

@bot.command()
@commands.has_permissions(manage_messages=True)
async def giveaway(ctx, duration: str, *, prize: str):
    seconds = convert_time(duration)
    if seconds == -1:
        await ctx.send("Use a valid time (10m, 1h, etc)!")
        return
    embed = discord.Embed(title="🎀 **KITTEN PARADISE GIVEAWAY** 🎀", description=f"React with 🎉!\n\n**Prize:** {prize}\n**Ends in:** {duration}\n**Host:** {ctx.author.mention}", color=BABY_PINK)
    embed.add_field(name="Rules:", value="🐾 Must be in server.\n🐾 No alts.\n🐾 Level 5+")
    g_msg = await ctx.send(embed=embed)
    await g_msg.add_reaction("🎉")
    await asyncio.sleep(seconds)
    new_msg = await ctx.channel.fetch_message(g_msg.id)
    users = [user async for user in new_msg.reactions[0].users() if not user.bot]
    if not users: await ctx.send("No entries. 💔")
    else:
        winner = random.choice(users)
        await ctx.send(f"🎉 **CONGRATS** <@{winner.id}>! You won **{prize}**!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def reroll(ctx, message_id: int):
    try:
        new_msg = await ctx.channel.fetch_message(message_id)
        users = [user async for user in new_msg.reactions[0].users() if not user.bot]
        winner = random.choice(users)
        await ctx.send(f"🎉 **NEW WINNER:** <@{winner.id}>!")
    except: await ctx.send("Invalid Message ID!")

# 5. EVENTS
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if not check_pinkie_status.is_running():
        check_pinkie_status.start()

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    current_id = message.channel.id
    parent_id = getattr(message.channel, "parent_id", None)
    target_clean_id = current_id if current_id in CLEAN_CHANNEL_IDS else parent_id if parent_id in CLEAN_CHANNEL_IDS else None
    if target_clean_id:
        custom_msg = CLEAN_CHANNEL_IDS[target_clean_id]
        async for old_msg in message.channel.history(limit=10):
            if old_msg.author == bot.user and old_msg.content == custom_msg:
                try: await old_msg.delete(); break 
                except: pass 
        await message.channel.send(custom_msg)
        return
    target_log_id = current_id if current_id in LOG_CHANNEL_IDS else parent_id if parent_id in LOG_CHANNEL_IDS else None
    if target_log_id: await message.channel.send(LOG_CHANNEL_IDS[target_log_id])
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN'))