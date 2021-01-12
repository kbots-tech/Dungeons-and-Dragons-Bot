import discord
import aiohttp
import json

from discord.ext import commands
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class spells(commands.Cog):

  def __init__(self, bot):
      self.bot = bot
      self.session = aiohttp.ClientSession()

  @commands.command(aliases=['spell','s'])
  async def spells(self,ctx,*,args = None,level=None,page = 0,message = None,embed_data = None):
    try:
        if not embed_data:
            async with self.session.get(f'{BASE_URL}/api/spells') as resp:
                data = json.loads(await resp.text())
            count = data['count']
            classes = data['results']
            url_list = {}
            for f in classes:
                url_list[f['name']] = f['url']
            if args:
                values = get_close_matches(args, url_list)
                args = values[0]
        
        if not args:
            embed = discord.Embed(title='D&D Spells',description=f'{count} total spells.',color=Color.red())
            class_names = ""
            for f in classes:
                if len(class_names)+len(f["name"]) > 1000:
                    embed.add_field(name='__Spell List:__',value=class_names)
                    class_names = ""
                else:
                    class_names+=f'\n*{f["name"]}*'
                
            embed.add_field(name='__Spell List:__',value=class_names)
                
            await ctx.send(embed=embed)
            return    
        
        async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
            data = json.loads(await resp.text())
        
        embed = discord.Embed(title=args,description=data['desc'][0],color=Color.red())
        fields = []
        try:
            fields.append(("Higher Level",data['higher_level'][0],False))
        except KeyError:
            fields.append(("Higher Level",'N/A',False))
        
        try:
            fields.append(("Range",data['range'],True))
        except KeyError:
            fields.append(("Range","N/A",True))
            
        try:
            fields.append(("Components",', '.join(data['components']),True))
        except KeyError:
            fields.append(("Components","N/A",True))
        
        try:
            fields.append(("Material",data['material'],True))
        except KeyError:
            fields.append(("Material","N/A",True))
        
        
        try:
            fields.append(("Ritual",data['ritual'],True))
        except KeyError:
            fields.append(("Ritual","N/A",True))
            
        try:
            fields.append(("Concentration",data['concentratio'],True))
        except KeyError:
            fields.append(("Concentration","N/A",True))
            
        try:
            fields.append(("Level",data['level'],True))
        except KeyError:
            fields.append(("Level",'N/A',True))
            
        try:
            fields.append(("Attack Type",data['attack_type'],True))
        except KeyError:
            fields.append(("Attack Type",'N/A',True))
            
        try:
            fields.append(("Damage Type",data['attack_type'],True))
        except KeyError:
            fields.append(("Attack Type",'N/A',True))
        
        for name,value,inline in fields:
            embed.add_field(name=name,value=value,inline=inline)
         
        if not message:
            message = await ctx.send(embed=embed)
        else:
            await message.edit(embed=embed)
    except TimeoutError:
        pass
    except IndexError:
        await ctx.send(embed=discord.Embed(title=f'{args} not found',description='Please Try again.',color=Color.red()))

def setup(bot):
	bot.add_cog(spells(bot))