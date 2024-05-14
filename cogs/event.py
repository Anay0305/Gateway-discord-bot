import discord
from discord.ext import commands
import sqlite3
from ast import literal_eval
from botinfo import *
from cogs.selfroles import DropdownSelfRoleView, ButtonSelfRoleView
from cogs.giveaway import GWBUTTON
import botinfo
import database
import emojis

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
        await database.create_tables()
        print(f'Logged in as {bot.user.name}({bot.user.id})')

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
