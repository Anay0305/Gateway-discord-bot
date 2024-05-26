import discord
from discord.ext import commands
import sqlite3
import datetime
from core.paginators import PaginationView
from botinfo import *
import botinfo
import os
from io import BytesIO
from ast import literal_eval
from typing import Union
import core.database as database
import core.emojis as emojis
import botinfo
import wavelink
import requests
import subprocess

class owner(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot

    @commands.command()
    @commands.is_owner()
    async def api_up(self, ctx: commands.Context):
        api_url = botinfo.api_url+"git_pull"
        try:
            response = requests.get(api_url)

            if response.status_code == 200:
                await ctx.send("Git pull command executed successfully.")
                await ctx.send(f"Output: ```{response.json()['output']}```")
            else:
                await ctx.reply(f"Error: {response.json()['error']}")

        except requests.exceptions.RequestException as e:
            await ctx.reply(f"Error: {e}")
    
    @commands.command(aliases=["autopush", "autoup", "ap"])
    @commands.is_owner()
    async def autoupdate(self, ctx: commands.Context):
        try:
            result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                await ctx.send("Git pull command executed successfully.")
                count = 0
                for i in self.bot.extensions:
                    x = i
                    if i.replace(".", "/") in output:
                        count+=1
                        self.bot.reload_extension(x)
                await ctx.send(f"Reloaded {count} cogs.")
            else:
                error_message = result.stderr
                await ctx.reply(f"Error: {error_message}")

        except Exception as e:
            await ctx.reply(f"Error: {e}")

    @commands.group(invoke_without_command=True)
    async def title(self, ctx):
        pass

    @title.command(name="give", aliases=["a"], description="Gives the title to user")
    async def title_give(self, ctx, member: discord.User, *, title):
        ls = workowner
        if ctx.author.id not in ls and ctx.author.id not in self.bot.owner_ids:
            return
        result = database.fetchone("*", "titles", "user_id", member.id)
        if result is None:
            val = (member.id, title.upper())
            database.insert("titles", "user_id, title", val)
        else:
            database.update("titles", "title", title.upper(), "user_id", member.id)
        await ctx.send(f'Given **{title}** title to {str(member)}')
        em = discord.Embed(description=f"{title} title was given to {member.mention} [{member.id}] by {ctx.author.mention} [{ctx.author.id}]")
        webhook = discord.SyncWebhook.from_url(webhook_badge_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Title Given Logs", avatar_url=self.bot.user.avatar.url)
                          
    @title.command(name="remove", aliases=["r"], description="Removes the title from user")
    async def title_remove(self, ctx, member: discord.User):
        ls = workowner
        if ctx.author.id not in ls and ctx.author.id not in self.bot.owner_ids:
            return
        result = database.fetchone("*", "titles", "user_id", member.id)
        if result is not None:
            database.delete("titles", "user_id", member.id)
        else:
            return await ctx.reply(f"{str(member)} don't have any title")
        await ctx.reply(f"Removed Title from {str(member)}")
        em = discord.Embed(description=f"Title was removed from {member.mention} [{member.id}] by {ctx.author.mention} [{ctx.author.id}]")
        webhook = discord.SyncWebhook.from_url(webhook_badge_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Title Removed Logs", avatar_url=self.bot.user.avatar.url)
        
    @commands.group(
        invoke_without_command=True, description="Shows the help menu for top"
    )
    async def bottop(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        ls = ["top", "top commands", "top users"]
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
         
    @bottop.command(name="users", aliases=["user"], description="Shows the top users of the bot")
    async def _user(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        count_db = database.fetchone("*", "count", "xd", 1)
        user = literal_eval(count_db['user_count'])
        #ls1 = {k: v for k, v in reversed(sorted(user.items(), key=lambda item: item[1]))}
        ls1 = user.copy()
        count = 0
        ls2 = []
        ls = []
        c = 0
        for i in ls1:
            c+=1
        cc = 0
        for i in ls1:
            cc+=ls1[i]
        for i in ls1:
            u = await self.bot.fetch_user(i)
            if u is None or u.id in workowner:
                pass
            else:
                count+=1
                ls2.append(f"`[{'0' + str(count) if count < 10 else count}]` | {str(u)} - {ls1[i]} Commands Runned")
                if count == 10:
                    break
        for i in range(0, len(ls2), 10):
           ls.append(ls2[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Top {count} Users of the Bot"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           embed.set_author(name=f"Total users - {c} with {cc} commands runned", icon_url=ctx.author.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    #@bottop.command(name="guilds", aliases=["guild", "servers", "server"], description="Shows the top guilds of the bot")
    async def _guild(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        count_db = database.fetchone("*", "count", "xd", 1)
        user = literal_eval(count_db['guild_count'])
        #ls1 = {k: v for k, v in reversed(sorted(user.items(), key=lambda item: item[1]))}
        ls1 = user.copy()
        count = 0
        ls2 = []
        ls = []
        for i in ls1:
            if i == 1036594185442177055:
                continue
            count+=1
            u = discord.utils.get(self.bot.guilds, id=i)
            if u is None:
                count-=1
                continue
            else:
                ls2.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.name} - {ls1[i]} Commands Runned")
                if count == 10:
                    break
        for i in range(0, len(ls2), 10):
           ls.append(ls2[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Top {count} Guilds of the Bot"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @bottop.command(name="commands", aliases=["command", "cmd", "cmds"], description="Shows the top commands of the bot")
    async def _commands(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        count_db = database.fetchone("*", "count", "xd", 1)
        user = literal_eval(count_db['cmd_count'])
        #ls1 = {k: v for k, v in reversed(sorted(user.items(), key=lambda item: item[1]))}
        ls1 = user.copy()
        count = 0
        ls2 = []
        ls = []
        c = 0
        for i in ls1:
            c+=ls1[i]
        for i in ls1:
            count+=1
            ls2.append(f"`[{'0' + str(count) if count < 10 else count}]` | {i} - {ls1[i]} Times Runned")
            if count == 10:
                break
        for i in range(0, len(ls2), 10):
           ls.append(ls2[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Top {count} Commands of the Bot"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           embed.set_author(name=f"Total commands runned - {c}", icon_url=ctx.author.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
    
    #@commands.command()
    @commands.is_owner()
    async def dailygrowth(self, ctx):
        no_em = discord.Embed(description=f"Till now there is no daily growth.", color=botinfo.root_color)
        d_db = database.fetchone("*", "daily", "id", self.bot.user.id)
        if d_db is None:
            return await ctx.reply(embed=no_em)
        else:
            count = 0
            for g in self.bot.guilds:
                count += len(g.members)
            em = discord.Embed(description=f"Today's Growth in Guilds: {d_db['guild']} Guilds\nToday's Growth in Users: {d_db['user']} Users\nTotal Guilds: {len(self.bot.guilds)} Guilds\nTotal Users: {count} Users", color=botinfo.root_color)
            return await ctx.reply(embed=em)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, id):
        if not id.isdigit():
            if id.lower() != "all":
                await ctx.reply(f"Either pass a shard id or type 'all'")
            else:
                for iid, shard in self.bot.shards.items():
                    await ctx.reply(f"Reloding Shard {iid}")
                    await shard.reconnect()
        else:
            sh = self.bot.get_shard(int(id))
            if sh is None:
                await ctx.reply(f"Either pass a shard id or type 'all'")
            else:
                await ctx.reply(f"Reloding Shard {id}")
                await sh.reconnect()

    @commands.command()
    async def shards(self, ctx):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        ls = []
        for id, shard in self.bot.shards.items():
            c = 0
            cc = 0
            for guild in self.bot.guilds:
                if guild.shard_id == id:
                    if wavelink.Pool.get_node().get_player(guild.id):
                        c += 1
                        if wavelink.Pool.get_node().get_player(guild.id).playing:
                            cc += 1
            em = discord.Embed(color=botinfo.root_color)
            em.title = "Shards information"
            em.set_footer(text=str(self.bot.user), icon_url=self.bot.user.display_avatar.url)
            em.description = (f"Shard ID: {id}\nLatency: {round(shard.latency * 1000)} ms\nStatus: {not shard.is_closed()}\nGuilds: {sum(1 for guild in self.bot.guilds if guild.shard_id == id)}\nGuilds Unavailable: {sum(1 for guild in self.bot.guilds if guild.unavailable)}\nUsers: {sum(len(guild.members) for guild in self.bot.guilds if guild.shard_id == id)}\nPlayers: {cc}/{c}")
            ls.append(em)
        page = PaginationView(embed_list=ls, ctx=ctx)
        await page.start(ctx)
        
    @commands.group(invoke_without_command=True, aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        pass

    @blacklist.group(invoke_without_command=True)
    @commands.is_owner()
    async def user(self, ctx:commands.Context):
        pass

    @user.command()
    @commands.is_owner()
    async def add(self, ctx, user:discord.User,*, reason=None):
        ls = self.bot.owner_ids
        if user.id in ls:
            if ctx.author.id == self.bot.main_owner.id:
                pass
            else:
                await ctx.send(f"{str(user)} is Your Daddy")
                return
        _db = database.fetchone("*", "bl", "main", 1)
        bl_db = literal_eval(_db["user_ids"])
        if user.id in bl_db:
            return await ctx.send(f"{str(user)} is already blacklisted")
        else:
            bl_db.append(user.id)
            database.update("bl", "user_ids", f"{bl_db}", "main", 1)
            if reason:
                try:
                    await user.send(f"You are blacklisted from using {self.bot.user.name} for {reason}")
                except:
                    pass
                await ctx.send(f"{str(user)} is added to blacklisted users for {reason}")
            else:
                try:
                    await user.send(f"You are blacklisted from using {self.bot.user.name}")
                except:
                    pass
                await ctx.send(f"{str(user)} is added to blacklisted users")
            webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
            webhook.send(embed=discord.Embed(title="User Blacklisted", description=f"User Name: {user.name} - {user.mention}\nUser Id: {user.id}\nReason: {reason or 'None'}\nBlacklisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Blacklisted User Logs", avatar_url=self.bot.user.avatar.url)

    @user.command()
    @commands.is_owner()
    async def remove(self, ctx,*, user:discord.User):
            _db = database.fetchone("*", "bl", "main", 1)
            bl_db = literal_eval(_db["user_ids"])
            if user.id not in bl_db:
                return await ctx.send(f"{str(user)} is already whitelisted")
            else:
                bl_db.remove(user.id)
                database.update("bl", "user_ids", f"{bl_db}", "main", 1)
                try:
                    await user.send(f"You are allowed to use the bot now")
                except:
                    pass
                webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
                webhook.send(embed=discord.Embed(title="User Whitelisted", description=f"User Name: {user.name} - {user.mention}\nUser Id: {user.id}\nWhitelisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Whitelisted User Logs", avatar_url=self.bot.user.avatar.url)
                return await ctx.send(f"{str(user)} is removed from blacklisted users")
    
    @user.command()
    async def show(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
            return await ctx.send("Only Bot Dev Can Run This Command")
        _db = database.fetchone("*", "bl", "main", 1)
        mem, ls = [], []
        count = 0
        bl_db = literal_eval(_db["user_ids"])
        if len(bl_db) == 0:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Blacklisted users - 0"
            embed.description = "No Blacklisted users"
            embed.set_footer(text=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        for i in bl_db:
            u = discord.utils.get(self.bot.users, id=i)
            if u is None:
                continue
            count+=1
            mem.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.mention} `[{u.id}]`")
        for i in range(0, len(mem), 10):
           ls.append(mem[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Blacklisted users - {count}"
            embed.description = "\n".join(k)
            embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)
    
    @blacklist.group(invoke_without_command=True, aliases=["guild"])
    @commands.is_owner()
    async def server(self, ctx:commands.Context):
        pass

    @server.command(name="add")
    @commands.is_owner()
    async def addd(self, ctx:commands.Context, *, guild: Union[discord.Guild, str]):
        if isinstance(guild, discord.Guild):
            _db = database.fetchone("*", "bl_guilds", "main", 1)
            bl_db = literal_eval(_db["guild_ids"])
            if guild.id in bl_db:
                return await ctx.send(f"{str(guild)} is already a blacklisted guild.")
            else:
                bl_db.append(guild.id)
                database.update("bl_guilds", "guild_ids", f"{bl_db}", "main", 1)
                webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
                webhook.send(embed=discord.Embed(title="Guild Blacklisted", description=f"Guild Name: {ctx.guild.name}\nGuild Id: {ctx.guild.id}\nGuild Members: {ctx.guild.member_count}\nBlacklisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Blacklist Guild Logs", avatar_url=self.bot.user.avatar.url)
                return await ctx.send(f"{str(guild)} is added to blacklisted guild.")
        else:
            _db = database.fetchone("*", "bl_guilds", "main", 1)
            bl_db = literal_eval(_db["guild_names"])
            if guild.lower() in bl_db:
                return await ctx.send(f"'{str(guild)}' is already a blacklisted guild.")
            else:
                bl_db.append(guild.lower())
                database.update("bl_guilds", "guild_names", f"{bl_db}", "main", 1)
                webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
                webhook.send(embed=discord.Embed(title="Guild Blacklisted", description=f"Guild containing: '{ctx.guild.name}'\nBlacklisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Blacklist Guild Logs", avatar_url=self.bot.user.avatar.url)
                return await ctx.send(f"'{str(guild)}' is added to blacklisted guild.")

    @server.command(name="remove")
    @commands.is_owner()
    async def removee(self, ctx:commands.Context, *, guild: Union[discord.Guild, str]):
        if isinstance(guild, discord.Guild):
            _db = database.fetchone("*", "bl_guilds", "main", 1)
            bl_db = literal_eval(_db["guild_ids"])
            if guild.id not in bl_db:
                return await ctx.send(f"{str(guild)} is not a blacklisted guild.")
            else:
                bl_db.remove(guild.id)
                database.update("bl_guilds", "guild_ids", f"{bl_db}", "main", 1)
                webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
                webhook.send(embed=discord.Embed(title="Guild Whitelisted", description=f"Guild Name: {ctx.guild.name}\nGuild Id: {ctx.guild.id}\nGuild Members: {ctx.guild.member_count}\nWhitelisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Whitelisted Guild Logs", avatar_url=self.bot.user.avatar.url)
                return await ctx.send(f"{str(guild)} is removed from blacklisted guild.")
        else:
            _db = database.fetchone("*", "bl_guilds", "main", 1)
            bl_db = literal_eval(_db["guild_names"])
            if guild.lower() not in bl_db:
                return await ctx.send(f"'{str(guild)}' is not a blacklisted guild.")
            else:
                bl_db.append(guild.lower())
                database.update("bl_guilds", "guild_names", f"{bl_db}", "main", 1)
                webhook = discord.SyncWebhook.from_url(botinfo.webhook_blacklist_logs)
                webhook.send(embed=discord.Embed(title="Guild Whitelisted", description=f"Guild containing: '{ctx.guild.name}'\nWhitelisted by: {ctx.author.name} - {ctx.author.mention} [{ctx.author.id}]", color=botinfo.root_color), username=f"{str(self.bot.user)} | Whitelisted Guild Logs", avatar_url=self.bot.user.avatar.url)
                return await ctx.send(f"'{str(guild)}' is removed from blacklisted guild.")
    
    @server.command(name="show")
    async def shows(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
            return await ctx.send("Only Bot Dev Can Run This Command")
        _db = database.fetchone("*", "bl_guilds", "main", 1)
        mem, ls = [], []
        count = 0
        bl_db = literal_eval(_db["guild_ids"])
        bl_db1 = literal_eval(_db["guild_names"])
        if len(bl_db) == 0 and len(bl_db1) == 0:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Blacklisted Guilds - 0"
            embed.description = "No Blacklisted Guilds"
            embed.set_footer(text=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        for i in bl_db:
            u = discord.utils.get(self.bot.guilds, id=i)
            if u is None:
                continue
            count+=1
            mem.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.name} `[{u.id}]`")
        for i in bl_db1:
            count+=1
            mem.append(f"`[{'0' + str(count) if count < 10 else count}]` | {i}")
        for i in range(0, len(mem), 10):
           ls.append(mem[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Blacklisted users - {count}"
            embed.description = "\n".join(k)
            embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @commands.command(description="To get the list of all running giveaways in all the server")
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True)
    async def galist(self, ctx: commands.Context):
        gw_db = database.fetchall1("*", "gwmain")
        em_no = discord.Embed(description="No Giveaway is presently running in any of the server!", color=botinfo.root_color)
        em_no.set_footer(text=f"{self.bot.user.name} Giveaway", icon_url=self.bot.user.avatar.url)
        if gw_db is None:
            return await ctx.send(embed=em_no)
        xd = {}
        for i, j in gw_db:
            x = literal_eval(j)
            for f in x:
                xd[f] = x[f]
        xdd = xd.copy()
        for i in xd:
            if not xd[i]['status']:
                del xdd[i]
        if len(xdd) == 0:
            return await ctx.send(embed=em_no)
        xddd = {}
        for i in xdd:
            xddd[xdd[i]['end_time']] = xdd[i]
        ls, count=[],1
        des = []
        for j in sorted(xddd):
            try:
                channel = self.bot.get_channel(xddd[j]['channel_id'])
                g_msg = await channel.fetch_message(int(xddd[j]['g_id']))
            except:
                continue
            des.append(f"`[{'0' + str(count) if count < 10 else count}]` | {xddd[j]['prize']} - [[{xddd[j]['g_id']}]({g_msg.jump_url})] | Server name: `{channel.guild.name}` Ends at: <t:{round(j)}:R>")
            count+=1
        if len(des) == 0:
            return await ctx.send(embed=em_no)
        for i in range(0, len(des), 10):
           ls.append(des[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Giveaways presently running in all the servers - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        xd = {}
        for ser in self.bot.guilds:
            xd[ser.id] = len(ser.members)
        ls = []
        server = []
        count = 1
        xd = {k: v for k, v in sorted(xd.items(), key=lambda item: item[1])}
        for ser in xd:
            s = discord.utils.get(self.bot.guilds, id=ser)
            server.append(f"[{count}] | {s.name} `[{s.id}]` - {len(s.members)} Members")
            count +=1
        for i in range(0, len(server), 10):
            ls.append(server[i: i + 10])
        em_list=[]
        for k in ls:
            em = discord.Embed(title=f"SERVERS OF {self.bot.user.name.upper()} - {count - 1}", description="\n".join(k),color=botinfo.root_color)
            em.set_footer(text=f"{self.bot.user.name.upper()}")
            em_list.append(em)
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)
    
    @commands.command()
    async def listening(self, ctx, status, *, activity):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        xd = ['online', 'idle', 'dnd', 'invisible']
        if status.lower() not in xd:
            return await ctx.reply("Please send a valid status\nOptions are: Online, idle, dnd, invisible")
        if status.lower() == 'online':
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{activity}"))
        if status.lower() == 'idle':
            await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{activity}"))
        if status.lower() == 'dnd':
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{activity}"))
        if status.lower() == 'invisible':
            await self.bot.change_presence(status=discord.Status.offline, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{activity}"))
        await ctx.reply("Changed the bot's Status")
    
    @commands.command()
    @commands.is_owner()
    async def getinvite(self, ctx, *,guild_id: int):
        xd = discord.utils.get(self.bot.guilds, id=guild_id)
        if xd is None:
            return await ctx.reply(f"Not a valid guild id")
        for channel in xd.channels:
            try:
                inv = await channel.create_invite()
                return await ctx.reply(str(inv))
            except:
                pass
                                    
    @commands.command()
    @commands.is_owner()
    async def gleave(self, ctx, *,guild_id: int):
        if ctx.author.id not in main_devs:
          return await ctx.send("Only Bot Dev Can Run This Command")
        xd = discord.utils.get(self.bot.guilds, id=guild_id)
        if xd is None:
            return await ctx.reply(f"Not a valid guild id")
        await xd.leave()
        await ctx.reply(f"I left {xd.name}")

    @commands.command()
    async def say(self, ctx, channel: discord.TextChannel = None, *,msg):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        if '@everyone' in msg:
            eme = discord.Embed(description=f"You can't Mention everyone", color=botinfo.root_color)
            return await ctx.send(embed=eme)
        if '@here' in msg:
            eme = discord.Embed(description=f"You can't Mention here", color=botinfo.root_color)
            return await ctx.send(embed=eme)
        if '<@&' in msg:
            eme = discord.Embed(description=f"You can't Mention role", color=botinfo.root_color)
            return await ctx.send(embed=eme)
        if '%' in msg:
            message = msg.replace('%','@')
            return await channel.send(message)
        await channel.send(msg)

    @commands.command()
    async def dm(self, ctx, user: discord.User, *, message: str):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")
        
    @commands.command()
    async def emsay(self, ctx, channel:discord.TextChannel=None, *,msg):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        await channel.send(embed=discord.Embed(description=msg, color=botinfo.root_color))

    @commands.command(aliases=['asi'])
    async def anyserverinfo(self, ctx, guild: discord.Guild):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        guild_roles = len(guild.roles)
        guild_members = len(guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        channels = text_channels + voice_channels
        pfp = ctx.author.display_avatar.url
        serverinfo = discord.Embed(colour=botinfo.root_color, title="Guild Information")
        serverinfo.add_field(name="General Information:",
                             value=f"Name: **{guild.name}**\n"
                                   f"ID: {guild.id}\n"
                                   f"Owner: {str(guild.owner)} ({guild.owner.mention})\n"
                                   f"Creation: <t:{round(guild.created_at.timestamp())}:R>\n"
                                   f"Total Member: {guild_members}\n"
                                   f"Roles: {guild_roles}\n"
                                   f"Channel: {channels}\n"
                                   f"Text Channel: {text_channels}\n"
                                   f"Voice Channel: {voice_channels}", inline=False)
        if guild.icon is not None:
            serverinfo.set_thumbnail(url=guild.icon.url)
            serverinfo.add_field(name="**SERVER ICON:**", value=f"[Icon]({guild.icon.url})", inline=False)
        if guild.banner is not None:
            serverinfo.set_image(url=guild.banner.url)
        serverinfo.set_footer(text=f"Requested by {ctx.author.name}" ,  icon_url=pfp)
        await ctx.send(embed=serverinfo)

    @commands.command(aliases=["ao"])
    @commands.is_owner()
    async def addowner(self, ctx, user: discord.Member):
        if ctx.author.id not in self.bot.owner_ids:
            return await ctx.send("Only Bot Dev Can Run This Command")
        if user.id in workowner:
            return await ctx.send(f"{str(user)} is already A Owner")
        workowner.append(user.id)
        await ctx.send(f"I added {user.mention} To Owner list")

    @commands.command(aliases=["ro"])
    @commands.is_owner()
    async def removeowner(self, ctx, user: discord.Member):
        if ctx.author.id not in self.bot.owner_ids:
            return await ctx.send("Only Bot Dev Can Run This Command")
        if user.id not in workowner:
            return await ctx.send(f"{str(user)} is Not A Owner")
        workowner.remove(user.id)
        await ctx.send(f"I removed {user.mention} From Owner list")

    @commands.command(description="List Of Bot's Owners",aliases=["lo",'ownerlist'])
    @commands.guild_only()
    @commands.is_owner()
    async def listowner(self, ctx):
        embed = discord.Embed(color=ctx.guild.me.color)
        st, count = "", 1
        for member in self.bot.owner_ids:
            ok = discord.utils.get(self.bot.users, id=member)
            st += f"[{'0' + str(count) if count < 10 else count}] | {str(ok)} [{ok.mention}]\n"
            test = count
            count += 1
        embed.title = f"Owners - {test}"
        embed.description = st
        await ctx.send(embed=embed)

    @commands.command(description="List Of Bot's Work Owners",aliases=["lwo",'workownerlist'])
    @commands.guild_only()
    @commands.is_owner()
    async def listworkowner(self, ctx):
        embed = discord.Embed(color=ctx.guild.me.color)
        st, count = "", 1
        for member in workowner:
            ok = discord.utils.get(self.bot.users, id=member)
            st += f"[{'0' + str(count) if count < 10 else count}] | {str(ok)} [{ok.mention}]\n"
            test = count
            count += 1
        embed.title = f"Work Owners - {test}"
        embed.description = st
        await ctx.send(embed=embed)

    @commands.command()
    async def backup(self, ctx: commands.Context):
        if ctx.author.id not in workowner:
          return await ctx.send("Only Bot Dev Can Run This Command")
        database = []
        for filename in os.listdir():
            if filename.endswith('.sqlite3'):
                database.append(filename)
        g = discord.utils.get(self.bot.guilds, id=1036594185442177055)
        x = discord.utils.get(g.categories, id=1036621345905188894)
        for i in database:
            c=discord.utils.get(g.channels, name=f"{i[:-8]}")
            if c is None:
                c=await g.create_text_channel(name=f"{i[:-8]}", category=x)
                webhook = await c.create_webhook(name=f"{i[:-8]}")
            else:
                ls = await c.webhooks()
                if len(ls) == 0:
                    webhook = await c.create_webhook(name=f"{i[:-8]}")
                else:
                    webhook = ls[0]
            with open(i, 'rb') as f:
                await webhook.send(f"Instant backup by {str(ctx.author)} - {ctx.author.id}\nTime for backup - {datetime.datetime.now()}", file=discord.File(BytesIO(f.read()), i), username=f"{str(self.bot.user)} | {i[:-8]} Backup", avatar_url=self.bot.user.avatar.url)
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(owner(bot))
