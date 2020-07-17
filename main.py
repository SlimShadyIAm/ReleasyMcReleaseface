import discord
from discord import Color, Embed
import os
from discord.ext import commands
import sqlite3


async def on_message(self, message):
    print('Message from {0.author}: {0.content}'.format(message))

initial_extensions = [
    'cogs.admin',
    'cogs.channel',
    'cogs.errhandle',
    'cogs.help',
    'cogs.info',
    'cogs.subscribe',
    'cogs.stats',
    'cogs.unsubscribe',
    'cogs.watcher',
]

bot = commands.Bot(command_prefix=".",
                   description='iOS Notification Service', case_insensitive=True)

if __name__ == '__main__':
    bot.remove_command("help")
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


@bot.event
async def on_ready():
    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(details='for new Apple updates', state='for new Apple updates', name='for new Apple updates', type=discord.ActivityType.watching))
    print(f'Successfully logged in and booted...!')
    try:
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        c.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='configs';")
        res = c.fetchone()
        if (res[0] == 0):
            c.execute("CREATE TABLE IF NOT EXISTS configs (server_id INTEGER PRIMARY KEY, iOS_role INTEGER, macOS_role INTEGER, iPadOS_role INTEGER, watchOS_role INTEGER, tvOS_role INTEGER, logging_channel INTEGER);")
            c.execute("CREATE UNIQUE INDEX idx_server_id ON configs (server_id);")
        conn.commit()
    finally:
        conn.close()

    for guild in bot.guilds:
        try:
            conn = sqlite3.connect('db.sqlite')
            c = conn.cursor()
            c.execute("SELECT * FROM configs WHERE server_id = ?;", (guild.id,))
            res = c.fetchall()
        finally:
            conn.close()

        if len(res) == 0:
            print(
                f"Found new guild we didn't have in database {guild}, updating.")
            try:
                conn = sqlite3.connect('db.sqlite')
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO configs (server_id, iOS_role, macOS_role, iPadOS_role, watchOS_role, tvOS_role, logging_channel) VALUES (?, ?, ?, ?, ?, ?, ?);",
                          (guild.id, -1, -1, -1, -1, -1, -1))
                conn.commit()
            finally:
                conn.close()


@bot.event
async def on_guild_join(guild):
    try:
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        c.execute("SELECT * FROM configs WHERE server_id = ?;", (guild.id,))
        res = c.fetchall()
    finally:
        conn.close()

    if len(res) == 0:
        print(f"Joined guild {guild}, updating database.")
        try:
            conn = sqlite3.connect('db.sqlite')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO configs (server_id, iOS_role, macOS_role, iPadOS_role, watchOS_role, tvOS_role, logging_channel) VALUES (?, ?, ?, ?, ?, ?, ?);",
                      (guild.id, -1, -1, -1, -1, -1, -1))
            conn.commit()
        finally:
            conn.close()
    intro = discord.Embed(title='Thank you for adding me to your guild!', color=Color(
        value=0x3f78eb), description=f'Here\'s a quick start guide. The command prefix is `{bot.command_prefix}`.`')
    intro.add_field(name="Set a channel to send updates to",
                    value="Without this, I won't send any updates when released. \nExample usage: `.channel set #general`", inline=False)
    intro.add_field(name="Subscribe to a device update",
                    value="Choose a device type to subscribe to. Possible devices: iOS, macOS, watchOS, iPadOS, tvOS. \nExample usage: `.subscribe ios`\nOptionally, you can set a role to ping when I post an update: `.susbcribe iOS <role name/ID/mention>`", inline=False)
    intro.add_field(name="Unsubscribe from a device update",
                    value="Changed your mind about a device? Use this command.\nExample usage: `.unsubscribe iOS`", inline=False)
    intro.add_field(name="Get an overview about your subscriptions",
                    value="Just run `.info`", inline=False)
    intro.add_field(name="Need help?",
                    value="Contact SlimShadyIAm#9999 on Discord, or [@SlimShadyDev](https://twitter.com/SlimShadyDev) on Twitter!", inline=False)

    channel = discord.utils.get(guild.channels, name="general")
    if channel is not None:
        await channel.send(embed=intro)
    else:
        channel = discord.utils.get(guild.channels, name="main")
        if channel is not None:
            await channel.send(embed=intro)
        else:
            try:
                channel = guild.channels[0]
                await channel.send(embed=intro)
            except:
                await guild.owner.send(embed=intro)
bot.run(os.environ.get('IOS_TOKEN'), bot=True, reconnect=True)
