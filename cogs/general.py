import psutil
import discord
import platform
from discord.ext import commands
import os
import sqlite3
import emojis
import datetime
import requests
from typing import Union
import os
import time
import wavelink
from paginators import PaginationView
from ast import literal_eval
from botinfo import *
from PIL import Image, ImageDraw, ImageFont
import requests
import numpy as np
from io import BytesIO
import re
import database
import emojis
import botinfo
import asyncio
from premium import check_upgraded
from cogs.music import voiceortext, interface

def identify_code_language(code):
    # Define regular expressions for common programming languages
    languages = {
        'Python': r'\b(def|if|elif|else|while|for|print|import|from|as|with|try|except|raise|class|return)\b',
        'Java': r'\b(public|private|protected|abstract|class|void|int|double|float|boolean|char|String|static|final|extends|implements|new|if|else|while|for|switch|case|default|break|continue|return)\b',
        'C#': r'\b(public|private|protected|internal|abstract|sealed|class|void|int|double|float|bool|string|static|readonly|using|namespace|try|catch|finally|if|else|while|for|switch|case|default|break|continue|return)\b',
        'JavaScript': r'\b(function|var|let|const|if|else|while|for|switch|case|default|break|continue|return|import|export|class|extends|super|async|await|try|catch|finally)\b',
        'Go': r'\b(func|var|const|if|else|switch|case|default|for|range|import|package|type|struct|interface|defer|panic|recover)\b',
        'Ruby': r'\b(def|if|elsif|else|while|for|case|when|do|end|module|class|require|include|extend|public|private|protected|self|super|return)\b',
        'PHP': r'\b(function|if|else|while|for|switch|case|default|break|continue|return|require|include|class|public|private|protected|static|final|abstract|interface|namespace)\b',
        'Rust': r'\b(fn|let|mut|const|if|else|while|for|loop|match|return|use|mod|struct|enum|trait|impl|pub|priv|unsafe|as|dyn|super|self)\b',
        'Swift': r'\b(func|var|let|if|else|while|for|switch|case|default|break|continue|return|import|class|struct|enum|protocol|extension|guard|defer)\b',
        'Perl': r'\b(sub|if|elsif|else|while|for|foreach|last|next|redo|return|my|our|use|package|sub|require|import|do)\b',
        'Kotlin': r'\b(fun|var|val|if|else|while|for|when|in|is|as|return|import|class|interface|object|package|init)\b',
        'Lua': r'\b(function|local|if|then|elseif|else|while|for|in|do|end|return|require|module)\b',
        'PowerShell': r'\b(function|if|elseif|else|while|for|foreach|do|until|break|continue|return|param|begin|process|end|switch|case|default|try|catch|finally|throw|trap)\b',
    }
    for i in languages:
        if re.search(languages[i], code):
            return i.lower()
    return None

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label="User Avatar", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()
    @discord.ui.button(label="Server Avatar", custom_id='No', style=discord.ButtonStyle.red)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()

class create(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=120)
        self.value = None

    @discord.ui.button(label="Users only", custom_id='users', style=discord.ButtonStyle.green)
    async def users(self, interaction, button):
        self.value = 'users'
        self.stop()
    @discord.ui.button(label="Bots Only", custom_id='bots', style=discord.ButtonStyle.green)
    async def bots(self, interaction, button):
        self.value = 'bots'
        self.stop()

    @discord.ui.button(label="Both", custom_id='both', style=discord.ButtonStyle.danger)
    async def both(self, interaction, button):
        self.value = 'both'
        self.stop()

class globalorlocal(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=120)
        self.value = None

    @discord.ui.button(label="Globally (Mutuals)", custom_id='users', style=discord.ButtonStyle.green)
    async def users(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'global'
        self.stop()

    @discord.ui.button(label="Locally", custom_id='bots', style=discord.ButtonStyle.blurple)
    async def bots(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'local'
        self.stop()

async def profile(bot: commands.Bot, ctx: commands.Context, user: discord.Member, b_db, u_db, p_ls, init, bot_bdg: list[discord.Emoji], user_bdg: list[discord.Emoji], total_cmd, user_rank, title):
    if u_db is None:
        totaltime = 0
        s_dic = {}
        f_dic = {}
        a_dic = {}
        t_dic = {}
    else:
        totaltime = u_db['totaltime']
        s_dic = literal_eval(u_db['server'])
        f_dic = literal_eval(u_db['friend'])
        a_dic = literal_eval(u_db['artist'])
        t_dic = literal_eval(u_db['track'])
    if b_db is None:
        bf_dic = {}
    else:
        bf_dic = literal_eval(b_db['user'])
    #response = requests.get("https://media.discordapp.net/attachments/1208408003703734282/1239335638709440582/Picsart_24-05-13_03-27-14-507.jpg?ex=66448702&is=66433582&hm=aaa675e8e5e8693aa0e9c620154363d08805ec53cf52e252e79dc1eed9b71705&=&format=webp&width=909&height=511")
    width = 1280
    height = 720

    # Create new image and ImageDraw object
    with open("profile_bg.jpg", 'rb') as file:
        image = Image.open(BytesIO(file.read())).convert("RGBA")
        file.close()
    image = image.resize((width,height))
    draw = ImageDraw.Draw(image)
    pfp = user.display_avatar.url
    pfp = pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")
    logo_res = requests.get(pfp)
    AVATAR_SIZE = 128
    avatar_image = Image.open(BytesIO(logo_res.content)).convert("RGB")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
    circle_image = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE))
    circle_draw = ImageDraw.Draw(circle_image)
    circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    image.paste(avatar_image, (160, 120), circle_image)
    font = ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 28)
    draw.text( (300, 120), f"{str(user)}", fill="black", font=font)
    px = 300
    for i in user_bdg:
        url = i.url
        url = url.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")
        res = requests.get(url)
        size = 28
        avatar_image = Image.open(BytesIO(res.content)).convert("RGBA")
        avatar_image = avatar_image.resize((size, size))
        pixel_data = avatar_image.load()
        background_color = (0, 0, 0)  # specify the background color in RGB format
        for y in range(avatar_image.size[1]):
            for x in range(avatar_image.size[0]):
                if pixel_data[x, y] == background_color:
                    pixel_data[x, y] = (0, 0, 0, 0)
        #circle_image = Image.new('L', (spotify_size, spotify_size))
        #circle_draw = ImageDraw.Draw(circle_image)
        #circle_draw.ellipse((0, 0, spotify_size, spotify_size), fill=255)
        image.paste(avatar_image, (px, 158), avatar_image)
        px+=32
    if title is not None:
        draw.text( (300, 184), text=title.title(), font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 28), fill="black")
    px = 300
    for i in bot_bdg:
        url = i.url
        url = url.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")
        res = requests.get(url)
        size = 28
        avatar_image = Image.open(BytesIO(res.content)).convert("RGBA")
        avatar_image = avatar_image.resize((size, size))
        pixel_data = avatar_image.load()
        background_color = (0, 0, 0)  # specify the background color in RGB format
        for y in range(avatar_image.size[1]):
            for x in range(avatar_image.size[0]):
                if pixel_data[x, y] == background_color:
                    pixel_data[x, y] = (0, 0, 0, 0)
        #circle_image = Image.new('L', (spotify_size, spotify_size))
        #circle_draw = ImageDraw.Draw(circle_image)
        #circle_draw.ellipse((0, 0, spotify_size, spotify_size), fill=255)
        image.paste(avatar_image, (px, 222), avatar_image)
        px+=32
    #draw.rounded_rectangle((970, 0, 1180, 50), radius=3, fill=(255, 0, 0, 128))
    draw.text( (640, 28), text="Sputnik", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 34), fill=(165,42,42), anchor="mm")
    #draw.rounded_rectangle((100, 0, 310, 50), radius=3, fill=(255, 0, 0, 128))
    draw.text( (215, 28), text=f"Rank #{user_rank}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 34), fill=(0, 10, 36), anchor="mm")
    count = 1
    for i in bf_dic:
        if user.id == i:
            break
        count +=1
    if user.id not in bf_dic:
        draw.text( (1065, 28), text="Music Rank Null", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 34), fill=(0, 10, 36), anchor="mm")
    else:
        draw.text( (1065, 28), text=f"Music Rank #{count}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 34), fill=(0, 10, 36), anchor="mm")
    tt = converttime(totaltime)
    if tt is None or tt == "":
        tt = "0m"
    draw.text((990, 215), text=f"Total Commands Runned:\n{total_cmd}\nTotal Listening Time:\n{tt}", font=ImageFont.truetype('Fonts/Alkatra-SemiBold.ttf', 28), fill="black", anchor="mm")
    mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw.text( (110, 305), text="Your Playlists", font=ImageFont.truetype('Fonts/Alkatra-SemiBold.ttf', 24), fill=(165,42,42), anchor="lt")
    p_pixel = 305
    count = 0
    for i, j, k in p_ls:
        if count >= 3:
            break
        count +=1
        p_pixel+=25
        k = converttime(k)
        draw.text( (110, p_pixel), text=f"{count}. {i} ({j} songs) - {k}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")
    if len(p_ls) == 0:
        draw.text( (110, 330), text=f"No Playlist Found", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")

    draw.text( (665, 353), text="Top Servers", font=ImageFont.truetype('Fonts/Alkatra-SemiBold.ttf', 26), fill=(165,42,42), anchor="lt")
    p_pixel = 357
    count = 0
    for i in s_dic:
        if count >= 5:
            break
        count +=1
        p_pixel+=25
        k = converttime(s_dic[i])
        g = bot.get_guild(i)
        if g is None:
            n = "Unknown Server"
        else:
            n = g.name
        draw.text( (665, p_pixel), text=f"{count}. {k} - {n}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")
    if len(s_dic) == 0:
        draw.text( (665, 384), text="No Data", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")

    draw.text( (110, 435), text="Top Friends", font=ImageFont.truetype('Fonts/Alkatra-SemiBold.ttf', 24), fill=(165,42,42), anchor="lt")
    p_pixel = 435
    count = 0
    for i in f_dic:
        if count >= 3:
            break
        count +=1
        p_pixel+=25
        k = converttime(f_dic[i])
        g = await bot.fetch_user(i)
        if g is None:
            n = "Unknown User"
        else:
            n = str(g)
        x = f"{count}. {k} - {n}"
        if len(x) >= 42:
            x = x[:40]+"..."
        draw.text( (110, p_pixel), text=f"{x}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")
    if len(f_dic) == 0 :
        draw.text( (110, 460), text="No Data", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")

    draw.text( (110, 567), text="Top Tracks", font=ImageFont.truetype('Fonts/Alkatra-SemiBold.ttf', 24), fill=(165,42,42), anchor="lt")
    p_pixel = 567
    count = 0
    for i in t_dic:
        if count >= 3:
            break
        count +=1
        p_pixel+=25
        k = converttime(t_dic[i])
        x = f"{count}. {k} - {i}"
        if len(x) >= 100:
            x = x[:95]+"..."
        draw.text( (110, p_pixel), text=f"{x}", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")
    if len(t_dic) == 0:
        draw.text( (110, 592), text="No Data", font=ImageFont.truetype('Fonts/Alkatra-Medium.ttf', 22), fill="black", anchor="lt")

    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await init.delete()
        await ctx.reply(file=discord.File(fp=image_binary, filename='profile.png'))

def converttime(seconds):
    time = int(seconds)
    month = time // (30 * 24 * 3600)
    time = time % (24 * 3600)
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    ls = []
    if month != 0:
        ls.append(f"{month}mo")
    if day != 0:
        ls.append(f"{day}d")
    if hour != 0:
        ls.append(f"{hour}h")
    if minutes != 0:
        ls.append(f"{minutes}m")
    if seconds != 0:
        ls.append(f"{seconds}s")
    return ' '.join(ls)

class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def time_formatter(self, seconds: float):

        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = ((str(days) + " days, ") if days else "") + \
            ((str(hours) + " hours, ") if hours else "") + \
            ((str(minutes) + " minutes, ") if minutes else "") + \
            ((str(seconds) + " seconds, ") if seconds else "")
        return tmp[:-2]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()
        if not message.guild:
                        return
        if not message.guild.me.guild_permissions.read_messages:
            return
        if not message.guild.me.guild_permissions.read_message_history:
            return
        if not message.guild.me.guild_permissions.view_channel:
            return
        if not message.guild.me.guild_permissions.send_messages:
            return
        if message.mentions:
            for user_mention in message.mentions:
                auto_db = database.fetchone("*", "afk", "user_id", user_mention.id)
                if auto_db is None:
                    continue
                try:
                    afk = literal_eval(auto_db['afkk'])
                except:
                    continue
                if message.guild.id in afk:
                  if afk[message.guild.id]['status'] == True:
                    if message.author.bot:
                        continue
                    reason = afk[message.guild.id]['reason']
                    t = afk[message.guild.id]['time']
                    afk[message.guild.id]['mentions']+=1
                    database.update("afk", "afkk", f"{afk}", "user_id", user_mention.id)
                    await message.channel.send(f'**{str(user_mention)}** went AFK <t:{t}:R>: {reason}', allowed_mentions=discord.AllowedMentions.none())
        auto_db = database.fetchone("*", "afk", "user_id", message.author.id)
        if auto_db is None:
            return
        afk = literal_eval(auto_db['afkk'])
        if message.guild.id in afk:
          if afk[message.guild.id]['status'] == True:
            meth = int(time.time()) - int(afk[message.guild.id]['time'])
            if meth == 0:
                return
            been_afk_for = await self.time_formatter(meth)
            await message.channel.send(f"{message.author.mention} I removed your Afk, You were afk for {been_afk_for}, you were mentioned {afk[message.guild.id]['mentions']} times in this server.", delete_after=60)
            afk[message.guild.id]['status'] = False
            afk[message.guild.id]['reason'] = None
            afk[message.guild.id]['time'] = 0
            afk[message.guild.id]['mentions'] = 0
            dic = {
                'afkk': f"{afk}"
            }
            database.update_bulk("afk", dic, "user_id", message.author.id)

    @commands.hybrid_command(name="uptime",
                    description="Shows you Bot's Uptime")
    async def uptime(self, ctx):
        bot = self.bot
        pfp = ctx.author.display_avatar.url
        uptime = datetime.datetime.utcnow() - starttime
        uptime = str(uptime).split('.')[0]
        embed = discord.Embed(title="Bot's Uptime", description=f"```{uptime}```",
                              color=botinfo.root_color)
        embed.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(aliases=["bi", "stats"], description="Gets information of the bot")
    async def botinfo(self, ctx):
        bot = self.bot
        s_id = ctx.guild.shard_id
        sh = self.bot.get_shard(s_id)
        count = 0
        for g in self.bot.guilds:
          count += len(g.members)
        txt = 0
        vc = 0
        cat = 0
        join = 0
        play = 0
        for i in self.bot.guilds:
            for j in i.channels:
                if isinstance(j, discord.TextChannel):
                    txt+=1
                elif isinstance(j, discord.VoiceChannel):
                    vc+=1
                elif isinstance(j, discord.CategoryChannel):
                    cat+=1
            if wavelink.Pool.get_node().get_player(i.id):
                join += 1
                if wavelink.Pool.get_node().get_player(i.id).playing:
                    play += 1
        files = 0
        lines = 0
        for i in os.scandir():
            if i.is_file():
                if i.name.endswith(".py"):
                    with open(i.name, "r") as f:
                        try:
                            lines+=len(f.readlines())
                        except:
                            continue
                    files+=1
            else:
                for j in os.scandir(i):
                    if j.name.endswith(".py"):
                        with open(f"{i.name}/{j.name}", "r") as f:
                            try:
                                lines+=len(f.readlines())
                            except:
                                continue
                        files+=1
        embed = discord.Embed(colour=botinfo.root_color)
        anay = self.bot.main_owner
        embed.set_author(name=f"| {self.bot.user.name}'s Information", icon_url=ctx.guild.me.display_avatar.url)
        embed.description = (f"**• Developers**\n> **[Anay](https://discord.com/users/{anay.id})**\n"
                             f"**• Bot Stats**\n**\u2192** Total Guilds: **{len(self.bot.guilds)} Guilds**\n**\u2192** Total users: **{count} Users**\n**\u2192** Channels:\n- Total: **{str(len(set(self.bot.get_all_channels())))} Channels**\n- Text: {txt} Channels\n- Voice: {vc} Channels\n- Categories:  {cat} Categories\n"
                             f"**• Players**\n**\u2192** Total: {join}\n**\u2192** Playing: {play}\n"
                             f"**• Server Usage**\n**\u2192** CPU Usage: {psutil.cpu_percent()}%\n**\u2192** Memory Usage: {psutil.virtual_memory().percent}%\n"
                             f"**• Latency:** {round(sh.latency * 1000)}ms\n"
                             f"**• Shards:** {ctx.guild.shard_id+1}/{len(self.bot.shards.items())}\n"
                             f"**• Python Version:** {platform.python_version()}\n"
                             f"**• Discord.py Version:** **{discord.__version__}**\n"
                             f"**• __Code Information__:**\n"
                             f"**\u2192** **Total no. of Files:** **[{files} Files](https://discord.gg/K4v4aEuwp6)**\n"
                             f"**\u2192** **Total no. of Lines:** **[{lines} Lines](https://discord.gg/K4v4aEuwp6)**")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        page = discord.ui.View()
        page.add_item(discord.ui.Button(label="Invite me", url=discord.utils.oauth_url(self.bot.user.id)))
        page.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/K4v4aEuwp6"))
        await ctx.reply(embed = embed, mention_author=False, view=page)

    @commands.hybrid_command(name="afk", description="Changes the afk status of user")
    async def afk(self, ctx, *,reason=None):
        if reason is None:
            reason = "I'm Afk :))"
        if "@everyone" in reason or "@here" in reason:
            await ctx.reply("You cannot mention everyone or here in a afk reason")
            return
        if "<&" in reason:
            await ctx.reply("You cannot mention a role in a afk reason")
            return
        if "discord.gg" in reason:
            await ctx.reply("You cannot advertise a server in a afk reason")
            return
        auto_db = database.fetchone("*", "afk", "user_id", ctx.author.id)
        if auto_db is None:
            ds = {}
            ds[ctx.guild.id] = {}
            ds[ctx.guild.id]['status'] = True
            ds[ctx.guild.id]['reason'] = reason
            ds[ctx.guild.id]['time'] = int(time.time())
            ds[ctx.guild.id]['mentions'] = 0
            val = (ctx.author.id, f"{ds}",)
            await ctx.send(f'**{str(ctx.author)}**, Your AFK is now set to: {reason}', allowed_mentions=discord.AllowedMentions.none())
            await asyncio.sleep(1)
            database.insert("afk", "user_id, afkk", val)
            return
        else:
            ds = literal_eval(auto_db['afkk'])
            ds[ctx.guild.id] = {}
            ds[ctx.guild.id]['status'] = True
            ds[ctx.guild.id]['reason'] = reason
            ds[ctx.guild.id]['time'] = int(time.time())
            ds[ctx.guild.id]['mentions'] = 0
            await ctx.send(f'**{str(ctx.author)}**, Your AFK is now set to: {reason}', allowed_mentions=discord.AllowedMentions.none())
            await asyncio.sleep(1)
            database.update("afk", "afkk", f"{ds}", "user_id", ctx.author.id)
            return

    @commands.hybrid_group(
        invoke_without_command=True, description="Shows the help menu for todo commands"
    )
    async def todo(self, ctx: commands.Context):
        ls = ["todo", "todo add", "todo remove", "todo list"]
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @todo.command(name="add", description="Adds a todo for the user")
    async def _add(self, ctx: commands.Context, *, arguments):
        auto_db = database.fetchone("*", "todo", "user_id", ctx.author.id)
        if auto_db is None:
            x = []
            x.append(arguments)
            val = (ctx.author.id, f"{x}")
            database.insert("todo", "user_id, todo", val)
        else:
            x = literal_eval(auto_db['todo'])
            x.append(arguments)
            database.update("todo", "todo", f"{x}", "user_id", ctx.author.id)
        await ctx.reply(f"Successfully add `{arguments}` to your todo list")

    @todo.command(name="remove", description="Removes a todo from the user")
    async def _remove(self, ctx: commands.Context, *, number):
        if not number.isdigit():
            return await ctx.reply("Please provide a integer")
        number = abs(int(number))
        auto_db = database.fetchone("*", "todo", "user_id", ctx.author.id)
        if auto_db is None:
            return await ctx.reply(f"You dont have any todo with number: {number}")
        x = literal_eval(auto_db['todo'])
        if len(x) < number:
            return await ctx.reply(f"You dont have any todo with number: {number}")
        else:
            x.pop(number-1)
            database.update("todo", "todo", f"{x}", "user_id", ctx.author.id)
        await ctx.reply(f"Successfully removed todo number {number} from your todo list")

    @todo.command(name="list", description="Shows you your pending todo work")
    async def _list(self, ctx: commands.Context):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        auto_db = database.fetchone("*", "todo", "user_id", ctx.author.id)
        em = discord.Embed(title=f"Todo list for {str(ctx.author)}", color=botinfo.root_color).set_footer(text=f"{self.bot.user.name}", icon_url=self.bot.user.avatar.url)
        if auto_db is None:
            em.description = f"There is no todo work"
            return await ctx.reply(embed=em)
        x = literal_eval(auto_db["todo"])
        if len(x) == 0:
            em.description = f"There is no todo work"
            return await ctx.reply(embed=em)
        ls, todo = [], []
        count = 1
        for i in x:
            todo.append(f"`[{'0' + str(count) if count < 10 else count}]` | {i}")
            count += 1
        for i in range(0, len(todo), 5):
           ls.append(todo[i: i + 5])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Todo list for {str(ctx.author)}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @commands.hybrid_group(
        invoke_without_command=True, description="Shows the user's profile for bot",
        aliases=['badges', 'badge', 'pr', 'pf']
    )
    async def profile(self, ctx, member: discord.Member = None):
            member = member or ctx.author
            init = await ctx.reply(f"Building up the profile of {str(member)}...", mention_author=False)
            query = "SELECT * FROM  badges WHERE user_id = ?"
            val = (member.id,)
            with sqlite3.connect('./database.sqlite3') as db:
              db.row_factory = sqlite3.Row
              cursor = db.cursor()
              cursor.execute(query, val)
              user_columns = cursor.fetchone()
            des = []
            if user_columns is None:
                pass
            else:
                if user_columns['OWNER'] == 1:
                    bdg = f"{emojis.owner}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['DEVELOPER'] == 1:
                    bdg = f"{emojis.dev}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['ADMIN'] == 1:
                    bdg = f"{emojis.admin}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['MOD'] == 1:
                    bdg = f"{emojis.mod}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['STAFF'] == 1:
                    bdg = f"{emojis.staff}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['PARTNER'] == 1:
                    bdg = f"{emojis.partner}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['SUPPORTER'] == 1:
                    bdg = f"{emojis.early_sup}"
                    des.append(discord.PartialEmoji.from_str(bdg))
                if user_columns['SPECIAL'] == 1:
                    bdg = f"{emojis.hype}"
                    des.append(discord.PartialEmoji.from_str(bdg))
            balance = discord.PartialEmoji.from_str("<:balance:933685821092016158>")
            bravery = discord.PartialEmoji.from_str("<:bravery:933685857582448671>")
            brillance = discord.PartialEmoji.from_str("<:brillance:933685893024337980>")
            bug_1 = discord.PartialEmoji.from_str("<:bug_hunter_1:933685410738085899>")
            bug_2 = discord.PartialEmoji.from_str("<:bug_hunter_2:933685491486847036>")
            early = discord.PartialEmoji.from_str("<:early_sup:933685551012397107>")
            hype = discord.PartialEmoji.from_str("<a:hype:933685735905710080>")
            partner = discord.PartialEmoji.from_str("<:partner:933685923567251517>")
            staff = discord.PartialEmoji.from_str("<a:staff:933685961932558337>")
            system = discord.PartialEmoji.from_str("<:system:933686023995682848>")
            veri_bot = discord.PartialEmoji.from_str("<:verified_bot:933686190920564736>")
            veri_dev = discord.PartialEmoji.from_str("<:verified_dev:933685666477379647>")
            act_dev = discord.PartialEmoji.from_str("<:active_developer:1040478576581029928>")
            badge = []
            if member.public_flags.bug_hunter == True:
                badge.append(bug_1)
            if member.public_flags.bug_hunter_level_2 == True:
                badge.append(bug_2)
            if member.public_flags.hypesquad_bravery == True:
                badge.append(bravery)
            if member.public_flags.hypesquad_balance == True:
                badge.append(balance)
            if member.public_flags.hypesquad_brilliance == True:
                badge.append(brillance)
            if member.public_flags.hypesquad == True:
                badge.append(hype)
            if member.public_flags.early_supporter == True:
                badge.append(early)
            if member.public_flags.early_verified_bot_developer == True:
                badge.append(veri_dev)
            if member.public_flags.verified_bot == True:
                badge.append(veri_bot)
            if member.public_flags.staff == True:
                badge.append(staff)
            if member.public_flags.system == True:
                badge.append(system)
            if member.public_flags.partner == True:
                badge.append(partner)
            if member.public_flags.active_developer == True:
                badge.append(act_dev)
            query = "SELECT * FROM  count WHERE xd = ?"
            val = (1,)
            cursor.execute(query, val)
            count_db = cursor.fetchone()
            user = literal_eval(count_db['user_count'])
            if member.id in user:
                cmd_runned = f"{user[member.id]} Commands"
            else:
                cmd_runned = "0 Command"
            mem = member
            query = "SELECT * FROM bot WHERE bot_id = ?"
            val = (self.bot.user.id,)
            cursor.execute(query, val)
            b_db = cursor.fetchone()
            query = "SELECT * FROM user WHERE user_id = ?"
            val = (mem.id,)
            cursor.execute(query, val)
            u_db = cursor.fetchone()
            query = "SELECT * FROM  pl WHERE user_id = ?"
            val = (mem.id,)
            cursor.execute(query, val)
            p_db = cursor.fetchone()
            if p_db is None:
                p_ls = []
            else:
                xd = literal_eval(p_db['pl'])
                p_ls = []
                for i in xd:
                    tm = 0
                    for j in xd[i]:
                        tm += int(j['info']['length'])/1000
                    p_ls.append((i, len(xd[i]), tm))
            query = "SELECT * FROM  count WHERE xd = ?"
            val = (1,)
            cursor.execute(query, val)
            count_db = cursor.fetchone()
            user = literal_eval(count_db['user_count'])
            query = "SELECT * FROM  titles WHERE user_id = ?"
            val = (mem.id,)
            cursor.execute(query, val)
            x = cursor.fetchone()
            if x is not None:
                if x['title'] is not None:
                    title = str(x['title']).capitalize()
                else:
                    title = None
            else:
                title = None
            cursor.close()
            db.close()
            u_count = 1
            for i in user:
                if i == mem.id:
                    break
                u_count+=1
            await profile(self.bot, ctx, mem, b_db, u_db, p_ls, init, des, badge, cmd_runned, u_count, title)

    @profile.command(name="add", aliases=["a"], description="Gives the badge to user")
    async def badge_add(self, ctx, member: discord.User, *, badge):
        ls = workowner
        if ctx.author.id not in ls and ctx.author.id not in self.bot.owner_ids:
            return
        if not badge:
            await ctx.reply("Mention a badge to Assign")
        badge = badge.upper()
        valid = ["ALL", "OWNER", "DEVELOPER", "ADMIN", "MOD", "STAFF", "PARTNER", "SUPPORTER", "SPECIAL"]
        if badge not in valid:
            return await ctx.send("Please send A valid Badge\nASSIGNABLE BADGES ARE: All, Owner, Developer, Admin, Mod, Staff, Partner, Supporter, Special")
        result = database.fetchone("*", "badges", "user_id", member.id)
        if result is None:
            val = (member.id,)
            database.insert("badges", "user_id", val)
        if badge == "ALL":
            dic = {}
            for i in valid[1:]:
                dic[i] = 1
            database.update_bulk("badges", dic, "user_id", member.id)
            await ctx.send(f'Given **All** badges to {str(member)}')
        else:
            database.update("badges", f"{badge}", 1, "user_id", member.id)
            await ctx.send(f'Given **{badge}** to {str(member)}')
        em = discord.Embed(description=f"{badge} badge(s) were given to {member.mention} [{member.id}] by {ctx.author.mention} [{ctx.author.id}]")
        webhook = discord.SyncWebhook.from_url(webhook_badge_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Badge Given Logs", avatar_url=self.bot.user.avatar.url)

    @profile.command(name="remove", aliases=["r"], description="Removes the badge from user")
    async def badge_remove(self, ctx, member: discord.User, *, badge):
        ls = workowner
        if ctx.author.id not in ls and ctx.author.id not in self.bot.owner_ids:
            return
        if not badge:
            await ctx.reply("Mention a badge to Remove")
        badge = badge.upper()
        valid = ["ALL", "OWNER", "DEVELOPER", "ADMIN", "MOD", "STAFF", "PARTNER", "SUPPORTER", "SPECIAL"]
        if badge not in valid:
            return await ctx.send("Please send A valid Badge\nASSIGNABLE BADGES ARE: All, Owner, Developer, Admin, Mod, Staff, Partner, Supporter, Special")
        result = database.fetchone("*", "badges", "user_id", member.id)
        if result is None:
            val = (member.id,)
            database.insert("badges", "user_id", val)
        if badge == "ALL":
            dic = {}
            for i in valid[1:]:
                dic[i] = 0
            database.update_bulk("badges", dic, "user_id", member.id)
            await ctx.send(f'Removed **All** badges from {str(member)}')
        else:
            database.update("badges", f"{badge}", 0, "user_id", member.id)
            await ctx.send(f'Removed **{badge}** from {str(member)}')
        em = discord.Embed(description=f"{badge} badge(s) were removed from {member.mention} [{member.id}] by {ctx.author.mention} [{ctx.author.id}]")
        webhook = discord.SyncWebhook.from_url(webhook_badge_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Badge Removed Logs", avatar_url=self.bot.user.avatar.url)

    @commands.hybrid_group(
        invoke_without_command=True, description="Shows the help menu for list commands"
    )
    async def list(self, ctx):
        ls = ["list", "list joinpos", "list bans", "list mods", "list admins", "list boosters", "list bots", "list inrole", "list roles", "list botemojis", "list emojis", "list early", "list createpos", "list vcmuted", "list timeouts"]
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @list.command(name="afks", aliases=['afk'], description="Shows all the afk users in the server")
    @commands.has_permissions(manage_messages=True)
    async def list_afks(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, roles = [], []
        count = 1
        xd = {}
        for i in ctx.guild.members:
          auto_db = database.fetchone("*", "afk", "user_id", i.id)
          if auto_db is None:
              continue 
          afk = literal_eval(auto_db['afkk'])
          if ctx.guild.id in afk:
            if afk[ctx.guild.id]['status'] == True:
              meth =int(afk[ctx.guild.id]['time'])
              if meth == 0:
                continue
              xd[meth] = i
        for i in sorted(xd):
            roles.append(f"`[{'0' + str(count) if count < 10 else count}]` | {xd[i].mention} - Been AFK <t:{round(i)}:R>")
            count += 1
        for i in range(0, len(roles), 10):
           ls.append(roles[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"List of AFK Users in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="roles", description="Shows all the roles in the server")
    async def list_roles(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, roles = [], []
        count = 1
        for role in list(reversed(ctx.guild.roles[1:])):
            roles.append(f"`[{'0' + str(count) if count < 10 else count}]` | {role.mention} `[{role.id}]` - {len(role.members)} Members")
            count += 1
        for i in range(0, len(roles), 10):
           ls.append(roles[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"List of Roles in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="bots", description="Shows a list of all bots in server")
    async def list_bots(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, bots = [], []
        count = 1
        for member in ctx.guild.members:
            if member.bot:
                bots.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}]")
                count += 1
        for i in range(0, len(bots), 10):
            ls.append(bots[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"Bots in {ctx.guild.name} - {count-1}"
            embed.description = "\n".join(k)
            embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
    
    @list.command(name="botemojis", description="Shows a list of all emojis the bot can see")
    async def list_botemojis(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, emo = [], []
        count = 1
        for emoji in self.bot.emojis:
            emo.append(f"`[{'0' + str(count) if count < 10 else count}]` | {emoji} - \\{emoji}")
            count += 1
        for i in range(0, len(emo), 10):
           ls.append(emo[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Emojis the bot can see - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="emojis", description="Shows a list of all emojis in the server")
    async def list_emojis(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, emo = [], []
        count = 1
        if not ctx.guild.emojis:
            await init.delete()
            return await ctx.reply("No emojis in the server", mention_author=False)
        for emoji in ctx.guild.emojis:
            emo.append(f"`[{'0' + str(count) if count < 10 else count}]` | {emoji} - \\{emoji}")
            count += 1
        for i in range(0, len(emo), 10):
           ls.append(emo[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Emojis in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
        
    @list.command(name="admins", description="Shows a list of all admins in the server")
    async def list_admins(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, admins = [], []
        count = 1
        for member in ctx.guild.members:
            if member.guild_permissions.administrator == True:
                if not member.bot:
                    admins.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}]")
                    count += 1
        for i in range(0, len(admins), 10):
           ls.append(admins[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Admins in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="mods", description="Shows the list of all mods in the server")
    async def list_mods(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, mods = [], []
        count = 1
        for member in ctx.guild.members:
            if member.guild_permissions.manage_emojis == True:
                if not member.bot:
                    mods.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}]")
                    count += 1
        for i in range(0, len(mods), 10):
           ls.append(mods[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Mods in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
        
    @list.command(name="bans", description="Shows the list of banned members in the server")
    async def list_bans(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, bans = [], []
        count = 1
        xd = [member async for member in ctx.guild.bans()]
        if len(xd) == 0:
            await init.delete()
            return await ctx.reply("There aren't any banned users.", mention_author=False)
        async for member in ctx.guild.bans():
            bans.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member.user} `[{member.user.id}]`")
            count += 1
        for i in range(0, len(bans), 10):
           ls.append(bans[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Banned Users in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
        
    @list.command(name="inrole", description="Shows the list of members in a role")
    async def list_inrole(self, ctx, *,role: discord.Role):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, inrole = [], []
        count = 1
        xd = [member for member in role.members]
        if len(xd) == 0:
            await init.delete()
            return await ctx.reply("There aren't any users in this role.", mention_author=False)
        for member in role.members:
            inrole.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}] - [{member.id}]")
            count += 1
        for i in range(0, len(inrole), 10):
           ls.append(inrole[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Members in Role {role.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="boosters", description="Shows the list of boosters of the server")
    async def list_boosters(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, boosters = [], []
        count = 1
        xd = [member for member in ctx.guild.premium_subscribers]
        if len(xd) == 0:
            await init.delete()
            return await ctx.reply("There aren't any boosters in this server.", mention_author=False)
        for member in ctx.guild.premium_subscribers:
            boosters.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}] - <t:{int(member.premium_since.timestamp())}:R>")
            count += 1
        for i in range(0, len(boosters), 10):
           ls.append(boosters[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Boosters in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="vcmuted", aliases=['vcmute', 'vcmutes'], description="Shows the list of Muted ids in vc of the server")
    async def list_vcmute(self, ctx: commands.Context):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        ls, vcmute = [], []
        count = 1
        for vc in ctx.guild.voice_channels:
            for i in vc.members:
                if i.voice.mute:
                    vcmute.append(f"`[{'0' + str(count) if count < 10 else count}]` | {i.name} [{i.mention}] - {vc.mention}")
                    count += 1
        if count == 1:
            await init.delete()
            return await ctx.reply("There aren't any id muted in vc of this server.", mention_author=False)
        for i in range(0, len(vcmute), 10):
           ls.append(vcmute[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Vc Muted IDs in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="timeouts", aliases=['timedouts', 'timedout', 'mutes', 'timeout'], description="Shows the list of Muted ids in vc of the server")
    async def list_muted(self, ctx: commands.Context):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        mem = {}
        for member in ctx.guild.members:
            if member.is_timed_out():
                mem[member.timed_out_until.timestamp()] = member
        ls, count = [], 1
        mutes = []
        for _t in sorted(mem):
            mutes.append(f"`[{'0' + str(count) if count < 10 else count}]` | {mem[_t]} - Timedout Till: <t:{round(_t)}:R>")
            count += 1
        if count == 1:
            await init.delete()
            return await ctx.reply("There aren't any id timedout in this server.", mention_author=False)
        for i in range(0, len(mutes), 10):
           ls.append(mutes[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Timedout Users in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name='early', description="Shows the list of early supporter ids in the server")
    async def list_early(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        mem = {}
        for member in ctx.guild.members:
            if member.public_flags.early_supporter == True:
                mem[member.created_at.timestamp()] = member
        if mem == "{}":
            await init.delete()
            return await ctx.reply("No early ids in the server", mention_author=False)
        ls, early = [], []
        count = 1
        for m in sorted(mem):
                early.append(f"`[{'0' + str(count) if count < 10 else count}]` | {mem[m]} [{mem[m].mention}] - <t:{round(mem[m].created_at.timestamp())}:R>")
                count += 1
        if count == 1:
            return await ctx.reply("No early ids in the server", mention_author=False)
        for i in range(0, len(early), 10):
            ls.append(early[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"Early Id's in {ctx.guild.name} - {count-1}"
            embed.description = "\n".join(k)
            embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @list.command(name="joinpos", description="Shows the join position of every user in the server")
    async def list_joinpos(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        mem = {}
        for member in ctx.guild.members:
            mem[member.joined_at.timestamp()] = member
        ls, count = [], 1
        joinpos = []
        for _t in sorted(mem):
            joinpos.append(f"`[{'0' + str(count) if count < 10 else count}]` | {mem[_t]} - Joined: <t:{round(mem[_t].joined_at.timestamp())}:R>")
            count += 1
        for i in range(0, len(joinpos), 10):
           ls.append(joinpos[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Join Position of every user in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
        
    @list.command(name="createpos", description="Shows the position of creation of all id in the server")
    async def list_createpos(self, ctx):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        mem = {}
        view = create(ctx)
        em = discord.Embed(description="Which type of Members you want to see?", color=botinfo.root_color)
        ok = await ctx.reply(embed=em, view=view, mention_author=False)
        await view.wait()
        if not view.value:
            await ctx.send("Timed Out")
        if view.value == 'users':
            for member in ctx.guild.members:
              if not member.bot:
                mem[member.created_at.timestamp()] = member
        if view.value == 'bots':
            for member in ctx.guild.members:
              if member.bot:
                mem[member.created_at.timestamp()] = member
        if view.value == 'both':
            for member in ctx.guild.members:
                mem[member.created_at.timestamp()] = member
        await ok.delete()
        ls, count = [], 1
        joinpos = []
        for _t in sorted(mem):
            joinpos.append(f"`[{'0' + str(count) if count < 10 else count}]` | {mem[_t]} - Created at: <t:{round(mem[_t].created_at.timestamp())}:R>")
            count += 1
        for i in range(0, len(joinpos), 10):
           ls.append(joinpos[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Creation every id in {ctx.guild.name} - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
        
    @commands.hybrid_command(aliases=["ms"], description="Show's the Ping of bot")
    @commands.guild_only()
    async def ping(self, ctx: commands.Context):
      pfp = ctx.author.display_avatar.url
      s_id = ctx.guild.shard_id
      sh = self.bot.get_shard(s_id)
      embed = discord.Embed(description=f"**Message ping:** {round(sh.latency * 1000)} ms ", colour=botinfo.root_color)
      embed.set_author(name=f"| Bot latency", icon_url=pfp)
      embed.timestamp = datetime.datetime.utcnow()
      await ctx.reply(embed=embed, mention_author = False)

    @commands.hybrid_command(aliases=["si"], description="Shows information about this server")
    async def serverinfo(self, ctx):
        guild_roles = len(ctx.guild.roles)
        guild_members = len(ctx.guild.members)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        channels = text_channels + voice_channels
        pfp = ctx.author.display_avatar.url
        serverinfo = discord.Embed(colour=botinfo.root_color, title="Guild Information")
        serverinfo.add_field(name="General Information:",
                             value=f"Name: **{ctx.guild.name}**\n"
                                   f"ID: {ctx.guild.id}\n"
                                   f"Owner: {str(ctx.guild.owner)} ({ctx.guild.owner.mention})\n"
                                   f"Creation: <t:{round(ctx.guild.created_at.timestamp())}:R>\n"
                                   f"Total Member: {guild_members}\n"
                                   f"Roles: {guild_roles}\n"
                                   f"Channel: {channels}\n"
                                   f"Text Channel: {text_channels}\n"
                                   f"Voice Channel: {voice_channels}", inline=False)
        if ctx.guild.icon is not None:
            serverinfo.set_thumbnail(url=ctx.guild.icon.url)
            serverinfo.add_field(name="**SERVER ICON:**", value=f"[Icon]({ctx.guild.icon.url})", inline=False)
        if ctx.guild.banner is not None:
            serverinfo.set_image(url=ctx.guild.banner.url)
        serverinfo.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
        await ctx.send(embed=serverinfo)

    @commands.hybrid_command(aliases=["ri"], description="Shows information about the Role")
    async def roleinfo(self, ctx, role: discord.Role):
        roleinfo = discord.Embed(colour=botinfo.root_color, title=f"{role.name}'s Information")
        roleinfo.add_field(name="Role Information:",
                                 value=f"**Role Name:** {role.name}\n"
                                       f"**Role ID:** {role.id}\n"
                                       f"**Role Position:** {role.position}\n"
                                       f"**Hex code:** {str(role.color)}\n"
                                       f"**Created At:** <t:{round(role.created_at.timestamp())}:R>\n"
                                       f"**Mentionability:** {role.mentionable}\n"
                                       f"**Separated:** {role.hoist}\n"
                                       f"**Integration:** {role.is_bot_managed()}\n", inline=False)
        role_perm = ', '.join([str(p[0]).replace("_", " ").title() for p in role.permissions if p[1]])
        if role_perm is None:
            role_perm = "No permissions"
        roleinfo.add_field(name="Allowed Permissions:",
                                 value=role_perm, inline=False)
        if len(role.members) != 0:
            role_memb = [m.mention for m in role.members]
            role_mem = ""
            if len(role.members) > 15:
                role_mem = "Too many Members to show here"
            else:
                role_mem = str(role_memb).replace("'", "").replace("[", "").replace("]", "")
            roleinfo.add_field(name=f"Role Members [{len(role.members)}]:",
                                     value=role_mem, inline=False)
        await ctx.send(embed=roleinfo)

    @commands.hybrid_command(description="Shows status information about the user")
    async def status(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        pfp = ctx.author.display_avatar.url
        dnd = f"{emojis.dnd}"
        on = f"{emojis.on}"
        idlee = f"{emojis.idle}"
        off = f"{emojis.off}"
        mobile = f"{emojis.mobile}"
        desktop = f"{emojis.desktop}"
        web = f"{emojis.web}"
        activity = f"{emojis.activity}"
        if member.status == discord.Status.online:
            st = f"{on} Online"
        elif member.status == discord.Status.idle:
            st = f"{idlee} Idle"
        elif member.status == discord.Status.dnd:
            st = f"{dnd} Do Not Disturb"
        else:
            st = f"{off} Invisible"
        d = []
        if member.status == discord.Status.offline:
            d.append("None")
        elif member.mobile_status == member.status:
            d.append(f"{mobile} Mobile")
        elif member.desktop_status == member.status:
            d.append(f"{desktop} Desktop")
        elif member.web_status == member.status:
            d.append(f"{web} Browser")
        dd = "\n".join(d)
        em = discord.Embed(title=f"Status information of {str(member)}", color=botinfo.root_color)
        em.add_field(name="Status", value=st, inline=False)
        em.add_field(name="Device", value=dd, inline=False)
        em.add_field(name="Activity", value=str(member.activity), inline=False)
        if ctx.author.avatar:
            i = ctx.author.display_avatar.url
        else:
            i = None
        em.set_footer(text=f"Requested by {str(ctx.author)}", icon_url=i)
        await ctx.reply(embed=em, mention_author=False)

    @commands.hybrid_command(aliases=["ui", "whois"], description="Shows information about the user")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        pfp = ctx.author.display_avatar.url
        user_columns = database.fetchone("*", "badges", "user_id", member.id)
        des = []
        if user_columns is None:
            pass
        else:
            if user_columns['OWNER'] == 1:
                bdg = f"{emojis.owner} ***Owner***"
                des.append(bdg)
            if user_columns['DEVELOPER'] == 1:
                bdg = f"{emojis.dev} **Developer**"
                des.append(bdg)
            if user_columns['ADMIN'] == 1:
                bdg = f"{emojis.admin} Admin"
                des.append(bdg)
            if user_columns['MOD'] == 1:
                bdg = f"{emojis.mod} Mod"
                des.append(bdg)
            if user_columns['STAFF'] == 1:
                bdg = f"{emojis.staff} Staff"
                des.append(bdg)
            if user_columns['PARTNER'] == 1:
                bdg = f"{emojis.partner} Partner"
                des.append(bdg)
            if user_columns['SUPPORTER'] == 1:
                bdg = f"{emojis.early_sup} Early Supporter"
                des.append(bdg)
            if user_columns['SPECIAL'] == 1:
                bdg = f"{emojis.hype} Special One's"
                des.append(bdg)
        if member in ctx.guild.members:
            order = sorted(ctx.guild.members, key=lambda member: member.joined_at or discord.utils.utcnow()).index(member) + 1
        balance = f"{emojis.balance} "
        bravery = f"{emojis.bravery} "
        brilliance = f"{emojis.brilliance} "
        bug_1 = f"{emojis.bug_1} "
        bug_2 = f"{emojis.bug_2} "
        early = f"{emojis.early_sup} "
        hype = f"{emojis.hype} "
        partner = f"{emojis.partner} "
        staff = f"{emojis.staff} "
        system = f"{emojis.system} "
        veri_bot = f"{emojis.verified_bot} "
        veri_dev = f"{emojis.verified_dev} "
        act_dev = f"{emojis.active_dev} "
        badge = ""
        if member.public_flags.bug_hunter == True:
            badge += bug_1
        if member.public_flags.bug_hunter_level_2 == True:
            badge += bug_2
        if member.public_flags.hypesquad_bravery == True:
            badge += bravery
        if member.public_flags.hypesquad_balance == True:
            badge += balance
        if member.public_flags.hypesquad_brilliance == True:
            badge += brilliance
        if member.public_flags.hypesquad == True:
            badge += hype
        if member.public_flags.early_supporter == True:
            badge += early
        if member.public_flags.early_verified_bot_developer == True:
            badge += veri_dev
        if member.public_flags.verified_bot == True:
            badge += veri_bot
        if member.public_flags.staff == True:
            badge += staff
        if member.public_flags.system == True:
            badge += system
        if member.public_flags.partner == True:
            badge += partner
        if member.public_flags.active_developer == True:
            badge += act_dev
        if not badge:
            badge = "None"
        achive = ""
        if member in ctx.guild.members:
            member_roles = len(member.roles)
            if member_roles < 20:
                role_string = ' • '.join([r.mention for r in reversed(member.roles)][:-1])
                member_roles = role_string
            else:
                member_roles = "Too many roles to show here."
        userinfo = discord.Embed(colour=botinfo.root_color, title=f"{member.name}'s profile")
        userinfo.add_field(name="General Information:",
                                 value=f"**Name:** {member}\n"
                                       f"**ID:** {member.id}\n"
                                       f"**Nick:** {member.nick}\n"
                                       f"**Join Pos**: {order}/{len(ctx.guild.members)}\n"
                                       f"**Badge**: {badge}\n"
                                       f"**Account Creation:** <t:{round(member.created_at.timestamp())}:R>\n"
                                       f"**Server Joined:** <t:{round(member.joined_at.timestamp())}:R>\n", inline=False)
        userinfo.add_field(name="Role Info:",
                                value=f"**Top Role:** {member.top_role.mention}\n"
                                    f"**Roles [{(len(member.roles)-1)}]:** {member_roles}\n"
                                    f"**Color:** {str(member.color)}", inline=False)
        if member in ctx.guild.members:
            perm_string = ""
            if member.guild_permissions.administrator == True:
                admin = "Administrator, "
                perm_string +=admin
            if member.guild_permissions.kick_members == True:
                kick = "Kick Members, "
                perm_string +=kick
            if member.guild_permissions.ban_members == True:
                ban = "Ban Members, "
                perm_string +=ban
            if member.guild_permissions.manage_channels == True:
                mc = "Manage Channels, "
                perm_string +=mc
            if member.guild_permissions.manage_guild == True:
                ms = "Manage Server, "
                perm_string +=ms
            if member.guild_permissions.manage_messages == True:
                mm = "Manage Messages, "
                perm_string +=mm
            if member.guild_permissions.mention_everyone == True:
                me = "Mention Everyone, "
                perm_string +=me
            if member.guild_permissions.manage_nicknames == True:
                mn = "Manage Nicknames, "
                perm_string +=mn
            if member.guild_permissions.manage_roles == True:
                mr = "Manage Roles, "
                perm_string +=mr
            if member.guild_permissions.manage_webhooks == True:
                mw = "Manage Webhooks, "
                perm_string +=mw
            if member.guild_permissions.manage_emojis == True:
                me = "Manage Emojis, "
                perm_string +=me
            if perm_string != "":
                userinfo.add_field(name="Key permissions:", value=perm_string[:-2], inline=False)
            else:
                pass
            if ctx.guild.owner.id == member.id:
                so = "**SERVER OWNER**"
                achive = so
            else:
                if member.guild_permissions.administrator == True:
                    sa = "**SERVER ADMIN**"
                    achive = sa
                elif member.guild_permissions.manage_guild == True:
                        sm = "**SERVER MANAGER**"
                        achive = sm
                else:
                    if member.guild_permissions.manage_messages == True:
                        sms = "**SERVER MODERATOR**"
                        achive = sms
            if achive != "":
                userinfo.add_field(name="Acknowledgements:", value=achive.title(), inline=False)
            else:
                pass
            if len(des) != 0:
                userinfo.add_field(name=f"{self.bot.user.name} Badges:", value='\n'.join(des))
        usr = await self.bot.fetch_user(member.id)
        if usr.banner:
            banner = usr.banner.url
            userinfo.set_image(url=banner)
        userinfo.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
        if member.avatar is not None:
           userinfo.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=userinfo)
        
    @commands.hybrid_command(description="Shows the server icon")
    async def servericon(self, ctx):
         pfp = ctx.author.display_avatar.url
         em=discord.Embed(title="SERVER ICON", color=botinfo.root_color)
         em.set_image(url=ctx.guild.icon.url)
         em.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
         await ctx.send(embed=em)

    @commands.hybrid_command(aliases=["av"], brief="Avatar", description="Shows the avatar of user")
    @commands.guild_only()
    async def avatar(self, ctx, member: Union[discord.Member, discord.User] = None):
        member = (
            member or ctx.author
        )
        if isinstance(member, discord.User):
            if member in ctx.guild.members:
                member = discord.utils.get(ctx.guild.members, id=member.id)
            else:
                member = member
        if not member.avatar:
            await ctx.reply(f"There is no avatar for {str(member)}")
            return
        if member.avatar.url != member.display_avatar.url:
            em = discord.Embed(description="Which avatar would you like to see?", color=botinfo.root_color)
            view = OnOrOff(ctx)
            hm = await ctx.reply(embed = em, view=view, mention_author=False)
            await view.wait()
            if view.value == 'Yes':
                await hm.delete()
                pfp=member.avatar.url
                if "gif" in pfp:
                    des = f'[PNG]({pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")}) | [GIF]({pfp})'
                else:
                  if "png" or "jpeg" or "webp" in pfp:
                    des = f'[PNG]({pfp.replace("webp", "png").replace("jpeg", "png")})'
                embed = discord.Embed(title=str(member), description=des, color=botinfo.root_color)
                embed.set_image(url=pfp)
                embed.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
                return await ctx.send(embed=embed)
            if view.value == 'No':
                await hm.delete()
                pfp=member.display_avatar.url
                

                if "gif" in pfp:
                    des = f'[PNG]({pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")}) | [GIF]({pfp})'
                else:
                  if "png" or "jpeg" or "webp" in pfp:
                    des = f'[PNG]({pfp.replace("webp", "png").replace("jpeg", "png")})'
                embed = discord.Embed(title=str(member), description=des, color=botinfo.root_color)
                embed.set_image(url=pfp)
                embed.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=ctx.author.display_avatar.url)
                return await ctx.send(embed=embed)
        else:
            pfp=member.avatar.url
            if "gif" in pfp:
                    des = f'[PNG]({pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")}) | [GIF]({pfp})'
            else:
                if "png" or "jpeg" or "webp" in pfp:
                    des = f'[PNG]({pfp.replace("webp", "png").replace("jpeg", "png")})'
            embed = discord.Embed(title=str(member), description=des, color=botinfo.root_color)
            embed.set_image(url=pfp)
            embed.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="banner",invoke_without_command=True, description="Shows the banner's help menu")
    async def banner(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["banner", "banner user", "banner server"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            if cmd.description is None:
                cmd.description = "No Description"
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"Banner Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @banner.command(name="user", description="Shows the user's banner")
    async def user_banner(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        member = await self.bot.fetch_user(member.id)
        em = discord.Embed(color=botinfo.root_color)
        em.set_author(name=str(member), icon_url=member.display_avatar.url)
        em.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        if member.banner is None:
            em.description = f"`{str(member)}` doesn't have any banner"
            return await ctx.reply(embed=em)
        else:
            pfp=member.banner.url
            if "gif" in pfp:
                des = f'[PNG]({pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")}) | [GIF]({pfp})'
            else:
                if "png" or "jpeg" or "webp" in pfp:
                    des = f'[PNG]({pfp.replace("webp", "png").replace("jpeg", "png")})'
            em.description = des
            em.set_image(url=pfp)
            await ctx.reply(embed=em)

    @banner.command(name="server", description="Shows the server's banner")
    async def server_banner(self, ctx):
        em = discord.Embed(color=botinfo.root_color)
        em.set_author(name=str(ctx.guild.name))
        em.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        if ctx.guild.banner is None:
            em.description = f"The server doesn't have any banner"
            return await ctx.reply(embed=em)
        else:
            pfp=ctx.guild.banner.url
            if "gif" in pfp:
                des = f'[PNG]({pfp.replace("gif", "png").replace("webp", "png").replace("jpeg", "png")}) | [GIF]({pfp})'
            else:
                if "png" or "jpeg" or "webp" in pfp:
                    des = f'[PNG]({pfp.replace("webp", "png").replace("jpeg", "png")})'
            em.description = des
            em.set_image(url=pfp)
            await ctx.reply(embed=em)

    @commands.hybrid_command(name='first-message', aliases=['firstmsg', 'fm', 'firstmessage'], description="Shows the first message of the channel")
    async def _first_message(self, ctx, channel: discord.TextChannel = None):
        pfp = ctx.author.display_avatar.url
        if channel is None:
            channel = ctx.channel
        first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]
        embed = discord.Embed(description=f"> {first_message.content}", color=botinfo.root_color)
        embed.add_field(name="First Message", value=f"[Jump]({first_message.jump_url})")
        embed.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(aliases=["mc"], description="Returns the members count for the server")
    async def membercount(self, ctx):
        humans = [member for member in ctx.guild.members if not member.bot]
        bots = [member for member in ctx.guild.members if member.bot]
        embed = discord.Embed(title=f"Member Count", color=botinfo.root_color)
        embed.add_field(name=f"**Total Members:**", value=f"{len(ctx.guild.members)} Members")
        embed.add_field(name=f"**Total Humans:**", value=f"{len(humans)} Members")
        embed.add_field(name=f"**Total Bots:**", value=f"{len(bots)} Members")
        await ctx.reply(embed=embed)
        
    @commands.hybrid_command(aliases=["smc"], description="Returns the status members count for the server")
    async def statusmembercount(self, ctx):
        on = [member for member in ctx.guild.members if member.status == discord.Status.online]
        dnd = [member for member in ctx.guild.members if member.status == discord.Status.dnd]
        off = [member for member in ctx.guild.members if member.status == discord.Status.offline]
        idle = [member for member in ctx.guild.members if member.status == discord.Status.idle]
        embed = discord.Embed(title=f"Member Count", color=botinfo.root_color)
        embed.add_field(name=f"**{emojis.on} Online:**", value=f"{len(on)} Members")
        embed.add_field(name=f"**{emojis.idle} Idle:**", value=f"{len(idle)} Members")
        embed.add_field(name=f"**{emojis.dnd} Dnd:**", value=f"{len(dnd)} Members")
        embed.add_field(name=f"**{emojis.off} Offline:**", value=f"{len(off)} Members")
        if ctx.guild.icon:
            i = ctx.guild.icon.url
        else:
            i = self.bot.user.avatar.url
        embed.set_footer(text=f"{len(ctx.guild.members)} Total Members", icon_url=i)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="keywords", aliases=["keyword"], description="Shows the keyword to use for setting the embed/message")
    async def keywords(self, ctx):
      em = discord.Embed(title="Here are some keywords, which you can use in your embed/message.", description="```$user_name - displays username.\n$user_username - display users username with his discriminator.\n$user_discriminator - display users discriminator.\n$user_id - display users ID.\n$user_avatar - display users avatar.\n$user_mention - mentions the user.\n$user_created - displays the timestamp of when the user id was created.\n$user_joined - displays the timestamp of when the user joined the server.\n$user_profile - direct link for the user's profile\n$server_name - displays server name.\n$server_id - displays server ID.\n$server_icon - displays server icon.\n$membercount - show the member count of the server.\n$membercount_ordinal - same as membercount but includes ordinal number (st, th, rd).\n\n```", color=botinfo.root_color)
      em.set_author(name="Keywords", icon_url=self.bot.user.avatar.url)
      await ctx.reply(embed=em)

async def setup(bot):
    await bot.add_cog(general(bot))
