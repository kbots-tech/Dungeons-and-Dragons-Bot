import discord
import aiohttp
import json
import aiofiles

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Modal, Option, Choice
from cogs.paginator import Paginator as paginator
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}'
QUERY_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}&type={1}&id={2}'



class DmHub(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
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




        if(query == "game"):
            embed = discord.Embed(title=gamedata['description'], description=gamedata['descriptionDetails'])
            file = await self.get_image(gamedata['coverart'])
            characters = ""
            for character in gamedata['characters']:
                print(character)
                try:
                    characters += f"*{character['name']}: * {character['summaryDescription']}\n"
                except KeyError:
                    characters += f"*NO NAME: * {character['summaryDescription']}\n"
            embed.add_field(name="Characters", value=characters, inline=False)
            embed.set_image(url="attachment://file.jpg")
            await ctx.send(embed=embed, file=file)

        elif(query == "character"):
            await self.character(ctx, gamedata, charactername, gameid)

    async def get_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('file.jpg', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
        return discord.File("file.jpg")

    async def character(self, ctx, gamedata, charactername, gameid):
        characterid = None
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
        async with self.session.get(QUERY_URL.format(gameid, "character", characterid)) as resp:
            characterdata = json.loads(await resp.text())
            print(QUERY_URL.format(gameid, "character", characterid))

        async with self.session.get(QUERY_URL.format(gameid, "race", characterdata['raceid'])) as resp:
            racedata = json.loads(await resp.text())
            print(racedata)
        async with self.session.get(
                QUERY_URL.format(gameid, "image", characterdata['appearance']['portraitid'])) as resp:
            imagedata = json.loads(await resp.text())
            print(imagedata)

        print(characterdata)
        try:
            if ("private" in characterdata['notes'][0]['text'].lower()):
                page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                      description="This characters bio is private")
            else:
                page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                      description=characterdata['notes'][0]['text'])
        except KeyError:
            page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                  description="This Character has no bio")

        for classes in characterdata['classes']:
            async with self.session.get(QUERY_URL.format(gameid, "class", classes['classid'])) as resp:
                classdata = json.loads(await resp.text())
                print(classdata)
                page1.add_field(name="Level", value=classes['level'], inline=True)
                page1.add_field(name="Class", value=classdata['name'], inline=True)

        file = await self.get_image(imagedata['url'])

        page1.add_field(name="Race: {0}".format(racedata['name']), value=racedata['details'], inline=False)
        page1.set_image(url="attachment://file.jpg")
        page1.set_footer(text=f"Game id: {gameid}")

        page2 = discord.Embed(title="Test2")

        embeds = [page1, page2]
        e = paginator(self.bot, ctx, [interactions.Embed(**page1.to_dict()), interactions.Embed(**page2.to_dict())], True )
        await e.start()
def setup(client):
    DmHub(client)
