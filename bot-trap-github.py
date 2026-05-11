# Modules needed to run bot
import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta

# Sets the specific permissions this bot needs in order to function
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Sets the command prefix, by default it's set to "~"
bot = commands.Bot(command_prefix="~", intents=intents)

# Absurdly ugly regex to detect discord links even if they have special characters between each letter, this can absolutely be improved
invite_regex = re.compile(r"(d[^\w\s]*i[^\w\s]*s[^\w\s]*c[^\w\s]*o[^\w\s]*r[^\w\s]*d[^\w\s]*\.[^\w\s]*g[^\w\s]*g[^\w\s]*/|d[^\w\s]*i[^\w\s]*s[^\w\s]*c[^\w\s]*o[^\w\s]*r[^\w\s]*d[^\w\s]*\.[^\w\s]*c[^\w\s]*o[^\w\s]*m[^\w\s]*/[^\w\s]*i[^\w\s]*n[^\w\s]*v[^\w\s]*i[^\w\s]*t[^\w\s]*e[^\w\s]*/[^\w\s]*)", re.IGNORECASE)

# ---=+ BUTTONS +=---
class ModView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    def disable_all(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.user_id)

        # Bans the user and removes any recently sent messages, default is "7" days
        if member:
            await member.ban(reason="User banned for sending discord links", delete_message_days=7)

        # Establishes who made the decision to ban or unmute
        embed = interaction.message.embeds[0]
        embed.add_field(
            name="Moderator Action",
            value=f"🔨 {interaction.user} banned <@{self.user_id}>",
            inline=False
        )
        embed.color = discord.Color.dark_red()
        self.disable_all()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    @discord.ui.button(label="Unmute", style=discord.ButtonStyle.success)
    async def unmute(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.user_id)

        if member:
            await member.timeout(None)

        # Establishes who made the decision to ban or unmute
        embed = interaction.message.embeds[0]
        embed.add_field(
            name="Moderator Action",
            value=f"🔊 {interaction.user} unmuted <@{self.user_id}>",
            inline=False
        )
        embed.color = discord.Color.green()
        self.disable_all()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

# ---=+ MESSAGE SCANNING +=---
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot or not message.guild:
        return

    # Copy and paste the role ID's for those you want to be exempt from this bot
    exempt={}

    if any(role.id in exempt for role in message.author.roles):
        return

    if invite_regex.search(message.content):
        member = message.author

        # Timeout for 1 hour
        await member.timeout(timedelta(hours=1), reason="Posted invite link")

        # Delete recent messages in this channel
        def check(m):
            return m.author.id == member.id

        await message.channel.purge(limit=50, check=check)

        # Send review message, the channel must have this name in order for review messages to be properly sent
        review_channel = discord.utils.get(
            message.guild.text_channels,
            name="the-bot-trap"
        )

# ---=+ REVIEW MESSAGE +=---

        # Review message header
        embed = discord.Embed(
            title="<a:weewoo:895345166360121416> Invite Link Detected <a:weewoo:895345166360121416>",
            color=discord.Color.blue()
        )

        # Users profile picture
        embed.set_thumbnail(url=member.display_avatar.url)
        # Adding users information
        embed.add_field(name="User: ", value=f"{member.mention} *({member.id})*", inline=False)
        embed.add_field(
            name="Account Created: ",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=True
        )
        embed.add_field(
            name="Joined Server: ",
            value=discord.utils.format_dt(member.joined_at, style="F"),
            inline=True
        )
        # What they said and where
        embed.add_field(name="Message", value=f"`{message.content}`", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        invite_link = message.content

        await review_channel.send(invite_link, embed=embed, view=ModView(member.id))

# ---=+ COMMANDS +=---    

@bot.command(name="ping", description="A simple ping command.")
async def ping(ctx):
   await ctx.send("The Bot Trap is Online!")

# ---=+ RUN +=---
bot.run("your bot token here")