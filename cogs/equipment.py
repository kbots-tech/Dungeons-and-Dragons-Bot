import discord
import aiohttp
import json

from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from discord_slash import cog_ext
from ButtonPaginator import Paginator
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class Equipment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        with open("items.json") as file:
            self.items = json.load(file)

    @cog_ext.cog_slash(
        name="equipment",
        description="Search through and get equipment information",
        options=[
            create_option(
                name="name",
                description="What equipment would you like to search for?",
                option_type=3,
                required=False,
            ),
        ]
    )
    async def _equipment(self, ctx, rename=None):
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

                await ctx.send(embed=embed)
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

            await ctx.send(embed=embed)
        except IndexError:
            await ctx.send(
                embed=discord.Embed(title=f'{rename} not found', description='Please Try again.', color=Color.red()))

    @commands.command(aliases=['w','weapon'])
    async def weapons(self, ctx, *, args=None):
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

            await ctx.send(embed=embed)
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Weapons']['items']])
            if values:
                await self.equipment(ctx, args=values[0])
            else:
                await ctx.send(
                    embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))

    @commands.command(aliases=['t', 'tool'])
    async def tools(self, ctx, *, args=None):
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

            await ctx.send(embed=embed)
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Tools']['items']])
            if values:
                await self.equipment(ctx, args=values[0])
            else:
                await ctx.send(embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))

    @commands.command(aliases=['a'])
    async def armor(self, ctx, *, args=None):
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

            await ctx.send(embed=embed)
            return
        else:
            values = get_close_matches(args, [item['name'] for item in self.items['Armor']['items']])
            if values:
                await self.equipment(ctx, args=values[0])
            else:
                await ctx.send(
                    embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))

def setup(bot):
    bot.add_cog(Equipment(bot))
