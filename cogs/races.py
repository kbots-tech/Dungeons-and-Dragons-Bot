import discord
import aiohttp
import json


from discord import Color
from difflib import get_close_matches
import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Option, Choice, OptionType
from cogs.paginator import Paginator

BASE_URL = 'https://www.dnd5eapi.co'


class Races(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @interactions.extension_command(
        name="race",
        description="Search through and get race information",
        options=[
            Option(
                name="race",
                description="What race would you like to search for?",
                type=OptionType.STRING,
                required=False,

            ),
        ]
    )
    async def _race(self, ctx, race=None):
        name = race
        while True:
            try:
                async with self.session.get(f'{BASE_URL}/api/races') as resp:
                    data = json.loads(await resp.text())
                count = data['count']
                races = data['results']
                url_list = {}
                for f in races:
                    url_list[f['name']] = f['url']
                if name:
                    values = get_close_matches(name, url_list)
                    name = values[0]
                if name:
                    async with self.session.get(f'{BASE_URL}{url_list[name]}') as resp:
                        data = json.loads(await resp.text())

                    page1 = discord.Embed(title=name, description=f'Basic Info', color=Color.red())
                    fields = [('Speed', data['speed'], True)]

                    fields.append(('Size', data['size'], True))

                    fields.append(('Size Description', data['size_description'], False))
                    fields.append(('Alignment', data['alignment'], False))
                    fields.append(('Age', data['age'], False))

                    languages = "_*Languages:*_ "
                    for f in data['languages']:
                        languages += f"{f['name']}, "
                    fields.append(('Language', f"{data['language_desc']}\n{languages}", False))

                    starting_proficiencies = ""
                    for f in data['starting_proficiencies']:
                        starting_proficiencies += f"{f['name']}, "
                    if not starting_proficiencies:
                        starting_proficiencies = "N/A"
                    fields.append(('Starting Proficiencies', starting_proficiencies, False))
                    for name,value,inline in fields:
                        page1.add_field(name=name, value=value, inline=inline)


                    fields = []
                    if data['traits']:
                        page2 = discord.Embed(title=name, description=f'Features', color=Color.red())
                        for f in data['traits']:
                            async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                feature = json.loads(await resp.text())
                            text = f"{feature['desc'][0]}\n"
                            proficiencies = ""
                            if feature['proficiencies']:
                                for f in feature['proficiencies']:
                                    proficiencies += f"{f['name']},"
                                text += f"Proficiencies: {proficiencies} \n"
                            fields.append((f['name'], text, False))
                    else:
                        page2 = discord.Embed(title=name, description='This race has no additional traits',
                                              color=Color.red())

                    for name,value,inline in fields:
                        page2.add_field(name=name, value=value, inline=inline)


                    fields = []
                    try:
                        page3 = discord.Embed(title=name,
                                              description=f"Feature Choices\n**Choose:** {data['trait_options']['choose']}",
                                              color=Color.red())
                        feature = ""
                        for f in data['trait_options']['from']:
                            async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                feature = json.loads(await resp.text())['desc'][0]

                            fields.append((f['name'], feature, False))
                    except KeyError:
                        page3 = discord.Embed(title=name,
                                              description=f'Feature Choices\nThis Character has no feature choices.',
                                              color=Color.red())
                    for name, value, inline in fields:
                        page3.add_field(name=name, value=value, inline=inline)

                    fields = []



                    for race in data['subraces']:
                        async with self.session.get(f'{BASE_URL}{race["url"]}') as resp:
                            subrace = json.loads(await resp.text())

                        fields.append((subrace['name'], subrace['desc'], True))
                        abilities = ""
                        if subrace['ability_bonuses']:
                            for ability in subrace['ability_bonuses']:
                                abilities += f"{ability['ability_score']['name']}, "

                            fields.append(("Ability Bonuses", abilities, False))

                        if subrace['starting_proficiencies']:
                            proficiencies = ""
                            for prof in subrace['starting_proficiencies']:
                                proficiencies += f"{prof['name']}, "

                            fields.append(("Starting Proficiencies", proficiencies, False))

                        if subrace['languages']:
                            languages = ""
                            for lan in subrace['languages']:
                                languages += f"{lan['name']}, "
                            fields.append(('Languages', languages, False))

                        traits = ""
                        for f in subrace['racial_traits']:
                            async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                trait = json.loads(await resp.text())
                            traits += f"_{trait['name']}:_ {trait['desc'][0]}\n\n"

                        fields.append(('Traits', traits, False))

                        try:
                            choices = f"_Choose {subrace['language_options']['choose']}:_\n"
                            for f in subrace['language_options']['from']:
                                choices += f"{f['name']},\n "

                            fields.append(('Language Choices', choices, True))
                        except KeyError:
                            pass

                        try:
                            options = f"_Choose {subrace['racial_trait_options']['choose']}_\n"
                            for f in subrace['racial_trait_options']['from']:
                                options += f"{f['name']},\n "

                            fields.append(('Trait Options', options, True))
                        except KeyError:
                            pass

                        if fields:
                            page4 = discord.Embed(title=name, description=f'Subclass', color=Color.red())
                        else:
                            page4 = discord.Embed(title=name, description=f'Subclass\nThis Class Has no Subclass',
                                                  color=Color.red())

                        for name, value, inline in fields:
                            page4.add_field(name=name, value=value, inline=inline)

                        embeds = [page1, page2, page3, page4]
                        e = Paginator(bot=self.bot,
                                      ctx=ctx,
                                      embeds=embeds,
                                      only=ctx.author)
                        await e.start()
                else:
                    embed = discord.Embed(title='D&D Races', description=f'{count} total races.', color=Color.red())
                    race_names = ""
                    for f in races:
                        race_names += f'\n*{f["name"]}*'

                    embed.add_field(name='__Race List:__', value=race_names)

                    await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
                    return

            except IndexError:
                embed = discord.Embed(title=f'{name} not found', description='Please Try again.', color=Color.red())
                await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])
                return


def setup(client):
    Races(client)
