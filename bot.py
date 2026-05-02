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
LOG_CHANNEL_IDS = {
    1499948539424411863: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif",
    1499947145296351242: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4yZ3o2OTB1ZnNldm54YnduczJzaHV3cHZpZ3R0MHM4bzdtaDIyZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/briNJuauNDIpnvidKl/giphy.gif"
}

BOOST_CHANNEL_ID = 1484728025059819611 
TIPS_CHANNEL_ID = 1484554927794819232
BABY_PINK = 0xFFB6C1
CUSTOM_PINK = 0xFFD4F4 # Your new hex

# --- DROPDOWN LOGIC ---
class TipsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="get started..",
        options=[
            discord.SelectOption(label="help", emoji="<a:1cutesy:1499882522685870100>"),
            discord.SelectOption(label="tips", emoji="<a:1cutesy:1499882522685870100>"),
            discord.SelectOption(label="awareness", emoji="<a:1cutesy:1499882522685870100>"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select):
        reqs = {
            "help": "example for neena",
            "tips": "example for neena",
            "awareness": "example for neena"
        }
        selection = select.values[0]
        # Sent as ephemeral so only the user can see it
        await interaction.response.send_message(reqs[selection], ephemeral=True)

# 3. COMMANDS
@bot.command()
@commands.has_permissions(administrator=True)
async def setuptips(ctx):
    channel = bot.get_channel(TIPS_CHANNEL_ID)
    if not channel:
        return await ctx.send("🐾 I couldn't find the channel!")

    # First message: The GIF
    await channel.send("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3hrOHAyOXVqbDBscXY4aW1icHM2MjM4bLIwbXRodnBmbHZoeGJxOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qWXr5zxyEE2fBgxYF5/giphy.gif")
    
    # Second message: The Embed with your EXACT layout
    embed = discord.Embed(color=CUSTOM_PINK)
    embed.description = (
        "<:xx_blank1308798611726794793:1500174266396704875>\n"
        "<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>꣑ৎ ࣪𓈒 ͜𓈒<:1cutesy:1487225560429105275> ༝⁺໒꒱ིྀ<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>\n"
        "<:xx_blank1308798611726794793:1500174266396704875>**help <a:001heart:1494073417056649568> tips <a:001heart:1494073417056649568> αwαreness<:xx_blank1308798611726794793:1500174266396704875>**\n\n"
        "<:xx_blank1308798611726794793:1500174266396704875><a:001heart:1494073417056649568>use drop down menu below\n"
        "<:xx_blank1308798611726794793:1500174266396704875><a:001heart:1494073417056649568>reαd before mαking α [ticket](https://discord.com/channels/1483873672208056511/1484049393387700336)\n"
        "<:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875><:xx_blank1308798611726794793:1500174266396704875>*⋆ ୨୧‧˚ ⋆ ୨୧‧˚* <a:1cutesy:1499882522685870100>"
    )
    
    await channel.send(embed=embed, view=TipsView())
    await ctx.send("🐾 Help & Tips menu is ready!")

# --- [OTHER ADMIN/GENERAL COMMANDS] ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    confirm = await ctx.send(f"🐾 successfully purged **{len(deleted)-1}** messages! meow")
    await asyncio.sleep(3)
    await confirm.delete()

# --- [EVENTS] ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.add_view(TipsView()) # Makes the view persistent

# [Your on_member_update and other events remain the same]

bot.run(os.environ.get('DISCORD_TOKEN'))