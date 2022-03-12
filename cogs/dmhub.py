import discord
import aiohttp
import json
import aiofiles
import imgbbpy

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Modal, Option, Choice
from cogs.paginator import Paginator as paginator
from cogs.characterfunctions import CharacterData

BASE_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}'
QUERY_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}&type={1}&id={2}'



class DmHub(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.client = imgbbpy.AsyncClient('token')
        self.session = aiohttp.ClientSession()
        with open("items.json") as file:
            self.items = json.load(file)

    @interactions.extension_command(
        name="dmhub",
        description="Search through and get equipment information",
        scope=788518409532997632,
        options=[
            Option(
                name="query",
                description="What type of query are you making?",
                type=3,
                required=True,
                choices=[
                    Choice(name="Game", value="game"),
                    Choice(name="Character", value="character"),
                ]
            ),
            Option(
                name="gameid",
                description="What is the Game ID?",
                type=3,
                required=True,
            ),
            Option(
                name="charactername",
                description="If getting character data what is their name?",
                type=3,
                required=False,
            ),
        ]
    )
    async def _dmhub(self, ctx, query=None, gameid=None, charactername=None ):
        async with self.session.get(BASE_URL.format(gameid)) as resp:
            gamedata = json.loads(await resp.text())

        if(query == "game"):
            if "descriptionDetails" in gamedata:
                embed = discord.Embed(title=gamedata['description'], description=gamedata['descriptionDetails'])
            else:
                embed = discord.Embed(title=gamedata['description'])
            if "coverart" in gamedata:
                url = await self.get_image(gamedata['coverart'])
            else:
                url = None
            characters = ""
            if "characters" in gamedata:
                for character in gamedata['characters']:
                    print(character)
                    try:
                        characters += f"*{character['name']}: * {character['summaryDescription']}\n"
                    except KeyError:
                        characters += f"*NO NAME: * {character['summaryDescription']}\n"
                embed.add_field(name="Characters", value=characters, inline=False)
            embed.set_image(url=url)
            await ctx.send(embeds=[interactions.Embed(**embed.to_dict())])

        elif(query == "character"):
            await self.character(ctx, gamedata, charactername, gameid)

    async def get_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('file2.jpg', mode='wb')
                    await f.write(await resp.read())
                    await f.close()

            image = await self.client.upload(file='file2.jpg')


            return image.url

    async def character(self, ctx, gamedata, charactername, gameid):
        characterid = None
        if "characters" in gamedata:
            for character in gamedata['characters']:
                print(character)
                try:
                    if charactername == character['name']:
                        characterid = character['id']
                except KeyError:
                    print("no name")


        if not characterid:
            await ctx.send("No Character with that name")
            return
        character = CharacterData(gameid, characterid)
        characterData = await character.baseData()
        print(characterData)
        pdf = await character.fillFields(characterData)
        print(pdf)





        embeds = [page1]
        e = paginator(self.bot, ctx, [interactions.Embed(**page1.to_dict()), interactions.Embed(**page2.to_dict())], True )
        await e.start()
def setup(client):
    DmHub(client)
