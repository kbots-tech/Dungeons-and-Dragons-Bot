import discord
import aiohttp
import json

from discord.ext import commands
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class spells(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command(aliases=['spells', 's'])
    async def spell(self, ctx, *, args=None):
        try:

            async with self.session.get(f'{BASE_URL}/api/spells') as resp:
                data = json.loads(await resp.text())
            count = data['count']
            classes = data['results']
            url_list = {}
            for f in classes:
                url_list[f['name']] = f['url']
            if args:
                values = get_close_matches(args, url_list)
                args = values[0]

            if not args:
                embed = discord.Embed(title='D&D Spells', description=f'{count} total spells.', color=Color.red())


                count = 0
                field = ""
                for spell in url_list:
                    field += f"{spell}\n"
                    if count == 54:
                        embed.add_field(name='_ _', value=field)
                        field = ""
                        count = 0
                    count += 1

                embed.add_field(name='_ _', value=field)
                await ctx.send(embed=embed)
                return

            async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
                data = json.loads(await resp.text())

            embed = discord.Embed(
                title=args,
                description=f"\nLevel {data['level']} {data['school']['name']}",
                color=Color.red())

            embed.add_field(
                name='Casting Time',
                value=data['casting_time'],
                inline=False
            )

            embed.add_field(
                name='Range',
                value=data['range'],
                inline=False
            )

            if 'material' in data:
                embed.add_field(
                    name='Components',
                    value=f"{', '.join(data['components'])}\n{data['material']}",
                    inline=False
                )
            else:
                embed.add_field(
                    name='Components',
                    value=f"{', '.join(data['components'])}",
                    inline=False
                )

            embed.add_field(
                name='Duration',
                value=data['duration']
            )

            embed.add_field(
                name='Description',
                value=data['desc'][0],
                inline=False
            )

            if 'higher_level' in data:
                embed.add_field(
                    name='Higher Level',
                    value=data['higher_level'][0]
                )

            await ctx.send(embed=embed)

        except TimeoutError:
            pass
        except IndexError:
            await ctx.send(
                embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))


def setup(bot):
    bot.add_cog(spells(bot))