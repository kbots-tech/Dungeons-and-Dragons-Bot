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


class classes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @cog_ext.cog_slash(
        name="classes",
        guild_ids=[788518409532997632],
        options=[
            create_option(
                name="args",
                description="What class would you like to search for?",
                option_type=3,
                required=False,
            ),
            create_option(
                name="levels",
                description="Include this option to view class levels.",
                option_type=1,
                required=False,
            ),
        ]
    )
    async def _classes(self, ctx, args=None, level=None):

        page = 0
        while True:
            try:
                if not embed_data:
                    async with self.session.get(f'{BASE_URL}/api/classes') as resp:
                        data = json.loads(await resp.text())
                    count = data['count']
                    classes = data['results']
                    url_list = {}
                    for f in classes:
                        url_list[f['name']] = f['url']
                    if args:
                        values = get_close_matches(args, url_list)
                        args = values[0]

                if level:
                    if not embed_data:
                        async with self.session.get(f'{BASE_URL}{url_list[args]}/levels') as resp:
                            data = json.loads(await resp.text())
                    else:
                        data = embed_data
                    if page == len(data):
                        page = page - 1

                    embed = discord.Embed(title=args, description=f'Level {page + 1}', color=Color.red())
                    try:
                        fields = [('Ability Score Bonuses', data[page]['ability_score_bonuses'], True)]
                    except KeyError:
                        fields = [('Ability Score Bonuses', 0, True)]
                    try:
                        fields.append(('Proficiency Bonus', data[page]['prof_bonus'], True))
                    except:
                        fields.append(('Proficiency Bonus', 0, True))

                    features = ""
                    for feat in data[page]['features']:
                        async with self.session.get(f'{BASE_URL}{feat["url"]}') as resp:
                            desc = json.loads(await resp.text())['desc'][0]
                        features += f"__*{feat['name']}*__\n{desc}\n\n"
                    if not features:
                        features = "N/A"
                    fields.append(('Features', features, False))

                    feature_choices = ""
                    for choice in data[page]['features']:
                        feature_choices += f"_{choice['name']}_\n"
                    if not feature_choices:
                        feature_choices = "N/A"
                    fields.append(('Feature Choices', feature_choices, False))

                    try:
                        spells = f"_Cantrips Known:_ {data[page]['spellcasting']['cantrips_known']}\n"
                        try:
                            spells += f"_Spells Known:_ {data[page]['spellcasting']['spells_known']}\n"
                        except KeyError:
                            pass
                        spells += f"_Level 1 Spells:_ {data[page]['spellcasting']['spell_slots_level_1']}\n"
                        spells += f"_Level 2 Spells:_ {data[page]['spellcasting']['spell_slots_level_2']}\n"
                        spells += f"_Level 3 Spells:_ {data[page]['spellcasting']['spell_slots_level_3']}\n"
                        spells += f"_Level 4 Spells:_ {data[page]['spellcasting']['spell_slots_level_4']}\n"
                        spells += f"_Level 5 Spells:_ {data[page]['spellcasting']['spell_slots_level_5']}\n"
                        spells += f"_Level 6 Spells:_ {data[page]['spellcasting']['spell_slots_level_6']}\n"
                        spells += f"_Level 7 Spells:_ {data[page]['spellcasting']['spell_slots_level_7']}\n"
                        spells += f"_Level 8 Spells:_ {data[page]['spellcasting']['spell_slots_level_8']}\n"
                        spells += f"_Level 9 Spells:_ {data[page]['spellcasting']['spell_slots_level_9']}\n"
                    except:
                        spells = "This class doesn't have spellcasting changes at this level."

                    fields.append(('Spellcasting', spells, False))

                    if 'subclass' in data[page]['url']:
                        async with self.session.get(f'{BASE_URL}{data[page]["url"]}') as resp:
                            subclass = json.loads(await resp.text())
                        features = ""
                        for feat in subclass['features']:
                            async with self.session.get(f'{BASE_URL}{feat["url"]}') as resp:
                                desc = json.loads(await resp.text())['desc'][0]
                            features += f"__*{feat['name']}*__\n{desc}\n\n"
                        fields.append(('Subclass Features', features, False))

                    embed.set_footer(text=f'Page {page + 1} of {len(data)}')

                else:
                    if not args:
                        embed = discord.Embed(title='D&D Classes', description=f'{count} total classes.',
                                              color=Color.red())
                        class_names = ""
                        for f in classes:
                            class_names += f'\n*{f["name"]}*'

                        embed.add_field(name='__Class List:__', value=class_names)

                        await ctx.send(embed=embed)
                        return
                    else:
                        if not embed_data:
                            async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
                                data = json.loads(await resp.text())
                        else:
                            print('recycling data')
                            data = embed_data
                        if page <= 0:
                            page = 0
                            saving_throws = ""
                            for f in data['saving_throws']:
                                saving_throws += f'\n*{f["name"]}*'
                            embed = discord.Embed(title=args,
                                                  description=f'Basic Info, do `>class {args} levels` to view levels ',
                                                  color=Color.red())
                            fields = [
                                ('Hit Dice', data['hit_die'], True),
                                ('Proficiency Choices', data['proficiency_choices'][0]['choose'], True),
                                ('Saving Throws', saving_throws, True),
                            ]
                            try:
                                fields.append(('Spellcasting Ability',
                                               data['spellcasting']['spellcasting_ability']['name'], True))
                            except KeyError:
                                pass


                        elif page == 1:
                            embed = discord.Embed(title=args, description='Proficiencies', color=Color.red())
                            choices = ""
                            proficiencies = ""
                            for f in data['proficiency_choices'][0]['from']:
                                choices += f'\n*{f["name"]}*'
                            for f in data['proficiencies']:
                                proficiencies += f'\n*{f["name"]}*'
                            fields = [
                                (f'Choose {data["proficiency_choices"][0]["choose"]}', choices, True),
                                (f'Proficiencies', proficiencies, True)
                            ]
                        elif page == 2:
                            equipment = data["starting_equipment"]
                            choices = data['starting_equipment_options']
                            embed = discord.Embed(title=args, description='Starting Equipment', color=Color.red())
                            fields = []
                            for f in equipment:
                                async with self.session.get(f'{BASE_URL}{f["equipment"]["url"]}') as resp:
                                    info = json.loads(await resp.text())
                                values = ""
                                if info['equipment_category']['index'] == 'armor':

                                    values += f"_Armor Category:_ {info['armor_category']}\n"
                                    values += f"_Armor Class:_ {info['armor_class']['base']}\n"
                                    values += f"_Dex Bonus:_ {info['armor_class']['dex_bonus']}\n"
                                    values += f"_Max Bonus:_ {info['armor_class']['max_bonus']}\n"
                                    values += f"_Strength Minimum:_ {info['str_minimum']}\n"
                                    values += f"_Stealth Disadvantage:_ {info['stealth_disadvantage']}\n"
                                    values += f"_Weight:_ {info['weight']}\n"
                                    values += f"_Cost:_ {info['cost']['quantity']} {info['cost']['unit']}\n"

                                elif info['equipment_category']['index'] == 'weapon':
                                    values += f"_Weapon Category_: {info['weapon_category']}\n"
                                    values += f"_Weapon Range:_ {info['weapon_range']}\n"
                                    values += f"_Category Range:_ {info['category_range']}\n"
                                    values += f"_Cost:_ {info['cost']['quantity']} {info['cost']['unit']}\n"
                                    values += f"_Weight:_ {info['weight']}\n"
                                    values += f"_Damage:_ {info['damage']['damage_dice']}\n"
                                    values += f"_Damage Type:_ {info['damage']['damage_type']['name']}\n"
                                    values += f"_Range_: Normal-{info['range']['normal']} Long-{info['range']['long']}\n"
                                    values += '_Properties:_ '
                                    for f in info['properties']:
                                        values += f"{f['name']}, "
                                    values += f"\n_Throwing Range:_ Normal-{info['throw_range']['normal']} Long-{info['throw_range']['long']}"



                                elif info['equipment_category']['index'] == 'tools':
                                    values += f"_Equipment Category_: {info['equipment_category']['name']}\n"
                                    values += f"_Equipment Category_: {info['tool_category']}\n"
                                    values += f"_Cost:_ {info['cost']['quantity']} {info['cost']['unit']}\n"
                                    values += f"_Desc:_ {info['desc'][0]}\n"

                                elif info['equipment_category']['index'] == 'adventuring-gear':
                                    values += f"_Equipment Category_: {info['equipment_category']['name']}\n"
                                    values += f"_Gear Category:_ {info['gear_category']['name']}\n"
                                    values += f"_Cost:_ {info['cost']['quantity']} {info['cost']['unit']}\n"
                                    try:
                                        values += f"_Weight:_ {info['weight']}\n"
                                    except KeyError:
                                        values += f"_Weight:_ N/A\n"
                                    try:
                                        values += f"_Desc:_ {info['desc'][0]}\n"
                                    except KeyError:
                                        values += f"_Desc:_ N/A\n"
                                else:
                                    values += f'\n ADD THIS:{info["equipment_category"]["index"]}'
                                if not info['equipment_category']['index'] == 'armor':
                                    fields.append((info['name'], values, False))
                                else:
                                    fields.append((f'{info["name"]} armor', values, False))
                            for f in choices:
                                values = ""
                                for d in f['from']:
                                    try:
                                        values += f"_{d['equipment']['name']}_\nor\n"
                                    except KeyError:
                                        try:
                                            values += f"_{d['equipment_option']['choose']} from {d['equipment_option']['from']['equipment_category']['name']}_\nor\n"
                                        except KeyError:
                                            try:
                                                for r in d:
                                                    try:
                                                        values += f"_{d[r]['quantity']} {d[r]['equipment']['name']}_, "
                                                    except KeyError:
                                                        values += f"_{d[r]['equipment_option']['choose']} from {d[r]['equipment_option']['from']['equipment_category']['name']}_, "
                                                values += "\nor\n"
                                            except KeyError:
                                                try:
                                                    values += f"_{d['equipment_category']['name']}_\nor\n"
                                                except KeyError:
                                                    for g in d['0']:
                                                        if len(g[0]) > 1:
                                                            values += f'_{str(g[0])}_\nor\n'

                                fields.append((f'Choose {f["choose"]}', values[:-3], True))
                        elif page == 3:
                            embed = discord.Embed(title=args, description='Spell Casting', color=Color.red())
                            fields = []
                            try:
                                for f in data['spellcasting']['info']:
                                    fields.append((f['name'], f['desc'][0], False))
                            except:
                                fields.append(('No Spells', "This character has no spellcasting ability", False))
                        else:
                            embed = discord.Embed(title=args, description=f'Subclasses', color=Color.red())
                            page = 4
                            fields = []
                            for url in data['subclasses']:
                                async with self.session.get(f'{BASE_URL}{url["url"]}') as resp:
                                    info = json.loads(await resp.text())
                                values = f'_Subclass Flavor:_ {info["subclass_flavor"]}\n'
                                if len(info['desc'][0]) + len(values) > 1024:
                                    print('thick boi')
                                    descrip = info['desc'][0].split('.')
                                    count = 0
                                    desc = ""
                                    while (len(desc) + len(descrip[count]) + len(values)) < 1024:
                                        desc += f'{descrip[count]}. '
                                        count += 1
                                else:
                                    desc = info['desc'][0]
                                values += f"_Desc:_ {desc}"
                                fields.append((info['name'], values, False))
                    embed.set_footer(text=f'Page {page + 1} of 5')
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if not message:
                    message = await ctx.send(embed=embed)
                else:
                    await message.edit(embed=embed)
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")

                def check(reaction, user):
                    return message == reaction.message and not user.bot and user.id == ctx.author.id

                reaction, user = await self.bot.wait_for(
                    'reaction_add', timeout=45, check=check)
                await reaction.remove(user)
                if reaction.emoji == "⬅️":
                    page -= 1
                elif reaction.emoji == "➡️":
                    page += 1
            except TimeoutError:
                message = await ctx.fetch_message(message.id)
                for reaction in message.reactions:
                    await reaction.clear()
                return
            except IndexError:
                await ctx.send(
                    embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))


def setup(bot):
    bot.add_cog(classes(bot))
