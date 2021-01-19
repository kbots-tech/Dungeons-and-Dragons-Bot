import discord
from datetime import datetime
from discord.ext import commands
from discord import Color


class help(commands.Cog, name='help'):

  def __init__(self, bot):
      self.bot = bot
      self.bot.remove_command('help')

  @commands.command(name='help', brief="List every command of the bot")
  async def all_commands(self, ctx,*,args=""):
        """ Provide a list of every command available command for the user,
        split by extensions and organized in alphabetical order.
        Will not show the event-only extensions """
        embed = discord.Embed(title='Dungeon Master Help',description=f'Dungeon master is the best bot for your D&D SRD Needs. Embeds feature pages to keep data concise and easy to read.',color=Color.red())
        
        embed.add_field(
            name='`>races [args]`',
            value='Use this command to get info about D&D race, if args is included it will give info about that race otherwise it will list all races.\n_Aliases:_ `>race`, `>races`, `>r`\neg: `>races dragonborn`',inline=False)
        embed.add_field(name='`>class [args] [levels]`',value='Use this command to get info about D&D class, if args is included it will give info about that class otherwise it will list all class.' 'If `levels` is appended to the end it will give info about each level.\n _Aliases:_ `>class`,`>races`, `>c`\neg: `>class bard levels` or `>class rogue`',
                        inline=False)
        embed.add_field(
            name='`>spells [args]`',
            value='Use this command to get info about D&D spell, if args is included it will give info about that spell otherwise it will list all races.\n_Aliases:_ `>spell`, `>spells`, `>s`\neg:`>spells fireball`',
            inline=False)
        embed.add_field(
            name='`>equipment [args]`',
            value='You can use this equipment to search through all items, this includes, tools, adventuring gear, armor, weapons etc. If no args are given it will list all items (sorted by category)\n_Aliases:_ `>e`\neg: `>equipment abacus`',
            inline=False)
        embed.add_field(
            name='`>armor [args]`',
            value='This command works the same as the equipment command but only returns and lists armor.\n_Aliases:_ `>a`, `>armor`',
            inline=False
        )
        embed.add_field(
            name='`>weapons [args]`',
            value='This command works the same as the equipment command but only returns and lists armor.\n_Aliases:_ `>w`, `>weapon`',
            inline=False
        )
        embed.add_field(
            name='`>monster [args]`',
            value='Use this command to get info about a monster or creature, if args is included it will give info about that creature otherwise it will list all creatures.\n _Aliases:_ `>monster`, `>mo`, `>m`\neg: `>monster aboleth`',
        )
        embed.add_field(
            name='`search [args]`',
            value='This comamnd can be used to search any item included in the above commands. It will return the first best match for optimal results you can narrow down your search by using the related command.\neg:`>search fireball`',
            inline=False
        )
        embed.add_field(
            name='`>character`',
            value='The creme de la creme of this bots commands, this command will walk you through the steps and generate a prefilled editable character sheet. Currently this is only for level 1 characters but planning is in place for a more advanced version.\n _Aliases:_ `>sheet`, `>cs`',
            inline=False
        )

        
        embed.add_field(name='Links',value="[Bot Invite](https://discord.com/oauth2/authorize?client_id=755592938922442782&permissions=10304&scope=bot) , [Support Server](https://discord.com/invite/wV5YdX94h4), [Github Repo](https://github.com/mcurranseijo/dnd-bot)")
        
        embed.add_field(name="Number of guilds", value=len(self.bot.guilds))


        await ctx.send(embed=embed)
  
  @commands.command(
      name='ping',
        brief='returns bot latency'
        )
  async def ping(self,ctx):
    await ctx.send(f'Pong! {round(self.bot.latency *1000)}ms')
            
  @commands.Cog.listener()
  async def on_command(self,ctx):
        print(f'command ran in {ctx.channel.name} by {ctx.author.name}')
        channel = self.bot.get_channel(790001914091274250)
        embed=discord.Embed(title='Command Logged',description=f'`{ctx.message.content}` ran by {ctx.author.mention} in {ctx.channel.mention}',color=0x008000,timestamp=datetime.now())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await channel.send(embed=embed)


def setup(bot):
	bot.add_cog(help(bot))