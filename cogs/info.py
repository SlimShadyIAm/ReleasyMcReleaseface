import asyncio
import sqlite3
import sys
import traceback
from os import path
from os.path import abspath, dirname

import discord
from discord import Color, Embed
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info')
    @commands.has_permissions(manage_guild=True)
    async def info(self, ctx):
        """Get info on subscribed devices, channnel where messages are sent"""

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
            guild_info = res[0]
            channel = discord.utils.get(ctx.guild.channels, id=guild_info[6])
            desc = f"New updates will be posted in {channel.mention}" if channel is not None else "You have not set a channel where updates go to! please use `.channel` to set this.\n**No updates will be posted until you do so.**\nPlease see `.help channel`"
            embed = Embed(title=f"Info for {ctx.guild}", color=Color(
                value=0x37b83b), description=desc)
            embed.set_footer(
                text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)

            devices = ['iOS', 'macOS', 'iPadOS', 'watchOS', 'tvOS']

            for i, device in enumerate(devices, start=1):
                role = discord.utils.get(ctx.guild.roles, id=guild_info[i])
                if role is not None and role.is_default():
                    embed.add_field(
                        name=device, value=f"@everyone will be pinged", inline=True)
                elif guild_info[i] == 0:
                    embed.add_field(
                        name=device, value="No role will be pinged", inline=True)
                elif guild_info[i] == -1:
                    embed.add_field(
                        name=device, value="Not subscribed", inline=True)
                else:
                    if role is not None:
                        embed.add_field(
                            name=device, value=f"{role.mention} will be pinged", inline=True)
                    else:
                        embed.add_field(
                            name=device, value="An invalid role is set, please fix this! Please use `.subscribe` (see `.help subscribe` for details)", inline=False)
            await ctx.send(embed=embed)
            return
        await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'An unforseen error occured, contact SlimShadyIAm#9999 (code: DB_INFO_ERR'))

    # err handling
    @info.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}'))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description="You need `MANAGE_SERVER` permission to run this command."))
        else:
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}. Send a screenshot of this error to SlimShadyIAm#9999'))
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Utilities(bot))
