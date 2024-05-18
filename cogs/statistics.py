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
from datetime import datetime, timedelta

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
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["lb", "lb m", "lb v"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            if cmd.description is None:
                cmd.description = "No Description"
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"LeaderBoard Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
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
            xd = {}
            coun = 0
            for i in des:
                coun += 1
                xd[i]=des[i]
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = {}
            if ctx.guild.icon:
                icon = ctx.guild.icon.url
            else:
                icon = ctx.guild.me.display_avatar.url
            if len(lss)==0:
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Text channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="messages", typee="users", start_=start_, end_=end_)
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
                    start_ = i
                    break
                dic = channel_db
            des = {}
            for i in dic:
                u = discord.utils.get(ctx.guild.channels, id=i)
                if u is not None:
                    des[u.name] = [dic[i], count]
                    count+=1
            lss = []
            xd = {}
            coun = 0
            for i in des:
                coun += 1
                xd[i]=des[i]
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = {}
            if ctx.guild.icon:
                icon = ctx.guild.icon.url
            else:
                icon = ctx.guild.me.display_avatar.url
            if len(lss) == 0:
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Text channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="messages", typee="channels", start_=start_, end_=end_)
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
            xd = {}
            coun = 0
            for i in des:
                coun += 1
                xd[i]=des[i]
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = {}
            if ctx.guild.icon:
                icon = ctx.guild.icon.url
            else:
                icon = ctx.guild.me.display_avatar.url
            if len(lss)==0:
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="voice", typee="users", start_=start_, end_=end_)
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
                    start_ = i
                    break
                dic = channel_db
            des = {}
            for i in dic:
                u = discord.utils.get(ctx.guild.channels, id=i)
                if u is not None:
                    des[u.name] = [dic[i], count]
                    count+=1
            lss = []
            xd = {}
            coun = 0
            for i in des:
                coun += 1
                xd[i]=des[i]
                if coun % 10 == 0 or coun == len(des):
                    lss.append(xd)
                    xd = {}
            if ctx.guild.icon:
                icon = ctx.guild.icon.url
            else:
                icon = ctx.guild.me.display_avatar.url
            if len(lss) == 0:
                return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the voice channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="voice", typee="channels", start_=start_, end_=end_)
            await page.start(ctx)

async def setup(bot):
    await bot.add_cog(Statistics(bot))
