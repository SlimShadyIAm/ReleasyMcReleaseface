# import asyncio
import discord
import feedparser
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
        print(data.entries[0]["title"])
        # get newest post date from cached data. any new post will have a date newer than this
        max_prev_date = max([something["published_parsed"] for something in self.data_old.entries])
        # track previous post names -- so we don't repost same one again
        prev_posts = [something["title"] for something in self.data_old.entries]
        # get new posts
        new_posts = [post for post in data.entries if checks(post, prev_posts, max_prev_date) ]
        # if there rae new posts
        if (len(new_posts) > 0):
            # check thier tags
            for post in new_posts:
                print(f'NEW GOOD ENTRY: {post.title} {post.link}')
                await post_update(post, self.bot)

        data_old = data
        
    @watcher.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

def checks(post, prev_posts, max_prev_date):
    filters = ["iOS", "watchOS", "macOS", "iPadOS", "tvOS"]
    device = post["title"].split(" ")[0]
    return post["published_parsed"] > max_prev_date and post["title"] not in prev_posts and device in filters

def post_update(post, bot):
    pass

def setup(bot):
    bot.add_cog(MembersCog(bot))
