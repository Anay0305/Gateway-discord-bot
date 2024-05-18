from typing import Optional, NamedTuple
from itertools import islice
import botinfo
from discord.ext import commands
import discord


def get_chunks(iterable, size):
    it = iter(iterable)
    return iter(lambda: tuple(islice(it, size)), ())


class Page(NamedTuple):
    index: int
    content: str


class Pages:
    def __init__(self, pages: list):
        self.pages = pages
        self.cur_page = 1

    @property
    def current_page(self) -> Page:
        return Page(self.cur_page, self.pages[self.cur_page - 1])

    @property
    def next_page(self) -> Optional[Page]:
        if self.cur_page == self.total:
            return None

        self.cur_page += 1
        return self.current_page

    @property
    def previous_page(self) -> Optional[Page]:
        if self.cur_page == 1:
            return None

        self.cur_page -= 1
        return self.current_page

    @property
    def first_page(self) -> Page:
        self.cur_page = 1
        return self.current_page

    @property
    def last_page(self) -> Page:
        self.cur_page = self.total
        return self.current_page

    @property
    def total(self):
        return len(self.pages)

class StatPaginationView(discord.ui.View):
    current = 0

    def __init__(self, file_list: list, ctx, links: list=None):
        super().__init__(timeout=90)
        self.file_list = file_list
        self.ctx = ctx
        self.links = links
        self.view = None
        self.message = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user == interaction.user or interaction.user.id in botinfo.main_devs:
            return True
        await interaction.response.send_message(
            f"Only **{self.user}** can interact. Run the command if you want to.",
            ephemeral=True,
        )
        return False
    
    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

    @discord.ui.button(label="≪", style=discord.ButtonStyle.blurple, disabled=True)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0

        self.previous.disabled = True
        button.disabled = True

        if len(self.file_list) >= 1:
            self.next.disabled = False
            self._last.disabled = False
        else:
            self.next.disabled = True
            self._last.disabled = True

        await interaction.response.edit_message(
            attachments=[self.file_list[self.current]], view=self
        )
        self.view = self.current

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green, disabled=True)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current = self.current - 1

        if len(self.file_list) >= 1:  # if list consists of 2 pages, if,
            self._last.disabled = (
                False  # then `last` and `next` need not to be disabled
            )
            self.next.disabled = False
        else:
            self._last.disabled = True  # else it should be disabled
            self.next.disabled = True  # because why not

        if self.current <= 0:  # if we are on first page,
            self.current = 0  # we disabled `first` and `previous`
            self.first.disabled = True
            button.disabled = True
        else:
            self.first.disabled = False
            button.disabled = False


        await interaction.response.edit_message(
            attachments=[self.file_list[self.current]], view=self
        )
        self.view = self.current
      
   
    @discord.ui.button(emoji="<a:Cross:937350485919289364>", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1

        if self.current >= len(self.file_list) - 1:
            self.current = len(self.file_list) - 1
            button.disabled = True
            self._last.disabled = True

        if len(self.file_list) >= 1:
            self.first.disabled = False
            self.previous.disabled = False
        else:
            self.previous.disabled = True
            self.first.disabled = True

        await interaction.response.edit_message(
            attachments=[self.file_list[self.current]], view=self
        )
        self.view = self.current

    @discord.ui.button(label="≫", style=discord.ButtonStyle.blurple, disabled=False)
    async def _last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.file_list) - 1

        button.disabled = True
        self.next.disabled = True

        if len(self.file_list) >= 1:
            self.first.disabled = False
            self.previous.disabled = False
        else:
            self.first.disabled = True
            self.previous.disabled = True

        await interaction.response.edit_message(
            attachments=[self.file_list[self.current]], view=self
        )
        self.view = self.current
    
    async def start(self, ctx: commands.Context, interaction: discord.Interaction=None):
        if len(self.file_list) != 1:
            if interaction is not None:
                self.message = await interaction.response.send_message(file=self.file_list[0], view=self, ephemeral=True)
            else:
                self.message = await ctx.send(file=self.file_list[0], view=self)
            self.user = ctx.author
            await self.wait()
            return self.message
        else:
            if interaction is not None:
                self.message = await interaction.response.send_message(file=self.file_list[0], ephemeral=True)
            else:
                self.message = await ctx.send(file=self.file_list[0])
            self.user = ctx.author
            return self.message
