import discord
from discord.ext import commands, tasks
import os
import asyncio
import random
import re

# 1. Permissions Setup
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.presences = True        

# UPDATED: Prefix is now ","
bot = commands.Bot(command_prefix=",", intents=intents)

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

# 4. COMMANDS
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

# --- GIVEAWAY SYSTEM ---

def convert_time(time_str):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = time_str[-1]
    if unit not in pos: return -1
    try:
        val = int(time_str[:-1])
        return val * time_dict[unit]
    except: return -1

@bot.command()
@commands.has_permissions(manage_messages=True)
async def giveaway(ctx, duration: str, *, prize: str):
    seconds = convert_time(duration)
    if seconds == -1:
        await ctx.send("Please use a valid time format (e.g., 10m, 1h, 30s)!")
        return

    embed = discord.Embed(
        title="🎀 **KITTEN PARADISE GIVEAWAY** 🎀",
        description=f"React with 🎉 to join the raffle!\n\n**Prize:** {prize}\n**Ends in:** {duration}\n**Hosted by:** {ctx.author.mention}",
        color=BABY_PINK
    )
    embed.add_field(name="Rules:", value="🐾 Must be in the server to win.\n🐾 No alt accounts.\n🐾 Must be active! (Level 5+)")
    embed.set_footer(text="Good luck, kitties! 🐾")
    
    g_msg = await ctx.send(embed=embed)
    await g_msg.add_reaction("🎉")

    await asyncio.sleep(seconds)

    new_msg = await ctx.channel.fetch_message(g_msg.id)
    users = [user async for user in new_msg.reactions[0].users() if not user.bot]

    if not users:
        await ctx.send("No one joined the giveaway. :( 💔")
    else:
        winner = random.choice(users)
        await ctx.send(f"🎉 **CONGRATULATIONS** <@{winner.id}>! You won the **{prize}**!\n*Make sure to check if they are Level 5!*")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def reroll(ctx, message_id: int):
    try:
        new_msg = await ctx.channel.fetch_message(message_id)
        users = [user async for user in new_msg.reactions[0].users() if not user.bot]
        if not users:
            await ctx.send("No entries found.")
            return
        winner = random.choice(users)
        await ctx.send(f"🎉 **NEW WINNER:** <@{winner.id}>! Congratulations!")
    except:
        await ctx.send("I couldn't find that message ID!")

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

    current_id = message.channel.id
    parent_id = getattr(message.channel, "parent_id", None)

    # Check CLEAN group
    target_clean_id = current_id if current_id in CLEAN_CHANNEL_IDS else parent_id if parent_id in CLEAN_CHANNEL_IDS else None
    if target_clean_id:
        custom_msg = CLEAN_CHANNEL_IDS[target_clean_id]
        async for old_msg in message.channel.history(limit=10):
            if old_msg.author == bot.user and old_msg.content == custom_msg:
                try: await old_msg.delete(); break 
                except: pass 
        await message.channel.send(custom_msg)
        return

    # Check LOG group
    target_log_id = current_id if current_id in LOG_CHANNEL_IDS else parent_id if parent_id in LOG_CHANNEL_IDS else None
    if target_log_id:
        await message.channel.send(LOG_CHANNEL_IDS[target_log_id])
    
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN'))