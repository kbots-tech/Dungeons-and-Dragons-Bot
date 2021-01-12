from discord.ext import commands
from settings import TOKEN


bot = commands.Bot(
	command_prefix=">.",  # Change to desired prefix
	case_insensitive=True  # Commands aren't case-sensitive
)

bot.author_id = 480055359462178826


@bot.event 
async def on_ready():  # When the bot is ready
	print("I'm in")
	print(bot.user)  # Prints the bot's username and identifier

extensions = [
	'cogs.spells','cogs.dev','cogs.help','cogs.classes','cogs.races','cogs.equipment', 'cogs.charactersheet'
]

if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loads every extension.

bot.run(TOKEN)  # Starts the bot
