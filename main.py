import interactions
from interactions.ext import wait_for

extensions = [
	'cogs.classes', 'cogs.dmhub', 'cogs.equipment', 'cogs.monsters', 'cogs.races', 'cogs.spells'
]

bot = interactions.Client(
	token="NzU4NDgwNjA3NjM4MDYxMDU2.X2vkHA.VRovcXFHJE5RtsEbG6VG9XkX-kA",
	sync_command=True, sync_on_reload=True
)
wait_for.setup(bot, add_method=True)

bot.author_id = 480055359462178826

for command in extensions:
	bot.load(command)

@bot.event
async def on_ready():  # When the bot is ready
	print("I'm in")

bot.start() # Starts the bot