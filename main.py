import discord
import os
from discord.ext import commands
import sqlite3

async def on_message(self, message):
    print('Message from {0.author}: {0.content}'.format(message))

initial_extensions = [
                        'cogs.watcher'
                    ]

bot = commands.Bot(command_prefix=".", description='iOS Notification Service', case_insensitive=True)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
    
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(details='for new Apple updates', state='for new Apple updates', name='for new Apple updates', type=discord.ActivityType.watching))
    print(f'Successfully logged in and booted...!')

    try:
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='configs';")
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
            print(f"Found new guild we didn't have in database {guild}, updating.")
            try:
                conn = sqlite3.connect('db.sqlite')
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO configs (server_id, iOS_role, macOS_role, iPadOS_role, watchOS_role, tvOS_role, logging_channel) VALUES (?, ?, ?, ?, ?, ?, ?);", (guild.id, -1, -1, -1, -1, -1, -1))
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
            c.execute("INSERT OR REPLACE INTO configs (server_id, iOS_role, macOS_role, iPadOS_role, watchOS_role, tvOS_role, logging_channel) VALUES (?, ?, ?, ?, ?, ?, ?);", (guild.id, -1, -1, -1, -1, -1, -1))
        finally:
            conn.close()

bot.run(os.environ.get('IOS_TOKEN'), bot=True, reconnect=True)
