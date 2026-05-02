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
intents.moderation = True 

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# 2. Configuration
CLEAN_CHANNEL_IDS = {
    1484730031048491049: "only post real scammers. youll be warned if you send any nsfw messages.",
    1483988599337783448: "catfishing = ban <3"
}

LOG_CHANNEL_IDS = {
    1499948539424411863: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif",
    1499947145296351242: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"
}

BOOST_CHANNEL_ID = 1484728025059819611 
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
                try:
                    async for entry in guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=5):
                        if entry.target.id == member.id:
                            for r in entry.after.roles:
                                if r.id == role.id and entry.user.id == bot.user.id:
                                    await member.remove_roles(role)
                                    break
                except: pass

# 4. COMMANDS
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 **chocolα's help menu** 🎀", description="Here are the commands available for you, kitties!", color=BABY_PINK)
    embed.add_field(name="🐾 **General**", value="`.help` | `.purge [amount]` | `.inrole [role]` | `.role [user] [name]` | `.testboost`", inline=False)
    embed.add_field(name="🖼️ **Profile**", value="`.av` - User Avatar\n`.sav` - Server Avatar\n`.banner` - User Banner\n`.sbanner` - Server Profile Banner\n`.guildbanner` - Server's Banner", inline=False)
    embed.add_field(name="🎁 **Giveaways**", value="`.giveaway [time] [prize]` | `.reroll [msg_id]`", inline=False)
    await ctx.send(embed=embed)

# --- FIXED AVATAR COMMANDS ---
@bot.command(aliases=['avatar'])
async def av(ctx, member: discord.Member = None):
    member = member or ctx.author
    # member.avatar pulls the GLOBAL avatar. If they don't have one, it pulls default.
    url = member.avatar.url if member.avatar else member.default_avatar.url
    embed = discord.Embed(title=f"🐾 {member.name}'s Global Avatar", color=BABY_PINK)
    embed.set_image(url=url)
    await ctx.send(embed=embed)

@bot.command(aliases=['serveravatar'])
async def sav(ctx, member: discord.Member = None):
    member = member or ctx.author
    url = member.guild_avatar.url if member.guild_avatar else member.display_avatar.url
    embed = discord.Embed(title=f"🐾 {member.name}'s Server Avatar", color=BABY_PINK)
    embed.set_image(url=url)
    await ctx.send(embed=embed)

# --- FIXED BANNER COMMANDS ---
@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    if not user.banner:
        return await ctx.send("🐾 This user doesn't have a global banner!")
    embed = discord.Embed(title=f"🐾 {member.name}'s Global Banner", color=BABY_PINK)
    embed.set_image(url=user.banner.url)
    await ctx.send(embed=embed)

@bot.command(aliases=['serverbanner'])
async def sbanner(ctx, member: discord.Member = None):
    member = member or ctx.author
    # This fetches the member specifically for this guild to see their server profile
    if not member.banner:
        return await ctx.send("🐾 This user doesn't have a server-specific banner!")
    embed = discord.Embed(title=f"🐾 {member.name}'s Server Profile Banner", color=BABY_PINK)
    embed.set_image(url=member.banner.url)
    await ctx.send(embed=embed)

@bot.command()
async def guildbanner(ctx):
    if not ctx.guild.banner:
        return await ctx.send("🐾 This server doesn't have a banner!")
    embed = discord.Embed(title=f"🐾 {ctx.guild.name}'s Banner", color=BABY_PINK)
    embed.set_image(url=ctx.guild.banner.url)
    await ctx.send(embed=embed)

# --- ADMIN COMMANDS ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    confirm = await ctx.send(f"🐾 successfully purged **{len(deleted)-1}** messages! meow")
    await asyncio.sleep(3)
    await confirm.delete()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, *, search: str):
    role = discord.utils.find(lambda r: search.lower() in r.name.lower(), ctx.guild.roles)
    if role is None:
        return await ctx.send(f"🐾 I couldn't find any role containing **{search}**!")
    if role in member.roles:
        await member.remove_roles(role)
        embed = discord.Embed(description=f"🐾 Removed **{role.name}** from {member.mention}", color=BABY_PINK)
    else:
        await member.add_roles(role)
        embed = discord.Embed(description=f"🐾 Added **{role.name}** to {member.mention}", color=BABY_PINK)
    await ctx.send(embed=embed)

@bot.command()
async def inrole(ctx, *, role: discord.Role):
    members = role.members
    if not members:
        return await ctx.send(f"No one has the **{role.name}** role yet!")
    member_pings = "\n".join([f"• <@{m.id}>" for m in members])
    embed = discord.Embed(title=f"Members with {role.name}", description=member_pings, color=BABY_PINK)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def testboost(ctx):
    boost_msg = (
        "<:xx_blank1308798611726794793:1500174266396704875> \n"
        "                          <a:0ggoki:1492955057359028365><a:0ggoki:1492955061662253140> \n"
        "<:xx_blank1308798611726794793:1500174266396704875>     ﹒**thαnk you for boosting**\n"
        "                     <a:000paw:1486941220222664843>     ֪ __kitten__ ⑅\n"
        f"                  . . ͡  ɞ {ctx.author.mention}"
    )
    await ctx.send(boost_msg)

# --- GIVEAWAY SYSTEM ---
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
    if seconds == -1: return await ctx.send("Use a valid time (10m, 1h, etc)!")
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
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        channel = bot.get_channel(BOOST_CHANNEL_ID)
        if channel:
            boost_msg = (
                "<:xx_blank1308798611726794793:1500174266396704875> \n"
                "                          <a:0ggoki:1492955057359028365><a:0ggoki:1492955061662253140> \n"
                "<:xx_blank1308798611726794793:1500174266396704875>     ﹒**thαnk you for boosting**\n"
                "                     <a:000paw:1486941220222664843>     ֪ __kitten__ ⑅\n"
                f"                  . . ͡  ɞ {after.mention}"
            )
            await channel.send(boost_msg)

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
    if target_log_id: 
        await message.channel.send(LOG_CHANNEL_IDS[target_log_id])
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN'))