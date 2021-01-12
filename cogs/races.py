import discord
import aiohttp
import json

from asyncio import TimeoutError
from discord.ext import commands
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class races(commands.Cog):

  def __init__(self, bot):
      self.bot = bot
      self.session = aiohttp.ClientSession()



  @commands.command(aliases=['r','race'])
  async def races(self,ctx,*,args = None,page = 0,message = None,embed_data = None):
      while True:
            try:
                if not embed_data:
                    async with self.session.get(f'{BASE_URL}/api/races') as resp:
                        data = json.loads(await resp.text())
                    count = data['count']
                    races = data['results']
                    url_list = {}
                    for f in races:
                        url_list[f['name']] = f['url']
                    if args:
                        values = get_close_matches(args, url_list)
                        args = values[0]
                if args:
                    if embed_data:
                        data = embed_data
                    else:
                        async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
                                data = json.loads(await resp.text())
                    if page <= 0:
                        page = 0
                        embed = discord.Embed(title=args,description=f'Basic Info',color=Color.red())
                        fields = [('Speed',data['speed'],True)]
                        
                        fields.append(('Size',data['size'],True))
                        
                        fields.append(('Size Description',data['size_description'],False))
                        fields.append(('Alignment',data['alignment'],False))
                        fields.append(('Age',data['age'],False))
                        
                        languages = "_*Languages:*_ "
                        for f in data['languages']:
                            languages+=f"{f['name']}, "
                        fields.append(('Language',f"{data['language_desc']}\n{languages}",False))
                        
                        starting_proficiencies = ""
                        for f in data['starting_proficiencies']:
                            starting_proficiencies+=f"{f['name']}, "
                        if not starting_proficiencies:
                            starting_proficiencies = "N/A"
                        fields.append(('Starting Proficiencies',starting_proficiencies,False))
                            
                    elif page == 1:
                        
                        fields = []
                        if data['traits']:
                            embed = discord.Embed(title=args,description=f'Features',color=Color.red())
                            for f in data['traits']:
                                async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                    feature = json.loads(await resp.text())
                                text = f"{feature['desc'][0]}\n"
                                proficiencies = ""
                                if feature['proficiencies']:
                                    for f in feature['proficiencies']:
                                        proficiencies += f"{f['name']},"
                                    text+=f"Proficiencies: {proficiencies} \n"
                                fields.append((f['name'],text,False))
                        else:
                            embed = discord.Embed(title=args,description='This race has no additional traits',color=Color.red())
                        
                        
                    elif page == 2:
                        fields = []
                        try:
                            embed = discord.Embed(title=args,description=f"Feature Choices\n**Choose:** {data['trait_options']['choose']}",color=Color.red())
                            feature = ""
                            for f in data['trait_options']['from']:
                                async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                    feature = json.loads(await resp.text())['desc'][0]
                                
                                fields.append((f['name'],feature,False))
                        except KeyError:
                            embed = discord.Embed(title=args,description=f'Feature Choices\nThis Character has no feature choices.',color=Color.red())
                    else:
                        page= 3
                        fields = []
                        
                        for race in data['subraces']:
                            async with self.session.get(f'{BASE_URL}{race["url"]}') as resp:
                                subrace = json.loads(await resp.text())
                            
                            
                            fields.append((subrace['name'],subrace['desc'],True))
                            abilities = ""
                            if subrace['ability_bonuses']:
                                for ability in subrace['ability_bonuses']:
                                    abilities+=f"{ability['ability_score']['name']}, "
                                
                                fields.append(("Ability Bonuses",abilities,False))
                            
                            if subrace['starting_proficiencies']:
                                proficiencies = ""
                                for prof in subrace['starting_proficiencies']:
                                    proficiencies+=f"{prof['name']}, "
                                   
                                fields.append(("Starting Proficiencies",proficiencies,False))
                                
                            if subrace['languages']:
                                languages = ""
                                for lan in subrace['languages']:
                                    languages+=f"{lan['name']}, "
                                fields.append(('Languages',languages,False))
                                
                            
                            traits = ""
                            for f in subrace['racial_traits']:
                                async with self.session.get(f'{BASE_URL}{f["url"]}') as resp:
                                    trait = json.loads(await resp.text())
                                traits+=f"_{trait['name']}:_ {trait['desc'][0]}\n\n"
                                
                            fields.append(('Traits',traits,False))
                            
                            try:
                                choices = f"_Choose {subrace['language_options']['choose']}:_\n"
                                for f in subrace['language_options']['from']:
                                    choices+=f"{f['name']},\n "
                                
                                fields.append(('Language Choices',choices,True))   
                            except KeyError:
                                pass
                            
                            try:
                                options = f"_Choose {subrace['racial_trait_options']['choose']}_\n"
                                for f in subrace['racial_trait_options']['from']:
                                    options+=f"{f['name']},\n "
                                    
                                fields.append(('Trait Options',options,True))
                            except KeyError:
                                pass
                                
                        if fields:
                            embed = discord.Embed(title=args,description=f'Subclass',color=Color.red())
                        else:
                            embed = discord.Embed(title=args,description=f'Subclass\nThis Class Has no Subclass',color=Color.red())
                else:
                    embed = discord.Embed(title='D&D Races',description=f'{count} total races.',color=Color.red())
                    race_names = ""
                    for f in races:
                        race_names+=f'\n*{f["name"]}*'
                        
                    embed.add_field(name='__Race List:__',value=race_names)
                            
                    await ctx.send(embed=embed)
                    return
                
                
                
                embed.set_footer(text = f'Page {page+1} of 4')
                for name,value,inline in fields:
                        embed.add_field(name=name,value=value,inline=inline)
                     
                if not message:
                    message = await ctx.send(embed=embed)
                else:
                    await message.edit(embed=embed)
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")
                        
                def check(reaction, user):
                    return message == reaction.message and not user.bot and user.id == ctx.author.id
                            
                reaction, user = await self.bot.wait_for('reaction_add', timeout=45, check=check)
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
                await ctx.send(embed=discord.Embed(title=f'{args} not found',description='Please Try again.',color=Color.red()))
  
def setup(bot):
	bot.add_cog(races(bot))