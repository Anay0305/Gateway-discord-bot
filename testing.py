import discord
import sqlite3
import core.database as database
import core.emojis as emojis
import botinfo
import requests
import typing
from core.voice_db import *
from discord.ext import commands
from ast import literal_eval
from core.paginators import PaginationView
from core.stats_pag import StatPaginationView
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime, timedelta
from io import BytesIO

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

def profile(icon, name, guild_id, banner, requester, mode:str, typee:str, data, current, total, start_date, end_date=None):
    width = 1033
    height = 502
    if end_date is None:
        end_date = str(datetime.now().date())
    banner = None
    if not banner:
        with open("Images/bg.jpg", 'rb') as file:
            image = Image.open(BytesIO(file.read())).convert("RGBA")
            file.close()
        image = image.resize((width,height))
    else:
        _res = requests.get(banner)
        image = Image.open(BytesIO(_res.content)).convert("RGBA")
        image = image.resize((width,height))
        image = image.filter(ImageFilter.GaussianBlur(radius=2))
        brightness_factor = 0.5
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness_factor)
    with open("Images/man.jpg", 'rb') as file:
        imagee = Image.open(BytesIO(file.read())).convert("RGBA")
        file.close()
    image = imagee.resize((width,height))
    draw = ImageDraw.Draw(image)
    #image.paste(imagee, (0, 0), mask=imagee)
    logo_res = requests.get(icon)
    AVATAR_SIZE = 72
    avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
    border_radius = 20
    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, AVATAR_SIZE, AVATAR_SIZE), radius=border_radius, fill=255)
    #image.paste(avatar_image, (18, 23), mask)
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 26)
    n = name
    while font.getlength(name) >= 415:
      name = name[0:-1]
    if n != name:
      name = name[0:-2] + "..."
    #draw.text( (105, 46), f"{name}", fill="white", font=font, anchor="lm")
    font = ImageFont.truetype('Fonts/Montserrat-Medium.ttf', 21)
    draw.text( (105, 66), f"Server Overview", fill="white", font=font, anchor="lt")
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 24)
    draw.text( (847, 31), f"Gateway", fill="white", font=font, anchor="mm")
    font = ImageFont.truetype('Fonts/Montserrat-MediumItalic.ttf', 16)
    #draw.text( (888, 66), f"Server Lookback Last 14 days\n~ TimeZone: UTC", fill="white", font=font, anchor="mm")
    font = ImageFont.truetype('Fonts/Montserrat-Bold.ttf', 24)
    draw.text( (32, 126), f"Messages", fill="white", font=font, anchor="lm")
    draw.text( (367, 126), f"Voice Activity", fill="white", font=font, anchor="lm")
    draw.text( (706, 126), f"Contributers", fill="white", font=font, anchor="lm")
    draw.text( (94, 322), f"Top Members", fill="white", font=font, anchor="lm")
    draw.text( (600, 322), f"Top Channels", fill="white", font=font, anchor="lm")
    image.save('Images/server_stats_mask.png')

ds = {
    "anayyy.dev | Anayyy": ["1 Message", 1, "https://cdn.discordapp.com/avatars/1141685323299045517/85bc43428128db92ceb8f75f97ee8d82.png?size=1024"]
}
profile("https://cdn.discordapp.com/icons/1183413203376554054/a_848ecf62181c3aa03650559ccbd8207d.png?size=1024", "Snaps", 1183413203376554054, "https://cdn.discordapp.com/banners/1183413203376554054/a_6925a0196db10b73adbf469efa88622a.png?size=1024", "Anay", "messages", "users", ds, 1, 10, "2024-05-22")