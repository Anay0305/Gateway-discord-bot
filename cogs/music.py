import discord
import os
import wavelink
from discord import app_commands
from discord.ext import commands
import asyncio
import typing
import datetime
import re
import random
import database
from typing import Union
import sqlite3
import botinfo
import emojis
from paginators import PaginationView
from ast import literal_eval
from premium import check_upgraded
from botinfo import *

URL_REG = re.compile(r'https?://(?:www\.)?.+')
SPOTIFY_URL_REG = re.compile(r'https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)')
msg_id = {}

def updatemsgid(guild_id, data):
    msg_id[guild_id] = data
    
def getmsgid(guild_id):
    try:
        d = msg_id[guild_id]
    except:
        d = None
    return d
pl_names = {}

def updateplname(id, data):
    pl_names[id] = data
    
def getplname(id):
    try:
        d = pl_names[id]
    except:
        d = "Cancel"
    return d

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

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [994130204949745705, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

class copyview(BasicView):
    def __init__(self, ctx: commands.Context, user: discord.Member):
        super().__init__(ctx, timeout=None)
        self.value = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only {str(self.user)} can interact with this message", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="<:Correct:1098134034455994388>", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(emoji="<:Wrong:1098134211275276300>", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()

class PlNameRoleButton(discord.ui.Button):
    def __init__(self, label, id, b_type="p2"):
        if b_type == "p":
            t = discord.ButtonStyle.blurple
        elif b_type == "p2":
            t = discord.ButtonStyle.green
        elif b_type == "secondary":
            t = discord.ButtonStyle.secondary
        else:
            t = discord.ButtonStyle.danger
        super().__init__(label=label, style=t, custom_id=label)
        self.name = label
        self.id = id

    async def callback(self, interaction: discord.Interaction):
        updateplname(self.id, self.name)
        self.view.stop()

class PlNamePanel(discord.ui.View):
    def __init__(self, stuff: list, id):
        super().__init__(timeout=None)
        for x in stuff:
            button = PlNameRoleButton(x, id)
            self.add_item(button)
        create = PlNameRoleButton("Create New", id, "p")
        self.add_item(create)
        create = PlNameRoleButton("Cancel", id, "danger")
        self.add_item(create)

class currentorqueue(BasicView):
    def __init__(self, ctx: commands.Context, user: discord.Member):
        super().__init__(ctx, timeout=None)
        self.value = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only {str(self.user)} can interact with this message", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Current Song", custom_id='currentsong', style=discord.ButtonStyle.green)
    async def __yes(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "currentsong"
        self.stop()

    @discord.ui.button(label="Current Queue", custom_id='queue', style=discord.ButtonStyle.blurple)
    async def __no(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "current"
        self.stop()

    @discord.ui.button(label="Cancel", custom_id='cancel', style=discord.ButtonStyle.red)
    async def __cancel(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "cancel"
        self.stop()

class voiceortext(BasicView):
    def __init__(self, ctx: commands.Context, user: discord.Member):
        super().__init__(ctx, timeout=None)
        self.value = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only {str(self.user)} can interact with this message", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Text", custom_id='currentsong', style=discord.ButtonStyle.green)
    async def __yes(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "text"
        self.stop()

    @discord.ui.button(label="Voice", custom_id='queue', style=discord.ButtonStyle.blurple)
    async def __no(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "voice"
        self.stop()

    @discord.ui.button(label="No", custom_id='cancel', style=discord.ButtonStyle.red)
    async def __cancel(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = "no"
        self.stop()

async def setfilter(player: wavelink.Player, filter):
    filter = filter.lower()
    if filter == "reset":
        await player.set_filters(wavelink.Filters().reset)
    elif filter == "lofi":
        await player.set_filters(wavelink.Filters(player._filters, timescale=wavelink.Timescale(speed =  0.7500000238418579, pitch = 0.800000011920929, rate = 1)))
    elif filter == "nightcore":
        await player.set_filters(wavelink.Filters(player._filters, timescale=wavelink.Timescale(speed = 1.2999999523162842, pitch = 1.2999999523163953, rate = 1)))
    elif filter == "8d":
        await player.set_filters(wavelink.Filters(player._filters, rotation=wavelink.Rotation(speed=0.29999))) 
    elif filter == "damon":
        await player.set_filters(wavelink.Filters(player._filters, timescale=wavelink.Timescale(speed =  0.6899999521238, pitch = 0.7999990000011920929, rate = 1)))
    elif filter == "daycore":
        await player.set_filters(wavelink.Filters(player._filters, timescale=wavelink.Timescale(speed =  0.8999999523162842, pitch = 0.9999999523162842, rate = 1)))
    elif filter == "bassboost":
        await player.set_filters(wavelink.Filters(player._filters, equalizer=wavelink.Equalizer.boost()))
    elif filter == "slowmode":
        await player.set_filters(wavelink.Filters(player._filters, timescale=wavelink.Timescale(speed = 0.8)))

class filters(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context, vc: wavelink.Player):
        options = []
        x = ["lofi", "nightcore", "daycore", "8d", "damon", "121", "reset"]
        for i in x:
            options.append(discord.SelectOption(label=f"{i.capitalize()}", value=i))
        super().__init__(placeholder="Select filter for song",
            custom_id="Filters",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.ctx = ctx
        self.vc = vc
        self.bot = bot
        
    async def interaction_check(self, interaction: discord.Interaction):
        c = False
        for i in self.ctx.guild.me.voice.channel.members:
            if i.id == interaction.user.id:
                c = True
                break
        if c:
            return True
        else:
            await interaction.response.send_message(f"Um, Looks like you are not in the voice channel...", ephemeral=True)
            return False
        
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "reset":
            self.vc.filterr = "None"
        else:
            self.vc.filterr = self.values[0].title()
        await setfilter(self.vc, self.values[0])
        await interaction.response.send_message(f"Set {self.values[0].capitalize()} filter", ephemeral=True)
        await interaction.message.edit(view=self.view)

class queueselect(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context, vc: wavelink.Player):
        options = []
        if vc is not None:
            count = 0
            for i in vc.queue:
                if count >= 25:
                    break
                count+=1
                options.append(discord.SelectOption(label=f"{i.title}", value=count))
            disable = False
        if len(options) == 0:
            options.append(discord.SelectOption(label="Anay", value="Anay"))
            disable = True
        super().__init__(placeholder="Current Queue",
            custom_id="current_queue",
            row=0,
            min_values=1,
            max_values=1,
            options=options,
            disabled=disable,
        )
        self.ctx = ctx
        self.vc = vc
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction):
        c = False
        for i in self.ctx.guild.me.voice.channel.members:
            if i.id == interaction.user.id:
                c = True
                break
        if c:
            return True
        else:
            await interaction.response.send_message(f"Um, Looks like you are not in the voice channel...", ephemeral=True)
            return False
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=False)
        val = int(self.values[0])
        await interaction.channel.send(embed=discord.Embed(description=f"Started playing song no. {val}.", color=0x7aaaff), delete_after=10)
        vc : wavelink.Player= self.vc
        vc.queue.put_at(0, vc.queue.get_at(val-1))
        await vc.stop()

class extraaction(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context, vc: wavelink.Player):
        options = []
        x = ["shuffle", "clear queue", "replay", "add to favourite", "add to playlist", "autoplay"]
        for i in x:
            options.append(discord.SelectOption(label=f"{i.title()}", value=i))
        super().__init__(placeholder="Select any action",
            custom_id="Actions",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.ctx = ctx
        self.vc = vc
        self.bot = bot
        
    async def interaction_check(self, interaction: discord.Interaction):
        c = False
        for i in self.ctx.guild.me.voice.channel.members:
            if i.id == interaction.user.id:
                c = True
                break
        if c:
            return True
        else:
            await interaction.response.send_message(f"Um, Looks like you are not in the voice channel...", ephemeral=True)
            return False
        
    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        vc = self.vc
        bot = self.bot
        ctx = self.ctx
        if val == "replay":
            await vc.seek(0)
            await interaction.response.send_message(f"Replayed the current song", ephemeral=True)
        elif val == "shuffle":
            q = self.vc.queue
            if len(q) <= 1:
                await interaction.response.send_message(f"The length of queue must be more than 2 for shuffle.", ephemeral=True)
            self.vc.queue.shuffle()
            await panelmsg(self.bot, self.ctx)
            await interaction.response.send_message(f"Shuffled the queue", ephemeral=True)
        elif val == "clear queue":
            self.vc.queue.clear()
            await panelmsg(self.bot, self.ctx)
            await interaction.response.send_message(f"Successfully cleared the queue", ephemeral=True)
        elif val == "autoplay":
            if vc.autoplay.value == 0:
                vc.autoplay = wavelink.AutoPlayMode.disabled
                em = discord.Embed(description=f"{interaction.user.mention} Disabled the autoplay", color=root_color)
            else:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                em = discord.Embed(description=f"{interaction.user.mention} Enabled the autoplay", color=root_color)
            await interaction.response.send_message(embed=em, ephemeral=True)
            await panelmsg(self.bot, self.ctx)
        elif val == "add to favourite":
            await interaction.response.defer(ephemeral=False, thinking=False)
            em = discord.Embed(description=f"{interaction.user.mention} Do you want to add the current song or the whole current queue in your Favourite songs playlist?")
            v = currentorqueue(ctx, interaction.user)
            init = await interaction.channel.send(embed=em, view=v)
            await v.wait()
            if v.value is None or v.value == "cancel":
                await init.delete()
            else:
                query = "SELECT * FROM  pl WHERE user_id = ?"
                val = (interaction.user.id,)
                with sqlite3.connect('./database.sqlite3') as db:
                    db.row_factory = sqlite3.Row
                    cursor = db.cursor()
                    cursor.execute(query, val)
                    p_db = cursor.fetchone()
                if p_db is None:
                    xd = {}
                else:
                    xd = literal_eval(p_db['pl'])
                query = await pladd(self, ctx, v.value)
                if "Favourite" in xd:
                    xd["Favourite"] = xd["Favourite"] + query
                else:
                    xd["Favourite"] = query
                if p_db is None:
                    sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
                    val = (ctx.author.id, f"{xd}")
                    cursor.execute(sql, val)
                else:
                    sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                    val = (f"{xd}", ctx.author.id)
                    cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                if v.value == "current":
                    q = "Current Queue"
                else:
                    q = "Current Song"
                em.description = f"{interaction.user.mention} Successfully added the {q} in your Favourite playlist\nTo play your favourite songs playlist just type `{str(self.bot.user)} play favourite`"
                await init.edit(embed=em, delete_after=15, view=None)
        else:
            await interaction.response.defer(ephemeral=False, thinking=False)
            em = discord.Embed(description=f"{interaction.user.mention} Do you want to add the current song or the whole current queue in the playlist?")
            v = currentorqueue(ctx, interaction.user)
            init = await interaction.channel.send(embed=em, view=v)
            await v.wait()
            if v.value is None or v.value == "cancel":
                await init.delete()
            else:
                query = "SELECT * FROM  pl WHERE user_id = ?"
                val = (interaction.user.id,)
                with sqlite3.connect('./database.sqlite3') as db:
                    db.row_factory = sqlite3.Row
                    cursor = db.cursor()
                    cursor.execute(query, val)
                    p_db = cursor.fetchone()
                if p_db is None:
                    xd = {}
                else:
                    xd = literal_eval(p_db['pl'])
                if v.value == "current":
                    q = "Current Queue"
                else:
                    q = "Current Song"
                em.description = f"{interaction.user.mention} To which playlist you want me to add the {q}?"
                x = round(random.random()*100000)
                vv = PlNamePanel(xd, x)
                await init.edit(embed=em, view=vv)
                await vv.wait()
                c = getplname(x)
                if c is None or c.lower() == "cancel":
                    await init.delete()
                elif c == "Create New":
                    em.description = f"{interaction.user.mention} Kindly Type the name for the new playlist you want to create and add the {q}"
                    await init.edit(embed=em, view=None)
                    def check(message):
                            return message.author == interaction.user and message.channel == interaction.channel
                    self.bot.mesaagecreate = True
                    try:
                            user_response = await self.bot.wait_for("message", timeout=120, check=check)
                            await user_response.delete()
                    except asyncio.TimeoutError:
                        await init.delete()
                        await interaction.message.edit(view=self.view)
                        return
                    self.bot.mesaagecreate = False
                    n = ""
                    for i in user_response.content:
                        if i == ' ':
                            break
                        n+=i
                    n = n.title()
                else:
                    n = c.title()
                query = await pladd(self, ctx, v.value)
                if n in xd:
                    xd[n] += query
                else:
                    xd[n] = query
                if p_db is None:
                    sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
                    val = (ctx.author.id, f"{xd}")
                    cursor.execute(sql, val)
                else:
                    sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                    val = (f"{xd}", ctx.author.id)
                    cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                if v.value == "current":
                    q = "Current Queue"
                else:
                    q = "Current Song"
                em.description = f"{interaction.user.mention} Successfully added the {q} in your {n.title()} playlist\nTo play your favourite songs playlist just type `{str(self.bot.user)} play {n.lower()}`"
                await init.edit(embed=em, delete_after=15, view=None)
        await interaction.message.edit(view=self.view)

class interface(discord.ui.View):
    def __init__(self, bot, ctx: commands.Context=None, panel=False, first=False, guild_id=None):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot
        self.value = None
        if ctx is not None:
            guild_id = ctx.guild.id
        self.prem = check_upgraded(guild_id)
        if ctx is None:
            self.vc = None
        else:
            self.vc: wavelink.Player = ctx.voice_client
        if self.prem:
            self.add_item(queueselect(bot, ctx, self.vc))
            if panel:
                #self.add_item(filters(bot, ctx, self.vc))
                self.add_item(extraaction(bot, ctx, self.vc))
            if first:
                for i in self.children:
                    try:
                        if i.custom_id == "pfav":
                            continue
                    except:
                        pass
                    i.disabled = True
        else:
            self.pfav.disabled = True
    
    async def interaction_check(self, interaction: discord.Interaction):
        c = False
        if self.ctx is None:
            return True
        if self.ctx.guild.me.voice is None:
            return True
        for i in self.ctx.guild.me.voice.channel.members:
            if i.id == interaction.user.id:
                c = True
                break
        if c:
            return True
        else:
            await interaction.response.send_message(f"Um, Looks like you are not in the voice channel...", ephemeral=True)
            return False

    #@discord.ui.button(label="First", custom_id='first', row=1, style=discord.ButtonStyle.gray)
    @discord.ui.button(emoji="<:first:1091162596511580250>", custom_id='first', row=1, style=discord.ButtonStyle.gray)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        if len(self.vc.queue.history) == 1:
            emb2 = discord.Embed(color=0x7aaaff)
            emb2.set_footer(text="| The first song of the queue is already playing.", icon_url=interaction.user.display_avatar.url)
            return await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)
        self.vc.queue.put_at(0, self.vc.current)
        self.vc.queue.put_at(0, self.vc.queue.history[0])
        self.vc.queue.history.clear()
        await self.vc.stop()
        emb2 = discord.Embed(color=0x7aaaff)
        emb2.set_footer(text="| Started the first song of the queue.", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)
        
    #@discord.ui.button(label="Back", custom_id='back', row=1, style=discord.ButtonStyle.green)
    @discord.ui.button(emoji="<:back:1091162558725099642>", custom_id='prev', row=1, style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        if len(self.vc.queue.history) == 1:
            emb2 = discord.Embed(color=0x7aaaff)
            emb2.set_footer(text="| No Previous song.", icon_url=interaction.user.display_avatar.url)
            return await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)
        self.vc.queue.put_at(0, self.vc.current)
        self.vc.queue.put_at(0, self.vc.queue.history[-2])
        self.vc.queue.history.delete(-1)
        await self.vc.stop()
        emb2 = discord.Embed(color=0x7aaaff)
        emb2.set_footer(text="| Started the previous song of the queue.", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)

    #@discord.ui.button(label="Pause", custom_id='rp', row=1, style=discord.ButtonStyle.gray)
    @discord.ui.button(emoji="<:pause:1091162575661711441>", custom_id='rp', row=1, style=discord.ButtonStyle.blurple)
    async def rp(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.vc
        if not vc.paused:
            await vc.pause(True)
            button.emoji = "<:play:1091162569781301278>"
            #button.label = "Resume"
            button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(view=self)
        else:
            await vc.pause(False)
            button.emoji = "<:pause:1091162575661711441>"
            #button.label = "Pause"
            button.style = discord.ButtonStyle.blurple
            await interaction.response.edit_message(view=self)
        
    #@discord.ui.button(label="Next", custom_id='skip', row=1, style=discord.ButtonStyle.green)
    @discord.ui.button(emoji="<:next:1091162563670184015>", custom_id='skip', row=1, style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        await self.vc.stop()
        emb2 = discord.Embed(color=0x7aaaff)
        emb2.set_footer(text="| Skipped the song", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)

    #@discord.ui.button(label="Last", custom_id='last', row=1, style=discord.ButtonStyle.gray)
    @discord.ui.button(emoji="<:fastforward:1091162556321767544>", custom_id='last', row=1, style=discord.ButtonStyle.gray)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        queue = self.vc.queue
        if len(queue) == 0 and self.vc.autoplay.value == 2:
            await self.vc.stop()
            em = discord.Embed(title="Queue concluded", color=0x070606)
            em.set_footer(text="| No more songs left to play in queue.", icon_url=self.ctx.guild.me.display_avatar.url)
            v = discord.ui.View()
            #v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
            return await interaction.channel.send(embed=em, view=v, mention_author=False, delete_after=15)
        else:
            last = self.vc.queue.pop()
            self.vc.queue.clear()
            await self.vc.queue.put_wait(last)
            await self.vc.stop()
            emb2 = discord.Embed(color=0x7aaaff)
            emb2.set_footer(text="| Started the last song of the queue.", icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=emb2, mention_author=False, delete_after=5)

    #@discord.ui.button(label="Loop", custom_id='loop', row=2, style=discord.ButtonStyle.gray)
    @discord.ui.button(emoji="<:repeat:1091162584901763143>", custom_id='loop', row=2, style=discord.ButtonStyle.gray)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.vc
        q = vc.queue
        if q.mode.value == 0:
            q.mode = wavelink.QueueMode.loop
            await interaction.response.send_message(f"The current song is set to loop", ephemeral=True)
        elif q.mode.value == 1:
            q.mode = wavelink.QueueMode.loop_all
            await interaction.response.send_message(f"The current queue will now be looped", ephemeral=True)
        else:
            q.mode = wavelink.QueueMode.normal
            await interaction.response.send_message(f"Now onwards nothing will be looped", ephemeral=True)
        await panelmsg(self.bot, self.ctx)

    #@discord.ui.button(label="Vol Down", custom_id='down', row=2, style=discord.ButtonStyle.green)
    @discord.ui.button(emoji="<:volume_down:1091162591356780545>", custom_id='down', row=2, style=discord.ButtonStyle.grey)
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        c = self.ctx.voice_client.volume
        if c >= 10:
            await self.ctx.voice_client.set_volume(c-10)
            await interaction.response.send_message(f"Changed the volume to {c-10}%", ephemeral=True)
        else:
            await self.ctx.voice_client.set_volume(0)
            await interaction.response.send_message(f"Changed the volume to 0%", ephemeral=True)
        await panelmsg(self.bot, self.ctx)

    #@discord.ui.button(label="Stop ", custom_id='stop', row=2, style=discord.ButtonStyle.red)
    @discord.ui.button(emoji="<:stop:1091166480583884871>", custom_id='stop', row=2, style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.vc.autoplay = wavelink.AutoPlayMode.disabled
        self.vc.queue.clear()
        await self.vc.stop()
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Destroyed the queue and stopped the player!", icon_url=interaction.user.display_avatar.url)
        v = discord.ui.View()
        await interaction.channel.send(embed=em, view=v, delete_after=10)

    #@discord.ui.button(label="Vol Up", custom_id='up', row=2, style=discord.ButtonStyle.primary)
    @discord.ui.button(emoji="<:volume_up:1091162580040548455>", custom_id='up', row=2, style=discord.ButtonStyle.grey)
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        c = self.ctx.voice_client.volume
        if c <= 90:
            await self.ctx.voice_client.set_volume(c+10)
            await interaction.response.send_message(f"Changed the volume to {c+10}%", ephemeral=True)
        else:
            await self.ctx.voice_client.set_volume(100)
            await interaction.response.send_message(f"Changed the volume to 100%", ephemeral=True)
        await panelmsg(self.bot, self.ctx)

    @discord.ui.button(emoji="<:fav_star:1238605811224416326>", custom_id='pfav', row=2, style=discord.ButtonStyle.grey)
    async def pfav(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        if self.ctx is not None:
            ctx = self.ctx
        else:
            ctx = await self.bot.get_context(interaction.message)
        ctx.channel = interaction.channel
        ctx.author = interaction.user
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed, delete_after=10)
        elif not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        elif ctx.author.voice.channel.id != ctx.guild.me.voice.channel.id:
            if ctx.voice_client.playing:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} Songs are already being played in {ctx.guild.me.voice.channel.mention}.", color=0x7aaaff)
                return await ctx.reply(embed=embed, delete_after=10)
            else:
                await ctx.voice_client.disconnect()
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.voice_client
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            em = discord.Embed(description=f"{interaction.user.mention} You dont have a favourite playlist")
            return await interaction.channel.send(embed=em, delete_after=10)
        else:
            x = literal_eval(p_db['pl'])
        query = "favourite"
        tracks = []
        coun = 0
        if query.strip().title() not in x:
            em = discord.Embed(description=f"{interaction.user.mention} You dont have a favourite playlist")
            return await interaction.channel.send(embed=em, delete_after=10)
        else:
            for i in x[query.strip().title()]:
                track = wavelink.Playable(i)
                track.extras = {"requester_id": ctx.author.id}
                coun += 1
                await vc.queue.put_wait(track)
        if vc.current:
            if coun == 1:
                track = vc.queue[-1]
                title = track.title
                url = track.uri
                tm = str(datetime.timedelta(milliseconds=track.length))
                try:
                    tm = tm[:tm.index(".")]
                except:
                    tm = tm
                emb = discord.Embed(description=f"\nAdded [{title}]({url}) - [{tm}] to the queue.", color=0x7aaaff)
                emb.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=emb, mention_author=False, delete_after=5)
            else:
                await ctx.send(embed=discord.Embed(color=0x7aaaff).set_footer(text=f"| {coun} Songs added to Queue", icon_url=self.bot.user.avatar.url), mention_author=False, delete_after=5)

        if not vc.current:
            vc.ctx = ctx
            await vc.play(vc.queue.get())
            if coun > 1:
                await ctx.send(embed=discord.Embed(color=0x7aaaff).set_footer(text=f"| {coun-1} Songs added to Queue", icon_url=self.bot.user.avatar.url), mention_author=False, delete_after=5)
        await panelmsg(self.bot, ctx)
        try:
            x = getmsgid(ctx.guild.id)
            ch = await self.bot.fetch_channel(x[0])
            msg = await ch.fetch_message(x[1])
            v = interface(self.bot, ctx)
            await msg.edit(view=v)
        except:
            pass

async def pladd(self, ctx, query):
        query = query.strip('<>')
        if SPOTIFY_URL_REG.match(query):
            spoturl_check = SPOTIFY_URL_REG.match(query)
            search_type = spoturl_check.group('type')
            spotify_id = spoturl_check.group('id')
            queue = []
            if search_type == "playlist":
                        tracks: wavelink.Search = await wavelink.Playable.search(query)
                        for i in tracks:
                            queue.append(i.raw_data)
            elif search_type == "album":
                try:
                    tracks: wavelink.Search = await wavelink.Playable.search(query)
                    for i in tracks:
                        queue.append(i.raw_data)
                except:
                    return await ctx.reply("I was not able to find this album! Please try again or use a different link.")
            else:
                tracks: wavelink.Search = await wavelink.Playable.search(query)
                for i in tracks:
                    queue.append(i.raw_data)
            
            if len(queue) == 0:
                return await ctx.reply("The URL you put is either not valid or doesn't exist!")

        else:
            if query.lower() == "current":
                if ctx.voice_client is None:
                    return await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} No song/queue is currently played.", color=0x7aaaff))
                elif not ctx.voice_client.playing:
                    return await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} No song/queue is currently played.", color=0x7aaaff))
                else:
                    x = [ctx.voice_client.current] + list(ctx.voice_client.queue)
                    queue = []
                    for i in x:
                        queue.append(i.raw_data)
            elif query.lower() == "currentsong":
                i = ctx.voice_client.current
                queue = []
                queue.append(i.raw_data)
            else:
                queue = []
                tracks: wavelink.Search = await wavelink.Playable.search(query)
                if len(tracks) == 0:
                    return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)
                queue.append(tracks[0].raw_data)
        return queue

async def stoppanel(bot, player, guild_id=None):
    query = "SELECT * FROM setup WHERE guild_id = ?"
    try:
        val = (player.guild.id,)
    except:
        val = (guild_id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        s_db = cursor.fetchone()
    if s_db is None:
        check = False
    else:
        try:
            c = bot.get_channel(s_db['channel_id'])
            if c is None:
                check = False
            else:
                msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                if msg is None:
                    check = False
                else:
                    check = True
        except:
            check = False
    if check:
        em = discord.Embed(title="No Song Currently Playing", description="To play your favourite songs playlist press <:fav_star:1238605811224416326> button.", color=8039167)
        em.set_image(url="https://media.discordapp.net/attachments/1091162329720295557/1093663343279099904/wp6400060.png?width=1066&height=533")
        em.set_footer(text=f"{bot.user.name} Song requester panel", icon_url=bot.user.avatar.url)
        v = interface(bot, None, True, True, player.guild.id)
        await msg.edit(content="**__Join the voice channel and send songs name or spotify link for song or playlist to play in this channel__**", embed=em, view=v)

async def panelmsg(bot, ctx: commands.Context, msg=None):
    track : wavelink.Playable = ctx.voice_client.current
    player: wavelink.Player = ctx.voice_client
    vc: wavelink.Player = ctx.voice_client
    if msg is None:
        query = "SELECT * FROM setup WHERE guild_id = ?"
        val = (player.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            s_db = cursor.fetchone()
        if s_db is None:
            check = False
        else:
            try:
                c = bot.get_channel(s_db['channel_id'])
                if c is None:
                    check = False
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        check = False
                    else:
                        check = True
                check = check
            except:
                check = False
        if not check:
            return
    try:
        req = discord.utils.get(bot.users, id=track.extras.requester_id)
    except:
        req = player.guild.me
    title = track.title
    thumb = track.artwork
    u = track.uri
    emb = msg.embeds[0]
    emb.title = None
    emb.description = f"\n[{track.title}]({u})\nTo play your favourite songs playlist press <:fav_star:1238605811224416326> button."
    emb.set_author(name="| Now Playing", icon_url=player.guild.me.display_avatar.url)
    emb.timestamp= datetime.datetime.now() + datetime.timedelta(milliseconds=int(track.length))
    emb.clear_fields()
    emb.add_field(name="Duration", value=converttime(track.length/1000))
    emb.add_field(name="Requester", value=f"[{str(req)}](https://discord.com/users/{req.id})")
    emb.add_field(name="Artist", value=track.author or "None")
    emb.set_image(url=None)
    #try:
    #    emb.add_field(name="Filter", value=vc.filterr)
    #except:
    #    emb.add_field(name="Filter", value="None")
    if vc.autoplay.value == 0:
        if len(vc.queue) == 0:
            emb.add_field(name="Queue Length", value=f"AutoPlay Enabled")
        else:
            emb.add_field(name="Queue Length", value=f"{len(vc.queue)} Songs + AutoPlay Enabled")
    else:
        emb.add_field(name="Queue Length", value=f"{len(vc.queue)}")
    emb.add_field(name="Volume", value=f"{ctx.voice_client.volume}%")
    if vc.queue.mode.value == 1:
        loop = "Song"
    elif vc.queue.mode.value == 2:
        loop = "Queue"
    else:
        loop = "None"
    emb.add_field(name="Looping", value=loop)
    emb.set_thumbnail(url=thumb)
    q = []
    count = 0
    for i in player.queue:
        if count >= 15:
            break
        count +=1
        tm = str(datetime.timedelta(milliseconds=i.length))
        try:
            tm = tm[:tm.index(".")]
        except:
            tm = tm
        try:
            title = i.stitle
        except:
            title = i.title
        ds = f"{count}. {title} - [{tm}]\n"
        q.append(ds)
    v = interface(bot=bot, ctx=ctx, panel=True, first=False)
    await msg.edit(content=None, embed=emb, view=v)

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        c = None
        if player and player.queue and player.autoplay.value == 2:
            c = await player.play(player.queue.get())
        if payload.player:
            try:
                ctx : commands.Context = payload.original.ctx
            except:
                ctx: commands.Context = payload.player.ctx
        try:
            x = getmsgid(player.guild.id)
            ch = await self.bot.fetch_channel(x[0])
            msg = await ch.fetch_message(x[1])
            try:
                await msg.delete()
            except:
                await msg.edit(view=None)
        except:
            pass
        if payload.reason == "stopped" and payload.player.autoplay.value == 2:
            await stoppanel(self.bot, player)
            return
        if payload.player.current is None and payload.player.queue.count == 0 and payload.player.autoplay.value == 2 and c is None:
            em = discord.Embed(title="Queue concluded", color=0x070606)
            em.set_footer(text="| No more songs left to play in queue.", icon_url=ctx.guild.me.display_avatar.url)
            v = discord.ui.View()
            await ctx.send(embed=em, view=v, mention_author=False, delete_after=15)
	    await self.bot.main_owner.send(payload.reason)
            await stoppanel(self.bot, player)
        if payload.reason == "finished":
            pass
        else:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
        track = payload.track
        dur = track.length/1000
        dic = {}
        for i in ctx.guild.me.voice.channel.members:
            if i.bot:
                continue
            query = "SELECT * FROM user WHERE user_id = ?"
            val = (i.id,)
            cursor.execute(query, val)
            u_db = cursor.fetchone()
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
            dic[i.id] = dur
            totaltime+=dur
            if player.guild.id in s_dic:
                s_dic[player.guild.id] += dur
            else:
                s_dic[player.guild.id] = dur

            tit = track.title
            if tit in t_dic:
                t_dic[tit] += dur
            else:
                t_dic[tit] = dur

            author_str = track.author.replace(' and ', ', ').replace(' & ', ', ')
            authors = [author.strip() for author in author_str.split(',')]
            for j in authors:
                if j in a_dic:
                    a_dic[j] += dur
                else:
                    a_dic[j] = dur

            for j in ctx.guild.me.voice.channel.members:
                if j.id == i.id or j.bot:
                    continue
                if j.id in f_dic:
                    f_dic[j.id] += dur
                else:
                    f_dic[j.id] = dur

            s_dic = {k: v for k, v in reversed(sorted(s_dic.items(), key=lambda item: item[1]))}
            f_dic = {k: v for k, v in reversed(sorted(f_dic.items(), key=lambda item: item[1]))}
            t_dic = {k: v for k, v in reversed(sorted(t_dic.items(), key=lambda item: item[1]))}
            a_dic = {k: v for k, v in reversed(sorted(a_dic.items(), key=lambda item: item[1]))}
            if u_db is None:
                sql = (f"INSERT INTO user(user_id, totaltime, server, friend, artist, track) VALUES(?, ?, ?, ?, ?, ?)")
                val = (i.id, totaltime, f"{s_dic}", f"{f_dic}", f"{a_dic}", f"{t_dic}",)
                cursor.execute(sql, val)
            else:
                sql = (f"UPDATE user SET totaltime = ? WHERE user_id = ?")
                val = (totaltime, i.id)
                cursor.execute(sql, val)
                sql = (f"UPDATE user SET server = ? WHERE user_id = ?")
                val = (f"{s_dic}", i.id)
                cursor.execute(sql, val)
                sql = (f"UPDATE user SET friend = ? WHERE user_id = ?")
                val = (f"{f_dic}", i.id)
                cursor.execute(sql, val)
                sql = (f"UPDATE user SET artist = ? WHERE user_id = ?")
                val = (f"{a_dic}", i.id)
                cursor.execute(sql, val)
                sql = (f"UPDATE user SET track = ? WHERE user_id = ?")
                val = (f"{t_dic}", i.id)
                cursor.execute(sql, val)
            db.commit()
        cursor.close()
        db.close()
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            query = "SELECT * FROM bot WHERE bot_id = ?"
            val = (self.bot.user.id,)
            cursor.execute(query, val)
            b_db = cursor.fetchone()
        if b_db is None:
            totaltime = 0
            s_dic = {}
            f_dic = {}
        else:
            totaltime = b_db['totaltime']
            s_dic = literal_eval(b_db['server'])
            f_dic = literal_eval(b_db['user'])
        totaltime+=dur
        if player.guild.id in s_dic:
            s_dic[player.guild.id] += dur
        else:
            s_dic[player.guild.id] = dur
        for i in dic:
            if i in f_dic:
                f_dic[i] += dur
            else:
                f_dic[i] = dur
        s_dic = {k: v for k, v in reversed(sorted(s_dic.items(), key=lambda item: item[1]))}
        f_dic = {k: v for k, v in reversed(sorted(f_dic.items(), key=lambda item: item[1]))}
        if b_db is None:
            sql = (f"INSERT INTO bot(bot_id, totaltime, server, user) VALUES(?, ?, ?, ?)")
            val = (self.bot.user.id, totaltime, f"{s_dic}", f"{f_dic}",)
            cursor.execute(sql, val)
        else:
            sql = (f"UPDATE bot SET totaltime = ? WHERE bot_id = ?")
            val = (totaltime, self.bot.user.id,)
            cursor.execute(sql, val)
            sql = (f"UPDATE bot SET server = ? WHERE bot_id = ?")
            val = (f"{s_dic}", self.bot.user.id,)
            cursor.execute(sql, val)
            sql = (f"UPDATE bot SET user = ? WHERE bot_id = ?")
            val = (f"{f_dic}", self.bot.user.id,)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        if payload.original:
            player = payload.player
            try:
                ctx : commands.Context = payload.original.ctx
            except:
                ctx: commands.Context = payload.player.ctx
            track = payload.player.current
            try:
                req = discord.utils.get(self.bot.users, id=track.extras.requester_id)
            except:
                req = player.guild.me
            try:
                qq = track.noqsongs
            except:
                qq = 0
            title = track.title
            thumb = track.artwork
            author = track.author
            u = track.uri
            s_db = database.fetchone("*", "setup", "guild_id", player.guild.id)
            if s_db is None:
                check = False
            else:
                try:
                    c = self.bot.get_channel(s_db['channel_id'])
                    if c is None:
                        check = False
                    else:
                        msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                        if msg is None:
                            check = False
                        else:
                            check = True
                    check = check and ctx.channel.id == s_db['channel_id']
                except:
                    check = False
            if check is False:
                emb = discord.Embed(description=f"\n[{title}]({u})", color=0x7aaaff).set_author(name="| Now Playing", icon_url=player.guild.me.display_avatar.url)
                emb.timestamp= datetime.datetime.now() + datetime.timedelta(milliseconds=int(track.length))
                emb.add_field(name="Duration", value=converttime(track.length/1000))
                emb.add_field(name="Requester", value=f"[{str(req)}](https://discord.com/users/{req.id})")
                emb.add_field(name="Artist", value=author or "None")
                emb.set_thumbnail(url=thumb)
                v = interface(self.bot, ctx)
                init = await ctx.send(embed=emb, mention_author=False, view=v)
                updatemsgid(ctx.guild.id, [init.channel.id, init.id])
                if qq > 0:
                    emb2 = discord.Embed()
                    emb2.set_footer(text=f"| Added {qq} songs to the queue", icon_url=req.display_avatar.url)
                    await ctx.send(embed=emb2, mention_author=False, delete_after=15)
            else:
                await panelmsg(self.bot, ctx, msg)
                pass
    
    @commands.hybrid_command(name="autoplay", description="Toggles the music autoplay")
    async def autoplay(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} A song should be playing in order to enable or disable autoplay.", color=0x7aaaff)
        if not vc.playing:
            return await ctx.reply(embed=embed)
        else:
            if vc.autoplay.value == 0:
                vc.autoplay = wavelink.AutoPlayMode.disabled
                await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Disabled AutoPlay.", icon_url=self.bot.user.avatar.url), delete_after=10)
            else:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Enabled AutoPlay.", icon_url=self.bot.user.avatar.url), delete_after=10)
            await panelmsg(self.bot, self.ctx)
    
    @commands.hybrid_command(name="play",aliases=["p"], description = "Plays a song")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)     
        elif not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        elif ctx.author.voice.channel.id != ctx.guild.me.voice.channel.id:
            if ctx.voice_client.playing:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} Songs are already being played in {ctx.guild.me.voice.channel.mention}.", color=0x7aaaff)
                return await ctx.reply(embed=embed)
            else:
                await ctx.voice_client.disconnect()
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.voice_client
        if query.lower() == "fav":
            query = "favourite"
        s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
        if s_db is None:
            check = False
        else:
            try:
                c = self.bot.get_channel(s_db['channel_id'])
                if c is None:
                    check = False
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        check = False
                    else:
                        check = True
                check = check and ctx.channel.id == s_db['channel_id']
            except:
                check = False
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            x = {}
        else:
            x = literal_eval(p_db['pl'])
        coun = 0
        xx = query.split("\n")
        for query in xx:
            if query.strip().title() in x:
                for i in x[query.strip().title()]:
                    track = wavelink.Playable(i)
                    track.extras = {"requester_id": ctx.author.id}
                    coun += 1
                    await vc.queue.put_wait(track)
            else:
                tracks: wavelink.Search = await wavelink.Playable.search(query)
                if not tracks:
                    return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)

                if isinstance(tracks, wavelink.Playlist):
                    tracks.track_extras(ctx=ctx, requester_id=ctx.author.id)
                    added: int = await vc.queue.put_wait(tracks)
                    coun += added

                else:
                    track: wavelink.Playable = tracks[0]
                    track.extras = {"requester_id": ctx.author.id}
                    coun += 1
                    await vc.queue.put_wait(track)

        if vc.current:
            if coun == 1:
                track = vc.queue[-1]
                title = track.title
                url = track.uri
                tm = str(datetime.timedelta(milliseconds=track.length))
                try:
                    tm = tm[:tm.index(".")]
                except:
                    tm = tm
                emb = discord.Embed(description=f"\nAdded [{title}]({url}) - [{tm}] to the queue.", color=0x7aaaff)
                emb.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=emb, mention_author=False, delete_after=5)
            else:
                await ctx.send(embed=discord.Embed(color=0x7aaaff).set_footer(text=f"| {coun} Songs added to Queue", icon_url=self.bot.user.avatar.url), mention_author=False, delete_after=5)

        if not vc.current:
            vc.ctx = ctx
            await vc.play(vc.queue.get())
            if coun > 1:
                await ctx.send(embed=discord.Embed(color=0x7aaaff).set_footer(text=f"| {coun-1} Songs added to Queue", icon_url=self.bot.user.avatar.url), mention_author=False, delete_after=5)
        if check:
            await panelmsg(self.bot, ctx, msg)
        else:
            try:
                x = getmsgid(ctx.guild.id)
                ch = await self.bot.fetch_channel(x[0])
                msg = await ch.fetch_message(x[1])
                v = interface(self.bot, ctx)
                await msg.edit(view=v)
            except:
                pass

    @play.autocomplete("query")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        if needle:
            tracks = await wavelink.Pool.fetch_tracks(f'spsearch:{needle}')
            if len(tracks) == 0:
                return []
            ls = []
            for i in tracks:
                if len(i.title) >= 100:
                    continue
                ls.append(app_commands.Choice(name=i.title, value=f"{i.uri}"))
            return ls
        else:
            pls = [
                app_commands.Choice(name="Love Songs", value="https://open.spotify.com/playlist/37i9dQZF1DXbQDZkQM83q7"),
                app_commands.Choice(name="Sad Songs", value="https://open.spotify.com/playlist/37i9dQZF1DXdFesNN9TzXT"),
                app_commands.Choice(name="Chillin Mood", value="https://open.spotify.com/playlist/37i9dQZF1DWTwzVdyRpXm1"),
                app_commands.Choice(name="Valentine's Special", value="https://open.spotify.com/playlist/37i9dQZF1DX14CbVHtvHRB"),
                app_commands.Choice(name="Make Me Breathe", value="https://open.spotify.com/playlist/0GRYdJKuf8gAiNAV7yQ7Ia?si=ie2Uikh-S9a_H5lyxGba6w&pi=a-nnfbnDHVQa2Z"),
                app_commands.Choice(name="Bomb that shit up", value="https://open.spotify.com/playlist/48YPLX3aA7NM1WVFHLWH8G?si=OMvZghTdSqKurfo3DHrgnQ"),
                app_commands.Choice(name="Heer ya Whore?", value="https://open.spotify.com/playlist/5W5icPTZTK6Oa9qLTrVvpT?si=X3CmeZinQq-CXGv_IBiUXg"),
                app_commands.Choice(name="Vrindavan Chalo", value="https://open.spotify.com/playlist/2fGmu0GPKtc6Ty3cdnpYNo?si=_Mn_la1QQYCGgzAzwMYRhg")
            ]
            query1 = "SELECT * FROM  pl WHERE user_id = ?"
            val1 = (ctx.author.id,)
            with sqlite3.connect('./database.sqlite3') as db1:
                db1.row_factory = sqlite3.Row
                cursor1 = db1.cursor()
                cursor1.execute(query1, val1)
                p_db = cursor1.fetchone()
            if p_db is None:
                return pls
            else:
                x = literal_eval(p_db['pl'])
            if x == "{}":
                return pls
            ls = []
            for i in x:
                ls.append(i)
            ls = [
                app_commands.Choice(name=f"{cog_name.title()} Playlist Made by you", value=cog_name)
                for cog_name in sorted(ls)
            ]
            if len(ls) < 20:
                xx = 20-len(ls)
                if len(pls) > xx:
                    pls = random.sample(pls, xx)
                return ls+pls
            else:
                return ls[:25]

    @commands.hybrid_command(name="current", aliases=['now'], description = "Gives you details of the current song")
    async def current(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} No song is currently played.", color=0x7aaaff)
        if not vc.playing:
            return await ctx.reply(embed=embed)
        now = vc.current
        x = datetime.datetime.now()
        try:
            requester = discord.utils.get(self.bot.users, id=now.extras.requester_id)
        except:
            requester = vc.guild.me
        track = now
        sauthor = track.author
        u = track.uri
        if vc.queue.mode.value == 1:
            loop = "Song"
        elif vc.queue.mode.value == 2:
            loop = "Queue"
        else:
            loop = None
        total = now.length/1000
        currentt = vc.position/1000
        bar = '━'
        slider = '●'
        size = 14
        percent = currentt / total * size;
        progarr = []
        for i in range(size):
            progarr.append(bar)
        progarr[round(percent)] = slider
        x = "".join(progarr)
        total = str(datetime.timedelta(seconds=int(total)))
        try:
            total = total[:total.index(".")]
        except:
            total = total
        currentt = str(datetime.timedelta(seconds=int(currentt)))
        try:
            currentt = currentt[:currentt.index(".")]
        except:
            currentt = currentt
        x = f"[{currentt}] {x} [{total}]"
        if vc.paused:
            pp = "Paused"
        else:
            pp = "Resumed"
        embed = discord.Embed(description=f"[{now.title}]({u}) \nAuthor: {sauthor or 'None'}\nRequested By: {requester.mention}\n{x}", color=0x7aaaff)
        embed.set_author(name=f"Now Playing", icon_url=f"{self.bot.user.avatar.url}")
        embed.set_footer(text=f"Volume: {vc.volume}% | {pp} | Looping: {loop}", icon_url=f"{ctx.author.display_avatar.url}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="shuffle", description="Shuffles the current queue")
    async def shuffle(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} No song is currently played.", color=0x7aaaff)
        if not vc.playing:
            return await ctx.reply(embed=embed)
        else:
            q = vc.queue
            if len(q) <= 1:
                return await ctx.reply(f"The length of queue must be more than 2 for shuffle.")
            else:        
                vc.queue.shuffle
                s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
                if s_db is None:
                    check = False
                else:
                    try:
                        c = self.bot.get_channel(s_db['channel_id'])
                        if c is None:
                            check = False
                        else:
                            msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                            if msg is None:
                                check = False
                            else:
                                check = True
                        check = check and ctx.channel.id == s_db['channel_id']
                    except:
                        check = False
                if check:
                    await panelmsg(self.bot, ctx, msg)
                else:
                    try:
                        x = getmsgid(ctx.guild.id)
                        ch = await self.bot.fetch_channel(x[0])
                        msg = await ch.fetch_message(x[1])
                        v = interface(self.bot, ctx)
                        await msg.edit(view=v)
                    except:
                        pass
                return await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Shuffled the current queue", icon_url=self.bot.user.avatar.url), delete_after=5)
                
    @commands.hybrid_command(name="replay", description="Replays the current song")
    async def replay(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} No song is currently played.", color=0x7aaaff)
        if not vc.playing:
            return await ctx.reply(embed=embed)
        else:
            await vc.seek(0)
            await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Replayed the current song", icon_url=self.bot.user.avatar.url))
    
    @commands.hybrid_command(description = "Changes the loop setting")
    async def loop(self, ctx: commands.Context, option: str = None):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0x7aaaff)
        if not vc.playing:
            return await ctx.reply(embed=embed)
        opt = ['s', 'q', 'n', 'song', 'queue', 'none']
        if option is None:
            option = 'n'
        else:
            if option.lower() not in opt:
                return await ctx.reply("There are only 3 options for looping: None, Song or Queue")
            option = option[0]
        if option == 'n':
            vc.queue.mode = wavelink.QueueMode.normal
            await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Now onwards nothing will be looped", icon_url=self.bot.user.avatar.url))
        if option == 's':
            vc.queue.mode = wavelink.QueueMode.loop
            await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| The current song is set to loop", icon_url=self.bot.user.avatar.url))
        if option == 'q':
            vc.queue.mode = wavelink.QueueMode.loop_all
            await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| The current queue will now be looped", icon_url=self.bot.user.avatar.url))
        s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
        if s_db is None:
            check = False
        else:
            try:
                c = self.bot.get_channel(s_db['channel_id'])
                if c is None:
                    check = False
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        check = False
                    else:
                        check = True
                check = check and ctx.channel.id == s_db['channel_id']
            except:
                check = False
        if check:
            await panelmsg(self.bot, ctx, msg)
            
    @commands.hybrid_command(description = "Searches a song")
    async def search(self, ctx, *, args):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        tracks = await wavelink.Pool.fetch_tracks(f'spsearch:{args}')
        if len(tracks) == 0:
            return await ctx.reply(f"Nothing found for `{args}`")
        count = 1
        des = ""
        for i in tracks:
            if count > 10:
                break
            else:
                des+=f"`[{'0' + str(count) if count < 10 else count}]` | [{i.title}]({i.uri}) - {i.author}\n"
                count+=1
        embed = discord.Embed(title=f"Results of searching {args}", description=des, color=0x7aaaff)
        embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        await init.delete()
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="queue", description = "Shows you the current queue")
    async def queue(self, ctx):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            await init.delete()
            return await ctx.reply(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            await init.delete()
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        emb = discord.Embed(
            description=f"{ctx.author.mention} There are no songs playing",color=0x7aaaff)
        if not vc.playing:
            await init.delete()
            return await ctx.reply(embed=emb)
        queue = vc.queue
        if len(queue) == 0:
            em = discord.Embed(color=0x070606)
            em.set_footer(text="| No more songs are there in the queue.", icon_url=ctx.guild.me.display_avatar.url)
            v = discord.ui.View()
            await init.delete()
            return await ctx.reply(embed=em, view=v, delete_after=15)
        ls, q = [], []
        count = 0
        for i in queue:
            song = [i]
            count += 1
            tm = str(datetime.timedelta(milliseconds=song[0].length))
            try:
                tm = tm[:tm.index(".")]
            except:
                tm = tm
            title = song[0].title
            q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{title}]({song[0].uri}) - [{tm}]")
        for i in range(0, len(q), 10):
           ls.append(q[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=0x7aaaff)
           embed.title = f"Current Queue - {count}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
    
    @commands.hybrid_command(name="qclear", description="Clears the current queue")
    async def clear(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        
        s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
        if s_db is None:
            check = False
        else:
            try:
                c = self.bot.get_channel(s_db['channel_id'])
                if c is None:
                    check = False
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        check = False
                    else:
                        check = True
                check = check and ctx.channel.id == s_db['channel_id']
            except:
                check = False
        if check:
            await panelmsg(self.bot, ctx, msg)
        else:
            try:
                x = getmsgid(ctx.guild.id)
                ch = await self.bot.fetch_channel(x[0])
                msg = await ch.fetch_message(x[1])
                v = interface(self.bot, ctx)
                await msg.edit(view=v)
            except:
                pass
        vc.queue.clear()
        await ctx.reply(embed=discord.Embed(color=0x7aaaff).set_footer(text="| Cleared the queue successfully", icon_url=self.bot.user.avatar.url))
    
    @commands.hybrid_command(name="remove", description="Remove a song from the current queue")
    async def remove(self, ctx: commands.Context, index, endindex=None):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        xd = vc.queue
        if endindex is not None:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd)) or (not endindex.isdigit()) or (int(endindex)) < 1 or (int(endindex) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} Both the numbers should be between 1 and {len(xd)}")
            elif (int(endindex)<int(index)):
                return await ctx.reply(f"{ctx.author.mention} End index should be greater than start index")
            else:
                for i in reversed(range(int(index)-1, int(endindex)-1)):
                    xd.delete(i)
                des = f"Successfully removed the songs from index number {int(index)} to {int(endindex)}"
        else:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} The number should be between 1 and {len(xd)}")
            else:
                xd.delete(int(index)-1)
                des = f"Successfully removed the song at index number {index}"
        s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
        if s_db is None:
            check = False
        else:
            try:
                c = self.bot.get_channel(s_db['channel_id'])
                if c is None:
                    check = False
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        check = False
                    else:
                        check = True
                check = check and ctx.channel.id == s_db['channel_id']
            except:
                check = False
        if check:
            await panelmsg(self.bot, ctx, msg)
        else:
            try:
                x = getmsgid(ctx.guild.id)
                ch = await self.bot.fetch_channel(x[0])
                msg = await ch.fetch_message(x[1])
                v = interface(self.bot, ctx)
                await msg.edit(view=v)
            except:
                pass
        emb2 = discord.Embed(color=0x7aaaff)
        emb2.set_footer(text=des, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=emb2, mention_author=False, delete_after=15)
    
    @commands.hybrid_command(name="moveto", aliases=['skipto'], description="Move the player to different position")
    async def moveto(self, ctx: commands.Context, index: str):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        xd = list(vc.queue.copy())
        if (
            (not index.isdigit()) or 
            (int(index)) < 1 or 
            (int(index) > len(xd))
        ):
            return await ctx.send(f"{ctx.author.mention} The index should be a number between 1 and {len(xd)} position!")
        vc.queue.clear()
        for i in xd[int(index)-1:]:
            await vc.queue.put_wait(i)
        await vc.stop()
        emb2 = discord.Embed(color=0x7aaaff)
        emb2.set_footer(text=f"| Moved the player to song no. {index}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=emb2, mention_author=False, delete_after=15)

    @commands.hybrid_command(name="stop", description = "Stops the song")
    async def stop(self, ctx: commands.Context):
        
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        if ctx.voice_client.playing:
            ctx.voice_client.autoplay = wavelink.AutoPlayMode.disabled
            ctx.voice_client.queue.clear()
            await ctx.voice_client.stop()
            em = discord.Embed(color=0x070606)
            em.set_footer(text="| Destroyed the queue and stopped the player!", icon_url=ctx.author.display_avatar.url)
            v = discord.ui.View()
            #v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
            await ctx.reply(embed=em, view=v)
        else:
            em = discord.Embed(color=0xff0000)
            em.set_footer(text="| The player is already stopped", icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=em)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            c = self.bot.get_channel(m_db['channel_id'])
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)

    @commands.hybrid_command(name="pause", description = "Pauses the song")
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0x7aaaff)
        if not ctx.voice_client.playing:
            return await ctx.reply(embed=embed)
        if ctx.voice_client.paused:
            embed.description = f"{ctx.author.mention} The song is already paused."
            return await ctx.reply(embed=embed)
        await ctx.voice_client.pause(True)
        em = discord.Embed(color=0xff0000)
        em.set_footer(text="| Paused the player", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.hybrid_command(name="resume", aliases=["continue"], description = "Resumes the song")
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0x7aaaff)
        if not ctx.voice_client.playing:
            return await ctx.reply(embed=embed)
        if not ctx.voice_client.paused:
            embed.description = f"{ctx.author.mention} The song is not paused."
            return await ctx.reply(embed=embed)
        await ctx.voice_client.pause(False)
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Resumed the player", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.hybrid_command(name="skip", aliases=['next'], pass_context=True, description = "Plays the next song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        vc: wavelink.Player = ctx.voice_client
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0x7aaaff)
        if not ctx.voice_client.playing:
            return await ctx.reply(embed=embed)
        queue = vc.queue
        if len(queue) == 0 and vc.autoplay.value == 2:
            await vc.stop()
            em = discord.Embed(title="Queue concluded", color=0x070606)
            em.set_footer(text="| No more songs left to play in queue.", icon_url=ctx.guild.me.display_avatar.url)
            v = discord.ui.View()
            #v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
            return await ctx.reply(embed=em, view=v)
        else:
            await vc.stop()
            emb2 = discord.Embed(color=0x7aaaff)
            emb2.set_footer(text="| Skipped the song", icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=emb2, mention_author=False, delete_after=15)

    @commands.hybrid_command(name="seek", description = "Changes the position of song")
    async def seek(self, ctx: commands.Context, time):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0x7aaaff)
        if not ctx.voice_client.playing:
            return await ctx.reply(embed=embed)
        track = ctx.voice_client.current
        if (
            (not time.isdigit()) or 
            (int(time)) < 0 or 
            (int(time) > track.length/1000)
        ):
            return await ctx.send(f"{ctx.author.mention} The time should be a number between 0 and {track.length/1000} seconds!")
        time = int(time)
        await ctx.voice_client.seek(int(time)*1000)
        em = discord.Embed(color=0x070606)
        em.set_footer(text=f"| Seeked the song to {time} seconds.!", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)
    
    @commands.hybrid_command(name = "volume", aliases=['v', 'vol'], description = "Change the bot's volume.")
    async def volume(self, ctx: commands.Context, volume):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        if (
            (not volume.isdigit()) or 
            (int(volume)) < 0 or 
            (int(volume) > 100)
        ):
            return await ctx.send(f"{ctx.author.mention} The volume should be a number between 0 and 100!")
        volume = int(volume)
        await ctx.voice_client.set_volume(volume)
        em = discord.Embed(color=0x070606)
        await panelmsg(self.bot, ctx)
        em.set_footer(text=f"| Changed the volume to {volume}%", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.hybrid_command(name="connect",aliases=["join", "j"], description = "Joins a voice channel")
    async def join(self, ctx: commands.Context, channel: typing.Optional[discord.VoiceChannel]):
        
        if channel is None:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
                return await ctx.reply(embed=embed)
            else:
                channel = ctx.author.voice.channel
        node = wavelink.Pool.get_node()
        player = node.get_player(ctx.guild)
        if player is not None:
            if player.connected():
                return await ctx.reply("I am already connected to a voice channel.")
        vc: wavelink.player = await channel.connect(cls=wavelink.Player, self_deaf=True)
        mbed=discord.Embed(description=f"{self.bot.user.name} Joins {channel.mention}", color=0x7aaaff)
        mbed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=mbed)

    @commands.hybrid_command(name="disconnect", aliases=["dc"], description = "Disconnects from voice channel")
    async def disconnect(self, ctx: commands.Context):
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"Already disconnected from the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        ctx.voice_client.queue.clear()
        await ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Destroyed the queue and left the voice channel!", icon_url=ctx.author.display_avatar.url)
        v = discord.ui.View()
        #v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
        await ctx.reply(embed=em, view=v)
        await asyncio.sleep(30)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            if ctx.voice_client is not None:
                await ctx.voice_client.stop()
                await ctx.voice_client.disconnect()
            c = self.bot.get_channel(m_db['channel_id'])
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)

    @commands.hybrid_command(name="forcefix", description="Makes the bot leaves the vc forcefully")
    async def forcefix(self, ctx: commands.Context):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("Fixed the player")
        except:
            await ctx.send("Error occured")

    @commands.hybrid_command(name="msetup", description="Setups the song request channel")
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx: commands.Context, *, channel: Union[discord.VoiceChannel, discord.TextChannel]=None):
        c = check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium by creating a ticket in the [Support Server](https://discord.gg/K4v4aEuwp6)", color=0x7aaaff).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/K4v4aEuwp6"))
            return await ctx.reply(embed=em, view=v)
        query = "SELECT * FROM setup WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            s_db = cursor.fetchone()
        if s_db is None:
            em = discord.Embed(title="No Song Currently Playing", description="To play your favourite songs playlist press <:fav_star:1238605811224416326> button.", color=8039167)
            em.set_image(url="https://media.discordapp.net/attachments/1091162329720295557/1093663343279099904/wp6400060.png?width=1066&height=533")
            em.set_footer(text=f"{self.bot.user.name} Song requester panel", icon_url=self.bot.user.avatar.url)
            if channel is None:
                if not ctx.guild.me.guild_permissions.manage_channels:
                    em = discord.Embed(description=f"{emojis.wrong} Unfortunately I am missing **`Manage Channels`** permissions to create a new channel in the server\nYou can mention a channel if you don't want to create a new one.", color=botinfo.wrong_color)
                    return await ctx.send(embed=em, delete_after=7)
                view = voiceortext(ctx, ctx.author)
                init = await ctx.reply(embed=discord.Embed(description=f"You didn't mention any channel so do you want me to create a music channel for this server?", color=root_color), view=view)
                await view.wait()
                await init.delete()
                if view.value == "voice":
                    c = await ctx.guild.create_voice_channel(name=f"sputnik song request")
                elif view.value == "text":
                    c = await ctx.guild.create_text_channel(name=f"sputnik song request")
                else:
                    return
            else:
                c = channel
            v = interface(self.bot, ctx, True, True)
            init = await c.send("**__Join the voice channel and send songs name or spotify link for song or playlist to play in this channel__**", embed=em, view=v)
            sql = (f"INSERT INTO setup(guild_id, channel_id, msg_id) VALUES(?, ?, ?)")
            val = (ctx.guild.id, c.id, init.id,)
            cursor.execute(sql, val)
            await ctx.reply(embed=discord.Embed(description=f"Song request channel set to {c.mention} for the server\nNow you can use my music commands there without any prefix", color=0x7aaaff))
        else:
            try:
                c = self.bot.get_channel(s_db['channel_id'])
                if c is None:
                    pass
                else:
                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                    if msg is None:
                        try:
                            await msg.delete()
                        except:
                            await msg.edit(view=None)
                    else:
                        pass
            except:
                pass
            sql = (f"DELETE FROM 'setup' WHERE guild_id = ?")
            val = (ctx.guild.id,)
            cursor.execute(sql, val)
            await ctx.reply(embed=discord.Embed(description=f"Song request channel removed from this server", color=0x7aaaff))
        db.commit()
        cursor.close()
        db.close()

    @commands.hybrid_command(name="247", description="Keeps the bot 24/7 in vc")
    @commands.has_permissions(manage_channels=True)
    async def _sss(self, ctx):
        c = check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium by creating a ticket in the [Support Server](https://discord.gg/K4v4aEuwp6)", color=0x7aaaff).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/K4v4aEuwp6"))
            return await ctx.reply(embed=em, view=v)
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0x7aaaff)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is None:
            if not getattr(ctx.guild.me.voice, "channel", None):
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            sql = (f"INSERT INTO '247'(guild_id, channel_id) VALUES(?, ?)")
            val = (ctx.guild.id, ctx.author.voice.channel.id)
            cursor.execute(sql, val)
            await ctx.reply(f"Now i will stay connected 24/7 in {ctx.author.voice.channel.mention}")
        else:
            sql = (f"DELETE FROM '247' WHERE guild_id = ?")
            val = (ctx.guild.id,)
            cursor.execute(sql, val)
            await ctx.reply(f"Now i will not stay connected 24/7 in {ctx.author.voice.channel.mention}")
        db.commit()
        cursor.close()
        db.close()
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await self.bot.wait_until_ready()
        guild = member.guild
        if member.id != self.bot.user.id:
            return
        
        node = wavelink.Pool.get_node()
        player = node.get_player(guild.id)
        if after.channel is None:
            await stoppanel(self.bot, player, member.guild.id)
            try:
                await player.stop()
                await player.disconnect()
            except:
                pass
        else:
            return
        await asyncio.sleep(30)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            c = self.bot.get_channel(m_db['channel_id'])
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)
            pass

    @commands.hybrid_group(
        invoke_without_command=True, aliases=['pl'], description="Shows the help menu for playlist commands"
    )
    async def playlist(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["playlist", "playlist add", "playlist remove", "playlist create", "playlist delete", "playlist copy", "playlist show"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"<:gateway_music:1040855483029913660> Playlist Commands", colour=0x7aaaff,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @playlist.command(name="show", description="Shows your playlists")
    async def show(self, ctx: commands.Context, name: str=None):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if name is None:
            em_no = discord.Embed(description="You have no playlist", color=0x7aaaff).set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
            if p_db is None:
                await init.delete()
                return await ctx.reply(embed=em_no)
            xd = literal_eval(p_db['pl'])
            if len(xd) == 0:
                await init.delete()
                return await ctx.reply(embed=em_no)
            else:
                ls, q = [], []
                count = 0
                for i in xd:
                    tm = 0
                    for j in xd[i]:
                        tm += j['info']['length']
                    tm = str(datetime.timedelta(milliseconds=tm))
                    try:
                        tm = tm[:tm.index(".")]
                    except:
                        tm = tm
                    count += 1
                    q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{i}](https://discord.gg/K4v4aEuwp6) - [{tm}]")
                for i in range(0, len(q), 10):
                    ls.append(q[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=0x7aaaff)
                    embed.title = f"{str(ctx.author)}'s Playlist - {count}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await init.delete()
                await page.start(ctx)
        else:
            name = name.title()
            em_no = discord.Embed(description=f"You have no playlist named `{name}`", color=0x7aaaff).set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
            if p_db is None:
                await init.delete()
                return await ctx.reply(embed=em_no)
            xd = literal_eval(p_db['pl'])
            if name not in xd:
                await init.delete()
                return await ctx.reply(embed=em_no)
            else:
                ls, q = [], []
                count = 0
                for i in xd[name]:
                    tm = str(datetime.timedelta(milliseconds=i['info']['length']))
                    try:
                        tm = tm[:tm.index(".")]
                    except:
                        tm = tm
                    count += 1
                    q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{i['info']['title']}]({i['info']['uri']}) - [{tm}]")
                for i in range(0, len(q), 10):
                    ls.append(q[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=0x7aaaff)
                    embed.title = f"{name} Playlist - {count}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await init.delete()
                await page.start(ctx)

    @show.autocomplete("name")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            return []  
        else:
            x = literal_eval(p_db['pl'])
        if x == "{}":
            return []
        ls = []
        for i in x:
            ls.append(i)
        if needle:
            xd = []
            for i in ls:
                if i.lower().startswith(needle.lower()):
                    xd.append(i)
            lss = []
            for i in xd:
                lss.append(app_commands.Choice(name=f"{i} Playlist", value=i))
            return lss[:25]
        else:
            lss = [
                app_commands.Choice(name=f"{cog_name} Playlist", value=cog_name)
                for cog_name in sorted(ls)
            ]
            return lss[:25]

    @playlist.command(name="copy", description="Copies a playlist from another user's playlist")
    async def copy(self, ctx: commands.Context, name: str, *, user: discord.Member):
        name = name.title()
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (user.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} don't have any playlist named {name}", color=0x7aaaff))
        else:
            xx = literal_eval(p_db['pl'])
            if name not in xx:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} don't have any playlist named {name}", color=0x7aaaff))
            else:
                v = copyview(ctx, user)
                em = discord.Embed(description=f"Do you want to allow {ctx.author.mention} to copy your playlist `{name}`?", color=0x7aaaff)
                em.set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
                init = await ctx.send(f"{user.mention}", embed=em, view=v)
                await v.wait()
                if v.value == 'No':
                    await init.delete()
                    await ctx.reply("The owner of the playlist denied to copy playlist for you")
                if v.value == 'Yes':
                    await init.delete()
                    query = "SELECT * FROM  pl WHERE user_id = ?"
                    val = (ctx.author.id,)
                    with sqlite3.connect('./database.sqlite3') as db:
                        db.row_factory = sqlite3.Row
                        cursor = db.cursor()
                        cursor.execute(query, val)
                        p_db = cursor.fetchone()
                    if p_db is None:
                        xxx = {}
                    else:
                        xxx = literal_eval(p_db['pl'])
                    if name in xxx:
                        vv = copyview(ctx, ctx.author)
                        init2 = await ctx.reply(f"You already have a playlist `{name}`\nDo you want to copy it with any other name?", view=vv)
                        await vv.wait()
                        if vv.value == 'No':
                            await init2.delete()
                        if vv.value == 'Yes':
                            await init2.edit("What should be the name for the copied playlist?", view=None)
                            def message_check(m):
                                return ( 
                                    m.author.id == ctx.author.id
                                    and m.channel == ctx.channel
                                )
                            user_response = await self.bot.wait_for("message", check=message_check)
                            await user_response.delete()
                            await init2.delete()
                            name1 = user_response.content
                            try:
                                w = name1.index(" ")
                                name1 = name1[:w].strip()
                            except ValueError:
                                name1 = name
                            xxx[name1] = xx[name]
                    else:
                        name1 = name
                        xxx[name1] = xx[name]
                    if p_db is None:
                        sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
                        val = (ctx.author.id, f"{xxx}")
                        cursor.execute(sql, val)
                    else:
                        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                        val = (f"{xxx}", ctx.author.id)
                        cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    em = discord.Embed(description=f"Successfully copied a playlist `{name1}` from {user.mention} with {len(xx[name])} song(s)", color=0x7aaaff)
                    em.set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
                    await ctx.reply(embed=em)

    @playlist.command(name="create", description="Creates a playlist for you")
    async def create(self, ctx: commands.Context, name: str, *, query: str):
        name = name.title()
        if "youtube.com" in query:
            return await ctx.reply("Songs from Youtube are not supported")
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            try:
                xx = literal_eval(p_db['pl'])
            except:
                xx = {}
            if name.title() in xx:
                return await ctx.reply(f"{ctx.author.mention} You already have a playlist named {name}")
        queue = await pladd(self, ctx, query)
        if p_db is None:
            xd = {}
            xd[name.title()] = queue
            sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
            val = (ctx.author.id, f"{xd}")
            cursor.execute(sql, val)
        else:
            xd = literal_eval(p_db['pl'])
            xd[name.title()] = queue
            sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
            val = (f"{xd}", ctx.author.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Created a playlist for you with name `{name.title()}` and {len(xd[name.title()])} Song(s)\nto play this playlist just type {ctx.prefix}play {name.title()}.", color=0x7aaaff))
    
    @playlist.command(name="delete", description="Delete a playlist for you")
    async def delete(self, ctx: commands.Context, name: str):
        name = name.title()
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name}")
        else:
            xx = literal_eval(p_db['pl'])
            if name.title() not in xx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name}")
            else:
                q = literal_eval(p_db['pl'])
                del q[name.title()]
                sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                val = (f"{q}", ctx.author.id)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Deleted your playlist with name `{name.title()}`", color=0x7aaaff))

    @delete.autocomplete("name")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            return []  
        else:
            x = literal_eval(p_db['pl'])
        if x == "{}":
            return []
        ls = []
        for i in x:
            ls.append(i)
        if needle:
            xd = []
            for i in ls:
                if i.lower().startswith(needle.lower()):
                    xd.append(i)
            lss = []
            for i in xd:
                lss.append(app_commands.Choice(name=f"{i} Playlist", value=i))
            return lss[:25]
        else:
            lss = [
                app_commands.Choice(name=f"{cog_name} Playlist", value=cog_name)
                for cog_name in sorted(ls)
            ]
            return lss[:25]
                
    @playlist.command(name="add", description="Adds a song/queue in your playlist")
    async def _add(self, ctx: commands.Context, name, *, query):
        name = name.title()
        if "youtube.com" in query:
            return await ctx.reply("Songs from Youtube are not supported")
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            xx = literal_eval(p_db['pl'])
            if name.title() not in xx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        else:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        queue = await pladd(self, ctx, query)
        xx[name.title()] = xx[name.title()] + queue
        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
        val = (f"{xx}", ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Added {len(queue)} songs to your playlist with name `{name.title()}`", color=0x7aaaff))

    @_add.autocomplete("name")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            return []  
        else:
            x = literal_eval(p_db['pl'])
        if x == "{}":
            return []
        ls = []
        for i in x:
            ls.append(i)
        if needle:
            xd = []
            for i in ls:
                if i.lower().startswith(needle.lower()):
                    xd.append(i)
            lss = []
            for i in xd:
                lss.append(app_commands.Choice(name=f"{i} Playlist", value=i))
            return lss[:25]
        else:
            lss = [
                app_commands.Choice(name=f"{cog_name} Playlist", value=cog_name)
                for cog_name in sorted(ls)
            ]
            return lss[:25]
                
    @playlist.command(name="remove", description="Removes song(s) from your playlist")
    async def _remove(self, ctx: commands.Context, name, index, endindex=None):
        name = name.title()
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            xxx = literal_eval(p_db['pl'])
            if name.title() not in xxx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        else:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        xd = xxx[name.title()]
        if endindex is not None:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd)) or (not endindex.isdigit()) or (int(endindex)) < 1 or (int(endindex) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} Both the numbers should be between 1 and {len(xd)}")
            elif (int(endindex)<int(index)):
                return await ctx.reply(f"{ctx.author.mention} End index should be greater than start index")
            else:
                for i in reversed(range(int(index)-1, int(endindex)-1)):
                    xd.pop(i)
                await ctx.reply(f"{ctx.author.mention} Successfully removed {int(endindex)-int(index)} songs from your playlist `{name.title()}`")
        else:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} The number should be between 1 and {len(xd)}")
            else:
                xd.pop(int(index)-1)
                await ctx.reply(f"{ctx.author.mention} Successfully removed 1 song from your playlist `{name.title()}`")
        xxx[name.title()] = xd
        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
        val = (f"{xxx}", ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @_remove.autocomplete("name")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        if p_db is None:
            return []  
        else:
            x = literal_eval(p_db['pl'])
        if x == "{}":
            return []
        ls = []
        for i in x:
            ls.append(i)
        if needle:
            xd = []
            for i in ls:
                if i.lower().startswith(needle.lower()):
                    xd.append(i)
            lss = []
            for i in xd:
                lss.append(app_commands.Choice(name=f"{i} Playlist", value=i))
            return lss[:25]
        else:
            lss = [
                app_commands.Choice(name=f"{cog_name} Playlist", value=cog_name)
                for cog_name in sorted(ls)
            ]
            return lss[:25]

async def setup(bot):
	await bot.add_cog(music(bot))
