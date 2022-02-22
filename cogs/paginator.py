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
                custom_id=f"page_back"
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
        if not self.message:
            self.message = await self.ctx.send(embeds=[interactions.Embed(**self.pages[0].to_dict())],
                                               components=[self.action_row])
        else:
            await self.message.edit(embeds=[interactions.Embed(**self.pages[self.page].to_dict())])

        async def check(button_ctx):
            print(f"PAIRS: {button_ctx.message.id} and {self.message.id}")
            if int(button_ctx.author.user.id) == int(self.ctx.author.user.id) and \
                    int(button_ctx.message.id) == int(self.message.id):
                return True
            return False

        while True:
            try:
                button_ctx: ComponentContext = await self.client.wait_for_component(
                    components=self.buttons, check=check, timeout=15
                )

                print(button_ctx)

                if button_ctx.custom_id == "page_for":
                    if (self.page != self.max_page):
                        self.page += 1
                else:
                    if (self.page != 0):
                        self.page -= 1

                self.buttons[1] = Button(
                    style=ButtonStyle.PRIMARY,
                    label=f"Page {self.page+1} of {len(self.pages)}",
                    custom_id="page_count",
                    disabled=True
                )
                self.action_row = ActionRow(components=self.buttons)
                await button_ctx.edit(embeds=[interactions.Embed(**self.pages[self.page].to_dict())],
                                      components=self.action_row)

            except asyncio.TimeoutError:

                self.buttons = [
                    Button(
                        style=ButtonStyle.PRIMARY,
                        label='<--',
                        custom_id="page_back",
                        disabled=True
                    ),
                    Button(
                        style=ButtonStyle.PRIMARY,
                        label=f"Page 1 of {len(self.pages)}",
                        custom_id="page_count",
                        disabled=True
                    ),
                    Button(
                        style=ButtonStyle.PRIMARY,
                        label='-->',
                        custom_id=f"page_for",
                        disabled=True
                    ),
                ]
                self.action_row = ActionRow(components=self.buttons)
                return await self.ctx.edit(embeds=[interactions.Embed(**self.pages[self.page].to_dict())], components=self.action_row)