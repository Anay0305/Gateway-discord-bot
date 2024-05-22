import discord
import sqlite3
import database
import emojis
import botinfo
import requests
import typing
from voice_db import *
from discord.ext import commands
from ast import literal_eval
from paginators import PaginationView
from stats_pag import StatPaginationView
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
    width = 960
    height = 500
    if end_date is None:
        end_date = str(datetime.now().date())

    if not banner:
        with open("bg.jpg", 'rb') as file:
            image = Image.open(BytesIO(file.read())).convert("RGBA")
            file.close()
    else:
        _res = requests.get(banner)
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
    draw.text( (955, 14), f"Page {current}/{total}", fill="white", font=font, anchor="rm")
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
            image.paste(avatar_image, (53, ls[int(c-1/2)]), mask)
            draw.text( (130, ls1[int(c-1/2)]), f"{data[i][1]}. ", fill=(255,255,255), font=num_font, anchor="lm")
            draw.text( (135 + num_font.getlength(f"{data[i][1]}. "), ls1[int(c-1/2)]), f"{i}\n{data[i][0]}", fill=(255,255,255), font=font, anchor="lm")
        else:
            image.paste(avatar_image, (500, ls[int(c-1/2)]), mask)
            draw.text( (130+447, ls1[int(c-1/2)]), f"{data[i][1]}. ", fill=(255,255,255), font=num_font, anchor="lm")
            draw.text( (135+447 + num_font.getlength(f"{data[i][1]}. "), ls1[int(c-1/2)]), f"{i}\n{data[i][0]}", fill=(255,255,255), font=font, anchor="lm")
    image.show()

ds = {
    "anayyy.dev | Anayyy": ["1 Message", 1, "https://cdn.discordapp.com/avatars/1141685323299045517/85bc43428128db92ceb8f75f97ee8d82.png?size=1024"]
}
profile("https://cdn.discordapp.com/icons/1183413203376554054/a_848ecf62181c3aa03650559ccbd8207d.png?size=1024", "Snaps", 1183413203376554054, "https://cdn.discordapp.com/banners/1183413203376554054/a_6925a0196db10b73adbf469efa88622a.png?size=1024", "Anay", "messages", "users", ds, 1, 10, "2024-05-22")