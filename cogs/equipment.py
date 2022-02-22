import discord
import aiohttp
import json

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Option, Choice, OptionType

from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class Equipment(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        with open("items.json") as file:
            self.items = json.load(file)

    @interactions.extension_command(
        name="equipment",
        description="Search through and get equipment information, inludes armor tools and weapons",
        options=[
            Option(
                name="rename",
                description="What equipment would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ]
    )
    async def _equipment(self, ctx, name=None):
        rename = name
        try:
            async with self.session.get(f'{BASE_URL}/api/equipment') as resp:
                data = json.loads(await resp.text())
            count = data['count']
            classes = data['results']
            url_list = {}
            for f in classes:
                url_list[f['name']] = f['url']
            if rename:
                values = get_close_matches(rename, url_list)
                rename = values[0]

            if not rename:
                embed = discord.Embed(title='D&D Equipment', description=f'{count} total items.', color=Color.red())
                for category in self.items:
                    per = int(len(self.items[category]['items'])/3)+1
                    count = 0
                    field = ""
                    embed.add_field(name=category, value='_ _', inline=False)
                    for item in self.items[category]['items']:
                        count+=1
                        if count == per:
                            count = 0
                            embed.add_field(name="_ _", value=field)
                            field = ""
                        field+=f"{item['name']}\n"

                    embed.add_field(name="_ _" , value=field)
                    field = ""

                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
                return

            async with self.session.get(f'{BASE_URL}{url_list[rename]}') as resp:
                data = json.loads(await resp.text())

            fields = []
            embed = discord.Embed(
                title=data['name'],
                color=Color.red()
            )
            embed.set_footer(text=data['equipment_category']['name'])
            if data['equipment_category']['name'] == "Armor":
                embed.title = f"{embed.title} Armor"
                embed.description = f"{data['armor_category']} armor"
                embed.add_field(
                    name='Cost',
                    value=f"{data['cost']['quantity']}{data['cost']['unit']}",
                    inline=True
                )

                if data['armor_class']['dex_bonus']:
                    dex = "+ DEX"
                else:
                    dex = ""
                embed.add_field(
                    name='AC',
                    value=f"{data['armor_class']['base']}{dex}",
                    inline=True
                )
                if data['str_minimum']:
                    embed.add_field(
                        name='STR Min',
                        value=data['str_minimum'],
                        inline=True
                    )
                embed.add_field(name="_ _", value="_ _", inline=False)

                embed.add_field(
                    name='Stealth Disdavantage',
                    value=data['stealth_disadvantage']
                )

                embed.add_field(
                    name='Weight',
                    value=data['weight']
                )
            elif data['equipment_category']['name'] == "Weapon":
                embed.description = data['weapon_category']
                embed.add_field(
                    name='Cost',
                    value=f"{data['cost']['quantity']}{data['cost']['unit']}",
                    inline=True
                )


                embed.add_field(
                    name='Damage',
                    value=f"{data['damage']['damage_dice']} {data['damage']['damage_type']['name']}"
                )
                embed.add_field(name='_ _', value='_ _', inline=False)

                embed.add_field(
                    name='Weight',
                    value=data['weight']
                )

                embed.add_field(
                    name='Properties',
                    value= '\n'.join([property['name'] for property in data['properties']])
                )


                if data['weapon_range'] == 'Ranged':
                    embed.add_field(
                        name='Range',
                        value=f"Normal: {data['range']['normal']} {data['range']['long']}",
                        inline=False
                    )


                embed.add_field(name="_ _", value="_ _", inline=False)
            elif data['equipment_category']['name'] == "Tools":
                if 'desc' in data:
                    embed.description = f"\n{data['desc'][0]}"

                embed.add_field(
                    name='Cost',
                    value=f"{data['cost']['quantity']}{data['cost']['unit']}",
                    inline=True
                )
                embed.add_field(
                    name='Weight',
                    value=data['weight']
                )
            elif data['equipment_category']['name'] == "Adventuring Gear":
                if 'desc' in data:
                    embed.description = data['desc'][0]
                elif 'contents' in data:
                    embed.description = f"Includes: {', '.join([item['item']['name']+' x'+str(item['quantity']) for item in data['contents']])}"

                embed.add_field(
                    name='Cost',
                    value=f"{data['cost']['quantity']}{data['cost']['unit']}",
                    inline=True
                )

                if 'weight' in data:
                    embed.add_field(
                        name='Weight',
                        value=data['weight']
                    )
            elif data['equipment_category']['name'] == "Mounts and Vehicles":

                embed.description = data['vehicle_category']

                if 'speed' in data:
                    embed.add_field(
                        name='Speed',
                        value=f"{data['speed']['quantity']} {data['speed']['unit']}"
                    )

                if 'capacity' in data:
                    embed.add_field(
                        name='Capacity',
                        value=data['capacity']
                    )

                embed.add_field(name='_ _', value='_ _', inline=True)

                embed.add_field(
                    name='Cost',
                    value=f"{data['cost']['quantity']}{data['cost']['unit']}",
                    inline=True
                )

                if 'weight' in data:
                    embed.add_field(
                        name='Weight',
                        value=data['weight']
                    )

            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
        except IndexError:
            embed = discord.Embed(title=f'{rename} not found', description='Please Try again.', color=Color.red())
            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])

    @interactions.extension_command(
        name="weapon",
        description="Search through and get weapon information",
        options=[
            Option(
                name="name",
                description="What armor would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ]
    )
    async def weapons(self, ctx, *, name=None):
        args = name
        if not args:
            embed = discord.Embed(title='D&D Equipment', description=f"{len(self.items['Weapons']['items'])} total items.", color=Color.red())
            count=0
            field = ''
            per = int(len(self.items['Weapons']['items'])/3)+1
            for item in self.items['Weapons']['items']:
                count += 1
                if count == per:
                    count = 0
                    embed.add_field(name="_ _", value=field)
                    field = ""
                field += f"{item['name']}\n"

            embed.add_field(name="_ _", value=field)
            field = ""

            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Weapons']['items']])
            if values:
                await self._equipment(ctx, name=values[0])
            else:
                embed = discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red())
                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
    @interactions.extension_command(
        name="tools",
        description="Search through and get tools information",
        options=[
            Option(
                name="name",
                description="What tool would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ]
    )
    async def tools(self, ctx, *, name=None):
        args = name
        if not args:
            embed = discord.Embed(title='D&D Equipment',
                                  description=f"{len(self.items['Tools']['items'])} total items.", color=Color.red())
            count = 0
            field = ''
            per = int(len(self.items['Tools']['items']) / 3) + 1
            for item in self.items['Tools']['items']:
                count += 1
                if count == per:
                    count = 0
                    embed.add_field(name="_ _", value=field)
                    field = ""
                field += f"{item['name']}\n"

            embed.add_field(name="_ _", value=field)
            field = ""

            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Tools']['items']])
            if values:
                await self._equipment(ctx, name=values[0])
            else:
                embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red())
                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])

    @interactions.extension_command(
        name="armor",
        description="Search through and get armor information",
        options=[
            Option(
                name="name",
                description="What armor would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ],scope = 788518409532997632
    )
    async def armor(self, ctx, name=None):
        args=name
        if not args:
            embed = discord.Embed(title='D&D Equipment',
                                  description=f"{len(self.items['Armor']['items'])} total items.", color=Color.red())
            count = 0
            field = ''
            per = int(len(self.items['Armor']['items']) / 3) + 1
            for item in self.items['Armor']['items']:
                count += 1
                if count == per:
                    count = 0
                    embed.add_field(name="_ _", value=field)
                    field = ""
                field += f"{item['name']}\n"

            embed.add_field(name="_ _", value=field)
            field = ""

            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Armor']['items']])
            if values:
                await self._equipment(ctx, name=values[0])
            else:

                embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red())
                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])

def setup(client):
    Equipment(client)
