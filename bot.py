import discord   # type: ignore
import datetime
import time
from discord.ext import commands    # type: ignore
from datetime import datetime, timedelta
from collections import defaultdict, deque
from discord.ext.commands import Bot # type: ignore

intents = discord.Intents.all()

bot = Bot(command_prefix=".", intents=intents)
guild_regions = {}


@bot.group(name="Mhelp", invoke_without_command=True)
async def help_command(ctx):
    embed = discord.Embed(
        title="Help Command which will help you use this bot ",
        description="Use `Mhelp <commanf>` for more information on a specific command.__*The prfix of this bot is *__  __*( . )*__",
        color=discord.Color.green()
    )
    embed.add_field(name="__*General Commands*__", value="`Mhelp`, `list`, `ping`", inline=False)
    embed.add_field(name="__*Moderation Commands*__", value="`ban`, `kick`, `unban`", inline=False)
    embed.add_field(name="__*Information Commands*__", value="`userinfo` , `serverinfo`", inline=False)
    embed.add_field(name="__*Mute & Unmute Commands*__", value="`mute` , `unmute`", inline=False)
    embed.add_field(name="__*Massages maagement Commands*__", value="`delet_massages` , `manage_massages`", inline=False)
    embed.add_field(name="__*Region selection Commands*__", value="`setregion`", inline=False)
    embed.add_field(name="__*verification Commands*__", value="`v!{username}`", inline=False)
    embed.add_field(name="__*Member count  Commands*__", value="`member_count`", inline=False)
    embed.add_field(name="__*Whitelist Commands*__", value="`add_whitelist` , `remove_whitelist`", inline=False)
    embed.add_field(name="__*AFK Commands*__", value="`afk`", inline=False)
    embed.set_footer(text="Developed and designed by Intruder")

    await ctx.send(embed=embed)

# Member count 

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def member_count(ctx):
    """Displays the total number of members in the server."""
    guild = ctx.guild
    member_count = guild.member_count

    # Create an embed object
    embed = discord.Embed(title="Member Count", color=discord.Color.blue())
    embed.add_field(name="Total Members", value=str(member_count), inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
    color=discord.Color.green()

    await ctx.send(embed=embed)


# List command to show all available commands

@bot.command(name='list')
async def list_commands(ctx):
    commands_list = [command.name for command in bot.commands]
    commands_text = "\n".join(commands_list)
    embed = discord.Embed(title="Commands You Get In THe Bot", description=commands_text, color=discord.Color.blue())
    await ctx.send(embed=embed)

# Example commands for testing
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def greet(ctx):
    await ctx.send("Hello!")    

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked for {reason}!')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned for {reason}!')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'User {user} has been unbanned!')
            return
            

@bot.command()
async def setregion(ctx, *, region: str):
    guild = ctx.guild
    guild_regions[guild.id] = region
    await ctx.send(f"Region for {guild.name} has been set to {region}.")

# Configuration: messages and time limit
SPAM_MESSAGE_LIMIT = 3  # Number of messages to trigger spam detection
SPAM_TIME_LIMIT = 5  # Time window in seconds

# Tracking user messages
user_messages = defaultdict(lambda: deque(maxlen=SPAM_MESSAGE_LIMIT))

# Anti-Spam Check
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    current_time = time.time()
    user_id = message.author.id

    # Add the current message's timestamp to the user's deque
    user_messages[user_id].append(current_time)

    # Check if the user is spamming
    if len(user_messages[user_id]) == SPAM_MESSAGE_LIMIT:
        time_diff = current_time - user_messages[user_id][0]
        if time_diff < SPAM_TIME_LIMIT:
            await message.channel.send(f"⚠️ {message.author.mention}, please stop spamming!")
            # Optionally, you could mute, kick, or ban the user
            # For example:
            # await message.author.kick(reason="Spamming")
    
    # Process commands after anti-spam checks
    await bot.process_commands(message)

# Command to adjust spam settings (optional)
@bot.command()
@commands.has_permissions(administrator=True)
async def set_spam_limit(ctx, message_limit: int, time_limit: int):
    global SPAM_MESSAGE_LIMIT, SPAM_TIME_LIMIT
    SPAM_MESSAGE_LIMIT = message_limit
    SPAM_TIME_LIMIT = time_limit
    await ctx.send(f"Anti-spam settings updated: {SPAM_MESSAGE_LIMIT} messages in {SPAM_TIME_LIMIT} seconds.")

# Create or get the "Muted" role

async def get_or_create_muted_role(guild):
    muted_role = discord.utils.get(guild.roles, name="Muted")
    if not muted_role:
        muted_role = await guild.create_role(name="Muted", reason="Muted role needed for muting members.")
        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)
    return muted_role

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = await get_or_create_muted_role(ctx.guild)
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🔇 {member.mention} has been muted.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 {member.mention} has been unmuted.")
    else:
        await ctx.send(f"{member.mention} is not muted.")

# Ensure the bot has the necessary permissions
@mute.error
@unmute.error
async def mute_unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member to mute/unmute.")
    else:
        await ctx.send("An error occurred while processing the command.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def delete_messages(ctx):
    """Deletes the top 200 messages sent within the last 3 hours."""
    now = datetime.utcnow()
    three_hours_ago = now - timedelta(hours=3)

    # Fetch the last 200 messages in the channel
    messages = await ctx.channel.history(limit=200).flatten()

    # Filter messages that are within the last 3 hours
    messages_to_delete = [msg for msg in messages if msg.created_at >= three_hours_ago]

    # Bulk delete the filtered messages
    if messages_to_delete:
        await ctx.channel.delete_messages(messages_to_delete)
        await ctx.send(f"🗑️ Deleted {len(messages_to_delete)} messages sent in the last 3 hours.")
    else:
        await ctx.send("No messages found in the last 3 hours to delete.")


# Serverinfo Command
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    region = guild_regions.get(guild.id, "None")

    embed = discord.Embed(  
        title=f"Server Info - {guild.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Verification Level", value=str(guild.verification_level), inline=True)

    await ctx.send(embed=embed)
    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Userinfo Command
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author  # Use the command invoker if no member is specified

    embed = discord.Embed(
        title=f"User Info - {member}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Discriminator", value=f"#{member.discriminator}", inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=member.status, inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

    await ctx.send(embed=embed)

# whitelist command 

whitelisted_users = []

@bot.command()
@commands.has_permissions(administrator=True)
async def add_whitelist(ctx, user: discord.Member):
    """Adds a user to the whitelist."""
    if user.id not in whitelisted_users:
        whitelisted_users.append(user.id)
        embed = discord.Embed(title="Whitelist Update", color=discord.Color.green())
        embed.add_field(name="User Added", value=f"{user.name} has been added to the whitelist.", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Whitelist Update", color=discord.Color.orange())
        embed.add_field(name="User Already Whitelisted", value=f"{user.name} is already in the whitelist.", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def remove_whitelist(ctx, user: discord.Member):
    """Removes a user from the whitelist."""
    if user.id in whitelisted_users:
        whitelisted_users.remove(user.id)
        embed = discord.Embed(title="Whitelist Update", color=discord.Color.red())
        embed.add_field(name="User Removed", value=f"{user.name} has been removed from the whitelist.", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Whitelist Update", color=discord.Color.orange())
        embed.add_field(name="User Not Whitelisted", value=f"{user.name} is not in the whitelist.", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

def is_whitelisted():
    def predicate(ctx):
        return ctx.author.id in whitelisted_users
    return commands.check(predicate)

@bot.command()
@is_whitelisted()
async def secret_command(ctx):
    """A command only accessible to whitelisted users."""
    embed = discord.Embed(title="Secret Command Access", color=discord.Color.blue())
    embed.add_field(name="Access Granted", value="You have access to the secret command!", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)






bot.run('YOUR TOCKEN')

