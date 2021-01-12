import discord
import aiohttp
import json

from asyncio import TimeoutError
from discord.ext import commands
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class equipment(commands.Cog):

  def __init__(self, bot):
      self.bot = bot
      self.session = aiohttp.ClientSession()

  @commands.command(aliases=['armor','weapon','e'])
  async def equipment(self,ctx,*,args = None,level=None,page = 0,message = None,embed_data = None):
        try:
            if not embed_data:
                async with self.session.get(f'{BASE_URL}/api/equipment') as resp:
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
                embed = discord.Embed(title='D&D Equipment',description=f'{count} total items.',color=Color.red())
                class_names = ""
                for f in classes:
                    if len(class_names)+len(f["name"]) > 1000:
                        embed.add_field(name='__Item List:__',value=class_names)
                        class_names = ""
                    else:
                        class_names+=f'\n*{f["name"]}*'
                    
                embed.add_field(name='__Item List:__',value=class_names)
                    
                await ctx.send(embed=embed)
                return
            
            async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
                    data = json.loads(await resp.text())
                    
            
            fields = []
            if data['equipment_category']['name'] == "Armor":
    	        fields.append(("Armor Category",data['armor_category'],True))
    	        fields.append(("Armor Class",f"_Base:_ {data['armor_class']['base']}\n_Dex Bonus:_ {data['armor_class']['dex_bonus']}\n_Max Bonus:_ {data['armor_class']['max_bonus']}",True))
    	        fields.append(("Strength Minimum",data['str_minimum'],True))
    	        fields.append(("Stealth Disadvantage",data['stealth_disadvantage'],True))
    	        fields.append(("Weight",data['weight'],True))
    	        fields.append(("Cost",f"{data['cost']['quantity']} {data['cost']['unit']}",True))
                
            elif data['equipment_category']['name'] == "Weapon":
                fields.append(("Weapon Category",data['weapon_category'],True))
                fields.append(("Weapon Range",data['weapon_range'],True))
                fields.append(("Cost",f"{data['cost']['quantity']} {data['cost']['unit']}",True))
                fields.append(("Cost",f"{data['damage']['damage_dice']} {data['damage']['damage_type']['name']}",True))
                fields.append(("Range",f"_Normal:_ {data['range']['normal']}\n_Long:_ {data['range']['long']}",True))
                fields.append(("Weight",data['weight'],True))
                properties = ""
                
                for f in data['properties']:
                    properties+= f"{f['name']}, "
                    
                fields.append(("Properties",properties,False))
    	            
                
            else:
                fields.append(('Equipment Category',data['equipment_category']['name'],True))
                
                fields.append(('Gear Category',data['gear_category']['name'],True))
                fields.append(('Cost',f"{data['cost']['quantity']} {data['cost']['unit']}",True))
            
            async with self.session.get(f'{BASE_URL}{url_list[args]}') as resp:
                data = json.loads(await resp.text())
            
            if data['equipment_category']['name'] != "Armor":
                try:
                    embed = discord.Embed(title=args,description=data['desc'][0],color=Color.red())
                except KeyError:
                    embed = discord.Embed(title=args,color=Color.red())
            else:
                try:
                    embed = discord.Embed(title=args+' Armor',description=data['desc'][0],color=Color.red())
                except KeyError:
                    embed = discord.Embed(title=args+" Armor",color=Color.red())
            
            for name,value,inline in fields:
                embed.add_field(name=name,value=value,inline=inline)
             
            if not message:
                message = await ctx.send(embed=embed)
            else:
                await message.edit(embed=embed)
        except TimeoutError:
            return
        except IndexError:
            await ctx.send(embed=discord.Embed(title=f'{args} not found',description='Please Try again.',color=Color.red()))

def setup(bot):
	bot.add_cog(equipment(bot))