import discord
from discord.ext import commands
import random
import string
import asyncio
from boto.s3.connection import S3Connection
import os
s3 = S3Connection(os.environ['TOKEN'], os.environ['BOT_TOKEN'])

bot = commands.Bot(command_prefix='anon.')
channel = discord.TextChannel
server = discord.Guild


@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='the wheel of Anonification'))

@bot.command()
async def wipe(ctx, chan_target, sec: int):
        channel = ctx.channel

        for target_channel in ctx.guild.channels:
            if ("<#%d>" % target_channel.id) == chan_target:
                break

        for target_role in ctx.guild.roles:
            if target_role.name == target_channel.name:
                break

        await channel.send('Target channel set to delete after **%d** seconds. Send "❌" to delete channel manually' % sec)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '❌'

        async def delete_all(target_channel, target_role):
            await channel.send(f"Deleting {target_channel.mention}")
            await target_channel.delete()
            await channel.send("Deleted channel")
            try:
                await channel.send(f"Deleting {target_role.mention}")
                await target_role.delete()
                await channel.send("Deleted role")
            except NameError:
                await channel.send(f"Error deleting role: {target_role.mention}")

        try:
            await bot.wait_for('reaction_add',timeout=sec, check=check)
        except asyncio.TimeoutError:
            await channel.send("**%d** seconds reached, cleaning up..." % sec)
            await delete_all(target_channel, target_role)
        else:
            await delete_all(target_channel,target_role)


@bot.command(description="Setting up channels and roles to make server disposable")
async def dconfig(ctx):
    await ctx.send("Configuring server to be disposable...")
    # Check if there is a channel already named "disposable"
    for channel in ctx.guild.channels:
        if channel.name == "disposable":
            await ctx.send("Disposable channel found. Please delete or rename channel for complete anonification")
            return print("Channel already exists")
    # Check if there is a channel already named "Hidden Pass"
    for role in ctx.guild.roles:
        if role.name == "Hidden Pass":
            await role.delete()
            await ctx.send("Deleted role with name `Hidden Pass`, will be replaced with a new one")
            print("Deleted role with name 'Hidden Pass'")
    # Creating "Hidden Pass" role
    rname = ''.join(random.choice(string.digits + string.ascii_lowercase)
                    for _ in range(15))
    role = await ctx.guild.create_role(name=rname)
    global hrole
    hrole = role
    print("Created role:", role)
    # Creating "disposable" channel
    global random_channel_name
    random_channel_name = rname
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    created_channel = await ctx.guild.create_text_channel(rname, overwrites=overwrites)
    print("Created disposable channel with name of:", rname)
    await ctx.author.add_roles(role)
    await ctx.send(f"{created_channel.mention}")


@bot.command()
async def dinv(ctx):
    try:
        print(hrole)
    except NameError:
        await ctx.send("**Running set up process first...**")
        await ctx.invoke(bot.get_command("dconfig"))
    else:
        mentions = ctx.message.mentions
        for i in mentions:
            await i.add_roles(hrole)
        ctx.send("Granted access to mentions.")


bot.run(s3)
