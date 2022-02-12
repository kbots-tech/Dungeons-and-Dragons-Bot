import discord
import aiohttp
import json
import aiofiles

from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from discord_slash import cog_ext
from ButtonPaginator import Paginator
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}'
QUERY_URL = 'https://us-central1-dmtool-cad62.cloudfunctions.net/query?gameid={0}&type={1}&id={2}'



class Equipment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        with open("items.json") as file:
            self.items = json.load(file)

    @cog_ext.cog_slash(
        name="dmhub",
        description="Search through and get equipment information",
        guild_ids=[751980284353839204],
        options=[
            create_option(
                name="query",
                description="What type of query are you making?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Game", value="game"),
                    create_choice(name="Character", value="character"),
                ]
            ),
            create_option(
                name="gameid",
                description="What is the Game ID?",
                option_type=3,
                required=True,
            ),
            create_option(
                name="charactername",
                description="If getting character data what is their name?",
                option_type=3,
                required=False,
            ),
        ]
    )
    async def _dmhub(self, ctx, query=None, gameid=None, charactername=None ):
        async with self.session.get(BASE_URL.format(gameid)) as resp:
            gamedata = json.loads(await resp.text())



        if(query == "game"):
            embed = discord.Embed(title=gamedata['description'], description=gamedata['descriptionDetails'])
            file = await self.get_image(gamedata['coverart'])
            characters = ""
            for character in gamedata['characters']:
                characters += f"*{character['name']}: * {character['summaryDescription']}\n"
            embed.add_field(name="Characters", value=characters, inline=False)
            embed.set_image(url="attachment://file.jpg")
            await ctx.send(embed=embed, file=file)

        elif(query == "character"):
            characterid = None
            for character in gamedata['characters']:
                if charactername == character['name']:
                    characterid = character['id']

            if not characterid:
                await ctx.send("No Character with that name")
                return
            async with self.session.get(QUERY_URL.format(gameid, "character", characterid)) as resp:
                characterdata = json.loads(await resp.text())
                print(QUERY_URL.format(gameid, "character", characterid))

            async with self.session.get(QUERY_URL.format(gameid, "race", characterdata['raceid'])) as resp:
                racedata = json.loads(await resp.text())
                print(racedata)
            async with self.session.get(QUERY_URL.format(gameid, "image", characterdata['appearance']['portraitid'])) as resp:
                imagedata = json.loads(await resp.text())
                print(imagedata)

            print(characterdata)
            try:
                if("private" in characterdata['notes'][0]['text'].lower()):
                    page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                          description="This characters bio is private")
                else:
                    page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                          description=characterdata['notes'][0]['text'])
            except KeyError:
                page1 = discord.Embed(title="Character info for {0}".format(charactername),
                                      description= "This Character has no bio")

            for classes in characterdata['classes']:
                async with self.session.get(QUERY_URL.format(gameid, "class", classes['classid'])) as resp:
                    classdata = json.loads(await resp.text())
                    print(classdata)
                    page1.add_field(name="Level", value=classes['level'],inline=True)
                    page1.add_field(name="Class", value=classdata['name'], inline=True)


            file = await self.get_image(imagedata['url'])

            page1.add_field(name="Race: {0}".format(racedata['name']), value=racedata['details'], inline= False)
            page1.set_image(url="attachment://file.jpg")
            await ctx.send(embed=page1, file=file)

    async def get_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('file.jpg', mode='wb')
                    await f.write(await resp.read())
                    await f.close()
        return discord.File("file.jpg")

def setup(bot):
    bot.add_cog(Equipment(bot))
