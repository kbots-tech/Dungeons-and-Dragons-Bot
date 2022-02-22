import discord
import aiohttp
import json
from discord import Color
from difflib import get_close_matches
import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Option, Choice, OptionType

BASE_URL = 'https://www.dnd5eapi.co'


class Spells(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @interactions.extension_command(
        name="spell",
        description="Search through and get spell information",
        options=[
            Option(
                name="name",
                description="What spell would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ],scope=788518409532997632

    )
    async def _spell(self, ctx, name=None):
        try:
            async with self.session.get(f'{BASE_URL}/api/spells') as resp:
                data = json.loads(await resp.text())
            count = data['count']
            classes = data['results']
            url_list = {}
            for f in classes:
                url_list[f['name']] = f['url']
            if name:
                values = get_close_matches(name, url_list)
                name = values[0]

            if not name:
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
                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
                return

            async with self.session.get(f'{BASE_URL}{url_list[name]}') as resp:
                data = json.loads(await resp.text())

            embed = discord.Embed(
                title=name,
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

            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])

        except TimeoutError:
            pass
        except IndexError:
            discord.Embed(title=f'{name} not found', description='Please Try again.', color=Color.red())
            await ctx.send(
                embeds=[interactions.Embed(**embed.to_dict())]
            )


def setup(client):
    Spells(client)