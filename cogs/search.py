

import discord
import aiohttp
import json

from asyncio import TimeoutError
from discord.ext import commands
from discord import Color
from difflib import get_close_matches

BASE_URL = 'https://www.dnd5eapi.co'


class Search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        with open("items.json") as file:
            self.items = json.load(file)
        with open("spells.json") as file:
            self.spells = json.load(file)
        with open("monsters.json") as file:
            self.monsters = json.load(file)

    @commands.command(aliases=['query'])
    async def search(self, ctx, *, args=None):
        values = get_close_matches(args, [item['name'] for item in self.items['Adventuring']['items']], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('equipment'), args=values[0])
            return
        values = get_close_matches(args, [item['name'] for item in self.items['Tools']['items']], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('equipment'), args=values[0])
            return
        values = get_close_matches(args, [item['name'] for item in self.items['Mounts and Vehicles']['items']], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('equipment'), args=values[0])
            return
        values = get_close_matches(args, [item['name'] for item in self.items['Weapons']['items']], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('equipment'), args=values[0])
            return
        values = get_close_matches(args, [item['name'] for item in self.items['Armor']['items']], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('equipment'), args=values[0])
            return
        values = get_close_matches(args, self.spells['spells'], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('spells'), args=values[0])
            return
        classes = [
            'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer',
            'Warlock', 'Wizard'
        ]
        values = get_close_matches(args, classes, cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('class'), args=values[0])
            return
        races = [
            'Dragonborn', 'Dwarf', 'Elf', 'Gnome', 'Half-Elf', 'Half-Orc', 'Halfling', 'Human', 'Tiefling'
        ]
        values = get_close_matches(args, races, cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('race'), args=values[0])
            return

        values = get_close_matches(args, self.monsters['monsters'], cutoff=.75)
        if values:
            await ctx.invoke(self.bot.get_command('monster'), args=values[0])
            return
        await ctx.send(
            embed=discord.Embed(title=f'{args} not found', description='Please Try again.', color=Color.red()))




def setup(bot):
    bot.add_cog(Search(bot))
