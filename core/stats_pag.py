import botinfo
from discord.ext import commands
import discord
from datetime import datetime
from io import BytesIO
import requests
import asyncio
import json

class PageChangeModal(discord.ui.Modal, title="Go to page"):

    page_number: discord.ui.TextInput[discord.ui.Modal] = discord.ui.TextInput(label="Page number", style=discord.TextStyle.short)

    def __init__(self, interface: 'StatPaginationView'):
        super().__init__(timeout=interface.timeout)
        self.interface = interface
        self.page_number.label = f"Page number (1-{len(interface.file_list)})"
        self.page_number.min_length = 1
        self.page_number.max_length = len(str(len(interface.file_list)))

    async def on_submit(self, interaction: discord.Interaction, /):
        await interaction.response.defer(ephemeral=False, thinking=False)
        try:
            if not self.page_number.value:
                raise ValueError("Page number not filled")

            self.interface.current = int(self.page_number.value) - 1
        except ValueError:
            await interaction.response.send_message(
                content=f"``{self.page_number.value}`` could not be converted to a page number",
                ephemeral=True
            )
        else:
            await interaction.message.edit(content="<a:loading:1215453200463958086>", attachments=[])
            if self.interface.ctx.guild.banner:
                banner = self.interface.ctx.guild.banner.url
            else:
                banner = None
            file_data = {
                'guild_icon': self.interface.icon,
                'guild_name': self.interface.ctx.guild.name,
                'guild_id': self.interface.ctx.guild.id,
                'guild_banner': banner,
                'requester': self.interface.ctx.author.display_name,
                'mode': self.interface.mode,
                'type': self.interface.typee,
                'data': self.interface.file_list[self.interface.current],
                'current': self.interface.current + 1,
                'total': len(self.interface.file_list),
                'start_date': self.interface.start_,
                'end_date': self.interface.end_
            }
            api_url = botinfo.api_url+"/leaderboard"
            payload = json.dumps(file_data)

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
            else:
                await interaction.message.delete()
                return await interaction.message.channel.send(f"Got some error while fetching the image.")
            await interaction.message.edit(content=None,
                attachments=[file], view=self.interface
            )

class StatPaginationView(discord.ui.View):
    current = 0

    def __init__(self, file_list: list, ctx, icon, mode, typee, start_, end_):
        super().__init__(timeout=300)
        self.file_list = file_list
        self.icon = icon
        self.start_ = start_
        self.end_ = end_
        self.mode = mode
        self.typee = typee
        self.ctx = ctx
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
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.current = 0
        await interaction.message.edit(content="<a:loading:1215453200463958086>", attachments=[])

        self.previous.disabled = True
        button.disabled = True

        if len(self.file_list) >= 1:
            self.next.disabled = False
            self._last.disabled = False
        else:
            self.next.disabled = True
            self._last.disabled = True
        if self.ctx.guild.banner:
            banner = self.ctx.guild.banner.url
        else:
            banner = None
        file_data = {
            'guild_icon': self.icon,
            'guild_name': self.ctx.guild.name,
            'guild_id': self.ctx.guild.id,
            'guild_banner': banner,
            'requester': self.ctx.author.display_name,
            'mode': self.mode,
            'type': self.typee,
            'data': self.file_list[self.current],
            'current': self.current + 1,
            'total': len(self.file_list),
            'start_date': self.start_,
            'end_date': self.end_
        }
        api_url = botinfo.api_url+"/leaderboard"
        payload = json.dumps(file_data)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=payload, headers=headers)

        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            await interaction.message.delete()
            return await interaction.message.channel.send(f"Got some error while fetching the image.")
        await interaction.message.edit(content=None,
            attachments=[file], view=self
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green, disabled=True)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.current = self.current - 1
        await interaction.message.edit(content="<a:loading:1215453200463958086>", attachments=[])

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

        if self.ctx.guild.banner:
            banner = self.ctx.guild.banner.url
        else:
            banner = None
        file_data = {
            'guild_icon': self.icon,
            'guild_name': self.ctx.guild.name,
            'guild_id': self.ctx.guild.id,
            'guild_banner': banner,
            'requester': self.ctx.author.display_name,
            'mode': self.mode,
            'type': self.typee,
            'data': self.file_list[self.current],
            'current': self.current + 1,
            'total': len(self.file_list),
            'start_date': self.start_,
            'end_date': self.end_
        }
        api_url = botinfo.api_url+"/leaderboard"
        payload = json.dumps(file_data)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=payload, headers=headers)

        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            await interaction.message.delete()
            return await interaction.message.channel.send(f"Got some error while fetching the image.")
        await interaction.message.edit(content=None,
            attachments=[file], view=self
        )
      
   
    @discord.ui.button(emoji="<a:Cross:937350485919289364>", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        await interaction.message.delete()
        return

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.current += 1
        await interaction.message.edit(content="<a:loading:1215453200463958086>", attachments=[])

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

        if self.ctx.guild.banner:
            banner = self.ctx.guild.banner.url
        else:
            banner = None
        file_data = {
            'guild_icon': self.icon,
            'guild_name': self.ctx.guild.name,
            'guild_id': self.ctx.guild.id,
            'guild_banner': banner,
            'requester': self.ctx.author.display_name,
            'mode': self.mode,
            'type': self.typee,
            'data': self.file_list[self.current],
            'current': self.current + 1,
            'total': len(self.file_list),
            'start_date': self.start_,
            'end_date': self.end_
        }
        api_url = botinfo.api_url+"/leaderboard"
        payload = json.dumps(file_data)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=payload, headers=headers)

        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            await interaction.message.delete()
            return await interaction.message.channel.send(f"Got some error while fetching the image.")
        await interaction.message.edit(content=None,
            attachments=[file], view=self
        )

    @discord.ui.button(label="≫", style=discord.ButtonStyle.blurple, disabled=False)
    async def _last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.file_list) - 1
        await interaction.message.edit(content="<a:loading:1215453200463958086>", attachments=[])

        button.disabled = True
        self.next.disabled = True

        if len(self.file_list) >= 1:
            self.first.disabled = False
            self.previous.disabled = False
        else:
            self.first.disabled = True
            self.previous.disabled = True

        if self.ctx.guild.banner:
            banner = self.ctx.guild.banner.url
        else:
            banner = None
        file_data = {
            'guild_icon': self.icon,
            'guild_name': self.ctx.guild.name,
            'guild_id': self.ctx.guild.id,
            'guild_banner': banner,
            'requester': self.ctx.author.display_name,
            'mode': self.mode,
            'type': self.typee,
            'data': self.file_list[self.current],
            'current': self.current + 1,
            'total': len(self.file_list),
            'start_date': self.start_,
            'end_date': self.end_
        }
        api_url = botinfo.api_url+"/leaderboard"
        payload = json.dumps(file_data)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=payload, headers=headers)

        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            await interaction.message.delete()
            return await interaction.message.channel.send(f"Got some error while fetching the image.")
        await interaction.message.edit(content=None,
            attachments=[file], view=self
        )

    @discord.ui.button(label="Go to Page", style=discord.ButtonStyle.grey, disabled=False)
    async def _goto(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        await interaction.response.send_modal(PageChangeModal(self))
    
    async def start(self, ctx: commands.Context, interaction: discord.Interaction=None, message: discord.Message=None):
        if message:
            await message.edit(content="<a:loading:1215453200463958086>", attachments=[])
        
        if self.ctx.guild.banner:
            banner = self.ctx.guild.banner.url
        else:
            banner = None
        file_data = {
            'guild_icon': self.icon,
            'guild_name': self.ctx.guild.name,
            'guild_id': self.ctx.guild.id,
            'guild_banner': banner,
            'requester': self.ctx.author.display_name,
            'mode': self.mode,
            'type': self.typee,
            'data': self.file_list[0],
            'current': self.current + 1,
            'total': len(self.file_list),
            'start_date': self.start_,
            'end_date': self.end_
        }
        api_url = botinfo.api_url+"/leaderboard"
        payload = json.dumps(file_data)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=payload, headers=headers)

        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            return await interaction.message.channel.send(f"Got some error while fetching the image.")
        if len(self.file_list) != 1:
            if message is not None:
                self.first.row = 1
                self.next.row = 1
                self.stop.row = 1
                self.previous.row = 1
                self._last.row = 1
                self._goto.row = 2
                await message.edit(content=None, attachments=[file], view=self)
                self.message = message
            elif interaction is not None:
                self.message = await interaction.response.send_message(file=file, view=self, ephemeral=True)
            else:
                self.message = await ctx.send(file=file, view=self)
            self.user = ctx.author
            await self.wait()
            return self.message
        else:
            if message is not None:
                self.remove_item(self.first)
                self.remove_item(self.previous)
                self.remove_item(self.stop)
                self.remove_item(self.next)
                self.remove_item(self._last)
                self.remove_item(self._goto)
                await message.edit(content=None, attachments=[file], view=self)
                self.message = message
            elif interaction is not None:
                self.message = await interaction.response.send_message(file=file, ephemeral=True)
            else:
                self.message = await ctx.send(file=file)
            self.user = ctx.author
            return self.message
