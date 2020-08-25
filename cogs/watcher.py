# import asyncio
import sqlite3
from os import path
from os.path import abspath, dirname
import time
import discord
import feedparser
from discord import Color, Embed
from discord.ext import commands, tasks
from asyncio import sleep
import sys
import traceback


class FeedObject:
    def __init__(self, name, url, checks):
        self.name = name
        self.url = url
        self.data_old = feedparser.parse(self.url)
        self.titles_old = [something["title"]
                           for something in self.data_old.entries]
        self.checks = checks


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.feeds = [
            FeedObject(
                "releases", "https://developer.apple.com/news/releases/rss/releases.rss", self.releases_checks),
            FeedObject(
                "newsroom", "https://www.apple.com/newsroom/rss-feed.rss", self.newsroom_checks)
        ]
        self.loop = self.watcher.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=60.0)
    async def watcher(self):
        for feed in self.feeds:
            data = feedparser.parse(feed.url)
            if len(data.entries) != 0:
                # has the feed changed?
                # get newest post date from cached data. any new post will have a date newer than this
                max_prev_date = max([something["published_parsed" if feed.name !=
                                               "newsroom" else "updated_parsed"] for something in feed.data_old.entries])

                # get new posts
                new_posts = [post for post in data.entries if feed.checks(
                    feed, post, max_prev_date)]
                # if there rae new posts
                if (len(new_posts) > 0):
                    # check thier tags
                    for post in new_posts:
                        print(f'NEW GOOD ENTRY: {post.title} {post.link}')
                        feed.titles_old.append(post.title)
                        await check_new_entries(post, self.bot, newsroom=feed.name == "newsroom")

                feed.data_old = data

    @ watcher.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    def releases_checks(self, feed, post, max_prev_date):
        filters = ["iOS", "watchOS", "macOS", "iPadOS", "tvOS"]
        device = post["title"].split(" ")[0]
        return post["published_parsed"] > max_prev_date and post["title"] not in feed.titles_old and device in filters

    def newsroom_checks(self, feed, post, max_prev_date):
        return post["updated_parsed"] > max_prev_date and post["title"] not in feed.titles_old

    @ watcher.error
    async def error(self, error):
        print("A watcher error occured")
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)
        await sleep(10)
        self.watcher.restart()


async def check_new_entries(post, bot, newsroom=False):
    device = post["title"].split(" ")[0] if not newsroom else "newsroom"
    BASE_DIR = dirname(dirname(abspath(__file__)))
    db_path = path.join(BASE_DIR, "db.sqlite")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM configs")
        res = c.fetchall()
    finally:
        conn.close()

    for guild in res:
        # PROD CODE
        if guild[6] == -1:
            continue

        index = {
            "iOS": 1,
            "macOS": 2,
            "iPadOS": 3,
            "watchOS": 4,
            "tvOS": 5,
            "newsroom": 7,
        }[device]

        role_id = guild[index]
        # TEST CODE
        # role_id = 525250808447631370

        if role_id != -1:
            print(
                f"pushing update of {device} to Guild {[guild[0]]}, pinging role {role_id}")
            await push_update(bot, guild, device, role_id, post)


async def push_update(bot, guild_info, device, role_id, post):
    guild = bot.get_guild(guild_info[0])

    if guild is None:
        return

    # TEST CODE
    channel = discord.utils.get(guild.channels, id=guild_info[6])
    # channel = discord.utils.get(guild_channels, id=621704381053534257)

    if channel is None:
        return

    if role_id == 0:
        await channel.send(f'New release! {post["title"]}\n{post["link"]}')
    else:
        role = discord.utils.get(guild.roles, id=role_id)
        if role.is_default():
            role = "@everyone"

        if role is not None:
            await channel.send(f'{role.mention if isinstance(role, discord.Role) else role} New release! {post["title"]}\n{post["link"]}')
        else:
            await channel.send(f'New release! {post["title"]}\n{post["link"]}')
            await channel.send(embed=Embed(title="Warning", color=Color(value=0xeba64d), description=f"It looks like role {role_id} doesn't exist. Please change this using `.subscribe devicename role`."))


def setup(bot):
    bot.add_cog(MembersCog(bot))
