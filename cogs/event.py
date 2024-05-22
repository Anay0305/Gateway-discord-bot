import discord
from discord.ext import commands
import sqlite3
from ast import literal_eval
from botinfo import *
from cogs.ticket import ticketpanel, tickredel, ticketchannelpanel
from cogs.selfroles import DropdownSelfRoleView, ButtonSelfRoleView
from cogs.giveaway import GWBUTTON
import botinfo
import database
import emojis
from cogs.music import interface
from premium import check_upgraded
import wavelink
import asyncio
import voice_db
import datetime

async def loadmsetup(bot: commands.AutoShardedBot):
    msetup_db = database.fetchall1("*", "setup")
    for i, j, k in msetup_db:
        try:
            c = bot.get_channel(j)
            if c is None:
                check = False
            else:
                msg: discord.Message = await c.fetch_message(k)
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
            v = interface(bot, None, True, True, i)
            await msg.edit(content="**__Join the voice channel and send songs name or spotify link for song or playlist to play in this channel__**", embed=em, view=v)

async def loadselfroles(bot: commands.AutoShardedBot):
    self_db = database.fetchall1("*", "srmain")
    for i, j, k in self_db:
        dbb = literal_eval(j)
        dbd = literal_eval(k)
        for i in dbb:
            v = ButtonSelfRoleView(stuff=i["data"])
            try:
                c = bot.get_channel(i['channel_id'])
                m = await c.fetch_message(i['message_id'])
                await m.edit(view=v)
                bot.add_view(v)
            except:
                pass
        for i in dbd:
            dd = i['data']
            reqrole = dd[0]["reqrole"]
            v = DropdownSelfRoleView(place=i["placeholder"], max=i["max_options"], stuff=i["data"], reqrole=reqrole)
            try:
                c = bot.get_channel(i['channel_id'])
                m = await c.fetch_message(i['message_id'])
                await m.edit(view=v)
                bot.add_view(v)
            except:
                pass

async def loadgw(bot: commands.AutoShardedBot):
    bot.add_view(GWBUTTON())
            
class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
        webhook.send(f"Shard {shard_id} is Now ready", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
            webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
            webhook.send(f"Shard {shard_id} is Disconnected", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        bot = self.bot
        try:
            await loadselfroles(bot)
        except:
            pass
        try:
            await loadgw(bot)
        except:
            pass
        bot.add_view(ticketpanel(bot))
        bot.add_view(ticketchannelpanel(bot))
        bot.add_view(tickredel(bot))
        bot.add_view(interface(bot))
        webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
        webhook.send(f"Shard {shard_id} is Resumed", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        try:
            await loadselfroles(bot)
        except:
            pass
        try:
            await loadgw(bot)
        except:
            pass
        await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
        bot.add_view(ticketpanel(bot))
        bot.add_view(ticketchannelpanel(bot))
        bot.add_view(tickredel(bot))
        bot.add_view(interface(bot))
        await loadmsetup(bot)
        await asyncio.sleep(3)
        query = "SELECT * FROM  '247'"
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute("DROP TABLE help")
            coun = 0
            try:
                cursor.execute(query)
                m_db = cursor.fetchall()
                for i in m_db:
                    try:
                        c = bot.get_channel(i['channel_id'])
                        if check_upgraded(c.guild.id):
                            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)
                            coun+=1
                    except:
                        pass
            except:
                pass
        db.commit()
        cursor.close()
        db.close()
        await database.create_tables()
        print(f'Logged in as {bot.user.name}({bot.user.id})')
        t = round(datetime.datetime.now().timestamp())
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            for i in bot.guilds:
                cursor.execute(f"INSERT OR IGNORE INTO roles(guild_id) VALUES({i.id})")
                cursor.execute(f"INSERT OR IGNORE INTO imp(guild_id) VALUES({i.id})")
                cursor.execute(f"INSERT OR IGNORE INTO prefixes(guild_id) VALUES({i.id})")
                cursor.execute(f"INSERT OR IGNORE INTO ignore(guild_id) VALUES({i.id})")
                cursor.execute(f"INSERT OR IGNORE INTO auto(guild_id) VALUES({i.id})")
                cursor.execute(f"INSERT OR IGNORE INTO logs(guild_id) VALUES({i.id})")
                cursor.execute(f"SELECT * FROM  invc WHERE guild_id = {i.id}")
                in_vc = cursor.fetchone()
                if in_vc is None:
                    x = {}
                else:
                    x = literal_eval(in_vc['vc'])
                for j in i.channels:
                    if str(j.type) == "voice":
                        if j.id not in x:
                            x[j.id] = None
                        check = True
                        for k in j.members:
                            if not k.bot:
                                check= False
                                if i.id in voice_db.user_start:
                                    if k.id not in voice_db.user_start[i.id]:
                                        voice_db.user_start[i.id][k.id] = t
                                else:
                                    voice_db.user_start[i.id] ={k.id: t}
                        if not check:
                            if i.id in voice_db.channel_start:
                                if j.id not in voice_db.channel_start[i.id]:
                                    voice_db.channel_start[i.id][j.id] = t
                            else:
                                voice_db.channel_start[i.id] ={j.id: t}
                if in_vc is None:
                    val = (i.id, f"{x}")
                    query = f"INSERT OR IGNORE INTO invc(guild_id, vc) VALUES(?, ?)"
                    cursor.execute(query, val)
                else:
                    query = f"UPDATE invc SET 'vc' = ? WHERE guild_id = ?"
                    val = (f"{x}", i.id,)
                    cursor.execute(query, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.wait_until_ready()
        bot = self.bot
        em = discord.Embed(title="Guild Joined", color=botinfo.root_color)
        em.add_field(name="Guild Information:", value=f"Server Name: {guild.name}\nServer Id: {guild.id}\nServer Owner: {guild.owner.name} [{guild.owner.id}]\nCreated At: <t:{round(guild.created_at.timestamp())}:R>\nMember Count: {len(guild.members)} Members\nRoles: {len(guild.roles)} Roles\nText Channels: {len(guild.text_channels)} Channels\nVoice Channels: {len(guild.voice_channels)} Channels")
        em.add_field(name="Bot Info:", value=f"Servers: {len(bot.guilds)} Servers\nUsers: {len(bot.users)} Users\nChannels: {str(len(set(bot.get_all_channels())))} Channels")
        try:
            em.set_thumbnail(url=guild.icon.url)
        except:
            pass
        em.set_footer(text=f"{str(bot.user)}", icon_url=bot.user.avatar.url)
        webhook = discord.SyncWebhook.from_url(webhook_join_leave_logs)
        bl_db = database.fetchone("*", "bl_guilds", "main", 1)
        if bl_db is not None:
            bl_db = literal_eval(bl_db["guild_names"])
            for i in bl_db:
                if i in guild.name.lower():
                    await guild.leave()
                    return webhook.send(content=f"Blacklist guild with name {i} was added.", username=f"{str(self.bot.user)} | Blacklisted guild Join Logs", avatar_url=self.bot.user.avatar.url)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Join Logs", avatar_url=self.bot.user.avatar.url)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO roles(guild_id) VALUES({guild.id})")
            cursor.execute(f"INSERT OR IGNORE INTO imp(guild_id) VALUES({guild.id})")
            cursor.execute(f"INSERT OR IGNORE INTO prefixes(guild_id) VALUES({guild.id})")
            cursor.execute(f"INSERT OR IGNORE INTO ignore(guild_id) VALUES({guild.id})")
            cursor.execute(f"INSERT OR IGNORE INTO auto(guild_id) VALUES({guild.id})")
            cursor.execute(f"INSERT OR IGNORE INTO logs(guild_id) VALUES({guild.id})")
        db.commit()
        cursor.close()
        db.close()
        in_vc = database.fetchone("*", "invc", "guild_id", guild.id)
        x = {}
        for i in guild.channels:
            if str(i.type) == 'voice':
                x[i.id] = None
        if in_vc is None:
            val = (guild.id, f"{x}")
            database.insert("invc", "guild_id, vc", val)
        else:
            database.update("invc", "vc", f"{x}", "guild_id", guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.wait_until_ready()
        bot = self.bot
        if guild is None:
          return
        em = discord.Embed(title="Guild Leave", color=botinfo.root_color)
        em.add_field(name="Guild Information:", value=f"Server Name: {guild.name}\nServer Id: {guild.id}\nCreated At: <t:{round(guild.created_at.timestamp())}:R>\nMember Count: {len(guild.members)} Members\nRoles: {len(guild.roles)} Roles\nText Channels: {len(guild.text_channels)} Channels\nVoice Channels: {len(guild.voice_channels)} Channels")
        em.add_field(name="Bot Info:", value=f"Servers: {len(bot.guilds)} Servers\nUsers: {len(bot.users)} Users\nChannels: {str(len(set(bot.get_all_channels())))} Channels")
        try:
            em.set_thumbnail(url=guild.icon.url)
        except:
            pass
        em.set_footer(text=f"{str(bot.user)}", icon_url=bot.user.avatar.url)
        webhook = discord.SyncWebhook.from_url(webhook_join_leave_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Leave Logs", avatar_url=self.bot.user.avatar.url)

async def setup(bot):
    await bot.add_cog(event(bot))
