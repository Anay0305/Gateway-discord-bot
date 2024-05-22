import botinfo
from discord.ext import commands
import discord
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime
from io import BytesIO
import requests
import asyncio

def converttime(seconds):
    time = int(seconds)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    ls = []
    if hour != 0:
        ls.append(f"{hour}hrs")
    if minutes != 0:
        ls.append(f"{minutes}mins")
    if seconds != 0:
        ls.append(f"{seconds}secs")
    return ' '.join(ls)

def lb_(icon, name, guild_id, banner, requester, mode:str, typee:str, data, current, total, start_date, end_date=None):
    width = 960
    height = 500
    if end_date is None:
        end_date = str(datetime.now().date())

    if not banner:
        with open("bg.jpg", 'rb') as file:
            image = Image.open(BytesIO(file.read())).convert("RGBA")
            file.close()
    else:
        _res = requests.get(banner.url)
        image = Image.open(BytesIO(_res.content)).convert("RGBA")
        image = image.resize((width,height))
        image = image.filter(ImageFilter.GaussianBlur(radius=2))
        brightness_factor = 0.5
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness_factor)
    draw = ImageDraw.Draw(image)
    with open("mask.jpg", 'rb') as file:
        imagee = Image.open(BytesIO(file.read())).convert("RGBA")
        file.close()
    imagee = imagee.resize((width,height))
    image.paste(imagee, (0, 0), mask=imagee)
    logo_res = requests.get(icon)
    AVATAR_SIZE = 83
    avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
    border_radius = 23
    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, AVATAR_SIZE, AVATAR_SIZE), radius=border_radius, fill=255)
    image.paste(avatar_image, (53, 31), mask)
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 24)
    draw.text( (150, 42), f"{name}", fill="white", font=font)
    draw.text( (150, 74), f"ID: {guild_id}", fill="white", font=font)
    if start_date == end_date:
        hm = f"Today: {start_date}"
    else:
        hm = f"{start_date} to {end_date}"
    if mode.lower() == "messages":
        if typee.lower() == "users":
            xd = "User Messages"
        else:
            xd = "Text Channels"
    else:
        if typee.lower() == "users":
            xd = "Voice Users"
        else:
            xd = "Voice Channels"
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 21)
    draw.text( (580, 42), f"{xd} LeaderBoard", fill="white", font=font)
    font = ImageFont.truetype('Fonts/Montserrat-SemiBold.ttf', 21)
    draw.text( (580, 74), hm, fill="white", font=font)
    font = ImageFont.truetype('Fonts/Montserrat-SemiBold.ttf', 20)
    draw.text( (45, 476), f"Requested By {str(requester)}", fill="white", font=font, anchor="lm")
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 20)
    draw.text( (915, 476), f"Powered By Sputnik", fill="white", font=font, anchor="rm")
    font = ImageFont.truetype('Fonts/Montserrat-Medium.ttf', 18)
    draw.text( (915, 16), f"Page {current}/{total}", fill="white", font=font, anchor="rm")
    ls = [
        139, 205, 271, 338, 404
    ]
    ls1 = [
        139+26, 205+26, 271+26, 338+26, 404+26
    ]
    c = 0
    for i in data:
        c+=1
        logo_res = requests.get(data[i][2])
        AVATAR_SIZE = 51
        avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
        avatar_image = avatar_image.resize((int(AVATAR_SIZE), int(AVATAR_SIZE)))
        mask = Image.new('L', (int(AVATAR_SIZE), int(AVATAR_SIZE)), 0)
        circle_draw = ImageDraw.Draw(mask)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        num_font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 20)
        if c % 2 != 0:
            image.paste(avatar_image, (53, ls[int((c-1)/2)]), mask)
            draw.text( (130, ls1[int((c-1)/2)]), f"{data[i][1]}. ", fill=(255,255,255), font=num_font, anchor="lm")
            draw.text( (135 + num_font.getlength(f"{data[i][1]}. "), ls1[int((c-1)/2)]), f"{i}\n{data[i][0]}", fill=(255,255,255), font=font, anchor="lm")
        else:
            image.paste(avatar_image, (500, ls[int((c-1)/2)]), mask)
            draw.text( (130+447, ls1[int((c-1)/2)]), f"{data[i][1]}. ", fill=(255,255,255), font=num_font, anchor="lm")
            draw.text( (135+447 + num_font.getlength(f"{data[i][1]}. "), ls1[int((c-1)/2)]), f"{i}\n{data[i][0]}", fill=(255,255,255), font=font, anchor="lm")

    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename='profile.png')
    
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
        file = lb_(self.icon, self.ctx.guild.name, self.ctx.guild.id, self.ctx.guild.banner, self.ctx.author, self.mode, self.typee, self.file_list[self.current], self.current+1, len(self.file_list), self.start_, self.end_)
        await asyncio.sleep(1)
        await interaction.response.edit_message(content=None,
            attachments=[file], view=self
        )
        self.view = self.current

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green, disabled=True)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
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


        file = lb_(self.icon, self.ctx.guild.name, self.ctx.guild.id, self.ctx.guild.banner, self.ctx.author, self.mode, self.typee, self.file_list[self.current], self.current+1, len(self.file_list), self.start_, self.end_)
        await asyncio.sleep(1)
        await interaction.response.edit_message(content=None,
            attachments=[file], view=self
        )
        self.view = self.current
      
   
    @discord.ui.button(emoji="<a:Cross:937350485919289364>", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
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

        file = lb_(self.icon, self.ctx.guild.name, self.ctx.guild.id, self.ctx.guild.banner, self.ctx.author, self.mode, self.typee, self.file_list[self.current], self.current+1, len(self.file_list), self.start_, self.end_)
        await asyncio.sleep(1)
        await interaction.response.edit_message(content=None,
            attachments=[file], view=self
        )
        self.view = self.current

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

        file = lb_(self.icon, self.ctx.guild.name, self.ctx.guild.id, self.ctx.guild.banner, self.ctx.author, self.mode, self.typee, self.file_list[self.current], self.current+1, len(self.file_list), self.start_, self.end_)
        await asyncio.sleep(1)
        await interaction.response.edit_message(content=None,
            attachments=[file], view=self
        )
        self.view = self.current
    
    async def start(self, ctx: commands.Context, interaction: discord.Interaction=None):
        file = lb_(self.icon, self.ctx.guild.name, self.ctx.guild.id, self.ctx.guild.banner, self.ctx.author, self.mode, self.typee, self.file_list[0], self.current+1, len(self.file_list), self.start_, self.end_)
        if len(self.file_list) != 1:
            if interaction is not None:
                self.message = await interaction.response.send_message(file=file, view=self, ephemeral=True)
            else:
                self.message = await ctx.send(file=file, view=self)
            self.user = ctx.author
            await self.wait()
            return self.message
        else:
            if interaction is not None:
                self.message = await interaction.response.send_message(file=file, ephemeral=True)
            else:
                self.message = await ctx.send(file=file)
            self.user = ctx.author
            return self.message
