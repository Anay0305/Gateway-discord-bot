import discord
import sqlite3
import core.database as database
import core.emojis as emojis
import botinfo
import requests
import json
import typing
from core.voice_db import *
from discord.ext import commands
from ast import literal_eval
from core.paginators import PaginationView
from core.stats_pag import StatPaginationView
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
        ls.append(f"{hour}h")
    if minutes != 0:
        ls.append(f"{minutes}m")
    if seconds != 0:
        ls.append(f"{seconds}s")
    return ' '.join(ls)

def converttime1(seconds):
    if seconds == 0:
        return "0 hours"
    time = int(seconds)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    ls = []
    if hour != 0:
        if hour == 1:
            x = "hour"
        else:
            x = "hours"
        ls.append(f"{hour} {x}")
    if minutes != 0:
        if minutes == 1:
            x = "min"
        else:
            x = "mins"
        ls.append(f"{minutes} {x}")
    if len(ls) == 0:
        if seconds != 0:
            ls.append(f"{seconds} seconds")
    return ' '.join(ls)

def convert_date(date_str):
    if date_str.lower() == 'today' or date_str.lower() == "daily":
        return datetime.today().strftime('%Y-%m-%d')
    elif date_str.lower() == 'yesterday':
        yesterday = datetime.today() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    
    formats = ['%d %b %Y', '%d %B %Y', '%d %b', '%d %B', '%d/%m/%y', '%d.%m.%y', '%d-%m-%y', '%m-%d-%y']
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

def getdata(guild_id):
    res = database.fetchone("*", "messages_db", "guild_id", guild_id)
    day_db = literal_eval(res['specific_day_messages'])
    res1 = database.fetchone("*", "voice_db", "guild_id", guild_id)
    day_db1 = literal_eval(res1['specific_day_time'])
    coun = 0
    dic = {}
    total_msgs = 0
    for i in reversed(day_db):
        coun += 1
        for k in day_db[i]['users']:
            total_msgs += day_db[i]['users'][k]['count']
        if coun == len(day_db):
            dic[coun] = total_msgs
        elif coun == 30:
            dic[30] = total_msgs
            break
        elif coun == 14:
            dic[14] = total_msgs
        elif coun == 7:
            dic[7] = total_msgs
        elif coun == 1:
            dic[1] = total_msgs
    if len(dic) >= 4:
        dic.remove(14)
    dic2 = {}
    for i in dic:
        date_list = date_range(f"last {i} days")
        xyz = []
        for j in date_list:
            if j in day_db:
                for k in day_db[j]['users']:
                    if k in xyz:
                        pass
                    else:
                        xyz.append(k)
        dic2[i] = len(xyz)
    coun = 0
    dic1 = {}
    total_time = 0
    for i in reversed(day_db1):
        coun += 1
        for k in day_db1[i]['users']:
            total_time += day_db1[i]['users'][k]['time']
        if coun == len(day_db1):
            dic1[coun] = converttime1(total_time)
        elif coun == 30:
            dic1[30] = converttime1(total_time)
            break
        elif coun == 14:
            dic1[14] = converttime1(total_time)
        elif coun == 7:
            dic1[7] = converttime1(total_time)
        elif coun == 1:
            dic1[1] = converttime1(total_time)
    if len(dic1) >= 4:
        dic1.remove(14)
    date_list = date_range(f"last {list(dic.items())[-1][0]} days")
    dic_text_users = {}
    dic_text_channels = {}
    for i in date_list:
        if i in day_db:
            for j in day_db[i]['users']:
                if j in dic_text_users:
                    dic_text_users[j]['count']+=day_db[i]['users'][j]['count']
                else:
                    dic_text_users[j] =day_db[i]['users'][j]
            for j in day_db[i]['channels']:
                if j in dic_text_channels:
                    dic_text_channels[j]['count']+=day_db[i]['channels'][j]['count']
                else:
                    dic_text_channels[j] =day_db[i]['channels'][j]
    date_list = date_range(f"last {list(dic1.items())[-1][0]} days")
    dic_vc_users = {}
    dic_vc_channels = {}
    for i in date_list:
        if i in day_db1:
            for j in day_db1[i]['users']:
                if j in dic_vc_users:
                    dic_vc_users[j]['time']+=day_db1[i]['users'][j]['time']
                else:
                    dic_vc_users[j] =day_db1[i]['users'][j]
            for j in day_db1[i]['channels']:
                if j in dic_vc_channels:
                    dic_vc_channels[j]['time']+=day_db1[i]['channels'][j]['time']
                else:
                    dic_vc_channels[j] =day_db1[i]['channels'][j]
    dic_text_users = dict(sorted(dic_text_users.items(), key=lambda item: item[1]['count'], reverse=True))
    dic_text_channels = dict(sorted(dic_text_channels.items(), key=lambda item: item[1]['count'], reverse=True))
    dic_vc_users = dict(sorted(dic_vc_users.items(), key=lambda item: item[1]['time'], reverse=True))
    dic_vc_channels = dict(sorted(dic_vc_channels.items(), key=lambda item: item[1]['time'], reverse=True))
    final = {
        "messages": list(dic.items()),
        "voice": list(dic1.items()),
        "contributors": list(dic2.items()),
        "top_member_text": list(dic_text_users.items()),
        "top_channel_text": list(dic_text_channels.items()),
        "top_member_vc": list(dic_vc_users.items()),
        "top_channel_vc": list(dic_vc_channels.items()),
        "lookback": list(dic.items())[-1][0] if list(dic.items())[-1][0] > list(dic1.items())[-1][0] else list(dic1.items())[-1][0]
    }
    return final

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

class SelectView(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context):
        options = [
            discord.SelectOption(label='Home', value="home"),
            discord.SelectOption(label='Top Members Text', value="memtext"),
            discord.SelectOption(label='Top Channels Text', value="chantext"),
            discord.SelectOption(label='Top Members Voice', value="memvc"),
            discord.SelectOption(label='Top Channels Voice', value="chanvc"),
        ]
        super().__init__(placeholder="Select Any Option",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.ctx = ctx
        self.bot = bot

    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=False)
        ctx = self.ctx
        if self.values[0] == "home":
            await interaction.message.edit(content="<a:loading:1215453200463958086>")
            view = View(self.bot, ctx)
            api_url = botinfo.api_url+"/server_top"
            if ctx.guild.icon:
                icon = ctx.guild.icon.url
            else:
                icon = self.bot.user.display_avatar.url
            if ctx.guild.banner:
                banner = ctx.guild.banner.url
            else:
                banner = None
            data = {
                "guild_name": ctx.guild.name,
                "icon": icon,
                "mem_ids": [i.id for i in ctx.guild.members],
                "chan_ids": [i.id for i in ctx.guild.channels],
                "data": getdata(ctx.guild.id),
                "guild_banner": banner
            }
            payload = json.dumps(data)

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
            else:
                await interaction.message.delete()
                return await ctx.send(f"Got some error while fetching the image.")
            await interaction.message.edit(content=None, attachments=[file], view=view)
            return
        elif self.values[0] == "memtext":
            res = database.fetchone("*", "messages_db", "guild_id", ctx.guild.id)
            user_db = literal_eval(res['user_messages'])
            day_db = literal_eval(res['specific_day_messages'])
            count = 1
            end_ = None
            for i in day_db:
                start_ = i
                break
            dic = user_db
            des = {}
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['count'], reverse=True))
            x = [i.id for i in ctx.guild.members]
            for i in dic:
                if i not in x:
                    continue
                des[dic[i]['display_name'] + " | " + dic[i]['name']] = [f"{dic[i]['count']} Messages", count, dic[i]['avatar']]
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
            page.add_item(self)
            await page.start(ctx=ctx, message=interaction.message)
        elif self.values[0] == "chantext":
            res = database.fetchone("*", "messages_db", "guild_id", ctx.guild.id)
            channel_db = literal_eval(res['channel_messages'])
            day_db = literal_eval(res['specific_day_messages'])
            count = 1
            end_ = None
            for i in day_db:
                start_ = i
                break
            dic = channel_db
            des = {}
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['count'], reverse=True))
            x = [i.id for i in ctx.guild.channels]
            for i in dic:
                if i not in x:
                    continue
                des["#" + dic[i]['name'] + f"[{i}]"] = [f"{dic[i]['count']} Messages", count, ctx.guild.me.display_avatar.url]
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
            page.add_item(self)
            await page.start(ctx=ctx, message=interaction.message)
        elif self.values[0] == "memvc":
            res = database.fetchone("*", "voice_db", "guild_id", ctx.guild.id)
            if res is None:
                return await interaction.message.edit(attachments=[], view=self, embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
            user_db = literal_eval(res['user_time'])
            day_db = literal_eval(res['specific_day_time'])
            count = 1
            end_ = None
            for i in day_db:
                start_ = i
                break
            dic = user_db
            des = {}
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['time'], reverse=True))
            x = [i.id for i in ctx.guild.members]
            for i in dic:
                if i not in x:
                    continue
                des[dic[i]['display_name'] + " | " + dic[i]['name']] = [converttime(dic[i]['time']), count, dic[i]['avatar']]
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
                return await interaction.message.edit(attachments=[], view=self, embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="voice", typee="users", start_=start_, end_=end_)
            page.add_item(self)
            await page.start(ctx=ctx, message=interaction.message)
        elif self.values[0] == "chanvc":
            res = database.fetchone("*", "voice_db", "guild_id", ctx.guild.id)
            if res is None:
                return await interaction.message.edit(attachments=[], view=self, embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the Voice channels."))
            channel_db = literal_eval(res['channel_time'])
            day_db = literal_eval(res['specific_day_time'])
            count = 1
            end_ = None
            for i in day_db:
                start_ = i
                break
            dic = channel_db
            des = {}
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['time'], reverse=True))
            x = [i.id for i in ctx.guild.channels]
            for i in dic:
                if i not in x:
                    continue
                des["#" + dic[i]['name'] + f"[{i}]"] = [converttime(dic[i]['time']), count, ctx.guild.me.display_avatar.url]
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
                return await interaction.message.edit(attachments=[], view=self, embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="There have been no interaction in the voice channels."))
            page = StatPaginationView(file_list=lss, ctx=ctx, icon=icon, mode="voice", typee="channels", start_=start_, end_=end_)
            page.add_item(self)
            await page.start(ctx=ctx, message=interaction.message)

class View(discord.ui.View):
    def __init__(self, bot: commands.AutoShardedBot, ctx: commands.Context, timeout = 120):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.bot = bot
        self.add_item(SelectView(bot, ctx))

    async def interaction_check(self, interaction: discord.Interaction):
        self.message = interaction.message
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

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
                        coun = channel_db[before.channel.id]['time'] + channel_time
                    else:
                        coun = channel_time
                    channel_db[before.channel.id] = {
                        'name': before.channel.name,
                        'time': coun
                    }
                    if before.channel.id in day_db[today]['channels']:
                        coun = day_db[today]['channels'][before.channel.id]['time'] + channel_time
                    else:
                        coun = channel_time
                    day_db[today]['channels'][before.channel.id] = {
                        'name': before.channel.name,
                        'time': coun
                    }
            if check_bl_channel(after.channel):
                if guild.id in user_start:
                    user_time = round(datetime.now().timestamp() - user_start[guild.id][member.id])
                    del user_start[guild.id][member.id]
                    if member.id in user_db:
                        coun = user_db[member.id]['time'] + user_time
                    else:
                        coun = user_time
                    user_db[member.id] = {
                        'name': member.name,
                        'display_name': member.display_name,
                        'avatar': member.display_avatar.url,
                        'time': coun
                    }
                    if member.id in day_db[today]['users']:
                        coun = day_db[today]['users'][member.id]['time'] + user_time
                    else:
                        coun = user_time
                    day_db[today]['users'][member.id] = {
                        'name': member.name,
                        'display_name': member.display_name,
                        'avatar': member.display_avatar.url,
                        'time': coun
                    }
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
        day_db[today]['users'] = dict(sorted(day_db[today]['users'].items(), key=lambda item: item[1]['time'], reverse=True))
        day_db[today]['channels'] = dict(sorted(day_db[today]['channels'].items(), key=lambda item: item[1]['time'], reverse=True))
        user_db = dict(sorted(user_db.items(), key=lambda item: item[1]['time'], reverse=True))
        channel_db = dict(sorted(channel_db.items(), key=lambda item: item[1]['time'] ,reverse=True))
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
            coun = user_db[message.author.id]['count'] + 1
        else:
            coun = 1
        user_db[message.author.id] = {
            'display_name': message.author.display_name,
            'name': message.author.name,
            'avatar': message.author.display_avatar.url,
            'count': coun
        }
        channel_db = literal_eval(res['channel_messages'])
        if message.channel.id in channel_db:
            coun = channel_db[message.channel.id]['count'] + 1
        else:
            coun = 1
        channel_db[message.channel.id] = {
            'name': message.channel.name,
            'count': coun
        }
        day_db = literal_eval(res['specific_day_messages'])
        today = f"{str(datetime.now().date())}"
        if today not in day_db:
            day_db[today] = {
                'users': {},
                'channels': {}
            }
        if message.author.id in day_db[today]['users']:
            coun = day_db[today]['users'][message.author.id]['count'] + 1
        else:
            coun = 1
        day_db[today]['users'][message.author.id] = {
            'display_name': message.author.display_name,
            'name': message.author.name,
            'avatar': message.author.display_avatar.url,
            'count': coun
        }
        if message.channel.id in day_db[today]['channels']:
            coun = day_db[today]['channels'][message.channel.id]['count'] + 1
        else:
            coun = 1
        day_db[today]['channels'][message.channel.id] = {
            'name': message.channel.name,
            'count': coun
        }
        day_db[today]['users'] = dict(sorted(day_db[today]['users'].items(), key=lambda item: item[1]['count'], reverse=True))
        day_db[today]['channels'] = dict(sorted(day_db[today]['channels'].items(), key=lambda item: item[1]['count'], reverse=True))
        user_db = dict(sorted(user_db.items(), key=lambda item: item[1]['count'], reverse=True))
        channel_db = dict(sorted(channel_db.items(), key=lambda item: item[1]['count'], reverse=True))
        dic = {
            'user_messages': f"{user_db}",
            'channel_messages': f"{channel_db}",
            'specific_day_messages': f"{day_db}"
        }
        database.update_bulk("messages_db", dic, "guild_id", message.guild.id)

    @commands.hybrid_group(name="statistics", aliases=["top", "stats", "lb", "leaderboard"], invoke_without_command=True, description="Shows The help page for LeaderBoard")
    async def statistics(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["lb", "lb s", "lb m", "lb v"]
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

    @statistics.command(description="Shows the user's activity statistics")
    async def me(self, ctx: commands.Context):
        pass

    @statistics.command(aliases=['s', 'sv'], description="Shows the server's activity statistics")
    async def server(self, ctx: commands.Context):
        view = View(self.bot, ctx)
        api_url = botinfo.api_url+"/server_top"
        if ctx.guild.icon:
            icon = ctx.guild.icon.url
        else:
            icon = self.bot.user.display_avatar.url
        if ctx.guild.banner:
            banner = ctx.guild.banner.url
        else:
            banner = None
        data = {
            "guild_name": ctx.guild.name,
            "icon": icon,
            "mem_ids": [i.id for i in ctx.guild.members],
            "chan_ids": [i.id for i in ctx.guild.channels],
            "data": getdata(ctx.guild.id),
            "guild_banner": banner
        }
        payload = json.dumps(data)

        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api_url, data=payload, headers=headers)
        if response.status_code == 200:
            file = discord.File(fp=BytesIO(response.content), filename='server_stats.png')
        else:
            return await ctx.send(f"Got some error while fetching the image.")
        await ctx.send(file=file, view=view)
        await view.wait()
    
    @statistics.command(aliases=['m', 'msg', 'msgs'], description="Shows the messages leaderboard of the server")
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
                    try:
                        date_list = date_range(start_date+" "+end_date)
                    except:
                        return await ctx.reply(embed=discord.Embed(color=botinfo.wrong_color).set_footer(text="Please enter the dates correctly."))
                dic = {}
                for i in date_list:
                    if i in day_db:
                        for j in day_db[i]['users']:
                            if j in dic:
                                dic[j]['count'] +=day_db[i]['users'][j]['count']
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
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['count'], reverse=True))
            x = [i.id for i in ctx.guild.members]
            for i in dic:
                if i not in x:
                    continue
                des[dic[i]['display_name'] + " | " + dic[i]['name']] = [f"{dic[i]['count']} Messages", count, dic[i]['avatar']]
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
                                dic[j]['count']+=day_db[i]['channels'][j]['count']
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
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['count'], reverse=True))
            x = [i.id for i in ctx.guild.channels]
            for i in dic:
                if i not in x:
                    continue
                des["#" + dic[i]['name'] + f"[{i}]"] = [f"{dic[i]['count']} Messages", count, ctx.guild.me.display_avatar.url]
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

    @statistics.command(aliases=['v', 'vc', 'vcs'], description="Shows the voice leaderboard of the server")
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
                                dic[j]['time']+=day_db[i]['users'][j]['time']
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
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['time'], reverse=True))
            x = [i.id for i in ctx.guild.members]
            for i in dic:
                if i not in x:
                    continue
                des[dic[i]['display_name'] + " | " + dic[i]['name']] = [converttime(dic[i]['time']), count, dic[i]['avatar']]
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
                                dic[j]['time']+=day_db[i]['channels'][j]['time']
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
            dic = dict(sorted(dic.items(), key=lambda item: item[1]['time'], reverse=True))
            x = [i.id for i in ctx.guild.channels]
            for i in dic:
                if i not in x:
                    continue
                des["#" + dic[i]['name'] + f"[{i}]"] = [converttime(dic[i]['time']), count, ctx.guild.me.display_avatar.url]
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
