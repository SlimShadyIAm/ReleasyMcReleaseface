# import asyncio
import discord
import feedparser
import sqlite3
from discord.ext import commands, tasks

class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feed = "https://developer.apple.com/news/releases/rss/releases.rss"
        self.data_old = feedparser.parse(self.feed)
        self.loop = self.watcher.start()
    
    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=20.0)
    async def watcher(self):
        data = feedparser.parse(self.feed)
        # has the feed changed?
        # get newest post date from cached data. any new post will have a date newer than this
        max_prev_date = max([something["published_parsed"] for something in self.data_old.entries])
        # track previous post names -- so we don't repost same one again
        prev_posts = [something["title"] for something in self.data_old.entries]
        # get new posts
        # new_posts = [post for post in data.entries if checks(post, prev_posts, max_prev_date) ]
        new_posts = [post for post in data.entries if checks(post, prev_posts, max_prev_date) ]
        # if there rae new posts
        if (len(new_posts) > 0):
            # check thier tags
            for post in new_posts:
                print(f'NEW GOOD ENTRY: {post.title} {post.link}')
                await check_new_entries(post, self.bot)

        self.data_old = data
        
    @watcher.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

def checks(post, prev_posts, max_prev_date):
    filters = ["iOS", "watchOS", "macOS", "iPadOS", "tvOS"]
    device = post["title"].split(" ")[0]
    # TEST CODE
    # return post["published_parsed"] > max_prev_date and post["title"] not in prev_posts and device in filters
    return device in filters

async def check_new_entries(post, bot):
    device = post["title"].split(" ")[0]
    try:
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        c.execute("SELECT * FROM configs")
        res = c.fetchall()
    finally:
        conn.close()
    
    for guild in res:
        # TEST CODE
        # if guild[6] == -1:
        #     continue
        
        index = {
            "iOS": 1,
            "macOS": 2,
            "iPadOS": 3,
            "watchOS": 4,
            "tvOS": 5,
        }[device]
        
        role_id = guild[index]
        # TEST CODE
        role_id = 525250808447631370

        if role_id != -1:
            await push_update(bot, guild, device, role_id, post)

async def push_update(bot, guild_info, device, role_id, post):
    guild = bot.get_guild(guild_info[0])

    if guild is None:
        return

    guild_channels = guild.channels
    # TEST CODE
    # channel = discord.utils.get(guild_channels, id=guild_info[6])
    channel = discord.utils.get(guild_channels, id=621704381053534257)

    if channel is None:
        return
    
    await channel.send(f'<@&{role_id}> New release! {post["title"]}\n{post["link"]}')

def setup(bot):
    bot.add_cog(MembersCog(bot))
