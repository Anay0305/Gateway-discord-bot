import discord
import json
import asyncio
import datetime
import time as timeee
import random
from ast import literal_eval
from paginators import PaginationView
from discord.ext import commands, tasks
import botinfo
import database
import emojis
import pytz

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
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(emoji=f"{emojis.wrong} ", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'No'
        self.stop()

class modeselect(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label=f"Starts With", custom_id='start', style=discord.ButtonStyle.blurple)
    async def s(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 's'
        self.stop()

    @discord.ui.button(label=f"Ends With", custom_id='Ends', style=discord.ButtonStyle.blurple)
    async def e(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'e'
        self.stop()

    @discord.ui.button(label=f"Contains", custom_id='contains', style=discord.ButtonStyle.green)
    async def c(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'c'
        self.stop()

    @discord.ui.button(label=f"Exact", custom_id='exact', style=discord.ButtonStyle.green)
    async def ex(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'ex'
        self.stop()

class snaps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def eventname(self, ctx: commands.Context, *, event_name: str):
        database.update("snaps_lb", "event_name", f"{event_name}", "main", 1)
        return await ctx.reply(embed=discord.Embed(description=f"Set Event name to `{event_name}`", color=botinfo.right_color))

    @commands.command(aliases=['lb'], description="Shows the leaderboard of team points for the ongoing server event.")
    @commands.has_guild_permissions(manage_roles=True)
    async def leaderboard(self, ctx: commands.Context):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager" or i.name.lower() == "captains" or i.name.lower() == "mentors":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        if len(team_lb) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"There are currently no teams present in the event.", color=botinfo.root_color))
        else:
            em = discord.Embed(color=botinfo.root_color)
            em.set_author(name=f"• {lb_db['event_name']}", icon_url=ctx.guild.icon.url, url=f"https://discord.gg/{ctx.guild.vanity_url_code}")
            des = ""
            count = 1
            ls = {}
            for i in team_lb:
                if team_lb[i] in ls:
                    ls[team_lb[i]].append(i)
                else:
                    ls[team_lb[i]] = [i]
            
            for i in reversed(sorted(ls)):
                for j in ls[i]:
                    r = ctx.guild.get_role(j)
                    if r is not None:
                        des += f"{count}. {r.mention} \n>    **{i} Points**\n"
                count+=1
            em.description = des.strip()
            em.set_footer(text="• Custom Leaderboard powered by Snaps ♡", icon_url=ctx.author.display_avatar.url)
            em.set_thumbnail(url=ctx.guild.icon.url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.group(invoke_without_command=True, aliases=['teams'], description="Shows the help menu for team commands.")
    async def team(self, ctx: commands.Context):
        ls = ["team", "team create", "team delete", "team addpoints", "team removepoints", "team addmember", "team removemember", "team show", "team reset"]
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

    @team.command(description="Creates a new team for the server event.")
    async def create(self, ctx: commands.Context, *, team_role: discord.Role):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        if team_role.id in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"Team {team_role.mention} is already created", color=botinfo.root_color))
        else:
            team_lb[team_role.id] = 0
            database.update("snaps_lb", "team_lb", f"{team_lb}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Created Team {team_role.mention} successfully", color=botinfo.right_color))
    
    @team.command(description="Deletes a existing team from the server event.")
    async def delete(self, ctx: commands.Context, *, team_role: discord.Role):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        team_users = literal_eval(lb_db['team_users'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"Team {team_role.mention} is not created", color=botinfo.root_color))
        else:
            del team_lb[team_role.id]
            if team_role.id in team_users:
                del team_users[team_role.id]
            database.update("snaps_lb", "team_lb", f"{team_lb}", "main", 1)
            database.update("snaps_lb", "team_users", f"{team_users}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Deleted Team {team_role.mention} successfully", color=botinfo.right_color))

    @team.command(description="Reset the current event team settings.")
    async def reset(self, ctx: commands.Context):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Reset Team settings of the event?", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            return await test.edit(content="Timed out!", view=None)
        await test.delete()
        if view.value == 'Yes':
            database.update("snaps_lb", "event_name", "Snaps Exclusive", "main", 1)
            database.update("snaps_lb", "team_lb", "{}", "main", 1)
            database.update("snaps_lb", "team_users", "{}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Reset Team Settings successfully for the server", color=botinfo.right_color))
        if view.value == 'No':
            return await ctx.reply(embed=discord.Embed(description=f"Cancelled the command", color=botinfo.wrong_color))

    @team.command(aliases=['ap'], description="Adds some points to the team for the event.")
    async def addpoints(self, ctx: commands.Context, team_role: discord.Role, *, points):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        try:
            points = abs(int(points))
            if points == 0:
                await ctx.send("You did not enter an postive number.")
                return
        except ValueError:
            await ctx.send("You did not enter an integer.")
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"There is no team {team_role.mention}.", color=botinfo.root_color))
        else:
            team_lb[team_role.id] += points
            database.update("snaps_lb", "team_lb", f"{team_lb}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Added {points} points to Team {team_role.mention}", color=botinfo.right_color))

    @team.command(aliases=['rp'], description="Removes some points from the team for the event.")
    async def removepoints(self, ctx: commands.Context, team_role: discord.Role, *, points):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        try:
            points = abs(int(points))
            if points == 0:
                await ctx.send("You did not enter an postive number.")
                return
        except ValueError:
            await ctx.send("You did not enter an integer.")
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"There is no team {team_role.mention}.", color=botinfo.root_color))
        else:
            if points > team_lb[team_role.id]:
                return await ctx.reply(embed=discord.Embed(description=f"Team {team_role.mention} has {team_lb[team_role.id]} points but you are trying to remove {points}.", color=botinfo.wrong_color))
            team_lb[team_role.id] -= points
            database.update("snaps_lb", "team_lb", f"{team_lb}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Removed {points} points from Team {team_role.mention}", color=botinfo.right_color))

    @team.command(aliases=['am'], description="Adds a member to the team for the event.")
    async def addmember(self, ctx: commands.Context, team_role: discord.Role, *, member: discord.Member):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        team_users = literal_eval(lb_db['team_users'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"There is no team {team_role.mention}.", color=botinfo.root_color))
        else:
            if team_role.id in team_users:
                if member.id in team_users[team_role.id]:
                    return await ctx.reply(embed=discord.Embed(description=f"{member.mention} is already added to {team_role.mention}.", color=botinfo.wrong_color))
                else:
                    team_users[team_role.id].append(member.id)
            else:
                team_users[team_role.id] = [member.id]
            database.update("snaps_lb", "team_users", f"{team_users}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Added {member.mention} to Team {team_role.mention}", color=botinfo.right_color))

    @team.command(aliases=['rm'], description="Removes a member from the team for the event.")
    async def removemember(self, ctx: commands.Context, team_role: discord.Role, *, member: discord.Member):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        team_users = literal_eval(lb_db['team_users'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"There is no team {team_role.mention}.", color=botinfo.root_color))
        else:
            if team_role.id in team_users:
                if member.id not in team_users[team_role.id]:
                    return await ctx.reply(embed=discord.Embed(description=f"{member.mention} is not added to {team_role.mention}.", color=botinfo.wrong_color))
                else:
                    team_users[team_role.id].remove(member.id)
            else:
                return await ctx.reply(embed=discord.Embed(description=f"{member.mention} is not added to {team_role.mention}.", color=botinfo.wrong_color))
            database.update("snaps_lb", "team_users", f"{team_users}", "main", 1)
            return await ctx.reply(embed=discord.Embed(description=f"Removed {member.mention} from Team {team_role.mention}", color=botinfo.right_color))
        
    @team.command(aliases=['showmembers', 'sm'], description="Shows the members of the team for the event.")
    async def show(self, ctx: commands.Context, *, team_role: discord.Role):
        c = False
        for i in ctx.author.roles:
            if i.name.lower() == "event manager" or i.name.lower() == "captains" or i.name.lower() == "mentors":
                c = True
                break
        if not c:
            return
        lb_db = database.fetchone("*", "snaps_lb", "main", 1)
        team_lb = literal_eval(lb_db['team_lb'])
        team_users = literal_eval(lb_db['team_users'])
        if team_role.id not in team_lb:
            return await ctx.reply(embed=discord.Embed(description=f"There is no team {team_role.mention}.", color=botinfo.root_color))
        else:
            if team_role.id not in team_users:
                return await ctx.reply(embed=discord.Embed(description=f"{team_role.mention} has 0 members till now.", color=botinfo.wrong_color))
            if len(team_users[team_role.id]) == 0:
                return await ctx.reply(embed=discord.Embed(description=f"{team_role.mention} has 0 members till now.", color=botinfo.wrong_color))
            ls, roles = [], []
            count = 1
            for i in team_users[team_role.id]:
                user = await ctx.guild.fetch_member(i)
                roles.append(f"`[{'0' + str(count) if count < 10 else count}]` | {user.mention} [{user.id}]")
                count += 1
            for i in range(0, len(roles), 10):
                ls.append(roles[i: i + 10])
            em_list = []
            no = 1
            for k in ls:
                embed =discord.Embed(color=botinfo.root_color)
                embed.title = f"List of Members in {team_role.name} - {count-1}"
                embed.description = "\n".join(k)
                embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                em_list.append(embed)
                no+=1
            page = PaginationView(embed_list=em_list, ctx=ctx)
            await page.start(ctx)

    @commands.group(invoke_without_command=True, aliases=['onlymedia'], description="Shows the help menu for media only commands.")
    async def mediaonly(self, ctx: commands.Context):
        ls = ["mediaonly", "mediaonly add", "mediaonly remove", "mediaonly show"]
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
    
    @mediaonly.command(name="show", aliases=['config'], description="Shows the media only channels of the server")
    @commands.has_guild_permissions(manage_guild=True)
    async def om_show(self, ctx: commands.Context):
        mo_db = database.fetchone("*", "media_only", "guild_id", ctx.guild.id)
        if mo_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There is no Media only channel in this server.", color=botinfo.root_color))
        else:
            lss = literal_eval(mo_db['channels'])
            if len(lss) == 0:
                return await ctx.reply(embed=discord.Embed(description=f"There is no Media only channel in this server.", color=botinfo.root_color))
            else:
                ls, roles = [], []
                count = 1
                for i in lss:
                    ch = ctx.guild.get_channel(i)
                    if ch is not None:
                        roles.append(f"`[{'0' + str(count) if count < 10 else count}]` | {ch.mention}")
                        count += 1
                for i in range(0, len(roles), 10):
                    ls.append(roles[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=botinfo.root_color)
                    embed.title = f"List of Media Only channels in server - {count-1}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await page.start(ctx)

    @mediaonly.command(description="Makes a channel to media only channel.")
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def add(self, ctx: commands.Context, *, channel: discord.TextChannel):
        mo_db = database.fetchone("*", "media_only", "guild_id", ctx.guild.id)
        if mo_db is None:
            lss = [channel.id]
            database.insert("media_only", "guild_id, channels", (ctx.guild.id, f"{lss}"))
            return await ctx.reply(embed=discord.Embed(description=f"Added {channel.mention} to media only channels.", color=botinfo.root_color))
        lss = literal_eval(mo_db['channels'])
        if channel.id in lss:
            return await ctx.reply(embed=discord.Embed(description=f"{channel.mention} is already added to media only channels.", color=botinfo.wrong_color))
        else:
            lss.append(channel.id)
            database.update("media_only", "channels", f"{lss}", "guild_id", ctx.guild.id)
            return await ctx.reply(embed=discord.Embed(description=f"Added {channel.mention} to media only channels.", color=botinfo.root_color))

    @mediaonly.command(description="Removes a channel from media only channels.")
    @commands.has_guild_permissions(manage_guild=True)
    async def remove(self, ctx: commands.Context, *, channel: discord.TextChannel):
        mo_db = database.fetchone("*", "media_only", "guild_id", ctx.guild.id)
        if mo_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{channel.mention} is not added to media only channels.", color=botinfo.wrong_color))
        lss = literal_eval(mo_db['channels'])
        if channel.id not in lss:
            return await ctx.reply(embed=discord.Embed(description=f"{channel.mention} is not added to media only channels.", color=botinfo.wrong_color))
        else:
            lss.remove(channel.id)
            database.update("media_only", "channels", f"{lss}", "guild_id", ctx.guild.id)
            return await ctx.reply(embed=discord.Embed(description=f"Removed {channel.mention} from media only channels.", color=botinfo.root_color))
        
    @commands.group(invoke_without_command=True, aliases=['autoresponder', 'ar'], description="Shows the help menu for autorespond commands")
    async def autoresponed(self, ctx: commands.Context):
        ls = ["ar", "ar add", "ar remove", "ar show", "ar reset"]
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

    @autoresponed.command(name="reset", description="Reset autoresponders for the server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def ar_reset(self, ctx: commands.Context):
        ar_db = database.fetchone("*", "autoresponder", "guild_id", ctx.guild.id)
        if ar_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There are no autoresponders for this server.", color=botinfo.root_color))
        else:
            lss = literal_eval(ar_db['data'])
            lssch = literal_eval(ar_db['ignore_channels'])
            if len(lss) == 0:
                return await ctx.reply(embed=discord.Embed(description=f"There are no autoresponders for this server.", color=botinfo.wrong_color))
            else:
                pass
        view = OnOrOff(ctx)
        em = discord.Embed(description=f"Would You Like To Reset AutoResponders for the event?", color=botinfo.root_color)
        try:
            em.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        except:
            em.set_author(name=str(ctx.author))
        test = await ctx.reply(embed=em, view=view)
        await view.wait()
        if not view.value:
            return await test.edit(content="Timed out!", view=None)
        await test.delete()
        if view.value == 'Yes':
            database.update("autoresponder", "data", "{}", "guild_id", ctx.guild.id)
            return await ctx.reply(embed=discord.Embed(description=f"Deleted all the autoresponders in this server.", color=botinfo.root_color))
        else:
            return await ctx.reply(embed=discord.Embed(description=f"Cancelled the command", color=botinfo.wrong_color))

    @autoresponed.command(name="show", aliases=['config'], description="Shows the current autoresponders.")
    @commands.has_guild_permissions(manage_guild=True)
    async def ar_show(self, ctx: commands.Context):
        ar_db = database.fetchone("*", "autoresponder", "guild_id", ctx.guild.id)
        if ar_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There are no autoresponders for this server.", color=botinfo.root_color))
        else:
            lss = literal_eval(ar_db['data'])
            lssch = literal_eval(ar_db['ignore_channels'])
            if len(lss) == 0:
                return await ctx.reply(embed=discord.Embed(description=f"There are no autoresponders for this server.", color=botinfo.root_color))
            else:
                em_list = []
                no = 1
                if len(lssch) > 0:
                    x = 1
                else:
                    x = 0
                for k in lss:
                    embed = discord.Embed(color=botinfo.root_color)
                    embed.title = f"List of AutoResponders in the server - {len(lss)}"
                    embed.add_field(name="Name:", value=k, inline=True)
                    embed.add_field(name="Value:", value=lss[k]['value'])
                    mode = ""
                    if lss[k]['mode'] == "s":
                        mode = "Starts with"
                    elif lss[k]['mode'] == "e":
                        mode = "Ends with"
                    elif lss[k]['mode'] == "c":
                        mode = "Contains"
                    elif lss[k]['mode'] == "ex":
                        mode = "Exact"
                    embed.add_field(name="Autoresponder Type:", value=mode, inline=True)
                    embed.add_field(name="Case Sensitive:", value=lss[k]['sensitive'], inline=True)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(lss)+x}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                if x == 1:
                    embed =discord.Embed(color=botinfo.root_color)
                    embed.title = f"List of Ignored channels for AutoResponders in the server - {len(lssch)}"
                    for i in lssch:
                        ch = ctx.guild.get_channel(i)
                        if i is None:
                            embed.description += f"#deleted-channel\n"
                        else:
                            embed.description += f"{ch.mention}\n"
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(lss)+x}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await page.start(ctx)
    
    @autoresponed.command(name="create", aliases=['add'], description="Creates an autoresponder in the server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def ar_create(self, ctx: commands.Context, *, name):
        ar_db = database.fetchone("*", "autoresponder", "guild_id", ctx.guild.id)
        if ar_db is None:
            lss = {}
        else:
            lss = literal_eval(ar_db['data'])
        check = False
        for i in lss:
            if str(i).lower() == name.lower():
                check = True
                break
        if check:
            return await ctx.reply(embed=discord.Embed(description=f"There is already an autoresponder with name `{name}` in this server.", color=botinfo.wrong_color))
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        init = await ctx.reply(embed=discord.Embed(description=f"What should i respond with when someone types `{name}` in any text channel?\n You can also use keywords, for bot keywords type `{ctx.prefix}keywords`.", color=botinfo.root_color).set_footer(text="Type 'cancel' to cancel the command"))
        try:
            user_response = await self.bot.wait_for("message", timeout=180, check=check)
            await user_response.delete()
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                title="Error",
                color=botinfo.root_color,
                description="You took too long to answer this question"
            ))
            await init.delete()
            return
        else:
            if str(user_response.content).lower() == "cancel":
                await init.delete()
                return
        view = OnOrOff(ctx)
        await init.edit(embed=discord.Embed(description=f"Do you want this autorespond to be case insensitive or want it in exact `{name}` format?\n'Yes' for Case Insensitive and 'No' for Case Sensitive.", color=botinfo.root_color), view=view)
        await view.wait()
        if not view.value:
            await init.delete()
            return
        elif view.value == "Yes":
            sensi = False
        elif view.value == "No":
            sensi = True
        view = modeselect(ctx)
        await init.edit(embed=discord.Embed(description=f"Select the autoresponding type for `{name}` from the below buttons.", color=botinfo.root_color), view=view)
        await view.wait()
        if not view.value:
            await init.delete()
            return
        lss[name] = {
            "value": user_response.content,
            "sensitive": sensi,
            "mode": view.value
        }
        if view.value == "s":
            mode = "Starts with"
        elif view.value == "e":
            mode = "Ends with"
        elif view.value == "c":
            mode = "Contains"
        elif view.value == "ex":
            mode = "Exact"
        if ar_db is None:
            database.insert("autoresponder", "guild_id, data", (ctx.guild.id, f"{lss}"))
        else:
            database.update("autoresponder", "data", f"{lss}", "guild_id", ctx.guild.id)
        await init.edit(embed=discord.Embed(description=f"Successfully created an autoresponder with \nName -> `{name}`\nMode -> {mode}\nCase Sensitive? -> {sensi}", color=botinfo.root_color), view=None)

    @autoresponed.command(name="delete", aliases=['remove'], description="Deletes an autoresponder from the server")
    @commands.has_guild_permissions(manage_guild=True)
    async def ar_delete(self, ctx: commands.Context, *, name):
        ar_db = database.fetchone("*", "autoresponder", "guild_id", ctx.guild.id)
        if ar_db is None:
            lss = {}
        else:
            lss = literal_eval(ar_db['data'])
        check = False
        for i in lss:
            if str(i).lower() == name.lower():
                check = True
                del lss[i]
                break
        if not check:
            return await ctx.reply(embed=discord.Embed(description=f"There is no autoresponder with name `{name}` in this server.", color=botinfo.wrong_color))
        else:
            database.update("autoresponder", "data", f"{lss}", "guild_id", ctx.guild.id)
            await ctx.reply(embed=discord.Embed(description=f"Successfully deleted an autoresponder with \nName -> `{name}`", color=botinfo.root_color))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()
        if isinstance(message.channel, discord.DMChannel):
            return
        guild = message.guild
        if not message.author.bot:
            pass
        else:
            mo_db = database.fetchone("*", "media_only", "guild_id", guild.id)
            if mo_db is None:
                pass
            else:
                lss = literal_eval(mo_db['channels'])
                if message.channel.id not in lss:
                    pass
                else:
                    if len(message.attachments) == 0:
                        try:
                            await asyncio.sleep(3)
                            await message.delete()
                        except:
                            pass
        if message.author.bot:
            return
        ar_db = database.fetchone("*", "autoresponder", "guild_id", guild.id)
        if ar_db is None:
            return
        lss = literal_eval(ar_db['data'])
        for k in lss:
            check = False
            if lss[k]['sensitive']:
                con = message.content
                name = k
            else:
                con = message.content.lower()
                name = k.lower()
            if lss[k]['mode'] == "s":
                if con.startswith(name):
                    check = True
            elif lss[k]['mode'] == "e":
                if con.endswith(name):
                    check = True
            elif lss[k]['mode'] == "c":
                if name in con:
                    check = True
            elif lss[k]['mode'] == "ex":
                if con == name:
                    check = True
            if check:
                member = message.author
                val = lss[k]['value']
                ind = pytz.timezone("Asia/Kolkata")
                ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                val= str(val).replace("$user_name", member.name).replace("$user_username", str(member)).replace("$user_discriminator", f"#{member.discriminator}").replace("$user_id", str(member.id)).replace("$user_avatar", str(member.display_avatar.url)).replace("$user_mention", str(member.mention)).replace("$user_created", f"<t:{round(member.created_at.timestamp())}:F>").replace("$user_joined", f"<t:{round(member.joined_at.timestamp())}:F>").replace("$user_profile", f"https://discord.com/users/{member.id}").replace("$server_name", guild.name).replace("$server_id", str(guild.id)).replace("$membercount_ordinal", ordinal(len(guild.members))).replace("$membercount", str(len(guild.members))).replace("$now", f"{datetime.datetime.now(ind)}")
                if guild.icon:
                    val = str(val).replace("$server_icon", guild.icon.url)
                else:
                    if "$server_icon" in val:
                        val = str(val).replace("$server_icon", "")
                await message.channel.send(val, mention_author=False)

async def setup(bot):
	await bot.add_cog(snaps(bot))
