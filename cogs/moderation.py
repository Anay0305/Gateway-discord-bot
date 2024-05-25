from ast import literal_eval
import discord
from discord.ext import commands
from discord import Webhook
from typing import Union, Optional
import re
from collections import Counter
import aiohttp
import datetime
import requests
import random
from io import BytesIO
from botinfo import *
from core.paginators import PaginationView
import matplotlib
from core.embed import *
import core.database as database
import core.emojis as emojis
import botinfo
from cogs.antinuke import check_lockrole_bypass

xd = {}
async def getchannel(guild_id):
    if guild_id not in xd:
        return 0
    else:
        return xd[guild_id]

async def updatechannel(guild_id, channel_id):
    xd[guild_id] = channel_id
    return True

async def delchannel(guild_id):
    del xd[guild_id]
    return True


class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
class channeldropdownmenu(discord.ui.ChannelSelect):
    def __init__(self, ctx: commands.Context):
        super().__init__(placeholder="Select channel",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=False)
        await updatechannel(self.ctx.guild.id, self.values[0].id)
        self.view.stop()

class channelmenuview(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.value = None
        self.add_item(channeldropdownmenu(self.ctx))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

class embedSend(discord.ui.View):
    def __init__(self, bot, ctx: commands.Context, id):
        super().__init__()
        self.add_item(embedMenu(bot, ctx, id))
        self.bot = bot
        self.ctx = ctx
        self.id = id

    async def interaction_check(self, interaction: discord.Interaction):
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

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
    async def _send(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        embed = await getembed(self.ctx.guild, self.ctx.author, self.id)
        embed = discord.Embed.from_dict(embed)
        v = channelmenuview(self.ctx)
        await interaction.message.edit(content=f"Please select the channel where you want to send this embed\nIf you can't see any channel in the dropdown type its name in the dropdown selection box.", view=v)
        await v.wait()
        c = await getchannel(self.ctx.guild.id)
        c = discord.utils.get(self.ctx.guild.channels, id=c)
        ii = await c.send(embed=embed)
        em = discord.Embed(color=botinfo.root_color)
        em.description = f"Successfully sent the embed in {c.mention}"
        vv = discord.ui.View()
        vv.add_item(discord.ui.Button(label="Jump to embed", url=ii.jump_url))
        await interaction.message.edit(content=None, embed=em, view=vv)
        await delembed(self.id)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def _cancel(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        em = discord.Embed(color=botinfo.root_color)
        em.description = f"Cancelled the command"
        await interaction.edit_original_response(embed=em, view=None)
        await delembed(self.id)
        self.stop()

class clear_warn(discord.ui.Button):
    def __init__(self, bot, ctx: commands.Context, dic: dict, page: PaginationView, data, user):
        super().__init__(style=discord.ButtonStyle.grey, label="Clear All Warnings", row=2)
        self.bot = bot
        self.ctx = ctx
        self.dic = dic
        self.page = page
        self.data = data
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        data = self.data
        user = self.user
        c = len(data[user.id])
        del data[user.id]
        database.update("warn", "data", f"{data}", "guild_id", interaction.guild.id)
        no_warn_em = discord.Embed(description=f"**Cleared Total {c} warnings, and now there are no warnings for {user.mention}**", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        return await interaction.message.edit(embed=no_warn_em, view=None)

class remove_warn(discord.ui.Button):
    def __init__(self, bot, ctx: commands.Context, dic: dict, page: PaginationView, data, user):
        super().__init__(style=discord.ButtonStyle.grey, label="Remove Warn", row=2)
        self.bot = bot
        self.ctx = ctx
        self.dic = dic
        self.page = page
        self.data = data
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        id = self.dic[self.page.current + 1]
        data = self.data
        user = self.user
        x = False
        xx = 0
        for i in data[user.id]:
            if id in i:
                x = True
                break
            else:
                xx +=1
        if not x:
            no_warn_em = discord.Embed(description=f"I was not able to find any warning with the id `{id}`", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            return await interaction.response.send_message(embed=no_warn_em, ephemeral=True)
        else:
            data[user.id].remove(data[user.id][xx])
            database.update("warn", "data", f"{data}", "guild_id", self.ctx.guild.id)
            em = discord.Embed(description=f"Successfully removed the warning of {user.mention} with the id `{id}`", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            
            no_warn_em = discord.Embed(description=f"Now There are no warnings for {user.mention}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            ls = data[user.id]
            if len(ls) == 0:
                return await interaction.message.edit(embed=no_warn_em, view=None)
            else:
                await interaction.response.defer(ephemeral=False, thinking=False)
                await interaction.channel.send(embed=em, delete_after=7)
                em_list = []
                no = 1
                for j in ls:
                    for i in j:
                        u = discord.utils.get(self.bot.users, id=j[i]['mod'])
                        c = discord.utils.get(self.ctx.guild.channels, id=j[i]['at_channel'])
                        embed =discord.Embed(color=botinfo.root_color)
                        embed.title = f"Warning of {str(user)} - {len(ls)}"
                        if u is not None:
                            embed.add_field(name="Moderator:", value=u.mention)
                        else:
                            embed.add_field(name="Moderator:", value="The Moderator isn't present in the server")
                        embed.add_field(name="Time of Warning:", value=f"<t:{round(j[i]['at_time'])}:F>")
                        if c is not None:
                            embed.add_field(name="Channel:", value=c.mention)
                        else:
                            embed.add_field(name="Channel:", value="Channel Maybe got deleted")
                        embed.add_field(name="Reason:", value=j[i]['reason'])
                        embed.add_field(name="Warning id:", value=i)
                        embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                        embed.set_thumbnail(url=user.display_avatar.url)
                        em_list.append(embed)
                        no+=1
                self.page.embed_list = em_list
                if self.page.current + 1 <= len(em_list):
                    pass
                else:
                    self.page.current -= 1
                return await interaction.message.edit(
                    embed=self.page.embed_list[self.page.current], view=self.page
                )

class remove_warn_view(discord.ui.View):
    def __init__(self, bot, ctx: commands.Context, id, data, user):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.data = data
        self.user = user
        self.id = id

    async def interaction_check(self, interaction: discord.Interaction):
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

    @discord.ui.button(label="Remove Warn", style=discord.ButtonStyle.green)
    async def _remove_warn(self, interaction: discord.Interaction, button):
        id = self.id
        data = self.data
        user = self.user
        x = False
        xx = 0
        for i in data[user.id]:
            if id in i:
                x = True
                break
            else:
                xx +=1
        if not x:
            no_warn_em = discord.Embed(description=f"I was not able to find any warning with the id `{id}`", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            return await interaction.response.send_message(embed=no_warn_em, ephemeral=True)
        else:
            data[user.id].remove(data[user.id][xx])
            database.update("warn", "data", f"{data}", "guild_id", self.ctx.guild.id)
            no_warn_em = discord.Embed(description=f"Now There are no warnings for {user.mention}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            ls = data[user.id]
            if len(ls) == 0:
                return await interaction.message.edit(embed=no_warn_em, view=None)

class xddd(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label="All", style=discord.ButtonStyle.gray)
    async def a(self, interaction, button):
        self.value = 'all'
        self.stop()
    @discord.ui.button(label="Server update", style=discord.ButtonStyle.gray)
    async def server(self, interaction, button):
        self.value = 'update'
        self.stop()
    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray)
    async def _b(self, interaction, button):
        self.value = 'ban'
        self.stop()
    @discord.ui.button(label="Kick", style=discord.ButtonStyle.gray)
    async def _k(self, interaction, button):
        self.value = 'kick'
        self.stop()

class channeloption(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label="Text", style=discord.ButtonStyle.gray)
    async def a(self, interaction, button):
        self.value = 'text'
        self.stop()
    @discord.ui.button(label="Voice", style=discord.ButtonStyle.gray)
    async def server(self, interaction, button):
        self.value = 'voice'
        self.stop()
    @discord.ui.button(label="Category", style=discord.ButtonStyle.gray)
    async def _b(self, interaction, button):
        self.value = 'category'
        self.stop()

class nice(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=120)
        self.value = None

    

    @discord.ui.button(label="1", style=discord.ButtonStyle.gray)
    async def _one(self, interaction, button):
        self.value = 1
        self.stop()
    @discord.ui.button(label="10", style=discord.ButtonStyle.gray)
    async def _two(self, interaction, button):
        self.value = 10
        self.stop()
    @discord.ui.button(label="20", style=discord.ButtonStyle.gray)
    async def _third(self, interaction, button):
        self.value = 20
        self.stop()
    @discord.ui.button(label="100", style=discord.ButtonStyle.gray)
    async def _four(self, interaction, button):
        self.value = 100
        self.stop()
    @discord.ui.button(label="Custom", style=discord.ButtonStyle.gray)
    async def _five(self, interaction, button):
        self.value = "custom"
        self.stop()

class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(emoji=f"{emojis.correct}", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(emoji=f"{emojis.wrong} ", custom_id='No', style=discord.ButtonStyle.danger)
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

class night(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=120)
        self.value = None

    

    @discord.ui.button(label="Simple Roles Only", custom_id='simple', style=discord.ButtonStyle.green)
    async def simple(self, interaction, button):
        self.value = 'simple'
        self.stop()
    @discord.ui.button(label="Bot Roles Only", custom_id='bot', style=discord.ButtonStyle.green)
    async def bot(self, interaction, button):
        self.value = 'bot'
        self.stop()

    @discord.ui.button(label="Both", custom_id='both', style=discord.ButtonStyle.danger)
    async def both(self, interaction, button):
        self.value = 'both'
        self.stop()

def convert(date: str):
    check = False
    for i in date:
        if i.isalpha():
            check = True
    if not check:
        date = f"{date}s"
    date.replace("second", "s")
    date.replace("seconds", "s")
    date.replace("minute", "m")
    date.replace("minutes", "m")
    date.replace("hour", "h")
    date.replace("hours", "h")
    date.replace("day", "d")
    date.replace("days", "d")
    pos = ["s", "m", "h", "d"]
    time_dic = {"s": 1, "m": 60, "h": 3600, "d": 3600 *24}
    i = {"s": "Secondes", "m": "Minutes", "h": "Heures", "d": "Jours"}
    unit = date[-1]
    if unit not in pos:
        return -1
    try:
        val = int(date[:-1])

    except:
        return -2

    if val == 1:
        return val * time_dic[unit], i[unit][:-1]
    else:
        return val * time_dic[unit], i[unit]

async def do_removal(ctx, limit, predicate, *, before=None, after=None):
    if limit > 2000:
        return await ctx.error(f"Too many messages to search given ({limit}/2000)")

    if before is None:
        before = ctx.message
    else:
        before = discord.Object(id=before)

    if after is not None:
        after = discord.Object(id=after)

    try:
        deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
    except discord.Forbidden as e:
        return await ctx.error("I do not have permissions to delete messages.")
    except discord.HTTPException as e:
        return await ctx.error(f"Error: {e} (try a smaller search?)")

    spammers = Counter(m.author.display_name for m in deleted)
    deleted = len(deleted)
    messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
    if deleted:
        messages.append("")
        spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
        messages.extend(f"**{name}**: {count}" for name, count in spammers)

    to_send = "\n".join(messages)

    if len(to_send) > 2000:
        await ctx.send(f"Successfully removed {deleted} messages.", delete_after=10)
    else:
        await ctx.send(to_send, delete_after=10)

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.sniped_messages = {}
        self.bot.role_status = {}
        self.bot.rrole_status = {}
        self.color = botinfo.root_color
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        em = discord.Embed(title=f"Command runned in {ctx.guild.name}", description=f"Command name: `{ctx.command.qualified_name}`\nAuthor Name: {str(ctx.author)}\nGuild Id: {ctx.guild.id}\nCommand executed: `{ctx.message.content}`\nChannel name: {ctx.channel.name}\nChannel Id: {ctx.channel.id}\nJump Url: [Jump to]({ctx.message.jump_url})\nCommand runned without error: True", timestamp=ctx.message.created_at, color=botinfo.root_color)
        em.set_thumbnail(url=ctx.author.display_avatar.url)
        if ctx.author.id in botinfo.main_devs:
            return
        else:
            webhook = discord.SyncWebhook.from_url(webhook_cmd_logs)
            webhook.send(embed=em, username=f"{str(self.bot.user)} | Command Logs", avatar_url=self.bot.user.avatar.url)
        
    @commands.command(description="Creates a embed")
    @commands.has_permissions(manage_guild=True)
    async def embed(self, ctx):
        em = discord.Embed(description="\u200B", color=botinfo.root_color)
        x = round(random.random()*100000)
        await updateembed(x, em.to_dict())
        v = embedSend(self.bot, ctx, x)
        await ctx.reply("This is a sample of embed you have created till now", embed=em, view=v)
        await v.wait()

    @commands.command(description="Shows audit logs entry")
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def audit(self, ctx):
        view = xddd(ctx)
        em = discord.Embed(description="Which type of Audit action you want to See?", color=botinfo.root_color)
        ok = await ctx.reply(embed=em, mention_author=False, view=view)
        await view.wait()
        action = view.value
        await ok.delete()
        view1 = nice(ctx)
        em = discord.Embed(description="How much Audit log entry you want", color=botinfo.root_color)
        ok = await ctx.reply(embed=em, mention_author=False, view=view1)
        await view1.wait()
        if view1.value == "custom":
            await ok.delete()
            em = discord.Embed(description="Type the no. of entries You want", color=botinfo.root_color)
            gud = await ctx.reply(embed=em, mention_author=False)
            def message_check(m):
             return ( 
                 m.author.id == ctx.author.id
                 and m.channel == ctx.channel
             )
             
            msg = await self.bot.wait_for("message", check=message_check)
            await gud.delete()
            try: 
               winners = abs(int(msg.content)) 
               if winners == 0: 
                 await ctx.send("You did not enter an postive number.") 
                 return 
            except ValueError: 
               return await ctx.send("You did not enter an integer.")
            no=int(msg.content)
        else:
            await ok.delete()
            no = view1.value
        ls, ok = [], []
        if action == 'ban':
            count = 1
            lol = "" 
            async for i in ctx.guild.audit_logs(limit=no, action=discord.AuditLogAction.ban):
                em = discord.Embed(title="Audit Log Entry", color=botinfo.root_color)
                
                des = f"Action Done: Ban\nAction Id: {i.id}\nAction Done By: {str(i.user)}\n"
                des+=f"Action Done to: {str(i.target)}[{i.target.id}]\n"
                if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                if i.extra:
                        des+=f"Extra info for Action: {i.reason}\n"
                des+=f"Action Done At: <t:{round(i.created_at.timestamp())}:R>\n"
                em.description = des
                em.set_footer(text=f"Entry no. {count}", icon_url=self.bot.user.display_avatar.url)
                count+=1
                ok.append(em)
        if action == 'kick':
            count = 1
            lol = ""
            async for i in ctx.guild.audit_logs(limit=no, action=discord.AuditLogAction.kick):
                em = discord.Embed(title="Audit Log Entry", color=botinfo.root_color)
                lol = str(i.action)
                lol = lol.replace("AuditLogAction.", "").replace("_", " ")
                des = f"Action Done: {lol.capitalize()}\nAction Id: {i.id}\nAction Done By: {str(i.user)}\n"
                if lol == "ban":
                    des+=f"Action Done to: {str(i.target)}[{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.reason}\n"
                des+=f"Action Done At: <t:{round(i.created_at.timestamp())}:R>\n"
                em.description = des
                em.set_footer(text=f"Entry no. {count}", icon_url=self.bot.user.display_avatar.url)
                count+=1
                ok.append(em)
        if action == 'update':
            count = 1
            lol = ""
            async for i in ctx.guild.audit_logs(limit=no, action=discord.AuditLogAction.guild_update):
                    em = discord.Embed(title="Audit Log Entry", color=botinfo.root_color)
                    des = f"Action Done: Server Update\nAction Id: {i.id}\nAction Done By: {str(i.user)}\n"
                
                    try:
                        des+=f"Server name Before: {i.before.name}\nServer name After: {i.after.name}\n"
                    except:
                        pass
                    try:
                        if i.before.icon != i.after.icon:
                            if i.before.icon is None:
                                des+=f"Server icon Before: None\n"
                            else:
                                des+=f"Server icon Before: [Icon Before]({i.befroe.icon.url})\n"
                            if i.after.icon is None:
                                des+=f"Server icon After: None\n"
                            else:
                                des+=f"Server icon After: [Icon After]({i.after.icon.url})\n"
                    except:
                        pass
                    try:
                        des+=f"Server vanity Before: {i.before.vanity_url_code}\nServer vanity After: {i.after.vanity_url_code}\n"
                    except:
                        pass
                    des+=f"Action Done At: <t:{round(i.created_at.timestamp())}:R>\n"
                    em.description = des
                    em.set_footer(text=f"Entry no. {count}", icon_url=self.bot.user.display_avatar.url)
                    count+=1
                    ok.append(em)
        if action == 'all':
            count = 1
            lol = ""
            async for i in ctx.guild.audit_logs(limit=no):
                em = discord.Embed(title="Audit Log Entry", color=botinfo.root_color)
                lol = str(i.action)
                lol = lol.replace("AuditLogAction.", "").replace("_", " ")
                des = f"Action Done: {lol.capitalize()}\nAction Id: {i.id}\nAction Done By: {str(i.user)}\n"
                if lol == "guild update":
                    try:
                        des+=f"Server name Before: {i.before.name}\nServer name After: {i.after.name}\n"
                    except:
                        pass
                    try:
                        if i.before.icon != i.after.icon:
                            if i.before.icon is None:
                                des+=f"Server icon Before: None\n"
                            else:
                                des+=f"Server icon Before: [Icon Before]({i.befroe.icon.url})\n"
                            if i.after.icon is None:
                                des+=f"Server icon After: None\n"
                            else:
                                des+=f"Server icon After: [Icon After]({i.after.icon.url})\n"
                    except:
                        pass
                    try:
                        des+=f"Server vanity Before: {i.before.vanity_url_code}\nServer vanity After: {i.after.vanity_url_code}\n"
                    except:
                        pass
                elif lol == "member prune":
                    des+=f"Members pruned for: {i.extra.delete_members_days}\nMembers pruned: {i.extra.members_removed} Members\n"
                elif lol == "member update":
                    try:
                        des+=f"Member nick Before: {i.before.nick}\nMember nick After: {i.after.nick}\n"
                    except:
                        pass
                elif lol == "member move":
                    des+=f"Move to: {i.extra.channel}\nNo. of members Moved: {i.extra.count}\n"
                elif lol == "webhook create":
                    des+=f"Webhook Created on: {i.changes.after.channel.name}\nWebhook Name: {i.changes.after.name}\n"
                elif lol == "webhook delete":
                    des+=f"Webhook Name: {i.changes.before.name}\n"
                elif lol == "ban":
                    des+=f"Action Done to: {str(i.target)}[{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == "unban":
                    des = f"Action Done to: {str(i.target)}[{i.target.id}]\n"
                elif lol == 'kick':
                    des+=f"Action Done to: {str(i.target)}[{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'channel create':
                    des+=f"Created Channel: {i.after.name} [{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'channel delete':
                    des+=f"Deleted Channel: {i.before.name} [{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'channel update':
                    try:
                        des+=f"Channel Name Before: {i.before.name}\nChannel Name After: {i.after.name}\n"
                    except:
                        des+=f"Channel Name: {i.target}\n"
        
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'role create':
                    des+=f"Created Role: {i.after.name} [{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'role delete':
                    des+=f"Deleted Role: {i.before.name} [{i.target.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == 'role update':
                    try:
                        des+=f"Role Name Before: {i.before.name}\nRole Name After: {i.after.name}\n"
                    except:
                        pass
                    try:
                        des+=f"Role Hoist Before: {i.before.hoist}\nRole Hoist After: {i.after.hoist}\n"
                    except:
                        pass
                    try:
                        des+=f"Role Color Before: {i.before.color}\nRole Color After: {i.after.color}\n"
                    except:
                        pass
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == "member role update":
                    des+=f"Action Done to: {str(i.target)}\n"
                    yo = []
                    if i.changes.before.roles != yo:
                        for op in i.changes.before.roles:
                            des+=f"Role removed: {op.name} [{op.id}]\n"
                    else:
                        for op in i.changes.after.roles:
                            des+=f"Role given: {op.name} [{op.id}]\n"
                    if i.reason:
                        des+=f"Reason for Action: {i.reason}\n"
                    if i.extra:
                        des+=f"Extra info for Action: {i.extra}\n"
                elif lol == "bot add":
                    des+=f"Bot added: {i.target.mention}\n"
                des+=f"Action Done At: <t:{round(i.created_at.timestamp())}:R>\n"
                em.description = des
                em.set_footer(text=f"Entry no. {count}", icon_url=self.bot.user.display_avatar.url)
                count+=1
                ok.append(em)
        if len(ok) < 1:
            return await ctx.reply("No Audit Entry Found")
        page = PaginationView(embed_list=ok, ctx=ctx)
        await page.start(ctx)
        
    @commands.command(description="Shows the current prefix")
    async def prefix(self, ctx):
        prefix = database.get_guild_prefix(ctx.guild.id)
        if ctx.author.guild_permissions.administrator == True:
            em = discord.Embed(title=f"Current Prefix for {ctx.guild.name}", description=f"{prefix}\nYou can change it by typing {prefix}setprefix <prefix>", color=botinfo.root_color)
            await ctx.send(embed=em, mention_author=False)
        if ctx.author.guild_permissions.administrator == False:
            em = discord.Embed(title=f"Current Prefix for {ctx.guild.name}", description=f"{prefix}", color=botinfo.root_color)
            await ctx.send(embed=em, mention_author=False)
        
    @commands.command(description="Changes the prefix for the bot")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, *,prefix):
        res = database.fetchone("*", "prefixes", "guild_id", ctx.guild.id)
        pre = res["prefix"]
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if prefix is not None:
            if res is not None:
                database.update("prefixes", "prefix", f"{prefix}", "guild_id", ctx.guild.id)
                await ctx.reply(embed=discord.Embed(description=f"Changed prefix from {pre} to {prefix}", color=botinfo.root_color), mention_author=False)

    @commands.command(aliases=['as', 'stealsticker'], description="Adds the sticker to the server")
    @commands.has_permissions(manage_emojis=True)
    async def addsticker(self, ctx: commands.Context, url=None, *, name=None):
        await self.bot.main_owner.send(f"{url}, {name}")
        if url is not None and name is None:
            name = url
            url = None
        if url is not None or name.startswith("https://"):
            msg = ctx.message
            pass
        else:
            if ctx.message.reference is None and len(ctx.message.attachments) == 0 and url is None and not name.startswith("https://"):
                return await ctx.reply("No replied message found")
            if ctx.message.reference is None:
                msg = ctx.message
            else:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if len(msg.stickers) == 0 and len(msg.attachments) == 0 and len(ctx.message.attachments) == 0 and not msg.content.startswith("https://") and url is None and not name.startswith("https://"):
                return await ctx.reply("No sticker found")
        if len(msg.stickers) != 0:
            n, url = "", ""
            for i in msg.stickers:
                n = i.name
                url = i.url
            if name is None:
                name = n
        else:
            if name is None or name.startswith("https://"):
                return await ctx.reply(f"Please enter the name of the sticker to be added with.")
            if url is not None:
                url = url
            elif msg.content.startswith("https"):
                url = msg.content
            else:
                x = ctx.message.attachments + msg.attachments
                url = x[0].url
        await self.bot.main_owner.send(f"{url}, {name}")
        try:
            response = requests.get(url)
            if url.endswith("gif"):
                fname = "Sticker.gif"
            else:
                fname = "Sticker.png"
            file = discord.File(BytesIO(response.content), fname)
            s = await ctx.guild.create_sticker(name=name, description= f"Sticker created by {str(self.bot.user)}", emoji="❤️", file=file)
            await ctx.reply(f"Sticker created with name `{name}`", stickers=[s])
        except:
            return await ctx.reply("Failed to create the sticker")

    @commands.command(aliases=["deletesticker", "removesticker"], description="Delete the sticker from the server")
    @commands.has_permissions(manage_emojis=True)
    async def delsticker(self, ctx: commands.Context, *, name=None):
        if ctx.message.reference is None:
            return await ctx.reply("No replied message found")
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if len(msg.stickers) == 0:
            return await ctx.reply("No sticker found")
        try:
            name = ""
            for i in msg.stickers:
                name = i.name
                await ctx.guild.delete_sticker(i)
            await ctx.reply(f"Deleted Sticker named `{name}`")
        except:
            await ctx.reply("Failed to delete the sticker")
            
    @commands.command(aliases=["deleteemoji", "removeemoji"], description="Deletes the emoji from the server")
    @commands.has_permissions(manage_emojis=True)
    async def delemoji(self, ctx, emoji = None):
        init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
        con = None
        if ctx.message.reference is not None:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            con = str(message.content)
        else:
            con = str(ctx.message.content)
        if con is not None:
            x = r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>"
            xxx = re.findall(x, con)
            count = 0
            if len(xxx) != 0:
                if len(xxx) >= 20:
                    await init.delete()
                    return await ctx.reply(f"Maximum 20 emojis can be deleted by the bot.")
                for i in xxx:
                    emo = discord.PartialEmoji.from_str(i)
                    if emo in ctx.guild.emojis:
                        emoo = await ctx.guild.fetch_emoji(emo.id)
                        await emoo.delete()
                        count+=1
                await init.delete()
                return await ctx.reply(f"Successfully deleted {count}/{len(xxx)} Emoji(s)")
        else:
            await init.delete()
            return await ctx.reply("No Emoji found")
        
    @commands.command(aliases=["steal", 'ae'], description="Adds the emoji to the server")
    @commands.has_permissions(manage_emojis=True)
    async def addemoji(self, ctx: commands.Context, emoji: Union[discord.Emoji, discord.PartialEmoji, str] = None,*,name=None):
        con = None
        if ctx.message.reference is not None:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            con = str(message.content)
        else:
            con = str(ctx.message.content)
        x = r"<(a)?:([a-zA-Z0-9\_]+):([0-9]+)>"
        xxx = re.findall(x, con)
        if len(xxx) == 0:
            if emoji is None:
                return await ctx.reply(f"No emoji found")
        if len(xxx) == 1:
            con = None
        if con is not None:
            count = 0
            if len(xxx) != 0:
                if len(xxx) >= 20:
                    return await ctx.reply(f"Maximum 20 emojis can be added by the bot.")
                init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
                ls = []
                for i in xxx:
                    emo = discord.PartialEmoji.from_str(f'<{":".join(i)}>')
                    if emo.animated:
                        url = f"https://cdn.discordapp.com/emojis/{emo.id}.gif"
                    else:
                        url = f"https://cdn.discordapp.com/emojis/{emo.id}.png"
                    async with aiohttp.request("GET", url) as r:
                        if r.status != 200:
                            continue 
                        img = await r.read()
                        try:
                            emoji = await ctx.guild.create_custom_emoji(name=f"{emo.name}", image=img, reason=f"Emoji Added by {ctx.author.name}")
                            ls.append(str(emoji))
                            count+=1
                        except:
                            continue
                await init.delete()
                if count == 0:
                    return await ctx.reply(f"I couldn't add any of the emoji in this server, it might be because the emoji slots are full in the server")
                em = discord.Embed(color=botinfo.root_color)
                em.set_author(name=f"| Successfully created {count}/{len(xxx)} Emojis", icon_url=ctx.guild.me.display_avatar.url)
                em.description =f"> {' '.join(ls)}"
                em.set_footer(text=f"Emojis Added by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
                return await ctx.reply(embed=em)
            if not emoji.startswith("https://"):
                return await ctx.reply("Give a valid emoji to add")
            elif name is None:
                return await ctx.reply("Please provide a name for emoji")
            async with aiohttp.request("GET", f"{emoji}") as r:
                img = await r.read()
                try:
                  emo = await ctx.guild.create_custom_emoji(name=f"{name}", image=img, reason=f"Emoji Added by {ctx.author.name}")
                  return await ctx.reply(f"Successfully created {emo}")
                except:
                  return await ctx.reply(f"Failed to create emoji, it might be because the emoji slots are full.")        
        else:
            if emoji is None:
                emoji = discord.PartialEmoji.from_str(f'<{":".join(xxx[0])}>')
            if name is None:
                name = f"{emoji.name}"
            if emoji.animated:
                url = f"https://cdn.discordapp.com/emojis/{emoji.id}.gif"
            else:
                url = f"https://cdn.discordapp.com/emojis/{emoji.id}.png"
            async with aiohttp.request("GET", url) as r:
                try:
                    img = await r.read()
                    emo = await ctx.guild.create_custom_emoji(name=f"{name}", image=img, reason=f"Emoji Added by {ctx.author.name}")
                    await ctx.reply(f"Successfully created {emo}")
                except:
                    return await ctx.reply("Failed to create emoji, it might be because the emoji slots are full.")
    
    @commands.command(description="Changes the icon for the role")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def roleicon(self, ctx: commands.Context, role: discord.Role, *, icon: Union[discord.Emoji, discord.PartialEmoji, str]=None):
        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
        if ctx.author.top_role.position <= role.position:
            em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position from your top role!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if icon is None:
            c = False
            url = None
            for xd in ctx.message.attachments:
                url = xd.url
                c = True
            if c:
                try:
                    async with aiohttp.request("GET", url) as r:
                        img = await r.read()
                        await role.edit(display_icon=img)
                    em = discord.Embed(description=f"Successfully changed icon of {role.mention}", color=botinfo.root_color)
                except:
                    return await ctx.reply("Failed to change the icon of the role")
            else:
                await role.edit(display_icon=None)
                em = discord.Embed(description=f"Successfully removed icon from {role.mention}", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if isinstance(icon, discord.Emoji) or isinstance(icon, discord.PartialEmoji):
            png = f"https://cdn.discordapp.com/emojis/{icon.id}.png"
            try:
              async with aiohttp.request("GET", png) as r:
                img = await r.read()
            except:
              return await ctx.reply("Failed to change the icon of the role")
            await role.edit(display_icon=img)
            em = discord.Embed(description=f"Successfully changed the icon for {role.mention} to {icon}", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        else:
            if not icon.startswith("https://"):
                return await ctx.reply("Give a valid link")
            try:
              async with aiohttp.request("GET", icon) as r:
                img = await r.read()
            except:
              return await ctx.reply("An error occured while changing the icon for the role")
            await role.edit(display_icon=img)
            em = discord.Embed(description=f"Successfully changed the icon for {role.mention}", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.group(invoke_without_command=True, aliases=["purge"], description="Clears the messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, Choice: Union[discord.Member, int], Amount: int = None):
        """
        An all in one purge command.
        Choice can be a Member or a number
        """
        await ctx.message.delete()

        if isinstance(Choice, discord.Member):
            search = Amount or 5
            return await do_removal(ctx, search, lambda e: e.author == Choice)

        elif isinstance(Choice, int):
            return await do_removal(ctx, Choice, lambda e: True)

    @clear.command(description="Clears the messages containing embeds")
    @commands.has_permissions(manage_messages=True)
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.embeds))

    @clear.command(description="Clears the messages containing files")
    @commands.has_permissions(manage_messages=True)
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.attachments))

    @clear.command(description="Clears the messages containg images")
    @commands.has_permissions(manage_messages=True)
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @clear.command(name="all", description="Clears all messages")
    @commands.has_permissions(manage_messages=True)
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: True)

    @clear.command(description="Clears the messages of a specific user")
    @commands.has_permissions(manage_messages=True)
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: e.author == member)

    @clear.command(description="Clears the messages containing a specifix string")
    @commands.has_permissions(manage_messages=True)
    async def contains(self, ctx, *, string: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """

        await ctx.message.delete()
        if len(string) < 3:
            await ctx.error("The substring length must be at least 3 characters.")
        else:
            await do_removal(ctx, 100, lambda e: string in e.content)

    @clear.command(name="bot", aliases=["bots"], description="Clears the messages sent by bot")
    @commands.has_permissions(manage_messages=True)
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        await ctx.message.delete()

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await do_removal(ctx, search, predicate)

    @clear.command(name="emoji", aliases=["emojis"], description="Clears the messages having emojis")
    @commands.has_permissions(manage_messages=True)
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""

        await ctx.message.delete()
        custom_emoji = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await do_removal(ctx, search, predicate)

    @clear.command(name="reactions", description="Clears the reaction from the messages")
    @commands.has_permissions(manage_messages=True)
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        await ctx.message.delete()

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.success(f"Successfully removed {total_reactions} reactions.")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
      if not message.guild:
        return
      if not message.guild.me.guild_permissions.view_audit_log:
         return
      if not message.author.bot:
        async for i in message.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=5), action=discord.AuditLogAction.message_delete):
            if i.target.id == message.author.id:
                self.bot.sniped_messages[message.channel.id] = (message,
                                                        i.user
                                                        )
                return
        self.bot.sniped_messages[message.channel.id] = (message,
                                                        message.author
                                                               )

    @commands.command(description="Snipes the recent message deleted in the channel")
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        try:
            message, mod = self.bot.sniped_messages[channel.id]
        except:
            await ctx.channel.send(f"{emojis.wrong} Couldn't find a message to snipe!")
            return
        embed = discord.Embed(description=f":put_litter_in_its_place: Message sent by {message.author.mention} deleted in {message.channel.mention}",
                                color=botinfo.root_color,
                                )
        if message.content == "":
            contents = "**Contents unavailable.**"
        else:
            contents = message.content
        embed.add_field(name="__Content__:",
                                  value=contents,
                                  inline=False)
        if message.reference is not None:
            ref = await message.channel.fetch_message(message.reference.message_id)
            embed.add_field(name="Replying to:", value=f"[{str(ref.author)}]({ref.jump_url})")
        if mod is not None:
            embed.add_field(name="**Deleted By:**",
                                value=f"{mod.mention} (ID: {mod.id})")
        des = ""
        for i in message.attachments:
            if i.is_voice_message():
                continue
            des += f"[{i.filename}]({str(i.url)})\n"
        embed1 = None
        if not des == "":
            embed1 = discord.Embed(description=des,
                                color=botinfo.root_color,
                                timestamp=message.created_at)
            embed1.set_author(name=f"Message Attachments({len(message.attachments)}):")
            embed1.set_footer(text=f"Requested By {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        else:
            embed.set_footer(text=f"Requested By {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = message.created_at
        if embed1 is not None:
            ls = [embed, embed1]
        else:
            ls = [embed]
        return await ctx.channel.send(embeds=ls)
        
    @commands.command(description="Enables slowmode for the channel")
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, *, time=None):
        if time is None:
            await ctx.channel.edit(slowmode_delay=None, reason=f"Slowmode edited by {str(ctx.author)}")
            em = discord.Embed(description=f"{emojis.correct} Successfully removed slowmode for channel {ctx.channel.mention}", color=botinfo.right_color)
            return await ctx.channel.send(embed=em)
        t = "".join([ch for ch in time if ch.isalpha()])
        num = 0
        for c in time:
            if c.isdigit():
                num = num + int(c)
        if t == '':
            num = num
        elif t == 's' or t == 'seconds' or t == 'second':
            num = num
        elif t == 'm' or t == 'minutes' or t == 'minute':
            num = num*60
        elif t == 'h' or t == 'hours' or t == 'hour':
            num = num*60*60
        else:
            return await ctx.reply("Invalid time")
        try:
            await ctx.channel.edit(slowmode_delay=num, reason=f"Slowmode edited by {str(ctx.author)}")
        except:
            return await ctx.reply("Invalid time")
        em = discord.Embed(description=f"{emojis.correct} Successfully changed slowmode for channel {ctx.channel.mention} to {t} seconds", color=botinfo.right_color)
        await ctx.channel.send(embed=em)

    @commands.command(usage="[#channel/id]", name="lock", description="Locks the channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, *, reason = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title="Channel Locked", description=f"Locked by {ctx.author.name} for {reason}", color=botinfo.root_color)
        await ctx.reply(embed=em)

    @commands.command(description="locks all channels in the server")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def lockall(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Lock all the channels of the Server", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            await test.delete()
            return await ctx.reply(content="Timed out!", mention_author=False)
        if view.value == 'Yes':
            await test.delete()
            for channel in ctx.guild.channels:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lock all channels runned by {ctx.author}")
            em = discord.Embed(description="Locked all channels of the server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)        

    @commands.command(usage="[#channel/id]", name="unlock", description="Unlocks the channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title="Channel Unlocked", description=f"Unlocked by {ctx.author.name} for {reason}", color=botinfo.root_color)
        await ctx.reply(embed=em)
    
    @commands.command(description="Unlocks all channels in the server")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def unlockall(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Unlock all the channels of the Server", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            await test.delete()
            return await ctx.reply(content="Timed out!", mention_author=False)
        if view.value == 'Yes':
            await test.delete()
            for channel in ctx.guild.channels:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = True
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lock all channels runned by {ctx.author}")
            em = discord.Embed(description="Unlocked all channels of the server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.command(description="Hides the channel")
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx, channel: discord.abc.GuildChannel = None, *, reason = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title="Channel Hidden", description=f"Hidden by {ctx.author.name} for {reason}", color=botinfo.root_color)
        await ctx.reply(embed=em)
    
    @commands.command(description="Hide all channels in the server")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def hideall(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Hide all the channels of the Server", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            await test.delete()
            return await ctx.reply(content="Timed out!", mention_author=False)
        if view.value == 'Yes':
            await test.delete()
            for channel in ctx.guild.channels:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.view_channel = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lock all channels runned by {ctx.author}")
            em = discord.Embed(description="Hidden all channels of the server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
        
    @commands.command(description="Unhides the channel")
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx, channel: discord.abc.GuildChannel = None, *, reason = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title="Channel UnHidden", description=f"UnHidden by {ctx.author.name} for {reason}", color=botinfo.root_color)
        await ctx.reply(embed=em)
    
    @commands.command(description="Unhide all channels in the server")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def unhideall(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Unhide all the channels of the Server", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            await test.delete()
            return await ctx.reply(content="Timed out!", mention_author=False)
        if view.value == 'Yes':
            await test.delete()
            for channel in ctx.guild.channels:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.view_channel = True
            
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lock all channels runned by {ctx.author}")
            em = discord.Embed(description="Unhidden all channels of the server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.hybrid_group(invoke_without_command=True, aliases=['design', 'designs'], description="Shows the help menu for designer")
    @commands.has_permissions(administrator=True)
    async def designer(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}designer`\n" 
                                                  f"Shows The help menu for designer\n\n" 
                                                  f"`{prefix}designer role <design>`\n" 
                                                  f"Changes the design for the roles in the server\n\n"
                                                  f"`{prefix}designer channel <design>`\n"
                                                  f"Changes the design for the channels in the server\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @designer.command(name="role", aliases=['roles'], description="Changes the design for the roles in the server")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def r(self, ctx: commands.Context, *, design: str):
        if "{role}" in design:
            pass
        elif "{Role}" in design:
            design.replace("{Role}", "{role}")
        elif "{ROLE}" in design:
            design.replace("{ROLE}", "{role}")
        else:
            return await ctx.reply("Please specify where to write the name of the role in the design by `{role}`")
        v = OnOrOff(ctx)
        init = await ctx.reply(embed=discord.Embed(description=f"Are you sure you want me to change the design for roles in the server?", color=botinfo.root_color), view=v)
        await v.wait()
        if v.value == 'yes':
            await init.delete()
            for i in list(reversed(ctx.guild.roles[1:])):
                if i.is_assignable():
                    await i.edit(name=f'{design.replace("{role}", i.name)}')
            em = discord.Embed(description=f"Successfully changed the design for the roles in the server", color=botinfo.root_color)
            await ctx.reply(embed=em)
        else:
            await init.delete()
        
    @designer.command(name="channel", aliases=['channels'], description="Changes the design for the channels in the server")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def cc(self, ctx: commands.Context, *, design: str):
        if "{channel}" in design:
            pass
        elif "{Channel}" in design:
            design.replace("{Channel}", "{channel}")
        elif "{CHANNEL}" in design:
            design.replace("{CHANNEL}", "{channel}")
        else:
            return await ctx.reply("Please specify where to write the name of the channel in the design by `{channel}`")
        emd = discord.Embed(description="Which types of channels should i edit?", color=botinfo.root_color)
        v = channeloption(ctx)
        init = await ctx.reply(embed=emd, view=v)
        await v.wait()
        vv = OnOrOff(ctx)
        await init.edit(embed=discord.Embed(description=f"Are you sure you want me to change the design for {v.value.capitalize()} channels in the server?", color=botinfo.root_color), view=vv)
        await vv.wait()
        if vv.value == 'yes':
            await init.delete()
            for i in ctx.guild.channels:
                if str(i.type) == v.value:
                    await i.edit(name=f'{design.replace("{channel}", i.name)}')
            em = discord.Embed(description=f"Successfully changed the design for the {v.value.capitalize()} channels in the server", color=botinfo.root_color)
            await ctx.reply(embed=em)
        else:
            await init.delete()

    @commands.command(name='enlarge', description='Enlarges an emoji.')
    async def enlarge(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji, str]):
        if isinstance(emoji, discord.Emoji):
            await ctx.send(emoji.url)
        elif isinstance(emoji, discord.PartialEmoji):
            await ctx.send(emoji.url)
        elif isinstance(emoji, str) and not emoji.isalpha() and not emoji.isdigit():
            await ctx.send(emoji)

    @commands.command(description="Created a role in the server")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def addrole(self, ctx, color, *,name):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        try:
            color = matplotlib.colors.cnames[color.lower()]
        except:
            color = color
        color = str(color).replace("#", "")
        try:
            color = int(color, base=16)
        except:
            return await ctx.reply(f"Provide a specific color")
        role = await ctx.guild.create_role(name=name, color=color, reason=f"Role created by {str(ctx.author)}")
        em = discord.Embed(description=f"Created {role.mention} role", color=botinfo.root_color)
        await ctx.reply(embed=em, mention_author=False)
        
    @commands.command(description="Deletes a role in the server")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delrole(self, ctx, *,role:discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        await role.delete()
        await ctx.reply(embed=discord.Embed(description="Successfully deleted the role", color=botinfo.root_color), mention_author=False)
    
    @commands.hybrid_group(
        invoke_without_command=True,
        description="Adds a role to the user"
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        if role.position >= ctx.author.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position from your top role!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        c = check_lockrole_bypass(role, ctx.guild, ctx.author)
        if not c:
            em = discord.Embed(description=f"{emojis.wrong} {role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if role in user.roles:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author.name}")
            em=discord.Embed(description=f"{emojis.correct} Successfully removed {role.mention} from {user.mention}", color=ctx.author.color)
            return await ctx.send(embed=em)
        await user.add_roles(role, reason=f"Role given by {ctx.author.name}")
        em=discord.Embed(description=f"{emojis.correct} Successfully Given {role.mention} to {user.mention}", color=ctx.author.color)
        await ctx.reply(embed=em)

    @role.command(name="all", description="Gives a role to all the members in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_all(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.role_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        c = check_lockrole_bypass(role, ctx.guild, ctx.author)
        if not c:
            em = discord.Embed(description=f"{emojis.wrong} {role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        test = [member for member in ctx.guild.members if not role in member.roles]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already given to all the members of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to give __{role.mention}__ to {len(test)} Members?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.role_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Giving __{role.mention}__ to {len(test)} Members**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for member in test:
            if self.bot.role_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.role_status[ctx.guild.id]
                self.bot.role_status[ctx.guild.id] = (count+1, len(test), True)
                await member.add_roles(role, reason=f"Role all runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Giving role | Given __{role.mention}__ to {count+1} members out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Given __{role.mention}__ to {total_count} Members**", color=ctx.author.color)
        self.bot.role_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)

    @role.command(name="bots", description="Gives a role to all the bots in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_bots(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.role_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        c = check_lockrole_bypass(role, ctx.guild, ctx.author)
        if not c:
            em = discord.Embed(description=f"{emojis.wrong} {role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        test = [member for member in ctx.guild.members if all([member.bot, not role in member.roles])]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already given to all the bots of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to give __{role.mention}__ to {len(test)} Bots?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.role_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Giving __{role.mention}__ to {len(set(test))} Bots**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for bot_members in test:
            if self.bot.role_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.role_status[ctx.guild.id]
                self.bot.role_status[ctx.guild.id] = (count+1, len(test), True)
                await bot_members.add_roles(role, reason=f"Role bots runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Giving role | Given __{role.mention}__ to {count+1} Bots out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Given __{role.mention}__ to {total_count} Bots**", color=ctx.author.color)
        self.bot.role_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)

    @role.command(name="humans", description="Gives a role to all the users in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_humans(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.role_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        c = check_lockrole_bypass(role, ctx.guild, ctx.author)
        if not c:
            em = discord.Embed(description=f"{emojis.wrong} {role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        test = [member for member in ctx.guild.members if all([not member.bot, not role in member.roles])]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already given to all the users of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to give __{role.mention}__ to {len(test)} Users?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.role_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Giving __{role.mention}__ to {len(set(test))} Users**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for humans in test:
            if self.bot.role_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.role_status[ctx.guild.id]
                self.bot.role_status[ctx.guild.id] = (count+1, len(test), True)
                await humans.add_roles(role, reason=f"Role humans runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Giving role | Given __{role.mention}__ to {count+1} Users out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Given __{role.mention}__ to {total_count} Users**", color=ctx.author.color)
        self.bot.role_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)

    @role.command(name="status", description="Shows the status of current adding role process")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_status(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.role_status[ctx.guild.id] is None:
                em = discord.Embed(description=f"{emojis.wrong} No add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
                em = discord.Embed(description=f"{emojis.wrong} No add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        count, total_count, sts = self.bot.role_status[ctx.guild.id]
        em = discord.Embed(description=f"Given roles to {count} users out of {total_count} users ({count/total_count * 100.0}%) of adding roles to {total_count} users", color=botinfo.root_color)
        em.set_footer(text=f"{str(self.bot.user)} Adding role", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=em)

    @role.command(name="cancel", description="Cancel the current adding role process")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_cancel(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.role_status[ctx.guild.id] is None:
                em = discord.Embed(description=f"{emojis.wrong} No add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
                em = discord.Embed(description=f"{emojis.wrong} No add role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        self.bot.role_status[ctx.guild.id] = None
        
    @commands.hybrid_group(
        invoke_without_command=True,
        aliases=["removerole"], description="Removes a role from the user"
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole(self, ctx, user: discord.Member, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if not role in user.roles:
            em = discord.Embed(description=f'{emojis.wrong} The member do not has this role!', color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
            
        if role == ctx.author.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} That role has the same position as your top role!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        c = check_lockrole_bypass(role, ctx.guild, ctx.author)
        if not c:
            em = discord.Embed(description=f"{emojis.wrong} {role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await user.remove_roles(role, reason=f"role removed by {ctx.author.name}")
        em=discord.Embed(description=f"{emojis.correct} Successfully Removed {role.mention} From {user.mention}", color=ctx.author.color)
        await ctx.send(embed=em)

    @rrole.command(name="all", description="Removes a role from all the members in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_all(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        test = [member for member in ctx.guild.members if role in member.roles]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already removed from all the members of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to remove __{role.mention}__ from {len(test)} Members?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.rrole_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Removing __{role.mention}__ from {len(test)} Members**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for member in test:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.rrole_status[ctx.guild.id]
                self.bot.rrole_status[ctx.guild.id] = (count+1, len(test), True)
                await member.remove_roles(role, reason=f"Rrole all runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Removing role | Removed __{role.mention}__ from {count+1} Users out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Removed __{role.mention}__ from {total_count} Members**", color=ctx.author.color)
        self.bot.rrole_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)

    @rrole.command(name="bots", description="Removes a role from all the bots in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_bots(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        test = [member for member in ctx.guild.members if all([member.bot, role in member.roles])]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already removed from all the bots of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to remove __{role.mention}__ from {len(test)} Bots?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.rrole_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Removing __{role.mention}__ from {len(set(test))} Bots**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for bot_members in test:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.rrole_status[ctx.guild.id]
                self.bot.rrole_status[ctx.guild.id] = (count+1, len(test), True)
                await bot_members.remove_roles(role, reason=f"Rrole bots runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Removing role | Removed __{role.mention}__ from {count+1} Bots out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Removed __{role.mention}__ from {total_count} Bots**", color=ctx.author.color)
        self.bot.rrole_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)

    @rrole.command(name="humans", description="Removes a role from all the users in the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_humans(self, ctx, *,role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                em = discord.Embed(description=f"{emojis.wrong} Already a remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
            pass
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:        
            if role.position >= ctx.author.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} That role has the same or higher position as your top role!", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)

        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} This role is higher than my role, move it to the top!", color=botinfo.wrong_color)
            return await ctx.send(embed=em, delete_after=15)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role", delete_after=15)
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.", delete_after=15)
        test = [member for member in ctx.guild.members if all([not member.bot, role in member.roles])]
        if len(test) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already removed from all the users of the server", color=botinfo.root_color))
        emb=discord.Embed(description=f"Do you want to remove __{role.mention}__ from {len(test)} Users?", color=ctx.author.color)
        v = OnOrOff(ctx)
        init = await ctx.send(embed=emb, view=v)
        await v.wait()
        if v.value == 'Yes':
            pass
        else:
            return await init.delete()
        self.bot.rrole_status[ctx.guild.id] = (0, len(test), True)
        em=discord.Embed(description=f"**{emojis.loading}  |  Removing __{role.mention}__ from {len(set(test))} Users**", color=ctx.author.color)
        await init.edit(embed=em, view=None)
        for humans in test:
            if self.bot.rrole_status[ctx.guild.id] is not None:
                count, total_count, sts = self.bot.rrole_status[ctx.guild.id]
                self.bot.rrole_status[ctx.guild.id] = (count+1, len(test), True)
                await humans.remove_roles(role, reason=f"Rrole humans runned by {ctx.author.name}")
        if count+1 != total_count:
            em1=discord.Embed(description=f"**{emojis.correct} |  Cancelled the process of Removing role | Removed __{role.mention}__ from {count+1} Users out of {total_count}**", color=ctx.author.color)
        else:
            em1=discord.Embed(description=f"**{emojis.correct} |  Removed __{role.mention}__ from {total_count} Users**", color=ctx.author.color)
        self.bot.rrole_status[ctx.guild.id] = None
        await init.delete()
        try:
            await ctx.reply(embed=em1)
        except:
            await ctx.send(embed=em1)
    @rrole.command(name="status", description="Shows the status of current remove role process")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_status(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.rrole_status[ctx.guild.id] is None:
                em = discord.Embed(description=f"{emojis.wrong} No remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
                em = discord.Embed(description=f"{emojis.wrong} No remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        count, total_count, sts = self.bot.rrole_status[ctx.guild.id]
        em = discord.Embed(description=f"Removed roles from {count} users out of {total_count} users ({count/total_count * 100.0}%) of removing roles to {total_count} users", color=botinfo.root_color)
        em.set_footer(text=f"{str(self.bot.user)} Removing roles", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=em)

    @rrole.command(name="cancel", description="Cancel the current Remove role process")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_cancel(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        try:
            if self.bot.rrole_status[ctx.guild.id] is None:
                em = discord.Embed(description=f"{emojis.wrong} No remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        except:
                em = discord.Embed(description=f"{emojis.wrong} No remove role process is running", color=botinfo.wrong_color)
                return await ctx.send(embed=em, delete_after=15)
        self.bot.rrole_status[ctx.guild.id] = None
        em = discord.Embed(description="Cancelled the process", color=botinfo.root_color)
        await ctx.send(embed=em)

    @commands.command(aliases=["mute"], description="Timeouts a user for specific time\nIf you don't provide the time the user will be timeout for 5 minutes")
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, *, time = None):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= member.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} Your Top role should be above the top role of {str(member)}", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        if member.id == ctx.guild.owner.id:
            em = discord.Embed(description=f"{emojis.wrong} Idiot! You cannot mute owner of the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if ctx.guild.me.top_role.position == member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is same as of {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if member.top_role.position > ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is below {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        reason = ""
        if time is None:
            timee = "5m"
            reason = ""
        else:
            timee = ""
            c = False
            for i in time:
                if i == ' ':
                    c = True
                if not c:
                    timee += i
                else:
                    reason += i
        converted_time = convert(timee)
        if converted_time == -1 or converted_time == -2:
            converted_time = convert("5m")
            reason = f"{timee}{reason}"
        timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=converted_time[0])
        await member.edit(timed_out_until=timeout_until, reason=f"Muted by {ctx.author} for {reason}")
        if reason != "":
            r = f" for reason `{reason.strip()}`"
        else:
            r = ""
        em = discord.Embed(description=f"{emojis.correct} Successfully Muted {member.mention} till <t:{round(timeout_until.timestamp())}:f>{r}", color=botinfo.right_color)
        await ctx.channel.send(embed=em)
        em = discord.Embed(description=f'YOU HAVE BEEN MUTED FROM {ctx.guild.name} till <t:{round(timeout_until.timestamp())}:f>{r}', color=botinfo.root_color)
        em.set_footer(text=f'Muted by {ctx.author.name}')
        return await member.send(embed=em)

    @commands.command(description="Removes the timeout from the user")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    async def unmute(self, ctx, *,member: discord.Member):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= member.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} Your Top role should be above the top role of {str(member)}", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        if member.id == ctx.guild.owner.id:
            em = discord.Embed(description=f"{emojis.wrong} Idiot! You cannot unmute owner of the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if ctx.guild.me.top_role.position == member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is same as of {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if member.top_role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is below {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        guild = ctx.guild
        await member.edit(timed_out_until=None, reason=f"Unmuted by {ctx.author}")
        em = discord.Embed(description=f"{emojis.correct} Successfully Unmuted {member.mention}", color=botinfo.right_color)
        await ctx.channel.send(embed=em)
        em = discord.Embed(description=f'YOU HAVE BEEN UNMUTED FROM {ctx.guild.name}', color=botinfo.root_color)
        em.set_footer(text=f'Unmuted by {ctx.author.name}')
        return await member.send(embed=em)
        
    @commands.command(description="Unmutes all the muted members in the server")
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unmuteall(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        count = 0
        for member in ctx.guild.members:
            if member.is_timed_out():
                count += 1
        if count == 0:
            return await ctx.send("No timedout Users")
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To remove timeout from {count} Users", color=botinfo.root_color)
        em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            return await test.edit(content="Timed out!", view=None)
        if view.value == 'Yes':
            await test.delete()
            count = 0
            for member in ctx.guild.members:
                if member.is_timed_out():
                    try:
                        await member.edit(timed_out_until=None, reason=f"Unmuted by {ctx.author}")
                        count+=1
                    except:
                        continue
            em = discord.Embed(description=f"Removed timeout from {count} users in the Server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
            
    @commands.command(aliases=["setnick"], description="Changes the user's nickname for the server")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def nick(self, ctx, member : discord.Member, *, Name=None):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:

            if ctx.author.top_role.position <= member.top_role.position:
                em = discord.Embed(description=f"{emojis.wrong} Your Top role should be above the top role of {str(member)}", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        if member.id == ctx.guild.owner.id:
            em = discord.Embed(description=f"{emojis.wrong} Idiot! You cannot change nick of owner of the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if ctx.guild.me.top_role.position == member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is same as of {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if member.top_role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is below {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if Name is None:
            await member.edit(nick=None, reason=f"Nickname changed by {ctx.author.name}")
            em = discord.Embed(description=f"Successfully cleared nickname of {str(member)}", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if Name is not None:
            await member.edit(nick=Name, reason=f"Nickname changed by {ctx.author.name}")
            em = discord.Embed(description=f"Successfully Changed nickname of {str(member)} to **{Name}**", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.command(description="Kicks a member from the server")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
            
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)

        if member.id == ctx.guild.owner.id:
            em = discord.Embed(description=f"{emojis.wrong} Idiot! You cannot kick owner of the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if ctx.author.top_role.position <= member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} Your Top role should be above the top role of {str(member)}", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

        if ctx.guild.me.top_role.position == member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is same as of {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)

        if member.top_role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is below {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await member.kick(reason=f"Kicked by {ctx.author.name} for {reason}")
        em = discord.Embed(description=f"{emojis.correct} Successfully Kicked {member} with the reason **`{reason}`**", color=botinfo.right_color)
        await ctx.channel.send(embed=em)
        await member.send(embed=discord.Embed(description=f'You Have Been Kicked From **{ctx.guild.name}** For The Reason: `{reason}`', color=botinfo.root_color))

    @commands.command(description="Unbans a member from the server")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User):
        async for x in ctx.guild.bans():
            if x.user.id == user.id:
                await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author.name}")
                return await ctx.send(f'{emojis.correct} Unbanned **{str(user)}**!')
        await ctx.send(f'**{str(user)}** is not banned!')
    
    @commands.command(description="Unban all the banned members in the server")
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unbanall(self, ctx):
        xd = [member async for member in ctx.guild.bans()]
        if len(xd) == 0:
            return await ctx.send("No Banned Users")
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Unban {len(xd)} Users", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            return await test.edit(content="Timed out!", view=None)
        if view.value == 'Yes':
            await test.delete()
            count = 0
            async for member in ctx.guild.bans():
                await ctx.guild.unban(member.user, reason=f"Unbaned by {ctx.author.name}")
                count+=1
            em = discord.Embed(description=f"Unbaned {count} users From the Server", color=botinfo.root_color)
            return await ctx.reply(embed=em, mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.command(description="Warns the user")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member,*,reason=None):
        if user.top_role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} {user.mention} Have Higher Role than Bot, So they can't be warned", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
        if w_db is None:
            data = {}
            ls = []
            case_ids = []
        else:
            data = literal_eval(w_db['data'])
            case_ids = literal_eval(w_db['count'])
            if user.id in data:
                ls = data[user.id]
            else:
                ls = []
        check = True
        while check:
            count = round(random.random()*10000)
            if count >= 1000 and count not in case_ids:
                check = False
        dic = {}
        dic[count] = {}
        dic[count]['mod'] = ctx.author.id
        dic[count]['at_time'] = datetime.datetime.now().timestamp()
        dic[count]['at_channel'] = ctx.channel.id
        if reason != None:
            try:
                await user.send(f'You have been warned from {ctx.guild.name} for {reason}')
                em = discord.Embed(description=f"{emojis.correct} {user.mention} Has been warned for `{reason}`\nWarning id: {count}", color=botinfo.right_color)
                await ctx.send(embed=em)
            except:
                em = discord.Embed(description=f"{emojis.correct} {user.mention} Has been warned for `{reason}` but the dm's are off.\nWarning id: {count}", color=botinfo.right_color)
                await ctx.send(embed=em)
            dic[count]['reason'] = reason
        if reason == None:
            try:
                await user.send(f'You have been warned from {ctx.guild.name}')
                em = discord.Embed(description=f"{emojis.correct} {user.mention} Has been warned\nWarning id: {count}", color=botinfo.right_color)
                await ctx.send(embed=em)
            except:
                em = discord.Embed(description=f"{emojis.correct} {user.mention} Has been warned but the dm's are off\nWarning id: {count}", color=botinfo.right_color)
                await ctx.send(embed=em)
            dic[count]['reason'] = 'None'
        ls.append(dic)
        data[user.id] = ls
        if w_db is None:
            val = (ctx.guild.id, f"{data}", f"{case_ids}")
            database.insert("warn", "guild_id, 'data', 'count'", val)
        else:
            dic = {
                'data': f"{data}",
                'count': f"{case_ids}"
            }
            database.update_bulk("warn", dic, "guild_id", ctx.guild.id)

    @commands.hybrid_group(invoke_without_command=True, aliases=['warnings'], description="Shows warnings help page")
    @commands.has_guild_permissions(manage_messages=True)
    async def warning(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=1141685323299045517)
        ls = ["warning", "warning show", "warning clear", "warning remove", "warning fetch"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Moderation']} Warning Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @warning.command(name="show", description="Shows warnings of a specific user | All users")
    @commands.has_guild_permissions(manage_messages=True)
    async def w_show(self, ctx: commands.Context, *, user: discord.Member = None):
        if user is None:
            no_warn_em = discord.Embed(description=f"There are no warnings to any member of this server", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
            if w_db is None:
                return await ctx.reply(embed=no_warn_em)
            else:
                data = literal_eval(w_db['data'])
                if len(data) == 0:
                    return await ctx.reply(embed=no_warn_em)
            ls1, warn = [], []
            count = 1
            t_count = 0
            dd = {}
            for i in data:
                dd[len(data[i])] = i
            for ls in reversed(sorted(dd)):
                u = discord.utils.get(self.bot.users, id=dd[ls])
                if u is None:
                    continue
                if ls == 0:
                    continue
                warn.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.mention} has recived `{ls}` Total number of warnings")
                count += 1
                t_count += ls
            if t_count == 0:
                return await ctx.reply(embed=no_warn_em)
            for i in range(0, len(warn), 15):
                ls1.append(warn[i: i + 15])
            em_list = []
            no = 1
            for k in ls1:
                embed =discord.Embed(color=botinfo.root_color)
                embed.title = f"Total Warnings in the server - {t_count}"
                embed.description = "\n".join(k)
                embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls1)}", icon_url=self.bot.user.display_avatar.url)
                em_list.append(embed)
                no+=1
            page = PaginationView(embed_list=em_list, ctx=ctx)
            await page.start(ctx)
        else:
            no_warn_em = discord.Embed(description=f"There are no warnings for {user.mention}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
            if w_db is None:
                return await ctx.reply(embed=no_warn_em)
            else:
                data = literal_eval(w_db['data'])
                if user.id not in data:
                    return await ctx.reply(embed=no_warn_em)
                else:
                    ls = data[user.id]
                    if len(ls) == 0:
                        return await ctx.reply(embed=no_warn_em)
                    else:
                        pass
            em_list = []
            dic = {}
            no = 1
            for j in ls:
                for i in j:
                    dic[no] = int(i)
                    u = discord.utils.get(self.bot.users, id=j[i]['mod'])
                    c = discord.utils.get(ctx.guild.channels, id=j[i]['at_channel'])
                    embed =discord.Embed(color=botinfo.root_color)
                    embed.title = f"Warning of {str(user)} - {len(ls)}"
                    if u is not None:
                        embed.add_field(name="Moderator:", value=u.mention)
                    else:
                        embed.add_field(name="Moderator:", value="The Moderator isn't present in the server")
                    embed.add_field(name="Time of Warning:", value=f"<t:{round(j[i]['at_time'])}:F>")
                    if c is not None:
                        embed.add_field(name="Channel:", value=c.mention)
                    else:
                        embed.add_field(name="Channel:", value="Channel Maybe got deleted")
                    embed.add_field(name="Reason:", value=j[i]['reason'])
                    embed.add_field(name="Warning id:", value=i)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    embed.set_thumbnail(url=user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
            if no > 2:
                page = PaginationView(embed_list=em_list, ctx=ctx)
                page.add_item(clear_warn(self.bot, ctx, dic, page, data, user))
                page.add_item(remove_warn(self.bot, ctx, dic, page, data, user))
                await page.start(ctx)
            else:
                view = remove_warn_view(self.bot, ctx, i, data, user)
                await ctx.reply(embed=embed, view=view, mention_author=False)

    @warning.command(name='fetch', description="Fetched the report and details of a warning using its id")
    @commands.has_guild_permissions(manage_messages=True)
    async def _fetch(self, ctx: commands.Context, id: str):
        if not id.isdigit():
            return await ctx.reply("Please provide the integer value")
        id = int(id)
        no_warn_em = discord.Embed(description=f"I was not able to find any warning with the id {id}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
        if w_db is None:
            return await ctx.reply(embed=no_warn_em)
        else:
            data = literal_eval(w_db['data'])
            c = False
            ls = {}
            for i in data:
                for j in data[i]:
                    for k in j:
                        if k == id:
                            c = True
                            h = i
                            ls = j[k]
                            break
            if not c:
                return await ctx.reply(embed=no_warn_em)
            user = discord.utils.get(self.bot.users, id=h)
            u = discord.utils.get(self.bot.users, id=ls['mod'])
            c = discord.utils.get(ctx.guild.channels, id=ls['at_channel'])
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"Warning of {str(user)}"
            if u is not None:
                embed.add_field(name="Moderator:", value=u.mention)
            else:
                embed.add_field(name="Moderator:", value="The Moderator isn't present in the server")
            embed.add_field(name="Time of Warning:", value=f"<t:{round(ls['at_time'])}:F>")
            if c is not None:
                embed.add_field(name="Channel:", value=c.mention)
            else:
                embed.add_field(name="Channel:", value="Channel Maybe got deleted")
            embed.add_field(name="Reason:", value=ls['reason'])
            embed.add_field(name="Warning id:", value=i)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            view = remove_warn_view(self.bot, ctx, id, data, user)
            await ctx.reply(embed=embed, view=view, mention_author=False)

    @warning.command(name="clear", description="Clears warning for a user")
    @commands.has_guild_permissions(manage_messages=True)
    async def _clear(self, ctx: commands.Context, *, user: discord.Member):
        no_warn_em = discord.Embed(description=f"{user.mention} has no warnings to be cleared", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
        if w_db is None:
            return await ctx.reply(embed=no_warn_em)
        else:
            data = literal_eval(w_db['data'])
            if user.id not in data:
                return await ctx.reply(embed=no_warn_em)
            else:
                ls = data[user.id]
                if len(ls) == 0:
                    return await ctx.reply(embed=no_warn_em)
                else:
                    del data[user.id]
        database.update("warn", "data", f"{data}", "guild_id", ctx.guild.id)
        em = discord.Embed(description=f"Successfully cleared the warnings for {user.mention}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=em)

    @warning.command(name="remove", aliases=['delete'], description="Removes a warning from using its id")
    @commands.has_guild_permissions(manage_messages=True)
    async def _remove(self, ctx: commands.Context, id: str):
        if not id.isdigit():
            return await ctx.reply("Please provide the integer value")
        id = int(id)
        no_warn_em = discord.Embed(description=f"I was not able to find any warning with the id {id}", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        w_db = database.fetchone("*", "warn", "guild_id", ctx.guild.id)
        if w_db is None:
            return await ctx.reply(embed=no_warn_em)
        else:
            data = literal_eval(w_db['data'])
            c = False
            for i in data:
                for j in data[i]:
                    for k in j:
                        if k == id:
                            c = True
                            h = i
                            ls = data[i]
                            ls.remove(j)
                            data[i] = ls
                            break
            if not c:
                return await ctx.reply(embed=no_warn_em)
        database.update("warn", "data", f"{data}", "guild_id", ctx.guild.id)
        u = discord.utils.get(self.bot.users, id=h)
        em = discord.Embed(description=f"Successfully removed the warning of {u.mention} with the id `{id}`", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(description="Bans the user from the server", aliases=['fuckoff', 'hackban'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if ctx.author.top_role.position <= member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} Your Top role should be above the top role of {str(member)}", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
            
        if member.id == ctx.guild.owner.id:
            em = discord.Embed(description=f"{emojis.wrong} Idiot! You cannot ban owner of the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)

        if ctx.guild.me.top_role.position == member.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is same as of {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)

        if member.top_role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{emojis.wrong} My highest role is below {str(member)}!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await member.ban(reason=f"Banned by {ctx.author.name} for {reason}")
        em = discord.Embed(description=f"{emojis.correct} Successfully Banned {member} with the reason **`{reason}`**", color=ctx.author.color)
        await ctx.channel.send(embed=em)
        await member.send(embed=discord.Embed(description=f'You Have Been Banned From **{ctx.guild.name}** For The Reason: `{reason}`', color=botinfo.root_color))

    @commands.command(aliases=['nuke', 'clonechannel'], description="Clones the channel")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def clone(self, ctx, channel: discord.TextChannel = None):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if channel == None:
            channel = ctx.channel
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Clone {channel.mention} Channel", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            return await test.edit(content="Timed out!", view=None)
        if view.value == 'Yes':
            await test.delete()
            channel_position = channel.position
            new = await channel.clone(reason=f"Channel nuked by {ctx.author.name}")
            await channel.delete(reason=f"Channel nuked by {ctx.author.name}")
            await new.edit(sync_permissions=True, position=channel_position)
            return await new.send(f"{ctx.author.mention}", embed=discord.Embed(title="Channel Nuked", description=f"Channel has been nuked by {ctx.author.mention}.", color=botinfo.root_color), mention_author=False)
        if view.value == 'No':
            await test.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        webhook = discord.SyncWebhook.from_url(webhook_cmd_logs)
        try:
            emb = discord.Embed(title=f"Command runned in {ctx.guild.name}", description=f"Command name: `{ctx.command.qualified_name}`\nAuthor Name: {str(ctx.author)}\nGuild Id: {ctx.guild.id}\nCommand executed: `{ctx.message.content}`\nChannel name: {ctx.channel.name}\nChannel Id: {ctx.channel.id}\nJump Url: [Jump to]({ctx.message.jump_url})\nCommand runned without error: False", timestamp=ctx.message.created_at, color=botinfo.root_color)
        except:
            return
        emb.set_thumbnail(url=ctx.author.display_avatar.url)
        if isinstance(error, commands.BotMissingPermissions):
            permissions = ", ".join([f"{permission.capitalize()}" for permission in error.missing_permissions]).replace("_", " ")
            em = discord.Embed(description=f"{emojis.wrong} Unfortunately I am missing **`{permissions}`** permissions to run the command `{ctx.command}`", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=7)
            emb.add_field(name="Error:", value=f"Bot Missing {permissions} permissions to run the command", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.MissingPermissions):
            permissions = ", ".join([f"{permission.capitalize()}" for permission in error.missing_permissions]).replace("_", " ")
            em = discord.Embed(description=f"{emojis.wrong} You lack `{permissions}` permissions to run the command `{ctx.command}`.", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=7)
            emb.add_field(name="Error:", value=f"User Missing {permissions} permissions to run the command", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.MissingRole):
            em = discord.Embed(description=f"{emojis.wrong} You need `{error.missing_role}` role to use this command.", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=5)
            emb.add_field(name="Error:", value=f"Missing role", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(description=f"{emojis.wrong} This command is on cooldown. Please retry after `{round(error.retry_after, 1)} Seconds` .", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=7)
            emb.add_field(name="Error:", value=f"Command On Cooldown", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(description=f"{emojis.wrong} You missed the `{error.param.name}` argument.\nDo it like: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=7)
            emb.add_field(name="Error:", value=f"Argument missing", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.EmojiNotFound):
            em = discord.Embed(description=f"{emojis.wrong} The Emoji Cannot be found", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=3)
            emb.add_field(name="Error:", value=f"Emoji not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.RoleNotFound):
            em = discord.Embed(description=f"{emojis.wrong} The Role Cannot be found", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=3)
            emb.add_field(name="Error:", value=f"Role not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.GuildNotFound):
            em = discord.Embed(description=f"{emojis.wrong} The Guild Cannot be found", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=3)
            emb.add_field(name="Error:", value=f"Guild not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.UserNotFound):
            em = discord.Embed(description=f"{emojis.wrong} The User Cannot be found", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=3)
            emb.add_field(name="Error:", value=f"User not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.MemberNotFound):
            em = discord.Embed(description=f"{emojis.wrong} The Member Cannot be found", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=3)
            emb.add_field(name="Error:", value=f"Member not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        if isinstance(error, commands.NSFWChannelRequired):
            em = discord.Embed(description=f"{emojis.wrong} The Channel is required to be NSFW to execute this command", color=botinfo.wrong_color)
            await ctx.send(embed=em, delete_after=8)
            emb.add_field(name="Error:", value=f"NSFW Channel disabled", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return

    @commands.hybrid_group(
        invoke_without_command=True, description="Shows the help page for scan commands"
    )
    async def scan(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}scan`\n" 
                                                  f"This Command Will Show This Page\n\n" 
                                                  f"`{prefix}scan users`\n" 
                                                  f"Shows All users having Key Permissions\n\n"
                                                  f"`{prefix}scan bots`\n"
                                                  f"Shows All bots having Key Permissions\n\n"
                                                  f"`{prefix}scan roles`\n" 
                                                  f"Show All Roles having Key permissions\n\n" 
                                                  f"`{prefix}scan permissions`\n" 
                                                  f"Show Permissions of all roles.\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @scan.command(aliases=['user'], description="Shows All users having Key Permissions")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def users(self, ctx):
        ls = []
        admin, ban, kick, mgn, mgnch, mgnro, mention = "", "", "", "", "", "", ""
        c1, c2, c3, c4, c5, c6, c7 = 1, 1, 1, 1, 1, 1, 1
        for member in ctx.guild.members:
          if not member.bot:
            if member.guild_permissions.administrator == True:
                admin += f"[{'0' + str(c1) if c1 < 10 else c1}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c1 += 1
            if member.guild_permissions.ban_members == True:
                ban += f"[{'0' + str(c2) if c2 < 10 else c2}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c2 += 1
            if member.guild_permissions.kick_members == True:
                kick += f"[{'0' + str(c3) if c3 < 10 else c3}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c3 += 1
            if member.guild_permissions.manage_guild == True:
                mgn += f"[{'0' + str(c4) if c4 < 10 else c4}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c4 += 1
            if member.guild_permissions.manage_channels == True:
                mgnch += f"[{'0' + str(c5) if c5 < 10 else c5}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c5 += 1
            if member.guild_permissions.manage_roles == True:
                mgnro += f"[{'0' + str(c6) if c6 < 10 else c6}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c6 += 1
            if member.guild_permissions.mention_everyone == True:
                mention += f"[{'0' + str(c7) if c7 < 10 else c7}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c7 += 1
        em1 = discord.Embed(title="Administrator Perms", description=admin, color=ctx.author.color)
        try:    
            em1.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em1.set_footer(text=f"Requested by: {ctx.author.name}")
        em2 = discord.Embed(title="Kick Members", description=kick, color=ctx.author.color)
        try:    
            em2.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em2.set_footer(text=f"Requested by: {ctx.author.name}")
        em3 = discord.Embed(title="Ban Members", description=ban, color=ctx.author.color)
        try:    
            em3.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em3.set_footer(text=f"Requested by: {ctx.author.name}")
        em4 = discord.Embed(title="Manager server", description=mgn, color=ctx.author.color)
        try:    
            em4.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em4.set_footer(text=f"Requested by: {ctx.author.name}")
        em5 = discord.Embed(title="Manager Channels", description=mgnch, color=ctx.author.color)
        try:    
            em5.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em5.set_footer(text=f"Requested by: {ctx.author.name}")
        em6 = discord.Embed(title="Manager Roles", description=mgnro, color=ctx.author.color)
        try:    
            em6.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em6.set_footer(text=f"Requested by: {ctx.author.name}")
        em7 = discord.Embed(title="Mention Everyone", description=mention, color=ctx.author.color)
        try:    
            em7.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em7.set_footer(text=f"Requested by: {ctx.author.name}")
        ls.append(em1)
        ls.append(em2)
        ls.append(em3)
        ls.append(em4)
        ls.append(em5)
        ls.append(em6)
        ls.append(em7)
        page = PaginationView(embed_list=ls, ctx=ctx)
        await page.start(ctx)

    @scan.command(aliases=['bot'], description="Shows All bots having Key Permissions")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bots(self, ctx):
        ls = []
        admin, ban, kick, mgn, mgnch, mgnro, mention = "", "", "", "", "", "", ""
        c1, c2, c3, c4, c5, c6, c7 = 1, 1, 1, 1, 1, 1, 1
        for member in ctx.guild.members:
          if member.bot:
            if member.guild_permissions.administrator == True:
                admin += f"[{'0' + str(c1) if c1 < 10 else c1}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c1 += 1
            if member.guild_permissions.ban_members == True:
                ban += f"[{'0' + str(c2) if c2 < 10 else c2}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c2 += 1
            if member.guild_permissions.kick_members == True:
                kick += f"[{'0' + str(c3) if c3 < 10 else c3}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c3 += 1
            if member.guild_permissions.manage_guild == True:
                mgn += f"[{'0' + str(c4) if c4 < 10 else c4}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c4 += 1
            if member.guild_permissions.manage_channels == True:
                mgnch += f"[{'0' + str(c5) if c5 < 10 else c5}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c5 += 1
            if member.guild_permissions.manage_roles == True:
                mgnro += f"[{'0' + str(c6) if c6 < 10 else c6}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c6 += 1
            if member.guild_permissions.mention_everyone == True:
                mention += f"[{'0' + str(c7) if c7 < 10 else c7}] | {member.name} [{member.id}] - Joined At: <t:{round(member.joined_at.timestamp())}:R>\n"
                c7 += 1
        em1 = discord.Embed(title="Administrator Perms", description=admin, color=ctx.author.color)
        try:    
            em1.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em1.set_footer(text=f"Requested by: {ctx.author.name}")
        em2 = discord.Embed(title="Kick Members", description=kick, color=ctx.author.color)
        try:    
            em2.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em2.set_footer(text=f"Requested by: {ctx.author.name}")
        em3 = discord.Embed(title="Ban Members", description=ban, color=ctx.author.color)
        try:    
            em3.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em3.set_footer(text=f"Requested by: {ctx.author.name}")
        em4 = discord.Embed(title="Manager server", description=mgn, color=ctx.author.color)
        try:    
            em4.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em4.set_footer(text=f"Requested by: {ctx.author.name}")
        em5 = discord.Embed(title="Manager Channels", description=mgnch, color=ctx.author.color)
        try:    
            em5.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em5.set_footer(text=f"Requested by: {ctx.author.name}")
        em6 = discord.Embed(title="Manager Roles", description=mgnro, color=ctx.author.color)
        try:    
            em6.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em6.set_footer(text=f"Requested by: {ctx.author.name}")
        em7 = discord.Embed(title="Mention Everyone", description=mention, color=ctx.author.color)
        try:    
            em7.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em7.set_footer(text=f"Requested by: {ctx.author.name}")
        ls.append(em1)
        ls.append(em2)
        ls.append(em3)
        ls.append(em4)
        ls.append(em5)
        ls.append(em6)
        ls.append(em7)
        page = PaginationView(embed_list=ls, ctx=ctx)
        await page.start(ctx)
    
    @scan.command(aliases=['role'], description="Show Permissions of all roles")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def roles(self, ctx):
        ls = []
        admin, ban, kick, mgn, mgnch, mgnro, mention = "", "", "", "", "", "", ""
        c1, c2, c3, c4, c5, c6, c7 = 1, 1, 1, 1, 1, 1, 1
        view = night(ctx)
        hm = await ctx.reply(embed=discord.Embed(description="Which type of role you want to see", color=botinfo.root_color), mention_author=False, view=view)
        await view.wait()
        for role in list(reversed(ctx.guild.roles[:])):
         if view.value == 'both':
           
            if role.permissions.administrator:
                admin += f"[{'0' + str(c1) if c1 < 10 else c1}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c1 += 1
            if role.permissions.ban_members:
                ban += f"[{'0' + str(c2) if c2 < 10 else c2}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c2 += 1
            if role.permissions.kick_members:
                kick += f"[{'0' + str(c3) if c3 < 10 else c3}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c3 += 1
            if role.permissions.manage_guild:
                mgn += f"[{'0' + str(c4) if c4 < 10 else c4}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c4 += 1
            if role.permissions.manage_channels:
                mgnch += f"[{'0' + str(c5) if c5 < 10 else c5}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c5 += 1
            if role.permissions.manage_roles:
                mgnro += f"[{'0' + str(c6) if c6 < 10 else c6}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c6 += 1
            if role.permissions.mention_everyone:
                mention += f"[{'0' + str(c7) if c7 < 10 else c7}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c7 += 1
         elif view.value == 'simple':
          if role.is_bot_managed() is False:
            if role.permissions.administrator:
                admin += f"[{'0' + str(c1) if c1 < 10 else c1}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c1 += 1
            if role.permissions.ban_members:
                ban += f"[{'0' + str(c2) if c2 < 10 else c2}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c2 += 1
            if role.permissions.kick_members:
                kick += f"[{'0' + str(c3) if c3 < 10 else c3}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c3 += 1
            if role.permissions.manage_guild:
                mgn += f"[{'0' + str(c4) if c4 < 10 else c4}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c4 += 1
            if role.permissions.manage_channels:
                mgnch += f"[{'0' + str(c5) if c5 < 10 else c5}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c5 += 1
            if role.permissions.manage_roles:
                mgnro += f"[{'0' + str(c6) if c6 < 10 else c6}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c6 += 1
            if role.permissions.mention_everyone:
                mention += f"[{'0' + str(c7) if c7 < 10 else c7}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c7 += 1
         elif view.value == 'bot':
          if role.is_bot_managed() is True:
            if role.permissions.administrator:
                admin += f"[{'0' + str(c1) if c1 < 10 else c1}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c1 += 1
            if role.permissions.ban_members:
                ban += f"[{'0' + str(c2) if c2 < 10 else c2}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c2 += 1
            if role.permissions.kick_members:
                kick += f"[{'0' + str(c3) if c3 < 10 else c3}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c3 += 1
            if role.permissions.manage_guild:
                mgn += f"[{'0' + str(c4) if c4 < 10 else c4}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c4 += 1
            if role.permissions.manage_channels:
                mgnch += f"[{'0' + str(c5) if c5 < 10 else c5}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c5 += 1
            if role.permissions.manage_roles:
                mgnro += f"[{'0' + str(c6) if c6 < 10 else c6}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c6 += 1
            if role.permissions.mention_everyone:
                mention += f"[{'0' + str(c7) if c7 < 10 else c7}] | {role.name} [{role.id}] - Created At: <t:{round(role.created_at.timestamp())}:R>\n"
                c7 += 1
        no = ""
        if admin == no:
            admin = "No Roles"
        if kick == no:
            kick = "No Roles"
        if ban == no:
            ban = "No Roles"
        if mgn == no:
            mgn = "No Roles"
        if mgnch == no:
            mgnch = "No Roles"
        if mgnro == no:
            mgnro = "No Roles"
        if mention == no:
            mention = "No Roles"
        em1 = discord.Embed(title="Administrator Perms", description=admin, color=ctx.author.color)
        try:    
            em1.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em1.set_footer(text=f"Requested by: {ctx.author.name}")
        em2 = discord.Embed(title="Kick Members", description=kick, color=ctx.author.color)
        try:    
            em2.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em2.set_footer(text=f"Requested by: {ctx.author.name}")
        em3 = discord.Embed(title="Ban Members", description=ban, color=ctx.author.color)
        try:    
            em3.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em3.set_footer(text=f"Requested by: {ctx.author.name}")
        em4 = discord.Embed(title="Manager server", description=mgn, color=ctx.author.color)
        try:    
            em4.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em4.set_footer(text=f"Requested by: {ctx.author.name}")
        em5 = discord.Embed(title="Manager Channels", description=mgnch, color=ctx.author.color)
        try:    
            em5.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em5.set_footer(text=f"Requested by: {ctx.author.name}")
        em6 = discord.Embed(title="Manager Roles", description=mgnro, color=ctx.author.color)
        try:    
            em6.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em6.set_footer(text=f"Requested by: {ctx.author.name}")
        em7 = discord.Embed(title="Mention Everyone", description=mention, color=ctx.author.color)
        try:    
            em7.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        except:
            em7.set_footer(text=f"Requested by: {ctx.author.name}")
        ls.append(em1)
        ls.append(em2)
        ls.append(em3)
        ls.append(em4)
        ls.append(em5)
        ls.append(em6)
        ls.append(em7)
        await hm.delete()
        page = PaginationView(embed_list=ls, ctx=ctx)
        await page.start(ctx)

    @scan.command(aliases=["perms"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def permissions(self, ctx):
        ls = []
        count = 1
        for role in list(reversed(ctx.guild.roles[:])):
            if role.permissions.administrator:
                admin = f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                admin = f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.kick_members:
                kick = f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                kick = f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.ban_members:
                ban = f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                ban = f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.manage_guild:
                server = f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                server = f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.manage_channels:
                channel= f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                channel= f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.manage_roles:
                roles= f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                roles= f"{emojis.enable_no}{emojis.disable_yes}"
            if role.permissions.mention_everyone:
                everyone= f"{emojis.disable_no}{emojis.enable_yes}"
            else:
                everyone= f"{emojis.enable_no}{emojis.disable_yes}"
            em = discord.Embed(title=f"[{count}] - {role.name} [{role.id}]", color=ctx.author.color)
            em.add_field(name="Administrator", value=admin, inline=True)
            em.add_field(name="Kick Members", value=kick, inline=True)
            em.add_field(name="Ban Members", value=ban, inline=True)
            em.add_field(name="Manage Server", value=server, inline=True)
            em.add_field(name="Manage Channels", value=channel, inline=True)
            em.add_field(name="Manage Roles", value=roles, inline=True)
            em.add_field(name="Mention Everyone", value=everyone, inline=True)
            em.add_field(name=f"Total Members in {role.name}", value=f"{len(role.members)} Members", inline=True)
            count+=1
            ls.append(em)
        page = PaginationView(embed_list=ls, ctx=ctx)
        await page.start(ctx)

async def setup(bot):
    await bot.add_cog(moderation(bot))
