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
from PIL import Image, ImageDraw, ImageFont
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

def lb_(mode:str, typee:str, data, current, total, start_date, end_date=str(datetime.now().date())):
    width = 960
    height = 500

    with open("lb_bg.jpg", 'rb') as file:
        image = Image.open(BytesIO(file.read())).convert("RGBA")
        file.close()
    image = image.resize((width,height))
    draw = ImageDraw.Draw(image)
    pfp = "https://cdn.discordapp.com/icons/1183413203376554054/a_848ecf62181c3aa03650559ccbd8207d.gif?size=1024"
    pfp = pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")
    logo_res = requests.get(pfp)
    AVATAR_SIZE = 78
    avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
    circle_image = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE))
    circle_draw = ImageDraw.Draw(circle_image)
    circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    image.paste(avatar_image, (45, 20), circle_image)
    pfp = "https://cdn.discordapp.com/avatars/1240005601220755557/2264a78516904e4e0ba9681cc136aa83.png?size=1024"
    pfp = pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")
    logo_res = requests.get(pfp)
    AVATAR_SIZE = 30
    avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
    circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 28)
    draw.text( (140, 36), f"Snaps Social • Active • Community !", fill="black", font=font)
    font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 24)
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
    draw.text( (760, 60), f"{xd} LeaderBoard\n{hm}", fill="black", font=font, anchor="mm")
    font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 20)
    draw.text( (45, 476), f"Requested By anayyy.dev", fill="white", font=font, anchor="lm")
    font = ImageFont.truetype('Fonts/Alkatra-Bold.ttf', 20)
    draw.text( (480, 476), f"Powered By Sputnik", fill="white", font=font, anchor="mm")
    font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 20)
    draw.text( (915, 476), f"Page {current}/{total}", fill="white", font=font, anchor="rm")
    c = 0
    for i in data:
        c+=1
        num_font = ImageFont.truetype('Fonts/Alkatra-Regular.ttf', 26-len(str(data[i][1])))
        user_font = ImageFont.truetype('Fonts/Alkatra-Regular.ttf', 24)
        data_font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 26)
        if c % 2 != 0:
            draw.text( (76, 148 + int((c-1)/2)*71), f"{data[i][1]}.", fill="white", font=num_font, anchor="mm")
            draw.text( (115, 126 + int((c-1)/2)*71), f"{i}", fill=(0, 135, 232), font=user_font, anchor="lt")
            if len(data[i]) > 1:
                draw.text( (115+ user_font.getlength(f"{i}"), 126 + int((c-1)/2)*71), f" • {data[i][2]}", fill=(46, 111, 158), font=user_font, anchor="lt")
            if mode.lower == "messages":
                x = f"{data[i][0]} Messages"
            else:
                x = converttime(data[i][0])
            draw.text( (115, 150+ int((c-1)/2)*71), f"{x}", fill="black", font=data_font, anchor="lt")
        else:
            draw.text( (76+462, 148 + int((c-1)/2)*71), f"{data[i][1]}.", fill="white", font=num_font, anchor="mm")
            draw.text( (115+462, 126 + int((c-1)/2)*71), f"{i} ", fill=(0, 135, 232), font=user_font, anchor="lt")
            if len(data[i]) > 1:
                draw.text( (115+462+user_font.getlength(f"{i}"), 126 + int((c-1)/2)*71), f" • {data[i][2]}", fill=(46, 111, 158), font=user_font, anchor="lt")
            if mode.lower == "messages":
                x = f"{data[i][0]} Messages"
            else:
                x = converttime(data[i][0])
            draw.text( (115+462, 150+ int((c-1)/2)*71), f"{x}", fill="black", font=data_font, anchor="lt")

    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename='profile.png')

def convert_date(date_str):
    if date_str.lower() == 'today' or date_str.lower() == "daily":
        return datetime.today().strftime('%Y-%m-%d')
    elif date_str.lower() == 'yesterday':
        yesterday = datetime.today() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    
    formats = ['%d %b %Y', '%d %B %Y', '%d %b', '%d %B', '%d/%m/%y', '%d.%m.%y']
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if '%Y' not in fmt:
                dt = dt.replace(year=datetime.now().year)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    try:
        day = int(date_str)
        today = datetime.today()
        current_month_year = today.strftime('%b %Y')
        dt = datetime.strptime(f"{day} {current_month_year}", "%d %b %Y")
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    return date_str

def date_range(start_date_str: str, end_date_str=None):
    if start_date_str.startswith("last"):
        start_date_str = start_date_str.replace("last","")
        if "m" in start_date_str:
            x = start_date_str.split()[0]
            months = int(x.strip())
            end_date = datetime.today()
            start_date = end_date - timedelta(days=months * 30)
        else:
            x = start_date_str.split()[0]
            days = int(x.strip())
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days - 1)
    else:
        start_date = datetime.strptime(convert_date(start_date_str), '%Y-%m-%d')
        if end_date_str is None:
            end_date_str = start_date_str
        end_date = datetime.strptime(convert_date(end_date_str), '%Y-%m-%d')
    delta = end_date - start_date
    dates = []
    for i in range(0, delta.days + 1):
        dates.append((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))
    return dates

def check_bl_channel(channel: typing.Union[discord.TextChannel, discord.VoiceChannel, None]):
    if isinstance(channel, discord.TextChannel):
        msg_db = database.fetchone("*", "messages_db", "guild_id", channel.guild.id)
        if msg_db is None:
            return False
        bl_channel_db = literal_eval(msg_db['bl_channels'])
        if channel.id in bl_channel_db:
            return True
        else:
            return False
    else:
        if channel is None:
            return True
        msg_db = database.fetchone("*", "voice_db", "guild_id", channel.guild.id)
        if msg_db is None:
            return False
        bl_channel_db = literal_eval(msg_db['bl_channels'])
        if channel.id in bl_channel_db:
            return True
        else:
            return False

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await self.bot.wait_until_ready()
        guild = member.guild
        database.insert("voice_db", "guild_id", (guild.id, ))
        res = database.fetchone("*", "voice_db", "guild_id", guild.id)
        channel_db = literal_eval(res['channel_time'])
        user_db = literal_eval(res['user_time'])
        day_db = literal_eval(res['specific_day_time'])
        today = f"{str(datetime.now().date())}"
        if today not in day_db:
            day_db[today] = {
                'users': {},
                'channels': {}
            }
        if before.channel is not None:
            if len(before.channel.members) == 0:
                if guild.id in channel_start:
                    channel_time = round(datetime.now().timestamp() - channel_start[guild.id][before.channel.id])
                    del channel_start[guild.id][before.channel.id]
                    if before.channel.id in channel_db:
                        channel_db[before.channel.id] += channel_time
                    else:
                        channel_db[before.channel.id] = channel_time
                    if before.channel.id in day_db[today]['channels']:
                        day_db[today]['channels'][before.channel.id] += channel_time
                    else:
                        day_db[today]['channels'][before.channel.id] = channel_time
            if check_bl_channel(after.channel):
                if guild.id in user_start:
                    user_time = round(datetime.now().timestamp() - user_start[guild.id][member.id])
                    del user_start[guild.id][member.id]
                    if member.id in user_db:
                        user_db[member.id] += user_time
                    else:
                        user_db[member.id] = user_time
                    if member.id in day_db[today]['users']:
                        day_db[today]['users'][member.id] += user_time
                    else:
                        day_db[today]['users'][member.id] = user_time
            else:
                if guild.id in channel_start:
                    if after.channel.id not in channel_start[guild.id]:
                        channel_start[guild.id][after.channel.id] = round(datetime.now().timestamp())
                else:
                    channel_start[guild.id] = {
                        after.channel.id: round(datetime.now().timestamp())
                    }
        else:
            if guild.id in user_start:
                user_start[guild.id][member.id] = round(datetime.now().timestamp())
            else:
                user_start[guild.id] = {
                    member.id: round(datetime.now().timestamp())
                }
            if guild.id in channel_start:
                if after.channel.id not in channel_start[guild.id]:
                    channel_start[guild.id][after.channel.id] = round(datetime.now().timestamp())
            else:
                channel_start[guild.id] = {
                    after.channel.id: round(datetime.now().timestamp())
                }
        day_db[today]['users'] = dict(sorted(day_db[today]['users'].items(), key=lambda item: item[1], reverse=True))
        day_db[today]['channels'] = dict(sorted(day_db[today]['channels'].items(), key=lambda item: item[1], reverse=True))
        user_db = dict(sorted(user_db.items(), key=lambda item: item[1], reverse=True))
        channel_db = dict(sorted(channel_db.items(), key=lambda item: item[1] ,reverse=True))
        dic = {
            'user_time': f"{user_db}",
            'channel_time': f"{channel_db}",
            'specific_day_time': f"{day_db}"
        }
        database.update_bulk("voice_db", dic, "guild_id", guild.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()
        if not message.guild or message.author.bot:
            return
        if check_bl_channel(message.channel):
            return
        database.insert("messages_db", "guild_id", (message.guild.id, ))
        res = database.fetchone("*", "messages_db", "guild_id", message.guild.id)
        user_db = literal_eval(res['user_messages'])
        if message.author.id in user_db:
            user_db[message.author.id] += 1
        else:
            user_db[message.author.id] = 1
        channel_db = literal_eval(res['channel_messages'])
        if message.channel.id in channel_db:
            channel_db[message.channel.id] += 1
        else:
            channel_db[message.channel.id] = 1
        day_db = literal_eval(res['specific_day_messages'])
        today = f"{str(datetime.now().date())}"
        if today not in day_db:
            day_db[today] = {
                'users': {},
                'channels': {}
            }
        if message.author.id in day_db[today]['users']:
            day_db[today]['users'][message.author.id] += 1
        else:
            day_db[today]['users'][message.author.id] = 1
        if message.channel.id in day_db[today]['channels']:
            day_db[today]['channels'][message.channel.id] += 1
        else:
            day_db[today]['channels'][message.channel.id] = 1
        day_db[today]['users'] = dict(sorted(day_db[today]['users'].items(), key=lambda item: item[1], reverse=True))
        day_db[today]['channels'] = dict(sorted(day_db[today]['channels'].items(), key=lambda item: item[1], reverse=True))
        user_db = dict(sorted(user_db.items(), key=lambda item: item[1], reverse=True))
        channel_db = dict(sorted(channel_db.items(), key=lambda item: item[1], reverse=True))
        dic = {
            'user_messages': f"{user_db}",
            'channel_messages': f"{channel_db}",
            'specific_day_messages': f"{day_db}"
        }
        database.update_bulk("messages_db", dic, "guild_id", message.guild.id)

    @commands.hybrid_group(aliases=["lb"], invoke_without_command=True)
    async def leaderboard(self, ctx: commands.Context):
        pass
    
    @leaderboard.command(aliases=['m', 'msg', 'msgs'], description="Shows the messages leaderboard of the server")
    async def messages(self, ctx: commands.Context, mode=None, start_date: str=None, *, end_date: str=None):
        res = database.fetchone("*", "messages_db", "guild_id", ctx.guild.id)
        if res is None:
            return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Text channels."))
        channel_db = literal_eval(res['channel_messages'])
        user_db = literal_eval(res['user_messages'])
        day_db = literal_eval(res['specific_day_messages'])
        if mode is not None:
            if "u" not in mode and "c" not in mode:
                if start_date is not None and end_date is not None:
                    end_date = start_date+" "+end_date
                elif start_date is not None:
                    end_date = start_date
                else:
                    end_date = None
                start_date = mode
                mode = None
        if mode is None or "u" in mode:
            count = 1
            if start_date is not None:
                if end_date is not None:
                    if "to" in str(start_date+end_date):
                        x = str(start_date+end_date).split("to")
                        start_date = x[0].strip()
                        end_date = x[1].strip()
                try:
                    try:
                        date_list = date_range(start_date, end_date)
                    except:
                        date_list = date_range(start_date+end_date)
                except:
                    return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="Please enter the dates correctly."))
                dic = {}
                for i in date_list:
                    if i in day_db:
                        for j in day_db[i]['users']:
                            if j in dic:
                                dic[j]+=day_db[i]['users'][j]
                            else:
                                dic[j] =day_db[i]['users'][j]
                start_ = date_list[0]
                end_ = date_list[-1]
            else:
                end_ = None
                for i in day_db:
                    for k in day_db[i]['users']:
                        if ctx.guild.id == k:
                            start_ = i
                            break
                dic = user_db
            des = {}
            for i in dic:
                u = discord.utils.get(ctx.guild.members, id=i)
                if u is not None:
                    des[u.name] = [dic[i], count, u.display_name]
                    count+=1
            lss = []
            xd = []
            coun = 0
            for i in des:
                coun += 1
                xd.append(des[i])
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = []
            file_list = []
            no = 1
            for k in lss:
                file = lb_("messages", "users", k, no, len(lss), start_, end_)
                file_list.append(file)
                no+=1
            if no == 1:   
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Text channels."))
            page = StatPaginationView(file_list=file_list, ctx=ctx)
            await page.start(ctx)
        else:
            count = 1
            if start_date is not None:
                if end_date is not None:
                    if "to" in start_date+end_date:
                        x = str(start_date+end_date).split("to")
                        start_date = x[0].strip()
                        end_date = x[1].strip()
                try:
                    try:
                        date_list = date_range(start_date, end_date)
                    except:
                        date_list = date_range(start_date+end_date)
                except:
                    return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="Please enter the dates correctly."))
                dic = {}
                for i in date_list:
                    if i in day_db:
                        for j in day_db[i]['channels']:
                            if j in dic:
                                dic[j]+=day_db[i]['channels'][j]
                            else:
                                dic[j] =day_db[i]['channels'][j]
                start_ = date_list[0]
                end_ = date_list[-1]
            else:
                end_ = None
                for i in day_db:
                    for k in day_db[i]['users']:
                        if ctx.guild.id == k:
                            start_ = i
                            break
            des = {}
            for i in dic:
                u = discord.utils.get(ctx.guild.channels, id=i)
                if u is not None:
                    des[u.name] = [dic[i], count]
                    count+=1
            lss = []
            xd = []
            coun = 0
            for i in des:
                coun += 1
                xd.append(des[i])
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = []
            file_list = []
            no = 1
            for k in lss:
                file = lb_("messages", "channels", k, no, len(lss), start_, end_)
                file_list.append(file)
                no+=1
            if no == 1:   
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Text channels."))
            page = StatPaginationView(file_list=file_list, ctx=ctx)
            await page.start(ctx)

    @leaderboard.command(aliases=['v', 'vc', 'vcs'], description="Shows the voice leaderboard of the server")
    async def voice(self, ctx: commands.Context, mode=None, start_date: str=None, *, end_date: str=None):
        res = database.fetchone("*", "voice_db", "guild_id", ctx.guild.id)
        if res is None:
            return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
        channel_db = literal_eval(res['channel_time'])
        user_db = literal_eval(res['user_time'])
        day_db = literal_eval(res['specific_day_time'])
        if mode is not None:
            if "u" not in mode and "c" not in mode:
                if start_date is not None and end_date is not None:
                    end_date = start_date+" "+end_date
                elif start_date is not None:
                    end_date = start_date
                else:
                    end_date = None
                start_date = mode
                mode = None
        if mode is None or "u" in mode:
            count = 1
            ls = {}
            if start_date is not None:
                if end_date is not None:
                    if "to" in str(start_date+end_date):
                        x = str(start_date+end_date).split("to")
                        start_date = x[0].strip()
                        end_date = x[1].strip()
                try:
                    try:
                        date_list = date_range(start_date, end_date)
                    except:
                        date_list = date_range(start_date+end_date)
                except:
                    return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="Please enter the dates correctly."))
                dic = {}
                for i in date_list:
                    if i in day_db:
                        for j in day_db[i]['users']:
                            if j in dic:
                                dic[j]+=day_db[i]['users'][j]
                            else:
                                dic[j] =day_db[i]['users'][j]
            else:
                dic = user_db
            des = []
            for i in dic:
                u = discord.utils.get(ctx.guild.members, id=i)
                if u is not None:
                    des.append(f"{count}. {u.mention} - **{converttime(dic[i])}**")
                    count+=1
            lss = []
            for i in range(0, len(des), 10):
                lss.append(des[i: i + 10])
            em_list = []
            no = 1
            for k in lss:
                embed =discord.Embed(color=botinfo.root_color)
                if ctx.guild.icon:
                    embed.set_author(name=f"| User Voice Time LeaderBoard for the server", icon_url=ctx.guild.icon.url)
                else:
                    embed.set_author(name=f"| User Voice Time LeaderBoard for the server", icon_url=ctx.guild.me.display_avatar)
                embed.description = "\n".join(k)
                embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(lss)}", icon_url=self.bot.user.display_avatar.url)
                em_list.append(embed)
                no+=1
            if no == 1:   
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
            page = PaginationView(embed_list=em_list, ctx=ctx)
            await page.start(ctx)
        else:
            count = 1
            ls = {}
            if start_date is not None:
                if end_date is not None:
                    if "to" in start_date+end_date:
                        x = str(start_date+end_date).split("to")
                        start_date = x[0].strip()
                        end_date = x[1].strip()
                try:
                    try:
                        date_list = date_range(start_date, end_date)
                    except:
                        date_list = date_range(start_date+end_date)
                except:
                    return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="Please enter the dates correctly."))
                dic = {}
                for i in date_list:
                    if i in day_db:
                        for j in day_db[i]['channels']:
                            if j in dic:
                                dic[j]+=day_db[i]['channels'][j]
                            else:
                                dic[j] =day_db[i]['channels'][j]
            else:
                dic = channel_db
            des = []
            for i in dic:
                u = discord.utils.get(ctx.guild.channels, id=i)
                if u is not None:
                    des.append(f"{count}. {u.mention} - **{converttime(dic[i])}**")
                    count+=1
            lss = []
            for i in range(0, len(des), 10):
                lss.append(des[i: i + 10])
            em_list = []
            no = 1
            for k in lss:
                embed =discord.Embed(color=botinfo.root_color)
                if ctx.guild.icon:
                    embed.set_author(name=f"| Channel Voice Time LeaderBoard for the server", icon_url=ctx.guild.icon.url)
                else:
                    embed.set_author(name=f"| Channel Voice Time LeaderBoard for the server", icon_url=ctx.guild.me.display_avatar)
                embed.description = "\n".join(k)
                embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(lss)}", icon_url=self.bot.user.display_avatar.url)
                em_list.append(embed)
                no+=1
            if no == 1:   
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the voice channels."))
            page = PaginationView(embed_list=em_list, ctx=ctx)
            await page.start(ctx)

async def setup(bot):
    await bot.add_cog(Statistics(bot))
