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
TIPS_CHANNEL_ID = 1484554927794819232
BABY_PINK = 0xFFB6C1
HELP_HEX = 0xFFD4F4 
DIVIDER_IMAGE = "https://media.discordapp.net/attachments/1483878740105887984/1500204166486823076/ffffdiv.png?ex=69f79581&is=69f64401&hm=92badebe6ac0febaa25412e7128172c6b436d6210314c34f04275d4c48b8e8d2&=&format=webp&quality=lossless&width=2560&height=722"

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
            e1 = discord.Embed(title="profile set up!", color=HELP_HEX, description="your profile is the first thing that attracts anybody! we urge you all to stay AWAY from profiles that are suggestive, or look \"ageplayer\" like. you will be banned, not just from our server, but others. pick a modest, colorful, gothic, cute core, or decent profile picture, depending on your personality type! (you can find profile inspo in [vanity](https://discord.com/channels/1483873672208056511/1499947145296351242) and [persona](https://discord.com/channels/1483873672208056511/1499948539424411863)")
            e2 = discord.Embed(title="finding servers", color=HELP_HEX, description="we specifically target ask2dm servers, as they have a wide variety of people. we recommend you keep your dms turned on and allow server dms to recieve dms. we provide servers in <#1483873673692581982>\n\nonce you join these servers, complete set up and head over to the intros channels they provide and paste an intro!\n\nonce done, head over to their ask-to-dm channels and send a message. the message must include gender, age, and any extra message after (optional)\nformat f(age) dms open for anything!")
            e3 = discord.Embed(title="finding the right person", color=HELP_HEX, description="you may get multiple dms. it is heavily suggested that you do not open all at once! your account will be flagged for spam and you won't be able to accept message requests! finding the right person may be hard, but keep your chin up! never respond to any NSFW messages asking you to show anything inappropriate, or anything suggesting you show anything inappropriate \"for a price.\" block them. if so!")
            e4 = discord.Embed(title="getting the bag!", color=HELP_HEX, description="this will take some time! results arent fast. in order to receive payments, its recommended that you request they pay via gift cards if you do not want to give them your personal pay accounts. you can use cash app, paypal, zelle, etc! if you don't have USD, you can use gift cards as well!\n\nsend an amazon link to whatever gift card you prefer!")
            embeds = [e1, e2, e3, e4]
        elif selection == "tips":
            e1 = discord.Embed(title="001 digital footprint & safety", color=HELP_HEX, description="be mindful— do not share your full legal name, number, address, school/workplace it is highly recommended that you use multitudes of various accounts, social media(s), email(s), and payment method(s) turn off location tags on your photo(s) when sending pictures one (only when it’s yours!) avoid presenting yourself into constant availability (appearing reachable 24/7), avoid using your own face if you are a MINOR (-18)\ndecide and set your own boundaries early on, and stick by them (t.o.s & <#1483875248083439719> still apply.) be vigilant! you’re smart girls— do not click suspicious payment links, or any in general— period.")
            e2 = discord.Embed(title="002. server culture", color=HELP_HEX, description="this can (& does) apply to our rules we uphold and promote here as well; no pressuring others to pass a person around— serious guys. we don’t treat people like prostitutes. they notice when you are attempting to share them, don’t do that. you’ll ruin it for yourself and others! do not utilize another person’s information as your own— it’s rude, and not yours; we’re all here to help each other out.")
            e3 = discord.Embed(title="003. presenting your image", color=HELP_HEX, description="don’t be shy— put yourself out there! create a[n] intro, be thoughtful with information; don’t make it boring, plain or dry! this is a person’s first impression of you & factor if they reach out to you or not! we offer intro templates\nᲘ⑅𐑼 stagnating or being inactive in servers slows down your success rate of catching a person’s attention!\ninteract, have open ended convos— invite yourself in / invite others. friendly, modest & welcoming— those are the kind of things to get you noticed!\nᲘ⑅𐑼 watch your behavior avoid presenting pushy behavior early— it raises suspicion and concern avoid inserting things like “looking4edada” “spoil me” “looking4owner”, you will be flagged or blacklisted for appearing as a seller / beggar. this is an SFW server. selling and begging is prohibited.")
            e4 = discord.Embed(title="004. photo choices & profile building", color=HELP_HEX, description="the world is your stage— play different characters ;3!\ndon’t limit yourself off just to one personality or one identity; have a variety!\nᲘ⑅𐑼 when looking for images, select them carefully— if you’re going to be a certain girl with certain characteristics, only choose images regarding it!\nex. girl w bangs, mid-shoulder hair, etc. (you’d only select images containing those characteristics) if you literally need to, make a pinterest board to keep track of your new personalities be mindful, none of these images are meant to be sent with an intent to sell it for a price; for the love of my ladies n tos— we do not sell here.\np.s. you have other resources, do NOT use our girls in <#1483988599337783448>!!")
            e5 = discord.Embed(title="005. patience is the one that pays ;3", color=HELP_HEX, description="yes, there is waiting and down time. let them find you through your intro— don’t be discouraged!\ndon’t attempt to rush the process. this process is meant to be slow and gradual. talk to them, get to know them more, make closure and build trust. just because you saw some lucky girl get it quicker than you or claimed to not put in much work, doesn’t mean it’s like that for everyone. chances are it will/may be 2-3 weeks you are taking to a guy before you receive anything. as long as you uphold your patience, you can make a bag successfully hehe!")
            embeds = [e1, e2, e3, e4, e5]
        elif selection == "awareness":
            e1 = discord.Embed(color=HELP_HEX, description="if you feel hesitant, something feel’s off/sketchy or you’re uncertain if you’re safe; please if applicable— take the quick route and block as soon as you feel in danger.\nᲘ⑅𐑼 if severity is amped; do not hesitate to reach out and bring in administration for help; if any do not respond, follow up the chain of command (helpers to mods to admin to owners) we’re always happy to help, and we value ensuring your safety babies! if it’s just uncertainty of how to answer a dm, and no severity or harm, feel free to ask other ladies; allow yourself to be open to different perspectives and opinions! ladies if you’re responding, administration or a member, please provide advice that falls under our server’s rules and t.o.s guidelines")
            e2 = discord.Embed(color=HELP_HEX, description="anybody who urges you to click α link, join α call, download an app, or give your password is trying to scam you or steal your information. be mindful.\nstay away from new accounts, anybody who claims to be α 'sugardaddy,' or anyone who wants you to pay first before receiving any type of payment!")
            embeds = [e1, e2]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

# 3. COMMANDS
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 **chocolα's help menu** 🎀", description="Here are the commands available for you, kitties!", color=BABY_PINK)
    embed.add_field(name="🐾 **General**", value="`.help` | `.purge [amount]` | `.inrole [role]` | `.role [user] [name]` | `.testboost` | `.setuptips`", inline=False)
    embed.add_field(name="🖼️ **Profile**", value="`.av` | `.sav` | `.banner` | `.sbanner` | `.guildbanner`", inline=False)
    embed.add_field(name="🔨 **Moderation**", value="`.ban [user] [reason]` | `.kick [user] [reason]` | `.timeout [user] [time] [reason]`", inline=False)
    embed.add_field(name="🎁 **Giveaways**", value="`.giveaway [time] [prize]` | `.reroll [msg_id]`", inline=False)
    await ctx.send(embed=embed)

# --- MODERATION COMMANDS (with DM fail warning) ---
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    embed = discord.Embed(title=f"<a:000kitty:1484802888122503178> Meow! You've been Banned from {ctx.guild.name}", color=HELP_HEX)
    embed.description = "You've been permanently banned from this server."
    embed.add_field(name="🐾 Reason:", value=reason, inline=False)
    embed.add_field(name="🐾 Appeal:", value="If you believe this was a mistake, please contact administration elsewhere.", inline=False)
    
    dm_sent = True
    try: await member.send(embed=embed)
    except: dm_sent = False
    
    await member.ban(reason=reason)
    msg = f"🐾 **{member.name}** has been banned. meow!"
    if not dm_sent: msg += "\n⚠️ *I couldn't DM the user (DMs closed), but they were still banned.*"
    await ctx.send(msg)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    embed = discord.Embed(title=f"<a:000kitty:1484802888122503178> Meow! You've been kicked from {ctx.guild.name}", color=HELP_HEX)
    embed.description = "You've been kicked from the server."
    embed.add_field(name="🐾 Reason:", value=reason, inline=False)
    
    dm_sent = True
    try: await member.send(embed=embed)
    except: dm_sent = False
    
    await member.kick(reason=reason)
    msg = f"🐾 **{member.name}** has been kicked. meow!"
    if not dm_sent: msg += "\n⚠️ *I couldn't DM the user (DMs closed), but they were still kicked.*"
    await ctx.send(msg)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, time: str, *, reason="No reason provided"):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = time[-1]
    if unit not in time_dict: return await ctx.send("🐾 Use a valid time (10m, 1h, etc)!")
    seconds = int(time[:-1]) * time_dict[unit]
    duration = datetime.timedelta(seconds=seconds)
    
    embed = discord.Embed(title=f"Meow! Time out! <a:000kitty:1484802888122503178>", color=HELP_HEX)
    embed.description = "Your talking privileges have been temporarily suspended. :3"
    embed.add_field(name="🐾 Duration:", value=time, inline=False)
    embed.add_field(name="🐾 Reason:", value=reason, inline=False)
    
    dm_sent = True
    try: await member.send(embed=embed)
    except: dm_sent = False
    
    await member.timeout(duration, reason=reason)
    msg = f"🐾 **{member.name}** has been timed out for {time}."
    if not dm_sent: msg += "\n⚠️ *I couldn't DM the user (DMs closed), but they were still timed out.*"
    await ctx.send(msg)

# --- UTILITY COMMANDS ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    confirm = await ctx.send(f"🐾 successfully purged **{len(deleted)-1}** messages! meow")
    await asyncio.sleep(3)
    await confirm.delete()

@bot.command()
async def inrole(ctx, *, role: discord.Role):
    # This command now works with full names including decor
    members = role.members
    if not members:
        return await ctx.send(f"🐾 No one has the **{role.name}** role yet!")
    
    member_pings = "\n".join([f"• {m.mention}" for m in members])
    # Handle long lists to avoid embed character limits
    if len(member_pings) > 2000:
        member_pings = member_pings[:1990] + "\n...and more!"
        
    embed = discord.Embed(title=f"Members with {role.name}", description=member_pings, color=BABY_PINK)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setuptips(ctx):
    channel = bot.get_channel(TIPS_CHANNEL_ID)
    if not channel: return await ctx.send("🐾 I couldn't find the channel!")
    await channel.send(DIVIDER_IMAGE)
    embed = discord.Embed(color=HELP_HEX)
    embed.description = (
        "<:xx_blank1308798611726794793:1500174266396704875>\n"
        "<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>꣑ৎ ࣪𓈒 ͜𓈒<:1cutesy:1487225560429105275> ༝⁺໒꒱ིྀ<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>\n"
        "<:xx_blank1308798611726794793:1500174266396704875>**help <a:001heart:1494073417056649568> tips <a:001heart:1494073417056649568> αwαreness<:xx_blank1308798611726794793:1500174266396704875>**\n\n"
        "<:xx_blank1308798611726794793:1500174266396704875><a:001heart:1494073417056649568>use drop down menu below\n"
        "<:xx_blank1308798611726794793:1500174266396704875><a:001heart:1494073417056649568>reαd before mαking α [ticket](https://discord.com/channels/1483873672208056511/1484049393387700336)\n"
        "<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>*⋆ ୨୧‧˚ ⋆ ୨୧‧˚* <a:1cutesy:1499882522685870100>"
    )
    await channel.send(embed=embed, view=TipsView())
    await ctx.send("🐾 Help system sent!")

# --- [ADD ALL OTHER COMMANDS: role, av, banner, giveaway, etc] ---

# 5. EVENTS
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.add_view(TipsView())

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    current_id = message.channel.id
    parent_id = getattr(message.channel, "parent_id", None)
    
    # GIF/Auto-response logic
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