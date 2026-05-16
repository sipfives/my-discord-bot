import discord
from discord.ext import commands, tasks
import os
import asyncio
import random
import datetime
import time
import re
import aiohttp
import json
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv

load_dotenv()

# --- 1. Permissions Setup ---
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.presences = True        
intents.moderation = True 

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# --- 2. Configuration (Keeping your original IDs) ---
TICKET_CATEGORY_ID = 1484550188885475348
TICKET_PROMPT_CHANNEL_ID = 1484049393387700336
TIPS_CHANNEL_ID = 1484554927794819232
BOOST_CHANNEL_ID = 1484728025059819611 
STAFF_ROLE_ID = 1485039399015157801
PIC_PERMS_ROLE_ID = 1486944861574926356

# Updated Server Name for DMs
SERVER_NAME_MOD = "kitten  •  SFW"

AUTHORIZED_CLOSE_ROLES = [1485039399015157801, 1483884626605768785, 1484294120510853200, 1484041123390423110]
STATUS_TRIGGER = "/pinkie"
HELP_HEX = 0xFFD4F4 
BABY_PINK = 0xFFB6C1

BOW_DIVIDER = "https://media.discordapp.net/attachments/1483878740105887984/1500204166486823076/ffffdiv.png"
GIPHY_DIVIDER = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"

assigned_by_bot = set()

CLEAN_CHANNEL_IDS = {
    1484730031048491049: "only post real scammers. youll be warned if you send any nsfw messages.",
    1483988599337783448: "catfishing = ban <3"
}

LOG_CHANNEL_IDS = {
    1499948539424411863: GIPHY_DIVIDER,
    1499947145296351242: GIPHY_DIVIDER
}

# --- HELPER: RELAXED SEARCH ---
def find_role_relaxed(guild, search_text):
    """Lifts the requirement to copy decor exactly."""
    search_text = search_text.lower()
    # Check ID first
    rid = re.sub(r'\D', '', search_text)
    if rid and len(rid) > 15:
        role = guild.get_role(int(rid))
        if role: return role

    # Fuzzy match: Ignore case and check if search_text is inside the role name
    for role in guild.roles:
        # Clean the role name of special characters for comparison
        clean_name = re.sub(r'[^\w\s]', '', role.name).lower()
        clean_search = re.sub(r'[^\w\s]', '', search_text).lower()
        
        if clean_search in clean_name or search_text in role.name.lower():
            return role
    return None

# --- PERSISTENT GIVEAWAY VIEW ---
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = []

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary, custom_id="enter_giveaway")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            return await interaction.response.send_message("🐾 You already entered! meow", ephemeral=True)
        self.participants.append(interaction.user.id)
        await interaction.response.send_message("🐾 You've entered the giveaway! Good luck!", ephemeral=True)

# --- PERSISTENT VIEWS ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if any(r.id in AUTHORIZED_CLOSE_ROLES for r in interaction.user.roles):
            await interaction.response.send_message("🐾 Please type the **reason** for closing this ticket below:")
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                reason_msg = await bot.wait_for("message", timeout=60.0, check=check)
                reason = reason_msg.content
                
                for member in interaction.channel.members:
                    if not member.bot and not any(r.id in AUTHORIZED_CLOSE_ROLES for r in member.roles):
                        try:
                            embed = discord.Embed(title="🎫 Ticket Closed", color=HELP_HEX)
                            embed.description = f"Your ticket in **{SERVER_NAME_MOD}** has been closed.\n\n🐾 **Closed by:** {interaction.user}\n🐾 **Reason:** {reason}"
                            await member.send(embed=embed)
                        except: pass
                
                await interaction.channel.send(embed=discord.Embed(description="🐾 **Closing ticket...**\nDeleting in 5 seconds.", color=HELP_HEX))
                await asyncio.sleep(5); await interaction.channel.delete()
            except asyncio.TimeoutError:
                await interaction.channel.send("🐾 Close request timed out. Click the button to try again!")
        else: await interaction.response.send_message("🐾 Sorry, only staff can close tickets! meow", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="create ticket", style=discord.ButtonStyle.gray, emoji="<a:00_pusheenwork:1485859767543926804>", custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild, cat = interaction.guild, interaction.guild.get_channel(TICKET_CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        if staff_role: overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        chan = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
        await chan.send(embed=discord.Embed(description=f"🐾 **help needed for ekitten**\nHi {interaction.user.mention}! Explain your issue.", color=HELP_HEX))
        await chan.send(content=f"<@&{STAFF_ROLE_ID}>", embed=discord.Embed(description="α helper will be here shortly! meow", color=HELP_HEX), view=CloseTicketView())
        
        # FIXED: Added safety check for the response message
        try:
            await interaction.response.send_message(f"🐾 Ticket opened! {chan.mention}", ephemeral=True)
        except:
            pass

class TipsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.select(placeholder="click me!", custom_id="tips_dropdown", options=[discord.SelectOption(label="help", emoji="<a:1cutesy:1499882522685870100>"), discord.SelectOption(label="tips", emoji="<a:1cutesy:1499882522685870100>"), discord.SelectOption(label="awareness", emoji="<a:1cutesy:1499882522685870100>")])
    async def select_callback(self, interaction, select):
        selection = select.values[0]
        embeds = []
        if selection == "help":
            e1 = discord.Embed(title="profile set up!", color=HELP_HEX, description="your profile is the first thing that attracts anybody! we urge you all to stay AWAY from profiles that are suggestive, or look \"ageplayer\" like. you will be banned, not just from our server, but others. pick a modest, colorful, gothic, cute core, or decent profile picture, depending on your personality type! (you can find profile inspo in [vanity](https://discord.com/channels/1483873672208056511/1499947145296351242) and [persona](https://discord.com/channels/1483873672208056511/1499948539424411863))")
            e2 = discord.Embed(title="finding servers", color=HELP_HEX, description="we specifically target ask2dm servers, as they have a wide variety of people. we recommend you keep your dms turned on and allow server dms to recieve dms. we provide servers in <#1483873673692581982>\n\nonce you join these servers, complete set up and head over to the intros channels they provide and paste an intro!\n\nonce done, head over to their ask-to-dm channels and send a message. the message must include gender, age, and any extra message after (optional)\nformat f(age) dms open for anything!")
            e3 = discord.Embed(title="finding the right person", color=HELP_HEX, description="you may get multiple dms. it is heavily suggested that you do not open all at once! your account will be flagged for spam and you won't be able to accept message requests! finding the right person may be hard, but keep your chin up! never respond to any NSFW messages asking you to show anything inappropriate, or anything suggesting you show anything inappropriate \"for a price.\" block them. if so!")
            e4 = discord.Embed(title="getting the bag!", color=HELP_HEX, description="this will take some time! results arent fast. in order to receive payments, its recommended that you request they pay via gift cards if you do not want to give them your personal pay accounts. you can use cash app, paypal, zelle, etc! if you don't have USD, you can use gift cards as well!\n\nsend an amazon link to whatever gift card you prefer!")
            embeds = [e1, e2, e3, e4]
        elif selection == "tips":
            e1 = discord.Embed(title="001 digital footprint & safety", color=HELP_HEX, description="be mindful— do not share your full legal name, number, address, school/workplace it is highly recommended that you use multitudes of various accounts, social media(s), email(s), and payment method(s) turn off location tags on your photo(s) when sending pictures one (only when it’s yours!) avoid presenting yourself into constant availability (appearing reachable 24/7), avoid using your own face if you are a MINOR (-18)\ndecide and set your own boundaries early on, and stick by them (t.o.s & <#1483875248083439719> still apply.) be vigilant! you’re smart girls— do not click suspicious payment links, or any in general— period.")
            e2 = discord.Embed(title="002. server culture", color=HELP_HEX, description="this can (& does) apply to our rules we uphold and promote here as well; no pressuring others to pass a person around— serious guys. we don’t treat people like prostitutes. they notice when you are attempting to share them, don’t do that. you’ll ruin it for yourself and others! do not utilize another person’s information as your own— it’s rude, and not yours; we’re all here to help each other out.")
            e3 = discord.Embed(title="003. presenting your image", color=HELP_HEX, description="don’t be shy— put yourself out there! create a[n] intro, be thoughtful with information; don’t make it boring, plain or dry! this is a person’s first impression of you & factor if they reach out to you or not! we offer intro templates\nᲘ⑅𐑼 stagnating or being inactive in servers slows down your success rate of catching a person’s attention!\ninteract, have open ended convos— invite yourself in / invite others. friendly, modest & welcoming— those are the kind of things to get you noticed!\nᲘ⑅𐑼 watch your behavior avoid presenting pushy behavior early— it raises suspicion and concern avoid inserting things like “looking4edada” \"spoil me\" \"looking4owner\", you will be flagged or blacklisted for appearing as a seller / beggar. this is an SFW server. selling and begging is prohibited.")
            e4 = discord.Embed(title="004. photo choices & profile building", color=HELP_HEX, description="the world is your stage— play different characters ;3!\ndon’t limit yourself off just to one personality or one identity; have a variety!\nᲘ⑅𐑼 when looking for images, select them carefully— if you’re going to be a certain girl with certain characteristics, only choose images regarding it!\nex. girl w bangs, mid-shoulder hair, etc. (you’d only select images containing those characteristics) if you literally need to, make a pinterest board to keep track of your new personalities be mindful, none of these images are meant to be sent with an intent to sell it for a price; for the love of my ladies n tos— we do not sell here.\np.s. you have other resources, do NOT use our girls in <#1483988599337783448>!!")
            e5 = discord.Embed(title="005. patience is the one that pays ;3", color=HELP_HEX, description="yes, there is waiting and down time. let them find you through your intro— don’t be discouraged!\ndon’t attempt to rush the process. this process is meant to be slow and gradual. talk to them, get to know them more, make closure and build trust. just because you saw some lucky girl get it quicker than you or changed to not put in much work, doesn’t mean it’s like that for everyone. chances are it will/may be 2-3 weeks you are taking to a guy before you receive anything. as long as you uphold your patience, you can make a bag successfully hehe!")
            embeds = [e1, e2, e3, e4, e5]
        elif selection == "awareness":
            e1 = discord.Embed(color=HELP_HEX, description="if you feel hesitant, something feel’s off/sketchy or you’certain if you’re safe; please if applicable— take the quick route and block as soon as you feel in danger.\nᲘ⑅𐑼 if severity is amped; do not hesitate to reach out and bring in administration for help; if any do not respond, follow up the chain of command (helpers to mods to admin to owners) we’re always happy to help, and we value ensuring your safety babies! if it’s just uncertainty of how to answer a dm, and no severity or harm, feel free to ask other ladies; allow yourself to be open to different perspectives and opinions! ladies if you’re responding, administration or a member, please provide advice that falls under our server’s rules and t.o.s guidelines")
            e2 = discord.Embed(color=HELP_HEX, description="anybody who urges you to click α link, join α call, download an app, or give your password is trying to scam you or steal your information. be mindful.\nstay away from new accounts, anybody who claims to be α 'sugardaddy,' or anyone who wants you to pay first before receiving any type of payment!")
            embeds = [e1, e2]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

# --- STATUS TASK ---
@tasks.loop(seconds=15)
async def check_pinkie_status():
    for guild in bot.guilds:
        role = guild.get_role(PIC_PERMS_ROLE_ID)
        if not role: continue
        for member in guild.members:
            if member.bot: continue
            has_trigger = False
            for act in member.activities:
                if isinstance(act, discord.CustomActivity):
                    text = (str(act.name) if act.name else "") + (str(act.state) if act.state else "")
                    if STATUS_TRIGGER in text.lower(): has_trigger = True; break
            if has_trigger and role not in member.roles:
                try: 
                    await member.add_roles(role)
                    assigned_by_bot.add(member.id)
                except: pass
            elif not has_trigger and role in member.roles:
                if member.id in assigned_by_bot:
                    try: await member.remove_roles(role)
                    except: pass

# --- COMMANDS ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 **chocolα's help menu** 🎀", color=BABY_PINK)
    embed.add_field(name="🐾 **General**", value="`.help` | `.purge` | `.setup_ticket` | `.setuptips` | `.testboost` | `.div` ", inline=False)
    embed.add_field(name="🎁 **Events**", value="`.giveaway [time] [winners] [prize]` | `.reroll [msg_id]` ", inline=False)
    embed.add_field(name="🔨 **Moderation**", value="`.ban [user_id]` | `.unban [user_id]` | `.kick` | `.timeout` | `.untimeout` | `.role` | `.inrole` ", inline=False)
    embed.add_field(name="🖼️ **Profile**", value="`.av` | `.sav` | `.banner` | `.sbanner` | `.guildbanner` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def purge(ctx, amount: int):
    if not ctx.author.guild_permissions.manage_messages: return
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def giveaway(ctx, duration: str, winners: int, *, prize: str):
    """🐾 Example: .giveaway 3d 1 dual bayonets"""
    if not ctx.author.guild_permissions.manage_messages: return
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    seconds = int(duration[:-1]) * time_dict.get(duration[-1], 60)
    end_time = int(time.time() + seconds)
    
    embed = discord.Embed(title=prize, color=0x3498db)
    embed.description = (
        f"Click 🎉 button to enter!\n"
        f"Winners: **{winners}**\n"
        f"Ends: <t:{end_time}:R> (Timer)"
    )
    embed.set_footer(text=f"Ends at | {datetime.datetime.fromtimestamp(end_time).strftime('%m/%d/%Y')}")
    
    view = GiveawayView()
    g_msg = await ctx.send(embed=embed, view=view)
    
    await asyncio.sleep(seconds)
    
    if not view.participants:
        return await ctx.send(f"🐾 Giveaway for **{prize}** ended, but no one entered! meow")
    
    selected_winners = random.sample(view.participants, min(len(view.participants), winners))
    winner_mentions = ", ".join([f"<@{w_id}>" for w_id in selected_winners])
    
    await ctx.send(f"🎉 **CONGRATS** {winner_mentions}! You won **{prize}**!")
    
    embed.description = f"Giveaway Ended!\nWinners: {winner_mentions}"
    await g_msg.edit(embed=embed, view=None)

@bot.command()
async def reroll(ctx, msg_id: int):
    if not ctx.author.guild_permissions.manage_messages: return
    try:
        msg = await ctx.channel.fetch_message(msg_id)
        users = [u async for u in msg.reactions[0].users() if not u.bot]
        if users: await ctx.send(f"🎉 **REROLL!** Congrats <@{random.choice(users).id}>!")
    except: await ctx.send("🐾 Couldn't find that message or reactions!")

@bot.command()
async def inrole(ctx, *, role_input: str):
    """🐾 Example: .inrole members"""
    role = find_role_relaxed(ctx.guild, role_input)
    if not role: return await ctx.send(embed=discord.Embed(description="🐾 Role not found!", color=BABY_PINK))

    active_members = [m for m in role.members if ctx.guild.get_member(m.id)]
    if not active_members: return await ctx.send(embed=discord.Embed(description="🐾 No active members!", color=BABY_PINK))

    pages = [active_members[i:i + 15] for i in range(0, len(active_members), 15)]
    current_page = 0

    def get_page_embed(page_idx):
        pings = "\n".join([f"• {m.mention}" for m in pages[page_idx]])
        emb = discord.Embed(title=f"Members with {role.name}", description=pings, color=BABY_PINK)
        emb.set_footer(text=f"Page {page_idx + 1} of {len(pages)}")
        return emb

    message = await ctx.send(embed=get_page_embed(current_page))
    if len(pages) > 1:
        await message.add_reaction("⬅️"); await message.add_reaction("➡️")
        def check(r, u): return u == ctx.author and str(r.emoji) in ["⬅️", "➡️"] and r.message.id == message.id
        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "➡️" and current_page < len(pages)-1: current_page += 1
                elif str(reaction.emoji) == "⬅️" and current_page > 0: current_page -= 1
                await message.edit(embed=get_page_embed(current_page))
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError: break

@bot.command()
async def ban(ctx, target=None, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.ban_members: return
    if target is None: return await ctx.send("🐾 Please provide a User ID or mention!")
    
    # FIXED: Added safety block for Unknown User ID
    try:
        user_id = int(re.sub(r'\D', '', target))
        user = await bot.fetch_user(user_id)
    except:
        return await ctx.send("🐾 Meow! I couldn't find a user with that ID.")

    dm = discord.Embed(title="<a:000kitty:1484802888122503178> Meow! You've been Banned", color=HELP_HEX)
    dm.description = f"You have been banned from **{SERVER_NAME_MOD}**"
    dm.add_field(name="🐾 Reason:", value=reason, inline=False)
    try: await user.send(embed=dm)
    except: pass
    await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}"); await ctx.send(f"🐾 **{user.name}** banned.")

@bot.command()
async def unban(ctx, user_id=None):
    if not ctx.author.guild_permissions.ban_members: return
    if user_id is None: return await ctx.send("🐾 Provide an ID!")
    
    # FIXED: Added safety block for Unban
    try:
        user = await bot.fetch_user(int(user_id))
        await ctx.guild.unban(user)
        await ctx.send(f"🐾 Unbanned **{user.name}**.")
    except:
        await ctx.send("🐾 User not found in bans!")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.moderate_members: return
    await member.timeout(None)
    await ctx.send(f"🐾 Removed timeout from {member.mention}.")

@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.kick_members: return
    if member is None: return await ctx.send("🐾 Please mention a member!")
    dm = discord.Embed(title="<a:000kitty:1484802888122503178> Meow! You've been Kicked", color=HELP_HEX)
    dm.description = f"You have been kicked from **{SERVER_NAME_MOD}**"
    dm.add_field(name="🐾 Reason:", value=reason, inline=False)
    try: await member.send(embed=dm)
    except: pass
    await member.kick(reason=reason); await ctx.send(f"🐾 **{member.name}** kicked.")

@bot.command()
async def timeout(ctx, member: discord.Member = None, time_str: str = None, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.moderate_members: return
    if member is None or time_str is None: return await ctx.send("🐾 Use format: .timeout @user 10m reason")
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    duration = datetime.timedelta(seconds=int(time_str[:-1]) * time_dict[time_str[-1]])
    dm = discord.Embed(title="Meow! Time out! 🐱", description=f"Your talking privileges in **{SERVER_NAME_MOD}** have been suspended.", color=HELP_HEX)
    dm.add_field(name="🐾 Duration:", value=time_str, inline=False)
    dm.add_field(name="🐾 Reason:", value=reason, inline=False)
    try: await member.send(embed=dm)
    except: pass
    await member.timeout(duration, reason=reason); await ctx.send(f"🐾 **{member.name}** timed out.")

@bot.command()
async def role(ctx, member: discord.Member, *, role_input: str):
    if not ctx.author.guild_permissions.manage_roles: return
    role_obj = find_role_relaxed(ctx.guild, role_input)
    if not role_obj: return await ctx.send("🐾 Role not found!")
    if role_obj in member.roles: 
        await member.remove_roles(role_obj)
        await ctx.send(embed=discord.Embed(description=f"🐾 Removed **{role_obj.name}**", color=BABY_PINK))
    else: 
        await member.add_roles(role_obj)
        await ctx.send(embed=discord.Embed(description=f"🐾 Added **{role_obj.name}**", color=BABY_PINK))

@bot.command()
async def av(ctx, member: discord.Member = None):
    member = member or ctx.author
    url = member.avatar.url if member.avatar else member.default_avatar.url
    await ctx.send(embed=discord.Embed(title=f"🐾 {member.name}'s Avatar", color=BABY_PINK).set_image(url=url))

@bot.command()
async def sav(ctx, member: discord.Member = None):
    member = member or ctx.author
    if not member.guild_avatar: return await ctx.send("🐾 No server avatar!")
    await ctx.send(embed=discord.Embed(title=f"🐾 {member.name}'s Server Avatar", color=BABY_PINK).set_image(url=member.guild_avatar.url))

@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    if not user.banner: return await ctx.send("🐾 No banner!")
    await ctx.send(embed=discord.Embed(title=f"🐾 {member.name}'s Banner", color=BABY_PINK).set_image(url=user.banner.url))

@bot.command()
async def sbanner(ctx):
    if not ctx.guild.banner: return await ctx.send("🐾 No server banner!")
    await ctx.send(embed=discord.Embed(title=f"🐾 {ctx.guild.name}'s Banner", color=BABY_PINK).set_image(url=ctx.guild.banner.url))

@bot.command()
async def guildbanner(ctx): await sbanner(ctx)

@bot.command()
async def testboost(ctx):
    boost_chan = bot.get_channel(BOOST_CHANNEL_ID)
    if not boost_chan: return
    msg = (f"<:xx_blank1308798611726794793:1500174266396704875>\n"
           f"                          <a:0ggoki:1492955057359028365><a:0ggoki:1492955061662253140>\n"
           f"<:xx_blank1308798611726794793:1500174266396704875>     ﹒**thαnk you for boosting**\n"
           f"                     <a:000paw:1486941220222664843>     ֪ __kitten__ ⑅\n"
           f"                  . . ͡  ɞ {ctx.author.mention}")
    await boost_chan.send(msg)

@bot.command()
async def div(ctx): await ctx.send(GIPHY_DIVIDER)

@bot.command()
async def setup_ticket(ctx):
    channel = bot.get_channel(TICKET_PROMPT_CHANNEL_ID)
    if not channel: return
    await channel.send(BOW_DIVIDER)
    e = discord.Embed(color=HELP_HEX)
    e.description = ("<:xx_blank1308798611726794793:1500174266396704875>\n"
                     "꣑ৎ ࣪𓈒 ͜𓈒<:1cutesy:1487225560429105275> ༝⁺໒꒱ིྀ\n"
                     "<a:001heart:1494073417056649568>reαd <#1484554927794819232> before [ticket]\n"
                     "<a:001heart:1494073417056649568> click button to mαke α ticket!")
    e.set_footer(text="chocolα - narko mαde me!")
    await channel.send(embed=e, view=TicketView())
    await ctx.send("🐾 Ticket setup complete!")

@bot.command()
async def setuptips(ctx):
    channel = bot.get_channel(TIPS_CHANNEL_ID)
    if not channel: return
    await channel.send(BOW_DIVIDER)
    e = discord.Embed(color=HELP_HEX)
    e.description = ("꣑ৎ ࣪𓈒 ͜𓈒<:1cutesy:1487225560429105275> ༝⁺໒꒱ིྀ\n"
                     "**help <a:001heart:1494073417056649568> tips <a:001heart:1494073417056649568> αwαreness**\n"
                     "<a:001heart:1494073417056649568>use drop down menu below")
    await channel.send(embed=e, view=TipsView())
    await ctx.send("🐾 Staff tips sent!")

# --- UPDATED EVENT LOGIC WITH COMMAND SYNC ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.CustomActivity(name="koki made me <3"))
    
    # Force Discord to register slash commands immediately
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash command(s) meow!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        
    bot.add_view(TipsView()); bot.add_view(TicketView()); bot.add_view(CloseTicketView()); bot.add_view(GiveawayView())
    bot.add_view(EmbedDashboardView(None))
    if not check_pinkie_status.is_running(): check_pinkie_status.start()

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    cid, pid = message.channel.id, getattr(message.channel, "parent_id", None)
    if cid in CLEAN_CHANNEL_IDS or pid in CLEAN_CHANNEL_IDS:
        target = cid if cid in CLEAN_CHANNEL_IDS else pid
        msg = CLEAN_CHANNEL_IDS[target]
        async for old in message.channel.history(limit=10):
            if old.author == bot.user and old.content == msg: await old.delete(); break
        await message.channel.send(msg); return
    if cid in LOG_CHANNEL_IDS or pid in LOG_CHANNEL_IDS:
        target = cid if cid in LOG_CHANNEL_IDS else pid
        await message.channel.send(LOG_CHANNEL_IDS[target])
    await bot.process_commands(message)

# ==========================================
#         DYNAMIC EMBED DASHBOARD ENGINE
# ==========================================
DATA_PATH = "embeds.json"

def get_embed_data(name):
    if not os.path.exists(DATA_PATH): return None
    with open(DATA_PATH, "r") as f: data = json.load(f)
    return data.get(name)

def update_embed_data(name, key, val):
    data = {}
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f: data = json.load(f)
    if name not in data: data[name] = {}
    data[name][key] = val
    with open(DATA_PATH, "w") as f: json.dump(data, f, indent=4)

def build_custom_embed(name):
    cfg = get_embed_data(name)
    if not cfg: return discord.Embed(description="*This embed has no content yet.*", color=0xCCCCCC)
    
    col = int(cfg.get("color", "0xFFD4F4").replace("0x", ""), 16) if cfg.get("color") else 0xFFD4F4
    emb = discord.Embed(title=cfg.get("title"), description=cfg.get("description"), color=col)
    
    if cfg.get("author_name"):
        emb.set_author(name=cfg["author_name"], icon_url=cfg.get("author_icon"))
    if cfg.get("footer_text"):
        emb.set_footer(text=cfg["footer_text"], icon_url=cfg.get("footer_icon"))
    if cfg.get("image"): emb.set_image(url=cfg["image"])
    if cfg.get("thumbnail"): emb.set_thumbnail(url=cfg["thumbnail"])
    return emb

class BasicInfoModal(Modal):
    def __init__(self, embed_name):
        super().__init__(title=f"Editing Basic Info: {embed_name}")
        self.embed_name = embed_name
        cfg = get_embed_data(embed_name) or {}
        self.title_input = TextInput(label="Title", default=cfg.get("title", ""), required=False, placeholder="Enter embed title...")
        self.desc_input = TextInput(label="Description", style=discord.TextStyle.long, default=cfg.get("description", ""), required=False, placeholder="Enter main description...")
        self.color_input = TextInput(label="Hex Color", default=cfg.get("color", "0xFFD4F4"), required=False, placeholder="e.g. 0xFFD4F4")
        self.add_item(self.title_input); self.add_item(self.desc_input); self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        update_embed_data(self.embed_name, "title", self.title_input.value)
        update_embed_data(self.embed_name, "description", self.desc_input.value)
        update_embed_data(self.embed_name, "color", self.color_input.value)
        await interaction.response.edit_message(embed=build_custom_embed(self.embed_name), view=EmbedDashboardView(self.embed_name))

class AuthorModal(Modal):
    def __init__(self, embed_name):
        super().__init__(title=f"Editing Author: {embed_name}")
        self.embed_name = embed_name
        cfg = get_embed_data(embed_name) or {}
        self.auth_name = TextInput(label="Author Name", default=cfg.get("author_name", ""), required=False)
        self.auth_icon = TextInput(label="Author Icon URL", default=cfg.get("author_icon", ""), required=False)
        self.add_item(self.auth_name); self.add_item(self.auth_icon)

    async def on_submit(self, interaction: discord.Interaction):
        update_embed_data(self.embed_name, "author_name", self.auth_name.value)
        update_embed_data(self.embed_name, "author_icon", self.auth_icon.value)
        await interaction.response.edit_message(embed=build_custom_embed(self.embed_name), view=EmbedDashboardView(self.embed_name))

class FooterModal(Modal):
    def __init__(self, embed_name):
        super().__init__(title=f"Editing Footer: {embed_name}")
        self.embed_name = embed_name
        cfg = get_embed_data(embed_name) or {}
        self.foot_text = TextInput(label="Footer Text", default=cfg.get("footer_text", ""), required=False)
        self.foot_icon = TextInput(label="Footer Icon URL", default=cfg.get("footer_icon", ""), required=False)
        self.add_item(self.foot_text); self.add_item(self.foot_icon)

    async def on_submit(self, interaction: discord.Interaction):
        update_embed_data(self.embed_name, "footer_text", self.foot_text.value)
        update_embed_data(self.embed_name, "footer_icon", self.foot_icon.value)
        await interaction.response.edit_message(embed=build_custom_embed(self.embed_name), view=EmbedDashboardView(self.embed_name))

class ImagesModal(Modal):
    def __init__(self, embed_name):
        super().__init__(title=f"Editing Images: {embed_name}")
        self.embed_name = embed_name
        cfg = get_embed_data(embed_name) or {}
        self.main_img = TextInput(label="Main Image URL", default=cfg.get("image", ""), required=False)
        self.thumb_img = TextInput(label="Thumbnail URL", default=cfg.get("thumbnail", ""), required=False)
        self.add_item(self.main_img); self.add_item(self.thumb_img)

    async def on_submit(self, interaction: discord.Interaction):
        update_embed_data(self.embed_name, "image", self.main_img.value)
        update_embed_data(self.embed_name, "thumbnail", self.thumb_img.value)
        await interaction.response.edit_message(embed=build_custom_embed(self.embed_name), view=EmbedDashboardView(self.embed_name))

class EmbedDashboardView(View):
    def __init__(self, embed_name):
        super().__init__(timeout=None)
        self.embed_name = embed_name

    @discord.ui.button(label="edit basic information (color / title / description)", style=discord.ButtonStyle.gray, custom_id="dash_edit_basic")
    async def edit_basic(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("🐾 Staff only! meow", ephemeral=True)
        await interaction.response.send_modal(BasicInfoModal(self.embed_name))

    @discord.ui.button(label="edit author", style=discord.ButtonStyle.gray, custom_id="dash_edit_author")
    async def edit_author(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("🐾 Staff only! meow", ephemeral=True)
        await interaction.response.send_modal(AuthorModal(self.embed_name))

    @discord.ui.button(label="edit footer", style=discord.ButtonStyle.gray, custom_id="dash_edit_footer")
    async def edit_footer(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("🐾 Staff only! meow", ephemeral=True)
        await interaction.response.send_modal(FooterModal(self.embed_name))

    @discord.ui.button(label="edit images", style=discord.ButtonStyle.gray, custom_id="dash_edit_images")
    async def edit_images(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("🐾 Staff only! meow", ephemeral=True)
        await interaction.response.send_modal(ImagesModal(self.embed_name))

# --- COMMANDS TO RUN THE SYSTEM ---
@bot.tree.command(name="embed", description="Manage interactive embed setups")
async def embed_slash(interaction: discord.Interaction, action: str, name: str):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("🐾 Staff only! meow", ephemeral=True)
    
    if action.lower() == "create":
        update_embed_data(name, "created", True)
        desc = (
            f"⭐ **successfully created an embed called:** `{name}`\n"
            f"please select from the buttons below for what you'd like to edit!\n"
            f"alternatively, you can edit these individually in slash commands with `/embed edit`."
        )
        preview_emb = build_custom_embed(name)
        await interaction.response.send_message(content=desc, embed=preview_emb, view=EmbedDashboardView(name))

@bot.command()
async def setup(ctx, embed_name: str, target_channel: discord.TextChannel = None):
    if not ctx.author.guild_permissions.manage_messages: return
    channel = target_channel or ctx.channel
    cfg = get_embed_data(embed_name)
    if not cfg:
        return await ctx.send(f"🐾 I couldn't find an embed configuration named `{embed_name}`! Build it with `/embed` first.")
    
    final_embed = build_custom_embed(embed_name)
    assigned_view = None
    if "ticket" in embed_name.lower(): assigned_view = TicketView()
    elif "tips" in embed_name.lower(): assigned_view = TipsView()
    
    await channel.send(embed=final_embed, view=assigned_view)
    await ctx.send(f"🐾 Custom embed `{embed_name}` posted smoothly to {channel.mention}!")

token = os.environ.get('DISCORD_TOKEN')
if token: bot.run(token)
