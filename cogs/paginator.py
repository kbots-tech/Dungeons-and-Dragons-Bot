import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, Option, Choice, OptionType

class paginator():
    def __init__(self, ctx, pages = []):
        self.ctx = ctx
        self.pages = pages
        buttons = buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='<--',
                custom_id="left"
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='-->',
                custom_id="right"
            ),
        ]
        self.page = 0;
        self.max_page = len(pages)-1
        self.action_row = ActionRow(buttons)
        self.message = ""

    async def start(self):
        self.message = await self.ctx.send(embeds=self.pages[0], components=[self.action_row])

    @interactions.extension_component('left')
    async def on_component(self, ctx):
        if(self.page != 0):
            self.page-=1
            await self.message.edit(embeds=self.pages[self.page])

    @interactions.extension_component('right')
    async def on_component(self, ctx):
        if (self.page != self.max_page):
            self.page += 1
            await self.message.edit(embeds=self.pages[self.page])
