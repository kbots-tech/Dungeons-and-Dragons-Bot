import asyncio
import interactions
from interactions import Button, ButtonStyle, ComponentContext, ActionRow


class Paginator():
    def __init__(self, bot, ctx=None, embeds=None, only=False):
        self.client = bot
        self.ctx = ctx
        self.pages = embeds
        self.only = only
        self.buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='<--',
                custom_id="page_back"
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label=f"Page 1 of {len(embeds)}",
                custom_id="page_count",
                disabled=True
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='-->',
                custom_id=f"page_for"
            ),
        ]
        self.page = 0;
        if embeds != None:
            self.max_page = len(embeds) - 1
        else:
            self.max_page = 0
        self.action_row = ActionRow(components=self.buttons)
        self.message = ""

    async def start(self):
        self.message = await self.ctx.send(embeds=self.pages[0], components=[self.action_row])
        while True:


            async def check(button_ctx):
                if int(button_ctx.author.user.id) == int(self.ctx.author.user.id):
                    return True
                await self.ctx.send("I wasn't asking you!", ephemeral=True)
                return False

            try:
                button_ctx: ComponentContext = await self.client.wait_for_component(
                    components=self.buttons, check=check, timeout=15
                )

                if button_ctx.custom_id == "page_for":
                    if (self.page != self.max_page):
                        self.page += 1
                else:
                    if (self.page != 0):
                        self.page -= 1

                self.buttons[1].label = f"Page {self.page+1} of {len(self.pages)}"
                self.action_row = ActionRow(components=self.buttons)

                await self.message.edit(embeds=self.pages[self.page])
                await self.message.edit(components=[self.action_row])
                await self.ctx.defer(ephemeral=True)
            except asyncio.TimeoutError:
                for button in self.buttons:
                    button.disabled = True
                self.action_row = ActionRow(components=self.buttons)
                return await self.message.edit(components=[self.action_row])
