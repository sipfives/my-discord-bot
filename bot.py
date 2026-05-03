import discord
from discord.ext import commands, tasks
import os
import asyncio
import random
import datetime

# 1. Permissions Setup
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.presences = True        
intents.moderation = True 

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# 2. Configuration (Triple-check these IDs in your server!)
TICKET_CATEGORY_ID = 1484550188885475348
TICKET_PROMPT_CHANNEL_ID = 1484049393387700336
TIPS_CHANNEL_ID = 1484554927794819232
BOOST_CHANNEL_ID = 1484728025059819611 
STAFF_ROLE_ID = 1483887906031669278

AUTHORIZED_CLOSE_ROLES = [
    1483887906031669278, # Staff
    1483884626605768785, # Manager
    1484294120510853200, # Admin
    1484041123390423110  # Owner/Specialist
]

STATUS_ROLE_NAME = "pic"
STATUS_TRIGGER = "/pinkie"
HELP_HEX = 0xFFD4F4 
BABY_PINK = 0xFFB6C1
DIVIDER_IMAGE = "https://media.discordapp.net/attachments/1483878740105887984/1500204166486823076/ffffdiv.png"

CLEAN_CHANNEL_IDS = {
    1484730031048491049: "only post real scammers. youll be warned if you send any nsfw messages.",
    1483988599337783448: "catfishing = ban <3"
}

LOG_CHANNEL_IDS = {
    1499948539424411863: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif",
    1499947145296351242: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"
}

# --- CLOSE BUTTON LOGIC ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_role_ids = [role.id for role in interaction.user.roles]
        is_staff = any(role_id in AUTHORIZED_CLOSE_ROLES for role_id in user_role_ids)
        if not is_staff:
            return await interaction.response.send_message("🐾 Sorry, only staff can close tickets! meow", ephemeral=True)
        
        embed = discord.Embed(description="🐾 **Closing ticket...**\nThis channel will be deleted in 5 seconds.", color=HELP_HEX)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- TICKET SYSTEM LOGIC ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="create ticket", style=discord.ButtonStyle.gray, emoji="<a:00_pusheenwork:1485859767543926804>")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category: return await interaction.response.send_message("🐾 Error: Category not found.", ephemeral=True)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role: overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        
        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        
        embed1 = discord.Embed(description=f"🐾 **help needed for ekitten**\n\nHi {interaction.user.mention}! Please describe your issue or question here.", color=HELP_HEX)
        await channel.send(embed=embed1)
        
        embed2 = discord.Embed(description="α helper will be here with you shortly! meow", color=HELP_HEX)
        await channel.send(content=f"<@&{STAFF_ROLE_ID}>", embed=embed2, view=CloseTicketView())
        await interaction.response.send_message(f"🐾 Ticket opened! {channel.mention}", ephemeral=True)

# --- DROPDOWN LOGIC ---
class TipsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="click me!",
        options=[
            discord.SelectOption(label="help", emoji="<a:1cutesy:1499882522685870100>"),
            discord.SelectOption(label="tips", emoji="<a:1cutesy:1499882522685870100>"),
            discord.SelectOption(label="awareness", emoji="<a:1cutesy:1499882522685870100>"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select):
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
            e5 = discord.Embed(title="005. patience is the one that pays ;3", color=HELP_HEX, description="yes, there is waiting and down time. let them find you through your intro— don’t be discouraged!\ndon’t attempt to rush the process. this process is meant to be slow and gradual. talk to them, get to know them more, make closure and build trust. just because you saw some lucky girl get it quicker than you or claimed to not put in much work, doesn’t mean it’s like that for everyone. chances are it will/may be 2-3 weeks you are taking to a guy before you receive anything. as long as you uphold your patience, you can make a bag successfully hehe!")
            embeds = [e1, e2, e3, e4, e5]
        elif selection == "awareness":
            e1 = discord.Embed(color=HELP_HEX, description="if you feel hesitant, something feel’s off/sketchy or you’re uncertain if you’re safe; please if applicable— take the quick route and block as soon as you feel in danger.\nᲘ⑅𐑼 if severity is amped; do not hesitate to reach out and bring in administration for help; if any do not respond, follow up the chain of command (helpers to mods to admin to owners) we’re always happy to help, and we value ensuring your safety babies! if it’s just uncertainty of how to answer a dm, and no severity or harm, feel free to ask other ladies; allow yourself to be open to different perspectives and opinions! ladies if you’re responding, administration or a member, please provide advice that falls under our server’s rules and t.o.s guidelines")
            e2 = discord.Embed(color=HELP_HEX, description="anybody who urges you to click α link, join α call, download an app, or give your password is trying to scam you or steal your information. be mindful.\nstay away from new accounts, anybody who claims to be α 'sugardaddy,' or anyone who wants you to pay first before receiving any type of payment!")
            embeds = [e1, e2]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

# --- BACKGROUND TASK ---
@tasks.loop(seconds=30)
async def check_pinkie_status():
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=STATUS_ROLE_NAME)
        if not role: continue
        for member in guild.members:
            if member.bot: continue
            has_trigger = False
            for act in member.activities:
                if isinstance(act, discord.CustomActivity):
                    text = (act.name or "") + (act.state or "")
                    if STATUS_TRIGGER in text.lower(): has_trigger = True; break
            if has_trigger and role not in member.roles:
                try: await member.add_roles(role)
                except: pass
            elif not has_trigger and role in member.roles:
                try: await member.remove_roles(role)
                except: pass

# --- COMMANDS ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 **chocolα's help menu** 🎀", color=BABY_PINK)
    embed.add_field(name="🐾 **General**", value="`.help` | `.purge` | `.setup_ticket` | `.setuptips` | `.testboost` ", inline=False)
    embed.add_field(name="🎁 **Events**", value="`.giveaway [time] [prize]` | `.reroll [msg_id]` ", inline=False)
    embed.add_field(name="🔨 **Moderation**", value="`.ban` | `.kick` | `.timeout` | `.role` | `.inrole` ", inline=False)
    embed.add_field(name="🖼️ **Profile**", value="`.av` | `.sav` | `.banner` | `.sbanner` | `.guildbanner` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def giveaway(ctx, duration: str, *, prize: str):
    if not ctx.author.guild_permissions.manage_messages: return
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    seconds = int(duration[:-1]) * time_dict.get(duration[-1], 60)
    embed = discord.Embed(title="🎀 **KITTEN PARADISE GIVEAWAY** 🎀", description=f"React with 🎉!\n\n**Prize:** {prize}\n**Ends in:** {duration}", color=BABY_PINK)
    g_msg = await ctx.send(embed=embed); await g_msg.add_reaction("🎉")
    await asyncio.sleep(seconds)
    new_msg = await ctx.channel.fetch_message(g_msg.id)
    users = [u async for u in new_msg.reactions[0].users() if not u.bot]
    if not users: await ctx.send("No entries. 💔")
    else: await ctx.send(f"🎉 **CONGRATS** <@{random.choice(users).id}>! You won **{prize}**!")

@bot.command()
async def reroll(ctx, message_id: int):
    if not ctx.author.guild_permissions.manage_messages: return
    msg = await ctx.channel.fetch_message(message_id)
    users = [u async for u in msg.reactions[0].users() if not u.bot]
    if not users: await ctx.send("No entries found.")
    else: await ctx.send(f"🎉 **NEW WINNER:** <@{random.choice(users).id}>!")

@bot.command()
async def setup_ticket(ctx):
    if not ctx.author.guild_permissions.administrator: return
    channel = bot.get_channel(TICKET_PROMPT_CHANNEL_ID)
    await channel.send(DIVIDER_IMAGE)
    e = discord.Embed(color=HELP_HEX)
    e.description = ("<:xx_blank1308798611726794793:1500174266396704875>\n"
                     "꣑ৎ ࣪𓈒 ͜𓈒<:1cutesy:1487225560429105275> ༝⁺໒꒱ིྀ\n"
                     "<a:001heart:1494073417056649568> click button to mαke α ticket!\n"
                     "*⋆ ୨୧‧˚ ⋆ ୨୧‧˚* <a:1cutesy:1499882522685870100>")
    await channel.send(embed=e, view=TicketView())
    await ctx.send("🐾 Ticket setup sent!")

@bot.command()
async def setuptips(ctx):
    if not ctx.author.guild_permissions.administrator: return
    channel = bot.get_channel(TIPS_CHANNEL_ID)
    await channel.send(DIVIDER_IMAGE)
    e = discord.Embed(color=HELP_HEX)
    e.description = ("<a:001heart:1494073417056649568> use drop down menu below\n"
                     "*⋆ ୨୧‧˚ ⋆ ୨୧‧˚* <a:1cutesy:1499882522685870100>")
    await channel.send(embed=e, view=TipsView())
    await ctx.send("🐾 Tips setup sent!")

@bot.command()
async def purge(ctx, amount: int):
    if not ctx.author.guild_permissions.manage_messages: return
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def role(ctx, member: discord.Member, *, search: str):
    if not ctx.author.guild_permissions.manage_roles: return
    rid = search.replace("<@&", "").replace(">", "")
    if rid.isdigit(): r = ctx.guild.get_role(int(rid))
    else: r = discord.utils.find(lambda x: search.lower() in x.name.lower(), ctx.guild.roles)
    if not r: return await ctx.send("🐾 Not found!")
    if r in member.roles: await member.remove_roles(r); await ctx.send(f"🐾 Removed {r.name}")
    else: await member.add_roles(r); await ctx.send(f"🐾 Added {r.name}")

@bot.command(aliases=['avatar'])
async def av(ctx, member: discord.Member = None):
    member = member or ctx.author
    url = member.avatar.url if member.avatar else member.default_avatar.url
    await ctx.send(embed=discord.Embed(title=f"🐾 {member.name}'s Avatar", color=BABY_PINK).set_image(url=url))

@bot.event
async def on_ready():
    print(f'Logged in αs {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="discord.gg/pinkie - narko/vanilla made me"))
    bot.add_view(TipsView()); bot.add_view(TicketView()); bot.add_view(CloseTicketView())
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

token = os.environ.get('DISCORD_TOKEN')
if token: bot.run(token)
else: print("❌ ERROR: DISCORD_TOKEN not found!")
