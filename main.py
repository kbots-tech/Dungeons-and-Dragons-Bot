import interactions

extensions = [
	'cogs.spells', 'cogs.races', 'cogs.monsters','cogs.equipment', 'cogs.classes'
]

bot = interactions.Client(
	token="TOKEN HERE",
	sync_command=True
)

bot.author_id = 480055359462178826

for command in extensions:
	bot.load(command)

@bot.event
async def on_ready():  # When the bot is ready
	print("I'm in")

bot.start() # Starts the bot