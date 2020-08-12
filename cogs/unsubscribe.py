import asyncio
from os import path
from os.path import abspath, dirname
import sqlite3
import sys
import traceback

import discord
from discord import Color, Embed
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unsubscribe')
    @commands.has_permissions(manage_guild=True)
    async def unsubscribe(self, ctx, device: str):
        """Unsubscribe from updates from a certain device/feed.\n
        Available devices: iOS, macOS, watchOS, iPadOS, tvOS, Newsroom\n
        Example usage: `.unsubscribe ios`"""

        devices = {"ios": "iOS_role",
                   "macos": "macOS_role",
                   "watchos": "watchOS_role",
                   "ipados": "iPadOS_role",
                   "tvos": "tvOS_role",
                   "newsroom": "newsroom_role"
                   }

        devices_proper = {"ios": "iOS",
                          "macos": "macOS",
                          "watchos": "watchOS",
                          "ipados": "iPadOS",
                          "tvos": "tvOS",
                          "newsroom": "Newsroom"
                          }
        device = device.lower()

        if device not in devices.keys():
            raise commands.BadArgument(
                "Please supply a valid device/feed to subscribe to.\nAvailable devices: iOS, macOS, watchOS, iPadOS, tvOS, Newsroom\n i.e `!unsubscribe macos`.")

        BASE_DIR = dirname(dirname(abspath(__file__)))
        db_path = path.join(BASE_DIR, "db.sqlite")
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM configs WHERE server_id = ?;",
                      (ctx.guild.id,))
            res = c.fetchall()
        finally:
            conn.close()

        if len(res) == 1:
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute(f"UPDATE configs SET {devices[device]} = ? WHERE server_id = ?;", (
                    -1, ctx.guild.id,))
                conn.commit()
            finally:
                conn.close()

            embed = Embed(title="Done!", color=Color(
                value=0x37b83b), description=f'You have unsubscribed from {devices_proper[device]} notifications.')
            embed.set_footer(
                text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'An unforseen error occured, contact SlimShadyIAm#9999 (code: DB_SUBSCRIBE_ERR'))
    # err handling

    @unsubscribe.error
    async def unsubscribe_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}'))
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error} See `.help unsubscribe` if you need help.'))
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description="You need `MANAGE_SERVER` permission to run this command."))
            return
        else:
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}. Send a screenshot of this error to SlimShadyIAm#9999'))
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            return


def setup(bot):
    bot.add_cog(Utilities(bot))
