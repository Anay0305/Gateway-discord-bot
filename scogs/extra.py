import discord
from discord.ext import commands, tasks
from discord import *
import random
from paginators import PaginationView, PaginatorView
from ast import literal_eval
import database
import emojis
import botinfo
import re
import difflib
from scogs.antinuke import check_lockrole_bypass

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

    @discord.ui.button(emoji=f"{emojis.correct}", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(emoji=f"{emojis.wrong} ", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()

class PngOrGif(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None
        
    @discord.ui.button(label="PNG", custom_id='png', style=discord.ButtonStyle.green)
    async def png(self, interaction, button):
        self.value = 'png'
        self.stop()

    @discord.ui.button(label="GIF", custom_id='gif', style=discord.ButtonStyle.green)
    async def gif(self, interaction, button):
        self.value = 'gif'
        self.stop()

    @discord.ui.button(label="MIX", custom_id='mix', style=discord.ButtonStyle.green)
    async def mix(self, interaction, button):
        self.value = 'mix'
        self.stop()

    @discord.ui.button(label="STOP", custom_id='stop', style=discord.ButtonStyle.danger)
    async def cancel(self, interaction, button):
        self.value = 'stop'
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
   
    @discord.ui.button(label="Cancel", custom_id='cancel', style=discord.ButtonStyle.gray)
    async def cancel(self, interaction, button):
        self.value = 'cancel'
        self.stop()

async def autopfp(self, c_id, type):
    if len(self.bot.users) < 1000:
        u = random.sample(self.bot.users, len(self.bot.users))
    else:
        u = random.sample(self.bot.users, 1000)
    c = 1
    channel = self.bot.get_channel(c_id)
    if channel is None:
        return
    if not channel.permissions_for(channel.guild.me).send_messages:
        return
    for i in u:
        if i.avatar and c <= 10:
          if type != 'mix':
            if type in i.avatar.url:
                try:
                    await channel.send(i.avatar.url)
                except:
                    return
                c += 1
          else:
                try:
                    await channel.send(i.avatar.url)
                except:
                    return
                c += 1
    del u

async def get_prefix(message: discord.Message):
    res = database.fetchone("prefix", "prefixes", "guild_id", message.guild.id)
    if res:
      prefix = str(res[0])
    if not res:
      prefix = '?'
    try:
        res1 = database.fetchone("*", "noprefix", "user_id", message.author.id)
        if res1 is not None:
            if res1['servers'] is not None:
                no_prefix = literal_eval(res1['servers'])
                if message.guild.id in no_prefix:
                    return [f"<@{message.guild.me.id}>", prefix, ""]
            if res1['main'] is not None:
                if res1['main'] == 1:
                    return [f"<@{message.guild.me.id}>", prefix, ""]
    except:
        pass
    return [f"<@{message.guild.me.id}>", prefix]

async def by_cmd(ctx, user: discord.Member, cmd):
    ig_db = database.fetchone("*", "bypass", "guild_id", ctx.guild.id)
    if ig_db is None:
        return False
    xd = literal_eval(ig_db['bypass_users'])
    xdd = literal_eval(ig_db['bypass_roles'])
    xddd = literal_eval(ig_db['bypass_channels'])
    if user.id not in xd:
        pass
    else:
        ls = xd[user.id]
        if 'cmd' in ls:
          lss = ls['cmd']
          if lss == "all":
              return True
          elif cmd in lss:
              return True
          else:
              pass
    for i in user.roles:
        if i.id in xdd:
            ls = xdd[i.id]
            if 'cmd' in ls:
              lss = ls['cmd']
              if lss == "all":
                  return True
              elif cmd in lss:
                  return True
              else:
                  pass
    if ctx.channel.id not in xddd:
      pass
    else:
        ls = xddd[ctx.channel.id]
        if 'cmd' in ls:
          lss = ls['cmd']
          if lss == "all":
              return True
          elif cmd in lss:
              return True
          else:
              pass
    return False

async def by_module(ctx, user: discord.Member, module):
    ig_db = database.fetchone("*", "bypass", "guild_id", ctx.guild.id)
    if ig_db is None:
        return False
    xd = literal_eval(ig_db['bypass_users'])
    xdd = literal_eval(ig_db['bypass_roles'])
    xddd = literal_eval(ig_db['bypass_channels'])
    if user.id not in xd:
        pass
    else:
        ls = xd[user.id]
        if 'module' in ls:
          lss = ls['module']
          if lss == "all":
              return True
          elif module in lss:
              return True
          else:
              pass
    for i in user.roles:
        if i.id in xdd:
            ls = xdd[i.id]
            if 'module' in ls:
              lss = ls['module']
              if lss == "all":
                  return True
              elif module in lss:
                  return True
              else:
                  pass
    if ctx.channel.id not in xddd:
      pass
    else:
        ls = xddd[ctx.channel.id]
        if 'module' in ls:
          lss = ls['module']
          if lss == "all":
              return True
          elif module in lss:
              return True
          else:
              pass
    return False

async def by_channel(ctx, user: discord.Member, channel: discord.TextChannel):
    ig_db = database.fetchone("*", "bypass", "guild_id", ctx.guild.id)
    if ig_db is None:
        return False
    xd = literal_eval(ig_db['bypass_users'])
    xdd = literal_eval(ig_db['bypass_roles'])
    if user.id not in xd:
        pass
    else:
        ls = xd[user.id]
        if 'channel' in ls:
          lss = ls['channel']
          if lss == "all":
              return True
          elif channel.id in lss:
              return True
          else:
              pass
    try:
        for i in user.roles:
            if i.id in xdd:
                ls = xdd[i.id]
                if 'channel' in ls:
                    lss = ls['channel']
                    if lss == "all":
                        return True
                    elif channel.id in lss:
                        return True
                    else:
                        pass
    except:
        pass
    return False

async def by_role(ctx, user: discord.Member, role: discord.Role):
    ig_db = database.fetchone("*", "bypass", "guild_id", ctx.guild.id)
    if ig_db is None:
        return False
    xd = literal_eval(ig_db['bypass_users'])
    xdd = literal_eval(ig_db['bypass_roles'])
    xddd = literal_eval(ig_db['bypass_channels'])
    if user.id not in xd:
        pass
    else:
        ls = xd[user.id]
        if 'role' in ls:
          lss = ls['role']
          if lss == "all":
              return True
          elif role.id in lss:
              return True
          else:
              pass
    for i in user.roles:
        if i.id in xdd:
            ls = xdd[i.id]
            if 'role' in ls:
              lss = ls['role']
              if lss == "all":
                  return True
              elif role.id in lss:
                  return True
              else:
                  pass
    if ctx.channel.id not in xddd:
      pass
    else:
        ls = xddd[ctx.channel.id]
        if 'role' in ls:
          lss = ls['role']
          if role.id in lss:
              return True
          elif lss == "all":
              return True
          else:
              pass
    return False

class extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autopfp_task.start()

    @tasks.loop(minutes=10)
    async def autopfp_task(self):
        await self.bot.wait_until_ready()
        pfp_db = database.fetchall1("*", "pfp")
        for i, j, k in pfp_db:
            await autopfp(self, j, k)

    @commands.group(
        invoke_without_command=True, description="Shows The help menu for pfp"
    )
    async def pfp(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}pfp`\n" 
                                                  f"Shows The help menu for pfp\n\n" 
                                                  f"`{prefix}pfp auto enable <channel>`\n" 
                                                  f"Sends pfp automatically every 2 mins\n\n"
                                                  f"`{prefix}pfp auto disable`\n"
                                                  f"Stops sending pfp\n\n"
                                                  f"`{prefix}pfp random <number>`\n" 
                                                  f"Sends random pfps\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)
    
    @pfp.group(invoke_without_command=True, description="Shows The help menu for pfp auto")
    async def auto(self, ctx):
        prefix = database.get_guild_prefix(ctx.guild.id)
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}pfp auto`\n" 
                                                  f"Shows The help menu for pfp auto\n\n" 
                                                  f"`{prefix}pfp auto enable <channel>`\n" 
                                                  f"Sends pfp automatically every 2 mins\n\n"
                                                  f"`{prefix}pfp auto disable`\n"
                                                  f"Stops sending pfp\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @auto.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx: commands.Context, *, channel: discord.TextChannel):
        view = PngOrGif(ctx)
        em = discord.Embed(description="Which type of pfp you want?\n**Note: The profile pictures may include expicit content as we are giving you profile picture of random users, So if you dont agree to it you can cancel the command.**", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        init = await ctx.reply(embed=em, view=view)
        await view.wait()
        if view.value == 'stop':
            return await init.delete()
        pfp_db = database.fetchone("*", "pfp", "guild_id", ctx.guild.id)
        if pfp_db is None:
            val = (ctx.guild.id, channel.id, view.value)
            database.insert("pfp", "guild_id, channel_id, 'type'", val)
        else:
            return await ctx.reply("It is already enabled")
        await init.delete()
        await ctx.reply(f"Now 5-10 profile pictures will be send in every 10 minutes in {channel.mention}.")
        await autopfp(self, channel.id, view.value)

    @auto.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx: commands.Context):
        pfp_db = database.fetchone("*", "pfp", "guild_id", ctx.guild.id)
        if pfp_db is not None:
            database.delete("pfp", "guild_id", ctx.guild.id)
        else:
            return await ctx.reply(f"It was already disabled")
        await ctx.reply(f"Now no profile pictures will be send.")

    @pfp.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def random(self, ctx: commands.Context, *, number):
        if number.isdigit():
            number = int(number)
        else:
            return await ctx.reply("Please provide a valid number")
        if abs(number) > 15:
            return await ctx.reply("The limit is only for 15 profile pictures")
        view = PngOrGif(ctx)
        em = discord.Embed(description="Which type of pfp you want?\n**Note: The profile pictures may include expicit content as we are giving you profile picture of random users, So if you dont agree to it you can cancel the command.**", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        init = await ctx.reply(embed=em, view=view)
        await view.wait()
        if view.value == 'stop':
            return await init.delete()
        if len(self.bot.users) < 10000:
            u = random.sample(self.bot.users, len(self.bot.users))
        else:
            u = random.sample(self.bot.users, 10000)
        if view.value == 'mix':
            await init.delete()
            c = 1
            for i in u:
                if i.avatar and c <= abs(number):
                        await ctx.send(i.avatar.url)
                        c += 1
        if view.value == 'png':
            await init.delete()
            c = 1
            for i in u:
                if i.avatar and c <= abs(number):
                    if 'png' in i.avatar.url:
                        await ctx.send(i.avatar.url)
                        c += 1
        if view.value == 'gif':
            await init.delete()
            c = 1
            for i in u:
                if i.avatar and c <= abs(number):
                    if 'gif' in i.avatar.url:
                        await ctx.send(i.avatar.url)
                        c += 1
        del u

    @commands.group(
        invoke_without_command=True, description="Shows The help menu for nightmode"
    )
    async def nightmode(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}nightmode`\n" 
                                                  f"Shows The help menu for nightmode\n\n" 
                                                  f"`{prefix}nightmode enable <perm>`\n" 
                                                  f"Take perms from every role that is below the bot\n\n"
                                                  f"`{prefix}nightmode disable`\n"
                                                  f"Give the role their permissions back\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @nightmode.command(name="enable", aliases=['on'], description="Enables nightmode for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(administrator=True)
    async def _enable(self, ctx, *, perms):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        valid = ['All', 'Admin', 'Kick', 'Ban', 'Manage server', 'Manage channels', 'Manage roles', 'Mention everyone']
        if perms.capitalize() not in valid:
            return await ctx.reply(f"Please give a valid perm to remove\nValid perms are {', '.join(valid)}")
        perms = perms.lower()
        prefix = database.get_guild_prefix(ctx.guild.id)
        imp_db = database.fetchone("*", "imp", "guild_id", ctx.guild.id)
        valid = ['all', 'admin', 'kick', 'ban', 'manage server', 'manage channels', 'manage roles', 'mention everyone']
        if imp_db['cmd'] in valid:
            em = discord.Embed(description=f"Nightmode is already enabled please kindly do `{prefix}nightmode off`", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
        adm, ki, ba, server, ch, ro, every = [], [], [], [], [], [], []
        view = night(ctx)
        em = discord.Embed(description="From which type of roles you want to remove Perms\nNote: Be sure that the top role of Bot has **Adminstrator Perms** and is **Whitelisted** from every anti-nuke bot Before clicking any of the buttons because during turning on the nightmode if bot gets kick/ban the changes wont be reversed", color=botinfo.root_color)
        ok = await ctx.reply(embed=em, view=view, mention_author=False)
        await view.wait()
        if not view.value:
            await ok.delete()
            return await ctx.reply("Timed out!", mention_author=True)
        if view.value == 'cancel':
            await ok.delete()
            em = discord.Embed(description=f"Successfully cancelled the command", color=botinfo.root_color)
            return await ctx.reply(embed=em)
        if view.value == 'simple':
            await ok.delete()
            if perms == 'all':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False, ban_members=False, manage_guild=False, mention_everyone=False, administrator = False, manage_roles=False, manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed every Dangerous perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'admin':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        permission = role.permissions
                        permission.update(administrator=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed admin perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'kick':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Kick perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'ban':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        permission = role.permissions
                        permission.update(ban_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Ban perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage server':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        permission = role.permissions
                        permission.update(manage_guild=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage server perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage channels':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        permission = role.permissions
                        permission.update(manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Channels perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage roles':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        permission = role.permissions
                        permission.update(manage_roles=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Roles perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'mention everyone':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is False:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(mention_everyone=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Mention everyone perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
        if view.value == 'bot':
            await ok.delete()
            if perms == 'all':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False, ban_members=False, manage_guild=False, mention_everyone=False, administrator = False, manage_roles=False, manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed every Dangerous perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'admin':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        permission = role.permissions
                        permission.update(administrator=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed admin perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'kick':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Kick perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'ban':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        permission = role.permissions
                        permission.update(ban_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Ban perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage server':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        permission = role.permissions
                        permission.update(manage_guild=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage server perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage channels':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        permission = role.permissions
                        permission.update(manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Channels perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage roles':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        permission = role.permissions
                        permission.update(manage_roles=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Roles perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'mention everyone':
                for role in ctx.guild.roles:
                  if role.is_bot_managed() is True:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(mention_everyone=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Mention everyone perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
        if view.value == 'both':
            await ok.delete()
            if perms == 'all':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False, ban_members=False, manage_guild=False, mention_everyone=False, administrator = False, manage_roles=False, manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed every Dangerous perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'admin':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.administrator:
                            adm.append(role.id)
                        permission = role.permissions
                        permission.update(administrator=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed admin perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'kick':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.kick_members:
                            ki.append(role.id)
                        permission = role.permissions
                        permission.update(kick_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Kick perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'ban':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.ban_members:
                            ba.append(role.id)
                        permission = role.permissions
                        permission.update(ban_members=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Ban perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage server':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_guild:
                            server.append(role.id)
                        permission = role.permissions
                        permission.update(manage_guild=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage server perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage channels':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_channels:
                            ch.append(role.id)
                        permission = role.permissions
                        permission.update(manage_channels=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Channels perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'manage roles':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.manage_roles:
                            ro.append(role.id)
                        permission = role.permissions
                        permission.update(manage_roles=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Manage Roles perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
            if perms == 'mention everyone':
                for role in ctx.guild.roles:
                    if role.position < ctx.guild.me.top_role.position:
                        if role.permissions.mention_everyone:
                            every.append(role.id)
                        permission = role.permissions
                        permission.update(mention_everyone=False)
                        await role.edit(permissions=permission, reason="Enabled Nightmode")
                await ctx.reply(embed=discord.Embed(description=f"Removed Mention everyone perms from every Role that is Below me\nRun `{prefix}nightmode off` to give back permissions to the roles", color=botinfo.root_color),mention_author=False)
        dic = {}
        dic['cmd'] = f"{perms}"
        if len(adm) != 0:
            dic['admin'] = f"{adm}"
        if len(ki) != 0:
            dic['kick'] = f"{ki}"
        if len(ba) != 0:
            dic['ban'] = f"{ba}"
        if len(server) != 0:
            dic['mgn'] = f"{server}"
        if len(ch) != 0:
            dic['mgnch'] = f"{ch}"
        if len(ro) != 0:
            dic['mgnro'] = f"{ro}"
        if len(every) != 0:
            dic['mention'] = f"{every}"
        database.update_bulk("imp", dic, "guild_id", ctx.guild.id)

    @nightmode.command(name='disable', aliases=['off'], description="Disables nightmode for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(administrator=True)
    async def _disable(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        prefix = database.get_guild_prefix(ctx.guild.id)
        imp_db = database.fetchone("*", "imp", "guild_id", ctx.guild.id)
        valid = ['all', 'admin', 'kick', 'ban', 'manage server', 'manage channels', 'manage roles', 'mention everyone']
        if imp_db['cmd'] not in valid:
            em = discord.Embed(description=f"Nightmode is already disabled please kindly do `{ctx.prefix}nightmode on <perm>`", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
        adm = imp_db['admin']
        ki = imp_db['kick']
        ba = imp_db['ban']
        server = imp_db['mgn']
        ch = imp_db['mgnch']
        ro = imp_db['mgnro']
        every = imp_db['mention']
        cm = imp_db['cmd']
        if cm == 'all':
            for role in ctx.guild.roles:
                if f"{role.id}" in adm:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.administrator:
                            permission = role.permissions
                            permission.update(administrator=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in ki:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.kick_members:
                            permission = role.permissions
                            permission.update(kick_members=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in ba:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.ban_members:
                            permission = role.permissions
                            permission.update(ban_members=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in server:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_guild:
                            permission = role.permissions
                            permission.update(manage_guild=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in ch:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_channels:
                            permission = role.permissions
                            permission.update(manage_channels=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in ro:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_roles:
                            permission = role.permissions
                            permission.update(manage_roles=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
                if f"{role.id}" in every:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.mention_everyone:
                            permission = role.permissions
                            permission.update(mention_everyone=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'admin':
            for role in ctx.guild.roles:
                if f"{role.id}" in adm:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.administrator:
                            permission = role.permissions
                            permission.update(administrator=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Admin permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'kick':
            for role in ctx.guild.roles:
                if f"{role.id}" in ki:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.kick_members:
                            permission = role.permissions
                            permission.update(kick_members=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Kick permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'ban':
            for role in ctx.guild.roles:
                if f"{role.id}" in ba:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.ban_members:
                            permission = role.permissions
                            permission.update(ban_members=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Ban permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'manage server':
            for role in ctx.guild.roles:
                if f"{role.id}" in server:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_guild:
                            permission = role.permissions
                            permission.update(manage_guild=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Manage server permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'manage channels':
            for role in ctx.guild.roles:
                if f"{role.id}" in ch:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_channels:
                            permission = role.permissions
                            permission.update(manage_channels=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Manage channels permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'manage roles':
            for role in ctx.guild.roles:
                if f"{role.id}" in ro:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.manage_roles:
                            permission = role.permissions
                            permission.update(manage_roles=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Manage roles permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        if cm == 'manage everyone':
            for role in ctx.guild.roles:
                if f"{role.id}" in every:
                    if role.position < ctx.guild.me.top_role.position:
                        if not role.permissions.mention_everyone:
                            permission = role.permissions
                            permission.update(mention_everyone=True)
                            await role.edit(permissions=permission, reason="Disabled Nightmode")
            await ctx.reply(embed=discord.Embed(description=f"Given Mention everyone permissions back to All the roles Below me\nRun `{prefix}nighmode enable <perms>` to Enable Night Mode", color=botinfo.root_color), mention_author=False)
        dic = {}
        dic['cmd'] = 0
        if cm == 'all':
            dic['admin'] = 0
            dic['kick'] = 0
            dic['ban'] = 0
            dic['mgn'] = 0
            dic['mgnch'] = 0
            dic['mgnro'] = 0
            dic['mention'] = 0
        if cm == 'admin':
            dic['admin'] = 0
        if cm == 'kick':
            dic['kick'] = 0
        if cm == 'ban':
            dic['ban'] = 0
        if cm == 'manage server':
            dic['mgn'] = 0
        if cm == 'manage channels':
            dic['mgnch'] = 0
        if cm == 'manage roles':
            dic['mgnro'] = 0
        if cm == 'mention everyone':
            dic['mention'] = 0
        database.update_bulk("imp", dic, "guild_id", ctx.guild.id)

    @commands.group(invoke_without_command=True, description="Custom role setup for the server")
    async def setup(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        setupem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}setup`\n"
                                                 f"This Command Will Show This Page\n\n"
                                                 f"`{prefix}setup reqrole`\n"
                                                 f"It will setup the required role to run some custom role commands\n\n"
                                                 f"`{prefix}setup create`\n"
                                                 f"To add an alias for giving and taking specific roles\n\n"
                                                 f"`{prefix}setup delete`\n"
                                                 f"To remove an alias from giving and taking specific roles\n\n"
                                                 f"`{prefix}setup official`\n"
                                                 f"Set The Official role\n\n"
                                                 f"`{prefix}setup friend`\n"
                                                 f"Set The Friend role\n\n"
                                                 f"`{prefix}setup guest`\n"
                                                 f"Set the Guest role\n\n"
                                                 f"`{prefix}setup vip`\n"
                                                 f"Set the Vip role.\n\n"
                                                 f"`{prefix}setup girl`\n"
                                                 f"Set the Girl role\n\n"
                                                 f"`{prefix}setup config`\n" 
                                                 f"Shows The current Custom role Settings For the server\n\n"
                                                 f"`{prefix}setup reset`\n" 
                                                 f"Resets the Custom Role Settings For the server")
        setupem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        setupem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        setup_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
        official = setup_db['official']
        friend = setup_db['friend']
        guest = setup_db['guest']
        vip = setup_db['vip']
        girl = setup_db['girls']
        if official == 0:
          off = f"Official role is not set"
          roff = f"Official role is not set"
        else:
          off = f"Gives <@&{official}> to member"
          roff = f"Removes <@&{official}> from member"
        if friend == 0:
          fr = f"Friend role is not set"
          rfr = f"Friend role is not set"
        else:
          fr = f"Gives <@&{friend}> to member"
          rfr = f"Removes <@&{friend}> from member"
        if guest == 0:
          gu = f"Guest role is not set"
          rgu = f"Guest role is not set"
        else:
          gu = f"Gives <@&{guest}> to member"
          rgu = f"Removes <@&{guest}> from member"
        if vip == 0:
          vi = f"Vip role is not set"
          rvi = f"Vip role is not set"
        else:
          vi = f"Gives <@&{vip}> to member"
          rvi = f"Removes <@&{vip}> from member"
        if girl == 0:
          gir = f"Girl role is not set"
          rgir = f"Girl role is not set"
        else:
          gir = f"Gives <@&{girl}> to member"
          rgir = f"Removes <@&{girl}> from member"
        setupem1 = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}official <member>`\n"
                                                 f"{off}\n\n"
                                                 f"`{prefix}friend <member>`\n"
                                                 f"{fr}\n\n"
                                                 f"`{prefix}guest <member>`\n"
                                                 f"{gu}\n\n"
                                                 f"`{prefix}vip <member>`\n"
                                                 f"{vi}\n\n"
                                                 f"`{prefix}girl <member>`\n"
                                                 f"{gir}\n\n"
                                                 f"`{prefix}rofficial <member>`\n"
                                                 f"{roff}\n\n"
                                                 f"`{prefix}rfriend <member>`\n"
                                                 f"{rfr}\n\n"
                                                 f"`{prefix}rguest <member>`\n"
                                                 f"{rgu}\n\n"
                                                 f"`{prefix}rvip <member>`\n"
                                                 f"{rvi}\n\n"
                                                 f"`{prefix}rgirl <member>`\n"
                                                 f"{rgir}\n\n")
        setupem1.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        setupem1.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        em_list = []
        em_list.append(setupem)
        em_list.append(setupem1)
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @setup.command(name="reset", description="Reset custom role settings for the server")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx, *, option):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if not option:
                await ctx.reply("Mention a badge to Remove")
            msg = option
            msg = msg.lower()
            valid = ["all", "reqrole", "custom", "official", "officials", "staff", "staffs", "friend", "friends", "guest", "guests", "girls", "girl", "vip", "vips"]
            if msg not in valid:
                return await ctx.send("Please send A valid Option\nValid Options ARE: All, Reqrole, Custom, Official/Staff, Friend, Guest, Vip, Girl")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if msg == "reqrole":
              msg = "role"
            if msg == "staff":
              msg = "official"
            if msg == "staffs":
              msg = "official"
            if msg == "officials":
              msg = "official"
            if msg == "friends":
              msg = "friend"
            if msg == "girl":
              msg = "girls"
            if msg == "vips":
              msg = "vip"
            if msg == "guests":
              msg = "guest"
            if msg == "all":
                if welcome_db == 0:
                    msg = msg.upper()
                    return await ctx.send(f"{msg} Is Not set")
                else:
                    dic = {
                        'role': 0,
                        'official': 0,
                        'friend': 0,
                        'guest': 0,
                        'vip': 0,
                        'girls': 0,
                        'custom': "{}"
                    }
                    database.update_bulk("roles", dic, "guild_id", ctx.guild.id)
                return await ctx.send(f"{ctx.author.mention} I Reset The Custom Role settings for : {ctx.guild.name}")
            if welcome_db == 0 or welcome_db is None:
                msg = msg.upper()
                return await ctx.send(f"{msg} Is Not set")
            else:
                if msg == "official" or msg == "custom":
                    if msg == "official":
                        dic = {
                            'official': 0
                        }
                        database.update_bulk("roles", dic, "guild_id", ctx.guild.id)
                    elif msg == "custom":
                        database.update("roles", "custom", "{}", "guild_id", ctx.guild.id)
                else:
                    database.update("roles", msg, 0, "guild_id", ctx.guild.id)
            msg = msg.title()
            return await ctx.send(f"{ctx.author.mention} I Reset {msg} for : {ctx.guild.name}")

    @setup.command(name="config", description="Shows the current custom role settings for the server")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db is None:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
            reqrole = welcome_db['role']
            official = welcome_db['official']
            friend = welcome_db['friend']
            guest = welcome_db['guest']
            vip = welcome_db['vip']
            girl = welcome_db['girls']
            if reqrole == 0:
              rr = f"Required Role is not set"
            else:
              rr = f"<@&{reqrole}>"
            if official == 0:
              off = f"Official role is not set"
            else:
              off = f"<@&{official}>"
            if friend == 0:
              fr = f"Friend Role is not set"
            else:
              fr = f"<@&{friend}>"
            if guest == 0:
              gu = f"Guest role is not set"
            else:
              gu = f"<@&{guest}>"
            if vip == 0:
              vi = f"Vip role is not set"
            else:
              vi = f"<@&{vip}>"
            if girl == 0:
              gir = f"Girl role is not set"
            else:
              gir = f"<@&{girl}>"
            embed = discord.Embed(title=f"Custom roles Settings For {ctx.guild.name}", color=botinfo.root_color)
            embed.add_field(name="Required Role:", value=rr)
            embed.add_field(name="Friend Role:", value=fr)
            embed.add_field(name="Official Role:", value=off)
            embed.add_field(name="Guest Role:", value=gu)
            embed.add_field(name="Vip Role:", value=vi)
            embed.add_field(name="Girl Role:", value=gir)
            c = True
            if c:
                ls = literal_eval(welcome_db['custom'])
                des = ""
                for i in ls:
                    r = discord.utils.get(ctx.guild.roles, id=ls[i])
                    if r is None:
                        ro = "Role was deleted"
                    else:
                        ro = r.mention
                    des+=f"{i.capitalize()}: {ro}\n"
                if des == "":
                    des = "No custom alias"
                embed.add_field(name="Custom Aliases", value=des, inline=False)
            await ctx.send(embed=embed)

    @setup.group(aliases=["requiredrole", "modrole"], description="Setups the required role for the server")
    @commands.has_permissions(administrator=True)
    async def reqrole(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db is None:
              val = (ctx.guild.id, role.id)
              database.insert("roles", "guild_id, role", val)
            else:
              database.update("roles", "role", role.id, "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Reqiured role role to run custom role commands is set to {role.mention}", color=botinfo.root_color)
            await ctx.reply(embed=em, mention_author=False)
            
    @setup.command(name="create", aliases=['add'], description="To add alias for giving and taking specific roles")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_create(self, ctx: commands.Context, alias, *, role: discord.Role):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if role.position >= ctx.guild.me.top_role.position:
            em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
        if not role.is_assignable():
            em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
        if welcome_db['role'] == 0:
            return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
        else:
            ls = literal_eval(welcome_db['custom'])
            if alias.lower() in ls:
                r = ls[alias.lower()]
                return await ctx.reply(embed=discord.Embed(description=f"There is already a custom alias with {alias} which is assigning {r.mention}", color=botinfo.root_color))
            elif self.bot.get_command(alias.lower()):
                return await ctx.reply(embed=discord.Embed(description=f"There is a bot command with {alias} try with any other alias", color=botinfo.root_color))
            else:
                ls[alias.lower()] = role.id
                database.update("roles", "custom", f"{ls}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Custom alias {alias.capitalize()} is set to {role.mention}\nJust type `{alias.lower()} <member>` to give or `r{alias.lower()} <member>` to take {role.mention}", color=botinfo.root_color)
            await ctx.reply(embed=em, mention_author=False)
            
    @setup.command(name="delete", aliases=['remove'], description="To remove alias for giving and taking specific roles")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_delete(self, ctx: commands.Context, alias):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
        if welcome_db['role'] == 0:
            return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
        else:
            ls = literal_eval(welcome_db['custom'])
            if alias.lower() not in ls:
                r = ls[alias.lower()]
                return await ctx.reply(embed=discord.Embed(description=f"There is not a custom alias with {alias} which is assigning any role", color=botinfo.root_color))
            elif len(ls) >= 20:
                return await ctx.reply(embed=discord.Embed(description=f"Only 20 custom aliases can be added in the server", color=botinfo.root_color))
            else:
                del ls[alias.lower()]
                database.update("roles", "custom", f"{ls}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Custom alias {alias.capitalize()} is removed from assigning any role", color=botinfo.root_color)
            await ctx.reply(embed=em, mention_author=False)

    @setup.command(name="staff", aliases=['staffs', 'official', 'officials'], description="Setups the staff role for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_staff(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['role'] == 0:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
            else:
                database.update("roles", "official", role.id, "guild_id", ctx.guild.id)
                em = discord.Embed(description=f"Official role is set to {role.mention}\nJust type `official <member>` to give or `rofficial <member>` to take {role.mention}", color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)

    @setup.command(name="friend", aliases=['firends'], description="Setups the friend role for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_friend(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['role'] == 0:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
            else:
                database.update("roles", "friend", role.id, "guild_id", ctx.guild.id)
                em = discord.Embed(description=f"Friend role is set to {role.mention}\nJust type `friend <member>` to give or `rfriend <member>` to take {role.mention}", color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)

    @setup.command(name="vip", aliases=['vips'], description="Setups the vip role for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_vip(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['role'] == 0:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`', mention_author=False)
            else:
                database.update("roles", "vip", role.id, "guild_id", ctx.guild.id)
                em = discord.Embed(description=f"Vip role is set to {role.mention}\nJust type `vip <member>` to give or `rvip <member>` to take {role.mention}", color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)

    @setup.command(name="guest", aliases=['guests'], description="Setups the guest role for the server")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setup_guest(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['role'] == 0:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
            else:
                database.update("roles", "guest", role.id, "guild_id", ctx.guild.id)
                em = discord.Embed(description=f"Guest role is set to {role.mention}\nJust type `guest <member>` to give or `rguest <member>` to take {role.mention}", color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)

    @setup.command(name="girl", aliases=['girls'], description="Setups the girl role for the server")
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def setup_girl(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.send(embed=em)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['role'] == 0:
                return await ctx.reply('First setup Your required role by Running `-setup reqrole @role/id`')
            if welcome_db['girls'] is not None:
                database.update("roles", "girls", role.id, "guild_id", ctx.guild.id)
                em = discord.Embed(description=f"Girl role is set to {role.mention}\nJust type `girl <member>` to give or `rgirl <member>` to take {role.mention}", color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)

    @commands.command(name="staff", aliases=['staffs', 'official', 'officials'], description="Gives the staff role to the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def _staff(self, ctx: commands.Context, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['official'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Official Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['official'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role in user.roles:
                await user.remove_roles(Role)
                em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
                return await ctx.send(embed=em)
            await user.add_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(name="friend", aliases=['friends'], description="Gives the friend role to the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def _friend(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['friend'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Friend Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['friend'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role in user.roles:
                await user.remove_roles(Role)
                em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
                return await ctx.send(embed=em)
            await user.add_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(name="vip", aliases=['vips'], description="Gives vip role to the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def _vip(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['vip'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Vip Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['vip'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role in user.roles:
                await user.remove_roles(Role)
                em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
                return await ctx.send(embed=em)
            await user.add_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(name="guest", aliases=['guests'], description="Gives guest role to the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def _guest(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['guest'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Guest Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['guest'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role in user.roles:
                await user.remove_roles(Role)
                em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
                return await ctx.send(embed=em)
            await user.add_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(name="girl", aliases=['girls'], description="Gives girl role to the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def _girls(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['girls'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Girl Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['girls'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role in user.roles:
                await user.remove_roles(Role)
                em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
                return await ctx.send(embed=em)
            await user.add_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(aliases=['rstaffs', 'rofficial', 'rofficials'], description="Removes the staff role from the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rstaff(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['official'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Official Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['official'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            await user.remove_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(aliases=['rfriends'], description="Removes the friend role from the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rfriend(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['friend'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Official Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['friend'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            await user.remove_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)
            
    @commands.command(aliases=["rvips"], description="Removes the vip role from the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rvip(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['vip'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Vip Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['vip'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            await user.remove_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(aliases=["rguests"], description="Removes the guest role from the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rguest(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['guest'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Guest Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['guest'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            await user.remove_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.command(aliases=["rgirls"], description="Removes the girls role from the user")
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rgirl(self, ctx, user: discord.Member):
            if user.id == ctx.author.id:
                return await ctx.reply("You cant change your own roles")
            welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
            if welcome_db['girls'] == 0:
                em = discord.Embed(description=f"{emojis.wrong} Girl Role Is Not Set.", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
            RRole = discord.utils.get(ctx.guild.roles, id=welcome_db['role'])
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if RRole not in ctx.author.roles:
                  em = discord.Embed(description=f"{emojis.wrong} You need {RRole.mention} role to use this command.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            Role = discord.utils.get(ctx.guild.roles, id=welcome_db['girls'])
            if Role is None:
                  em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            if Role.position >= ctx.guild.me.top_role.position:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            c = check_lockrole_bypass(Role, ctx.guild, ctx.author)
            if not c:
                  em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                  return await ctx.send(embed=em)
            await user.remove_roles(Role)
            em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {user.mention}", color=ctx.author.color)
            await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()
        if message.guild is None:
            return
        ctx = await self.bot.get_context(message)
        if isinstance(message.channel, discord.DMChannel):
            return
        if not message.guild.me.guild_permissions.read_messages:
            return
        if not message.guild.me.guild_permissions.read_message_history:
            return
        if not message.guild.me.guild_permissions.view_channel:
            return
        if not message.guild.me.guild_permissions.send_messages:
            return
        welcome_db = database.fetchone("*", "roles", "guild_id", ctx.guild.id)
        content = ""
        if welcome_db is not None:
            ls = literal_eval(welcome_db['custom'])
            content = message.content.lower()
        else:
            return
        c = True
        if message.guild.me.guild_permissions.manage_roles:
            if not c:
                pass
            else:
                ig_db = database.fetchone("*", "ignore", "guild_id", ctx.guild.id)
                if ig_db is not None:
                    xd = literal_eval(ig_db['user'])
                    if message.author.id in xd:
                        return
                    xdd = literal_eval(ig_db['channel'])
                    c_channel = await by_channel(ctx, message.author, message.channel)
                    if message.channel.id in xdd and not c_channel:
                        return
                    xddd = literal_eval(ig_db['role'])
                    oke = discord.utils.get(message.guild.members, id=message.author.id)
                    if oke is not None:
                        for i in message.author.roles:
                            if i.id in xddd:
                                c_role = await by_role(ctx, message.author, i)
                                if not c_role:
                                    return
                pre = await get_prefix(message)
                check = False
                for k in pre:
                    if content.startswith(k):
                        content = content.replace(k, "").strip()
                        check = True
                        prefix = k
                for i in ls:
                    if (content.startswith(f"{i} ") or content.startswith(f"r{i} ") or content == i or content == "r"+i) and check:
                        u = None
                        for j in message.mentions:
                            if j.bot:
                                continue
                            else:
                                u = j
                                break
                        x = r"<@?([0-9]+)>"
                        xxx = re.findall(x, message.content)
                        if len(xxx) == 0:
                            if u is None:
                                if content.startswith(f"{i} ") or content == i:
                                    em = discord.Embed(description=f"{emojis.wrong} You forgot to mention the user argument.\nDo it like: `{prefix}{i} <user>`", color=botinfo.wrong_color)
                                if content.startswith(f"r{i} ") or content == "r"+i:
                                    em = discord.Embed(description=f"{emojis.wrong} You forgot to mention the user argument.\nDo it like: `{prefix}r{i} <user>`", color=botinfo.wrong_color)
                                return await ctx.reply(embed=em, delete_after=7)
                            else:
                                return
                        if u.id == message.author.id:
                            em = discord.Embed(description=f"{emojis.wrong} You cant change your own roles", color=botinfo.wrong_color)
                            return await ctx.reply(embed=em, delete_after=7)
                        else:
                            r = discord.utils.get(message.guild.roles, id=welcome_db['role'])
                            if r is None:
                                pass
                            else:
                                if r not in message.author.roles:
                                    em = discord.Embed(description=f"{emojis.wrong} You need {r.mention} role to use this command.", color=botinfo.wrong_color)
                                    return await ctx.reply(embed=em, delete_after=7)
                                Role = discord.utils.get(ctx.guild.roles, id=ls[i])
                                if Role is None:
                                    em = discord.Embed(description=f"{emojis.wrong} The role is Deleted.", color=botinfo.wrong_color)
                                    return await ctx.send(embed=em, delete_after=7)
                                if Role.position >= ctx.guild.me.top_role.position:
                                    em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is above my top role.", color=botinfo.wrong_color)
                                    return await ctx.send(embed=em, delete_after=7)
                                c = check_lockrole_bypass(Role, ctx.guild, discord.utils.get(message.guild.members, id=message.author.id))
                                if not c:
                                    em = discord.Embed(description=f"{emojis.wrong} {Role.mention} is a locked role and you cannot assign or remove it unless your whitelisted for it.", color=botinfo.wrong_color)
                                    return await ctx.send(embed=em)
                                elif Role in u.roles:
                                    await u.remove_roles(Role)
                                    em=discord.Embed(description=f"{emojis.correct} Successfully Removed {Role.mention} from {u.mention}", color=ctx.author.color)
                                    return await ctx.reply(embed=em)
                                else:
                                    if content.startswith(f"{i} "):
                                        await u.add_roles(Role)
                                        em=discord.Embed(description=f"{emojis.correct} Successfully Given {Role.mention} to {u.mention}", color=ctx.author.color)
                                        return await ctx.reply(embed=em)
                                    else:
                                        em=discord.Embed(description=f"{emojis.wrong} {u.mention} Does't Have {Role.mention}", color=ctx.author.color)
                                        return await ctx.reply(embed=em)

    #@commands.group(invoke_without_command=True, description="Mentions a role by providing its custom name")
    async def tag(self, ctx: commands.Context, name: str=None, *, message: str=None):
        if name is None:
            ls = ["tag", "tag create", "tag delete", "tag show"]
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
            return await ctx.send(embed=listem)
        tag_db = database.fetchone("*", "tagroles", "guild_id", ctx.guild.id)
        em=discord.Embed(description=f"{emojis.wrong} There is no role set with tag name `{name}`", color=botinfo.wrong_color)
        if tag_db is None:
            return await ctx.reply(embed=em, mention_author=False)
        dic = literal_eval(tag_db['data'])
        if name.lower() not in dic:
            close_matches = difflib.get_close_matches(name.lower(), 
                [i for i in dic], 3, 0.75)
            if len(close_matches) == 0:
                return await ctx.reply(embed=em, mention_author=False)
            else:
                des = ""
                for i in close_matches:
                    des += f"> {i} \n"
                em=discord.Embed(description=f"{emojis.wrong} I couldn't find any role set with tag name `{name}`, but I found some roles with similar name:\n{des}", color=ctx.author.top_role.color)
                return await ctx.reply(embed=em)
        else:
            role = ctx.guild.get_role(dic[name.lower()])
            if role is None:
                em=discord.Embed(description=f"{emojis.wrong} The role set with this tag name has been deleted", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            else:
                view = OnOrOff(ctx)
                em = discord.Embed(description=f"Would You Like To mention {role.mention} with {len(role.members)} in it?", color=botinfo.root_color)
                em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
                test = await ctx.reply(embed=em, view=view)
                await view.wait()
                if not view.value:
                    return await test.edit(content="Timed out!", view=None)
                if view.value == 'Yes':
                    await test.delete()
                    em = discord.Embed(description=f"", color=botinfo.root_color)
                    return await ctx.reply(embed=em, mention_author=False)
                if view.value == 'No':
                    await test.delete()
                    em = discord.Embed(description="Alright I won't mention the role.", color=botinfo.wrong_color)
                    return await ctx.reply(embed=em, mention_author=False)

    #@tag.command(name="create", aliases=['add'], description="Assigns a tag name to a role in the server")
    @commands.has_guild_permissions(manage_guild=True)
    async def tag_create(self, ctx: commands.Context, *, role: discord.Role):
        pass


async def setup(bot):
    await bot.add_cog(extra(bot))
