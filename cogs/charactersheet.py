from multiprocessing.connection import wait
import discord
import aiohttp
import pdfrw
import asyncio
from discord.ext import commands
import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow
from math import floor
from ButtonPaginator import Paginator

BASE_URL = 'https://www.dnd5eapi.co'


async def get_data(args):
    url = f"{BASE_URL}{args}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def get_field(choice):
    if 'str' in choice.lower():
        return 60
    elif 'dex' in choice.lower():
        return 61
    elif 'con' in choice.lower():
        return 62
    elif 'int' in choice.lower():
        return 63
    elif 'wis' in choice.lower():
        return 64
    elif 'cha' in choice.lower():
        return 65
    elif 'acrobatics' in choice.lower():
        return 87
    elif 'animal' in choice.lower():
        return 88
    elif 'arcana' in choice.lower():
        return 89
    elif 'athletics' in choice.lower():
        return 90
    elif 'deception' in choice.lower():
        return 91
    elif 'history' in choice.lower():
        return 92
    elif 'insight' in choice.lower():
        return 93
    elif 'intimidation' in choice.lower():
        return 94
    elif 'investigation' in choice.lower():
        return 95
    elif 'medicine' in choice.lower():
        return 96
    elif 'nature' in choice.lower():
        return 97
    elif 'perception' in choice.lower():
        return 98
    elif 'performance' in choice.lower():
        return 99
    elif 'persuasion' in choice.lower():
        return 100
    elif 'religion' in choice.lower():
        return 101
    elif 'sleight' in choice.lower():
        return 102
    elif 'stealth' in choice.lower():
        return 103
    elif 'survival' in choice.lower():
        return 104


class Classes(interactions.Extension):

    def __init__(self, bot):
        self.userInputs = None
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.fields = {}


    @interactions.extension_command(
        name="charactersheet",
        description="TESTING UPDATED CS COMMAND",
        scope=[788518409532997632]
    )
    async def charactersheet(self, ctx):

        embed = interactions.Embed(
            title='WELCOME!',
            description='Welcome to the dungeon master character creator,'
                  'this command will guide you through making a 1st'
                  'level D&D character, in the future you will be'
                  'able to level up as well.'
                  'The first step will be to select your class and race'
                        'when your ready react with ✅',
            color=0xde2939,
        )
        buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='agreed',
                custom_id="start"
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='❌',
                custom_id="cancel"
            ),
        ]

        action_row = interactions.ActionRow(components=buttons)
        await ctx.send(embeds=[embed], components=[action_row], ephemeral =True)

    @interactions.extension_component
    async def start(ctx: ComponentContext):
        self.fields[ctx.author.id] = ['NO']*334

        input = interactions.TextInput(style=interactions.TextStyleType.SHORT,
                               label="Let's get straight to it: what's 1 + 1?",
                               custom_id="text_input_response",
                               min_length=1,
                               max_length=3)

        modal = interactions.Modal(
            title="Application Form",
            custom_id="mod_app_form",
            components=[input],
        )

        await ctx.popup(modal)

    @commands.Cog.listener("mod_app_form")
    async def modal_response(self, ctx, response: str):
        character_name = await self.answer(ctx, "What is your characters name?", message=ctx, name="character")
        self.fields[ctx.author.id][0] = self.fields[ctx.author.id][17] = character_name

        # Class Selection
        classes = (await get_data('/api/classes'))['results']
        desc = " Reply With the number matching your class choice\n"
        for count, name in enumerate(classes):
            desc += f"**{count + 1}** {name['name']}\n"
        while True:
            try:
                c_class = {'count': int(await self.answer(ctx, "Select a Class.", desc, ctx, 500)) - 1}
                break
            except ValueError:
                pass
        c_class['url'] = classes[c_class['count']]['url']
        c_class['name'] = classes[c_class['count']]['name']
        self.fields[ctx.author.id][14] = c_class['name']

        # Race Selection
        races = (await get_data('/api/races'))['results']
        desc = " Reply With the number matching your class choice\n"
        for count, name in enumerate(races):
            desc += f"**{count + 1}** {name['name']}\n"
        while True:
            try:
                race = {'count': int(await self.answer(ctx, "Select a Race.", desc, message, 500)) - 1}
                break
            except ValueError:
                pass
        race['url'] = races[race['count']]['url']
        race['name'] = races[race['count']]['name']
        self.fields[ctx.author.id][333] = race['name']
        race_data = await get_data(race['url'])

        embed = discord.Embed(
            title='Ability Score',
            description="This step will have you set your ability scores,"
                        "modifiers and bonuses from your class and race will"
                        "be calculated automatically so just give your base"
                        "stat and I'll take care of the rest",
            color=0xde2939,
        )
        await ctx.edit(embed=embed)
        await self.reaction(ctx, ctx.author, ctx, '✅', 500)

        while True:
            try:
                self.fields[ctx.author.id][21] = int(await self.answer(ctx, "What is your strength roll?", message=ctx, timeout=500))
                break
            except ValueError:
                pass

        while True:
            try:
                self.fields[ctx.author.id][30] = int(await self.answer(ctx, "What is your dexterity roll?", message=ctx, timeout=500))
                break
            except ValueError:
                pass

        while True:
            try:
                self.fields[ctx.author.id][36] = int(await self.answer(
                    ctx,
                    "What is your constitution roll?",
                    message=ctx,
                    timeout=500))
                break
            except ValueError:
                pass

        while True:
            try:
                self.fields[ctx.author.id][47] = int(await self.answer(
                    ctx,
                    "What is your intelligence roll?",
                    message=message,
                    timeout=500))
                break
            except ValueError:
                pass

        while True:
            try:
                self.fields[ctx.author.id][74] = int(await self.answer(ctx, "What is your wisdom roll?", message=message, timeout=500))
                break
            except ValueError:
                pass

        while True:
            try:
                self.fields[ctx.author.id][81] = int(await self.answer(ctx, "What is your charisma roll?", message=message, timeout=500))
                break
            except ValueError:
                pass

        for bonus in race_data['ability_bonuses']:
            field_name = bonus['ability_score']['index']
            if field_name == 'str':
                field = 21
            elif field_name == 'dex':
                field = 30
            elif field_name == 'con':
                field = 36
            elif field_name == 'int':
                field = 47
            elif field_name == 'wis':
                field = 74
            elif field_name == 'cha':
                field = 81
            self.fields[ctx.author.id][field] += bonus['bonus']

        # Strength
        self.fields[ctx.author.id][27] = floor((self.fields[ctx.author.id][21] - 10) / 2)
        self.fields[ctx.author.id][29] = self.fields[ctx.author.id][27]
        self.fields[ctx.author.id][55] = self.fields[ctx.author.id][27]
        # Dexterity
        self.fields[ctx.author.id][33] = floor((self.fields[ctx.author.id][30] - 10) / 2)
        self.fields[ctx.author.id][24] = self.fields[ctx.author.id][33]
        self.fields[ctx.author.id][48] = self.fields[ctx.author.id][33]
        self.fields[ctx.author.id][53] = self.fields[ctx.author.id][33]
        self.fields[ctx.author.id][86] = self.fields[ctx.author.id][33]
        self.fields[ctx.author.id][106] = self.fields[ctx.author.id][33]
        # Constitution
        self.fields[ctx.author.id][41] = floor((self.fields[ctx.author.id][36] - 10) / 2)
        self.fields[ctx.author.id][49] = self.fields[ctx.author.id][41]
        # Intelligence
        self.fields[ctx.author.id][69] = floor((self.fields[ctx.author.id][47] - 10) / 2)
        self.fields[ctx.author.id][50] = self.fields[ctx.author.id][69]
        self.fields[ctx.author.id][73] = self.fields[ctx.author.id][69]
        self.fields[ctx.author.id][77] = self.fields[ctx.author.id][69]
        self.fields[ctx.author.id][57] = self.fields[ctx.author.id][69]
        self.fields[ctx.author.id][82] = self.fields[ctx.author.id][69]
        self.fields[ctx.author.id][85] = self.fields[ctx.author.id][69]
        # Wisdom
        self.fields[ctx.author.id][80] = floor((self.fields[ctx.author.id][74] - 10) / 2)
        self.fields[ctx.author.id][51] = self.fields[ctx.author.id][80]
        self.fields[ctx.author.id][54] = self.fields[ctx.author.id][80]
        self.fields[ctx.author.id][58] = self.fields[ctx.author.id][80]
        self.fields[ctx.author.id][84] = self.fields[ctx.author.id][80]
        self.fields[ctx.author.id][79] = self.fields[ctx.author.id][80]
        self.fields[ctx.author.id][108] = self.fields[ctx.author.id][80]
        # Charisma
        self.fields[ctx.author.id][107] = floor((self.fields[ctx.author.id][81] - 10) / 2)
        self.fields[ctx.author.id][52] = self.fields[ctx.author.id][107]
        self.fields[ctx.author.id][56] = self.fields[ctx.author.id][107]
        self.fields[ctx.author.id][59] = self.fields[ctx.author.id][107]
        self.fields[ctx.author.id][83] = self.fields[ctx.author.id][107]
        self.fields[ctx.author.id][105] = self.fields[ctx.author.id][107]

        # Class Data
        class_data = (await get_data(c_class['url']))
        class_levels = (await get_data(class_data['class_levels']))
        try:
            bonus = class_levels[0]["prof_bonus"]
        except:
            bonus = 2
        self.fields[ctx.author.id][22] = bonus
        self.fields[ctx.author.id][45] = f"d{class_data['hit_die']}"
        starting_equipment = (await get_data(class_data['starting_equipment']))

        # Proficiency Info
        for score in class_data['saving_throws']:
            field_num = await get_field(score['index'])
            self.fields[ctx.author.id][field_num] = "Yes"
        proficiencies = "PROFICIENCIES:\n"
        for prof in race_data['starting_proficiencies']:
            if 'skill' in prof['index']:
                field = await get_field(prof['index'])
                self.fields[ctx.author.id][field] = 'Yes'
            else:
                proficiencies += f"{prof['name']}, "

        prof_choices = class_data['proficiency_choices']

        for prof in class_data['proficiencies']:
            proficiencies += f"{prof['name']}, "

        # Prof Choices
        embed = discord.Embed(
            title='Time for proficiency choices',
            description="Simply reply with the number of the choice you'd like"
                        "to add and it'll be set and saved. Skills will be added"
                        "and items put in your proficiencies box.",
            color=0xde2939,
        )
        await message.edit(embed=embed)
        await self.reaction(ctx, ctx.author, message, '✅', 500)

        for choice in prof_choices:
            desc = " Reply With the number matching your class choice\n"
            for count, option in enumerate(choice['from']):
                desc += f"**{count+1}** {option['name']}\n"
            count = 1
            while count <= int(choice['choose']):
                selection = int(await self.answer(
                    ctx,
                    f"Choose A Proficiency {count} of {choice['choose']}",
                    desc,
                    message,
                    500))-1
                if 'Skill' in choice['from'][selection]['name']:
                    while True:
                        try:
                            field = int(await get_field(choice['from'][selection]['name']))
                            break
                        except ValueError:
                            pass
                    self.fields[ctx.author.id][field] = 'Yes'
                else:
                    proficiencies += f"{choice['from'][selection]['name']}\n "
                count += 1

        # Languages
        languages = "LANGUAGES:\n"
        for lang in race_data['languages']:
            languages += f"{lang['name']}, "

        # Equipment Selection
        embed = discord.Embed(
            title='Almost there time for equipment choices',
            description="Simply reply with the number of the choice you'd like"
                        "to add and it'll be set and saved. Weapons and armor"
                        "will be equipped and all the needed info supplied.",
            color=0xde2939,
        )
        await message.edit(embed=embed)
        await self.reaction(ctx, ctx.author, message, '✅', 500)

        equipment = ""
        armor_class = 0
        for stuff in starting_equipment["starting_equipment"]:
            item = await get_data(stuff['equipment']['url'])
            if item['equipment_category']['name'] == 'Weapon':
                if self.fields[ctx.author.id][66] == "NO":
                    self.fields[ctx.author.id][66] = item['name']
                    if item['weapon_range'] == 'Melee':
                        self.fields[ctx.author.id][67] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                    elif item['weapon_range'] == 'Ranged':
                        self.fields[ctx.author.id][67] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                    damage = item['damage']
                    self.fields[ctx.author.id][68] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                elif self.fields[ctx.author.id][70] == "NO":
                    self.fields[ctx.author.id][70] = item['name']
                    if item['weapon_range'] == 'Melee':
                        self.fields[ctx.author.id][71] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                    elif item['weapon_range'] == 'Ranged':
                        self.fields[ctx.author.id][71] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                    damage = item['damage']
                    self.fields[ctx.author.id][72] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                elif self.fields[ctx.author.id][75] == "NO":
                    self.fields[ctx.author.id][75] = item['name']
                    if item['weapon_range'] == 'Melee':
                        self.fields[ctx.author.id][76] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                    elif item['weapon_range'] == 'Ranged':
                        self.fields[ctx.author.id][76] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                    damage = item['damage']
                    self.fields[ctx.author.id][77] = f"{damage['damage_dice']} {damage['damage_type']['name']}"

            elif item['equipment_category']['name'] == 'Armor':
                armor_class += item['armor_class']['base']

            equipment += f"{item['name']} x{stuff['quantity']}\n"

        for stuff in starting_equipment["starting_equipment_options"]:
            desc = ""
            for count, option in enumerate(stuff['from']):

                if 'equipment' in option:
                    desc += f"**{count+1}:** {option['equipment']['name']}\n"
                elif 'equipment_option' in option:
                    desc += f"**{count+1}:** {option['equipment_option']['choose']} from {option['equipment_option']['from']['equipment_category']['name']}\n"
                elif 'equipment_category' in option:
                    desc += f"**{count+1}** {option['equipment_category']['name']}\n"
                else:
                    package = f"**{count+1}**"
                    for item in option:
                        if 'equipment' in option[item]:
                            q = option[item]['quantity']
                            package += f" {q}: {option[item]['equipment']['name']}, "
                        elif 'equipment_option' in option[item]:
                            q = option[item]['equipment_option']['choose']
                            name = option[item]['equipment_option']['from']['equipment_category']['name']
                            package += f" {q}: {name}, "
                    desc += f"{package}\n"

            while True:
                try:
                    choice = int(await self.answer(ctx, "Select An Item", desc, ctx, 500))-1
                    break
                except:
                    await ctx.send("Please reply with a number.", delete_after=2)
            selection = stuff['from'][choice]
            if 'equipment' in selection:
                item = await get_data(selection['equipment']['url'])
                if item['equipment_category']['name'] == 'Weapon':
                    if self.fields[ctx.author.id][66] == "NO":
                        self.fields[ctx.author.id][66] = item['name']
                        if item['weapon_range'] == 'Melee':
                            self.fields[ctx.author.id][67] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                        elif item['weapon_range'] == 'Ranged':
                            self.fields[ctx.author.id][67] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                        damage = item['damage']
                        self.fields[ctx.author.id][68] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                    elif self.fields[ctx.author.id][70] == "NO":
                        self.fields[ctx.author.id][70] = item['name']
                        if item['weapon_range'] == 'Melee':
                            self.fields[ctx.author.id][71] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                        elif item['weapon_range'] == 'Ranged':
                            self.fields[ctx.author.id][71] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                        damage = item['damage']
                        self.fields[ctx.author.id][72] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                    elif self.fields[ctx.author.id][75] == "NO":
                        self.fields[ctx.author.id][75] = item['name']
                        if item['weapon_range'] == 'Melee':
                            self.fields[ctx.author.id][76] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                        elif item['weapon_range'] == 'Ranged':
                            self.fields[ctx.author.id][76] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                        damage = item['damage']
                        self.fields[ctx.author.id][77] = f"{damage['damage_dice']} {damage['damage_type']['name']}"

                elif item['equipment_category']['name'] == 'Armor':
                    armor_class += item['armor_class']['base']
                if 'quantity' in selection:
                    q = selection['quantity']
                else:
                    q = 1
                equipment += f"{item['name']} x{q}\n"
            elif 'equipment_option' in selection:
                cycle = 0
                choices = selection['equipment_option']['choose']
                while cycle < choices:
                    print(f"{count}, {choices}")
                    info = await get_data(selection['equipment_option']['from']['equipment_category']['url'])
                    desc = ""
                    for count, item in enumerate(info['equipment']):
                        desc += f"**{count+1}:** {item['name']}\n"
                    while True:
                        try:
                            choice = int(await self.answer(ctx, f'Select An Item {cycle+1} of {choices}', desc, ctx, 500))-1
                            break
                        except:
                            await ctx.send("Please Reply With a Valid Number", delete_after=5)
                    item = await get_data(info['equipment'][choice]['url'])
                    if item['equipment_category']['name'] == 'Weapon':
                        if 'damage' in item:
                            damage = item['damage']
                        else:
                            damage = {'damage_dice': '', 'damage_type': {'name': 'N/A'}}
                        if self.fields[ctx.author.id][66] == "NO":
                            self.fields[ctx.author.id][66] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][67] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][67] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                            self.fields[ctx.author.id][68] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                        elif self.fields[ctx.author.id][70] == "NO":
                            self.fields[ctx.author.id][70] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][71] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][71] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]

                            self.fields[ctx.author.id][72] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                        elif self.fields[ctx.author.id][75] == "NO":
                            self.fields[ctx.author.id][75] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][76] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][76] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                            self.fields[ctx.author.id][77] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                        elif item['equipment_category']['name'] == 'Armor':
                            armor_class += item['armor_class']['base']

                        equipment += f"{item['name']} x1\n"
                    cycle += 1
            elif 'equipment_category' in selection:
                info = await get_data(selection['equipment_category']['url'])
                desc = ""
                for num, item in enumerate(info['equipment']):
                    desc += f"**{num+1}:** {item['name']}\n"
                while True:
                    try:
                        num = int(await self.answer(ctx, "Select an item", desc, ctx, 500))-1
                        break
                    except ValueError:
                        await ctx.send('Please give a valid number', delete_after=5)
                equipment += f"{info['equipment'][num]['name']} x1\n"
            else:
                for thing in selection:
                    if 'equipment' in selection[thing]:
                        q = selection[thing]['quantity']
                        item = await get_data(selection[thing]['equipment']['url'])
                    else:
                        q = 1
                        items = await get_data(selection[thing]['equipment_option']['from']['equipment_category']['url'])
                        options = ""
                        for count, item in enumerate(items['equipment']):
                            options += f"**{count+1}:** {item['name']}\n"
                        try:
                            number = int(await self.answer(ctx, "Select An Item", options, ctx, 500))-1
                        except:
                            await ctx.send("Please reply with a valid number", delete_after=5)
                        item = await get_data(items['equipment'][number]['url'])

                    if item['equipment_category']['name'] == 'Weapon':
                        if self.fields[ctx.author.id][66] == "NO":
                            self.fields[ctx.author.id][66] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][67] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][67] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                            damage = item['damage']
                            self.fields[ctx.author.id][68] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                        elif self.fields[ctx.author.id][70] == "NO":
                            self.fields[ctx.author.id][70] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][71] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][71] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                            damage = item['damage']
                            self.fields[ctx.author.id][72] = f"{damage['damage_dice']} {damage['damage_type']['name']}"
                        elif self.fields[ctx.author.id][75] == "NO":
                            self.fields[ctx.author.id][75] = item['name']
                            if item['weapon_range'] == 'Melee':
                                self.fields[ctx.author.id][76] = self.fields[ctx.author.id][27] + self.fields[ctx.author.id][22]
                            elif item['weapon_range'] == 'Ranged':
                                self.fields[ctx.author.id][76] = self.fields[ctx.author.id][33] + self.fields[ctx.author.id][22]
                            damage = item['damage']
                            self.fields[ctx.author.id][77] = f"{damage['damage_dice']} {damage['damage_type']['name']}"

                    elif item['equipment_category']['name'] == 'Armor':
                        armor_class += item['armor_class']['base']

                    equipment += f"{item['name']} x{q}\n"

        # Features
        embed = discord.Embed(
            title='The final step class features',
            description="If your class has special feature options you'll be asked for them now,"
                        "if it doesn't your all done and after clicking '✅' you'll have a fresh"
                        "new character sheet ready to go!",
            color=0xde2939,
        )
        await ctx.edit(embed=embed)
        await self.reaction(ctx, ctx.author, ctx, '✅', 500)

        features = ""
        for feature in class_levels[0]['features']:
            data = await get_data(feature['url'])
            features += f"{data['name']}: {data['desc'][0]}\n\n"

        for trait in race_data['traits']:
            data = await get_data(trait['url'])
            features += f"{data['name']}: {data['desc'][0]}\n\n"

        for option in class_levels[0]['feature_choices']:
            group = await get_data(option['url'])
            desc = ""
            for numero, name in enumerate(group['choice']['from']):
                desc += f"**{numero+1}:** {name['name']}\n"
            while True:
                try:
                    choice = int(await self.answer(ctx, "Select An Item", desc, ctx, 500))-1
                    break
                except:
                    await ctx.send("Please reply with a number.", delete_after=2)
            trait = await get_data(group['choice']['from'][choice]['url'])
            features += f"{trait['name']}: {trait['desc'][0]}\n\n"

        self.fields[ctx.author.id][118] = features

        if self.fields[ctx.author.id][60] != 'NO':
            self.fields[ctx.author.id][29] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][61] != 'NO':
            self.fields[ctx.author.id][48] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][62] != 'NO':
            self.fields[ctx.author.id][49] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][63] != 'NO':
            self.fields[ctx.author.id][50] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][64] != 'NO':
            self.fields[ctx.author.id][51] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][65] != 'NO':
            self.fields[ctx.author.id][52] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][87] != 'NO':
            self.fields[ctx.author.id][53] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][88] != 'NO':
            self.fields[ctx.author.id][54] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][89] != 'NO':
            self.fields[ctx.author.id][77] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][90] != 'NO':
            self.fields[ctx.author.id][55] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][91] != 'NO':
            self.fields[ctx.author.id][56] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][92] != 'NO':
            self.fields[ctx.author.id][57] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][93] != 'NO':
            self.fields[ctx.author.id][58] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][94] != 'NO':
            self.fields[ctx.author.id][59] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][95] != 'NO':
            self.fields[ctx.author.id][73] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][96] != 'NO':
            self.fields[ctx.author.id][84] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][97] != 'NO':
            self.fields[ctx.author.id][82] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][98] != 'NO':
            self.fields[ctx.author.id][79] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][99] != 'NO':
            self.fields[ctx.author.id][83] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][100] != 'NO':
            self.fields[ctx.author.id][105] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][101] != 'NO':
            self.fields[ctx.author.id][85] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][102] != 'NO':
            self.fields[ctx.author.id][106] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][103] != 'NO':
            self.fields[ctx.author.id][86] += self.fields[ctx.author.id][22]
        if self.fields[ctx.author.id][104] != 'NO':
            self.fields[ctx.author.id][108] += self.fields[ctx.author.id][22]

        # Final info and sending PDF

        self.fields[ctx.author.id][25] = race_data['speed']
        self.fields[ctx.author.id][28] = class_data['hit_die'] + self.fields[ctx.author.id][41]
        self.fields[ctx.author.id][31] = self.fields[ctx.author.id][28]
        self.fields[ctx.author.id][37] = 1
        self.fields[ctx.author.id][23] = armor_class
        self.fields[ctx.author.id][112] = f"{proficiencies}\n\n{languages}"
        self.fields[ctx.author.id][117] = equipment
        self.fields[ctx.author.id][110] = self.fields[ctx.author.id][80] + 10
        if self.fields[ctx.author.id][98] != "NO":
            self.fields[ctx.author.id][110] += self.fields[ctx.author.id][22]

        output = await self.fill_pdf(fields=self.fields[ctx.author.id])
        await ctx.edit(embed=discord.Embed(title="Sending Character Sheet Now", color=0xde2939))
        await ctx.send(embed=discord.Embed(title=f"Your Character Sheet for {self.fields[ctx.author.id][0]}", color=0xde2939), file=discord.File(output))
        await ctx.author.send(
            embed=discord.Embed(
                title="Your Character Sheet",
                description=f"And here's a backup for {self.fields[ctx.author.id][0]}",
                color=0xde2939,),
            file=discord.File(output))

    @staticmethod
    async def fill_pdf(fields, in_file=None, out_file=None):
        if in_file is None:
            in_file = pdfrw.PdfReader('./5eSheet.pdf')
        if out_file is None:
            out_file = f'./5eSheetOutput.pdf'
        in_file.Root.AcroForm.update({pdfrw.PdfName.NeedAppearances: True})
        for i in range(len(in_file.Root.AcroForm.Fields)):
            item = in_file.Root.AcroForm.Fields[i]
            if item.FT == '/Btn':
                if fields[i] != 'NO':
                    item.AS = 'Yes'
            else:
                if fields[i] != 'NO':
                    item.V = str(fields[i])
        else:
            pdfrw.PdfWriter().write(out_file, in_file)
        return out_file

    async def reaction(self, ctx, author, message, emojis, timeout):
        self.userInputs[ctx.author.id] = "none"
        print(self.userInputs[ctx.author.id])
        
        buttons = [
                    interactions.Option.create_button(
                        style=ButtonStyle.green,
                        label='agreed',
                        custom_id="agreed"
                    ),
                    interactions.Option.create_button(
                        style=ButtonStyle.green,
                        label='❌',
                        custom_id="cancel"
                    ),
                ]

        action_row = interactions.Option.create_actionrow(*buttons)
        await message.edit(components=[action_row])
        while(self.userInputs[ctx.author.id] == "none"):
            """Wait here"""
        
        if(self.userInputs[ctx.author.id] == "y"):
            return
        else:
            await ctx.send("Creation Cancelled")



    @commands.Cog.listener()
    async def on_component(self, ctx):
        if(self.userInputs[ctx.author.id] == 'none'):
            self.userInputs[ctx.author.id] = "y"
        else:
            print("NO BUTTON FOR YOU")

    @commands.Cog.listener()
    async def agreed(self, ctx):
        if(self.userInputs[ctx.author.id] == 'none'):
            self.userInputs[ctx.author.id] = "y"
        else:
            print("NO BUTTON FOR YOU")

            

    async def message_check(self, message, user, timeout):
        return await asyncio.wait_for(self._message_check(message, user), timeout=timeout)

    async def _message_check(self, message, user):
        while True:
            done, pending = await asyncio.wait([
                self.bot.wait_for('message'),
                self.bot.wait_for('reaction_add')
            ], return_when=asyncio.FIRST_COMPLETED)
            if not done:
                break
            else:
                stuff = done.pop().result()

                if type(stuff) == type(message):
                    if stuff.channel.id == message.channel.id and stuff.author.id == user.id:
                        return stuff
                else:
                    if stuff[0].message.id == message.id and stuff[1].id == user.id:
                        return stuff

    async def answer(self, ctx, question, desc=None, message=None, timeout=0):
        return await asyncio.wait_for(self._answer(ctx, question, desc, message), timeout=timeout)

    async def _answer(self, ctx, question, desc, message):
        if not message:
            await ctx.send(
                embed=discord.Embed(
                    title=question,
                    color=0xde2939,
                    description=desc
                ))
        else:
            await message.edit(
                embed=discord.Embed(
                    title=question,
                    color=0xde2939,
                    description=desc
                ))
        while True:
            reply = (await self.bot.wait_for('message'))
            if reply.channel.id == ctx.channel.id and reply.author.id == ctx.author.id:
                await reply.delete()
                return reply.content


def setup(client):
    Classes(client)
