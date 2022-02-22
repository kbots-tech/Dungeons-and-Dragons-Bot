import discord
import aiohttp
import json

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Option, Choice, OptionType

from cogs.paginator import Paginator
from discord import Color
from difflib import get_close_matches
from math import floor

BASE_URL = 'https://www.dnd5eapi.co'


class Monsters(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @interactions.extension_command(
        name="monster",
        description="Search through and get monster information",
        options=[
            Option(
                name="creature",
                description="What monster would you like to search for?",
                type=OptionType.STRING,
                required=False,
            ),
        ],
        scope=788518409532997632
    )
    async def _monster(self, ctx, creature=None):
        name = creature

        async with self.session.get(f'{BASE_URL}/api/monsters') as resp:
            data = json.loads(await resp.text())
        count = data['count']
        classes = data['results']
        url_list = {}
        for f in classes:
            url_list[f['name']] = f['url']

        if not name:
            embed = discord.Embed(
                title='D&D Monsters',
                description=f'{count} total monsters.',
                color=Color.red())
            class_names = ""
            for f in classes:
                if len(class_names) + len(f["name"]) > 1000:
                    embed.add_field(name='__Item List:__', value=class_names)
                    class_names = ""
                else:
                    class_names += f'\n*{f["name"]}*'

            embed.add_field(name='__Item List:__', value=class_names)
            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
            return
        else:
            values = get_close_matches(name, url_list)
            if not values:

                embed = discord.Embed(title=f'{name} not found', description='Please Try again.', color=Color.red())

                await ctx.send(
                embeds = [interactions.Embed(**embed.to_dict())])
                return
            name = values[0]

        async with self.session.get(f'{BASE_URL}{url_list[name]}') as resp:
            data = json.loads(await resp.text())

        page1 = discord.Embed(
            title=data['name'],
            description=f"{data['size']} {data['type']}, {data['alignment']}",
            color=Color.red()
        )
        speeds = []
        for speed in data['speed']:
            speeds.append(f"{speed}:{data['speed'][speed]}")
        fields = [
            ('Armor Class', data['armor_class'], False),
            ('Hit Points', f"{data['hit_points']} ({data['hit_dice']})", False),
            ('Speed', ', '.join(speeds), False),
            ('STR', f"{data['strength']} ({floor((data['strength'] - 10) / 2)})", True),
            ('DEX', f"{data['dexterity']} ({floor((data['dexterity'] - 10) / 2)})", True),
            ('CON', f"{data['constitution']} ({floor((data['constitution'] - 10) / 2)})", True),
            ('INT', f"{data['intelligence']} ({floor((data['intelligence'] - 10) / 2)})", True),
            ('WIS', f"{data['wisdom']} ({floor((data['wisdom'] - 10) / 2)})", True),
            ('CHA', f"{data['charisma']} ({floor((data['charisma'] - 10) / 2)})", True),
            ]
        skills = []
        saving_throws = []
        for prof in data['proficiencies']:
            if prof['value'] > 0:
                num = f"+{prof['value']}"
            else:
                num = prof['value']
            if 'Saving Throw:' in prof['proficiency']['name']:
                name = prof['proficiency']['name'].replace('Saving Throw:', '')
                saving_throws.append(f"{name} {num}")
            elif 'Skill:' in prof['proficiency']['name']:
                name = prof['proficiency']['name'].replace('Skill:', '')
                skills.append(f"{name} {num}")

        senses = []
        for sense in data['senses']:
            senses.append(f"{sense}:{data['senses'][sense]}")

        fields.append(('Saving Throws', ', '.join(saving_throws), False))
        fields.append(('Skills', ', '.join(skills), False))
        fields.append(('Senses', ', '.join(senses), False))

        fields.append(('Languages', data['languages'], False))

        fields.append(('Challenge Rating', data['challenge_rating'], False))

        names = []
        for condition in data['damage_immunities']:
            names.append(condition)
        fields.append(('Damage Immunities', ', '.join(names), False))

        names = []
        for condition in data['damage_resistances']:
            names.append(condition)
        fields.append(('Damage Resistance', ', '.join(names), False))

        names = []
        for condition in data['damage_vulnerabilities']:
            names.append(condition['name'])
        fields.append(('Damage Vulnerabilities', ', '.join(names), False))

        names = []
        for condition in data['condition_immunities']:
            names.append(condition['name'])
        fields.append(('Condition Immunities', ', '.join(names), False))

        abilities = ""
        for ability in data['special_abilities']:
            abilities += f"__*{ability['name']}*__\n{ability['desc']}\n"
        fields.append(('Special Abilities', abilities, False))

        for name, value, inline in fields:
            if (name and value):
                page1.add_field(name=name, value=value, inline=inline)


        page2 = discord.Embed(
            title=data['name'],
            description="__**Actions**__",
            color=Color.red()
        )
        fields = []
        for action in data['actions']:
            fields.append((action['name'], action['desc'], False))

        if 'legendary_actions' in data:
            if data['legendary_actions']:
                fields.append(("\n\n__**Legendary Actions**__", "** **", False))

            for action in data['legendary_actions']:
                fields.append((action['name'], action['desc'], False))

        for name, value, inline in fields:
            if(name and value):
                page2.add_field(name=name, value=value, inline=inline)

        embeds = [page1, page2]
        e = Paginator(bot=self.bot,
                      ctx=ctx,
                      embeds=embeds,
                      only=ctx.author)
        await e.start()

def setup(client):
    Monsters(client)
