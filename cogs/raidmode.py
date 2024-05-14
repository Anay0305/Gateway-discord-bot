import discord
from discord.ext import commands
from discord import *
import os
import sqlite3
import datetime
from ast import literal_eval
import database
import emojis
import botinfo

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
      
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

class config(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None    

    @discord.ui.button(label="Default", style=discord.ButtonStyle.gray)
    async def a(self, interaction, button):
        self.value = 'def'
        self.stop()
    @discord.ui.button(label="Customize", style=discord.ButtonStyle.gray)
    async def server(self, interaction, button):
        self.value = 'custom'
        self.stop()

class xddd(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None    

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.red)
    async def _b(self, interaction, button):
        self.value = 'ban'
        self.stop()
    @discord.ui.button(label="Kick", style=discord.ButtonStyle.green)
    async def _k(self, interaction, button):
        self.value = 'kick'
        self.stop()

class lockconfig(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None    

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.red)
    async def _b(self, interaction, button):
        self.value = 1
        self.stop()
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.green)
    async def _k(self, interaction, button):
        self.value = 0
        self.stop()

class raidmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, user):
        raid_db = database.fetchone("*", "raidmode", "guild_id", user.guild.id)
        if raid_db is None:
            return
        if raid_db['lock'] == 1:
            return await user.guild.kick(user, reason="Lock Down")
        x = datetime.datetime.utcnow()-datetime.timedelta(seconds=raid_db['time'])
        ls = []
        for j in user.guild.members:
            if j.joined_at.timestamp() >= x.timestamp():
                ls.append(j)
        if len(ls) >= raid_db['max']:
            for j in ls:
                if raid_db['PUNISHMENT'] == 'KICK':
                    try:
                        await user.guild.kick(j, reason="ANTI RAID MODE IS TRIGGERED")
                    except:
                        pass
                if raid_db['PUNISHMENT'] == 'BAN':
                    try:
                        await user.guild.ban(j, reason="ANTI RAID MODE IS TRIGGERED")
                    except:
                        pass
            if raid_db['lockdown'] == 1:
                database.update("raidmode", "lock", 1, "guild_id", user.guild.id)
        
    @commands.hybrid_group(
        invoke_without_command=True,
        description="Shows the raidmode's help menu"
    )
    async def raidmode(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["raidmode", "raidmode enable", "raidmode disable", "raidmode config", "raidmode punishment", "raidmode autolockdown", "raidmode lockdown"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Raidmode']} Raidmode Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem) 
        
    @raidmode.command(description="Shows the current settings for raidmode")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", ctx.guild.id)
        if raid_db is not None:
            if raid_db['toggle'] == 1:
                pass
        else:
            em = discord.Embed(description=f"Raidmode is disabled for the server\nYou can enable it by typing `{ctx.prefix}raidmode enable`", color=botinfo.root_color)
            return await ctx.reply(embed=em)
        em = discord.Embed(title=f"Raidmode configuration for {ctx.guild.name}", color=botinfo.root_color)
        em.add_field(name="Time limit", value=f"{raid_db['time']} {'second' if raid_db['time'] == 1 or raid_db['time'] == 0  else 'seconds'}")
        em.add_field(name="User limit", value=f"{raid_db['max']} {'user' if raid_db['max'] == 1 or raid_db['max'] == 0 else 'users'}")
        em.add_field(name="Punishment type", value=raid_db['PUNISHMENT'].capitalize())
        if raid_db['lockdown'] == 1:
            l = "Enabled"
        else:
            l = "Disabled"
        em.add_field(name="Auto Lockdown", value=l)
        em.set_footer(text=f"{str(self.bot.user)} Raidmode")
        if raid_db['lock'] == 1:
            l = "Enabled"
        else:
            l = "Disabled"
        em.add_field(name="Lockdown", value=l)
        em.set_footer(text=f"{str(self.bot.user)} Raidmode", icon_url=self.bot.user.avatar.url)
        return await ctx.reply(embed=em)

    @raidmode.command(description="Enables the raidmode")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", ctx.guild.id)
        if raid_db is not None:
            if raid_db['toggle'] == 1:
                await ctx.reply("Raidmode is already enabled!!")
                return
        em = discord.Embed(description="Which type of settings you want to have for raidmode?", color=botinfo.root_color)
        v = config(ctx)
        msg = await ctx.reply(embed=em, view=v)
        await v.wait()
        if v.value == 'def':
            await msg.delete()
            if raid_db is None:
                val = (ctx.guild.id, 1,)
                database.insert("raidmode", "guild_id, toggle", val)
            em = discord.Embed(description=f"Enabled raidmode successfully with 15 User limit in 10 Seconds and punishment is Kick with Auto Lockdown Enabled\nIf you want to disable it type `{ctx.prefix}raidmode disable`", color=botinfo.root_color)
            await ctx.reply(embed=em)
            return
        if v.value == 'custom':
            await msg.delete()
            xd = await ctx.send("Time limit for users to join in seconds:")
            def message_check(m):
                return (
                    m.author.id == ctx.author.id
                    and ctx.channel == m.channel
                    and m.content.isdigit()
                )
            message = await self.bot.wait_for("message", check=message_check)
            t = int(message.content)
            await message.delete()
            await xd.edit(content=f"How many users can join within this time limit:")
            message = await self.bot.wait_for("message", check=message_check)
            u = int(message.content)
            await message.delete()
            await xd.edit(content=f"What should be the punishment (kick or ban)?")
            def message_check(m):
                return (
                    m.author.id == ctx.author.id
                    and ctx.channel == m.channel
                )
            message = await self.bot.wait_for("message", check=message_check)
            while not message.content.lower().startswith("k") or message.content.lower().startswith("b"):
                await message.delete()
                await xd.edit(content=f"What should be the punishment (kick or ban)? Type only kick or ban")
                message = await self.bot.wait_for("message", check=message_check)
            if message.content.lower().startswith("k"):
                p = "KICK"
            if message.content.lower().startswith("b"):
                p = "BAN"
            await message.delete()
            await xd.edit(content=f"Should I enable lockdown whenever raid is triggered (yes or no)?")
            def message_check(m):
                return (
                    m.author.id == ctx.author.id
                    and ctx.channel == m.channel
                )
            message = await self.bot.wait_for("message", check=message_check)
            while not message.content.lower().startswith("y") and message.content.lower().startswith("n"):
                await message.delete()
                await xd.edit(content=f"Should I enable lockdown whenever raid is triggered (yes or no)? Type only yes or no")
                message = await self.bot.wait_for("message", check=message_check)
            if message.content.lower().startswith("y"):
                l = 1
            if message.content.lower().startswith("n"):
                l = 0
            if raid_db is None:
                val = (ctx.guild.id, 1, f'{p}', t, u, l, 0)
                database.insert("raidmode", "guild_id, toggle, PUNISHMENT, time, max, lockdown, lock", val)
            await xd.delete()
            await message.delete()
            if l == 1:
                l = "Enabled"
            else:
                l = "Disabled"
            em = discord.Embed(description=f"Enabled raidmode successfully with {u} User limit in {t} Seconds and Punishment {p.capitalize()} with Auto Lockdown {l}\nIf you want to disable it type `{ctx.prefix}raidmode disable`", color=botinfo.root_color)
            await ctx.reply(embed=em)
            return

    @raidmode.command(description="Disables the raidmode")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", ctx.guild.id)
        if raid_db is not None:
            if raid_db['toggle'] == 1:
                pass
        else:
            await ctx.reply("Raidmode is already disabled!!")
            return
        database.delete("raidmode", "guild_id", ctx.guild.id)
        em = discord.Embed(description=f"Disabled raidmode successfully\nIf you want to enable it again type `{ctx.prefix}raidmode enable`", color=botinfo.root_color)
        await ctx.reply(embed=em)
        return

    @raidmode.command(description="Changes the punishment for raiding server")
    @commands.has_permissions(administrator=True)
    async def punishment(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", user.guild.id)
        if raid_db is None:
            await ctx.reply("Raidmode is disabled!!")
            return
        if raid_db is not None:
            if raid_db['toggle'] == 0:
                await ctx.reply("Raidmode is disabled!!")
                return
        v = xddd(ctx)
        xd = await ctx.reply(embed=discord.Embed(description="Select the punishment for raiding the server", color=botinfo.root_color), view=v)
        await v.wait()
        if raid_db['PUNISHMENT'] == v.value.upper():
            em = discord.Embed(description=f'Punishment is already set to {v.value.capitalize()}', color=botinfo.root_color)
            await xd.delete()
            return await ctx.reply(embed=em)
        else:
            pass
        database.update("raidmode", "PUNISHMENT", f'{v.value.upper()}', "guild_id", ctx.guild.id)
        em = discord.Embed(description=f'Punishment is set to {v.value.capitalize()}', color=botinfo.root_color)
        await xd.edit(embed=em, view=None)

    @raidmode.command(description="Changes the status of lockdown")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", user.guild.id)
        if raid_db is None:
            await ctx.reply("Raidmode is disabled!!")
            return
        if raid_db is not None:
            if raid_db['toggle'] == 0:
                await ctx.reply("Raidmode is disabled!!")
                return
        v = lockconfig(ctx)
        xd = await ctx.reply(embed=discord.Embed(description="Should i enable or disable the Lockdown?", color=botinfo.root_color), view=v)
        await v.wait()
        if raid_db['lock'] == v.value:
            if v.value == 1:
                l = "Enabled"
            else:
                l = "Disabled"
            em = discord.Embed(description=f'Lockdown is already {l}', color=botinfo.root_color)
            await xd.delete()
            return await ctx.reply(embed=em)
        else:
            pass
        database.update("raidmode", "lock", v.value, "guild_id", ctx.guild.id)
        if v.value == 1:
            l = "Enabled"
        else:
            l = "Disabled"
        em = discord.Embed(description=f'Lockdown is now {l}', color=botinfo.root_color)
        await xd.edit(embed=em, view=None)

    @raidmode.command(description="Changes the status of autolockdown")
    @commands.has_permissions(administrator=True)
    async def autolockdown(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        raid_db = database.fetchone("*", "raidmode", "guild_id", user.guild.id)
        if raid_db is None:
            await ctx.reply("Raidmode is disabled!!")
            return
        if raid_db is not None:
            if raid_db['toggle'] == 0:
                await ctx.reply("Raidmode is disabled!!")
                return
        v = lockconfig(ctx)
        xd = await ctx.reply(embed=discord.Embed(description="Should i enable or disable the Auto Lockdown?", color=botinfo.root_color), view=v)
        await v.wait()
        if raid_db['lockdown'] == v.value:
            if v.value == 1:
                l = "Enabled"
            else:
                l = "Disabled"
            em = discord.Embed(description=f'Auto Lockdown is already {l}', color=botinfo.root_color)
            await xd.delete()
            return await ctx.reply(embed=em)
        else:
            pass
        database.update("raidmode", "lockdown", v.value, "guild_id", ctx.guild.id)
        if v.value == 1:
            l = "Enabled"
        else:
            l = "Disabled"
        em = discord.Embed(description=f'Auto Lockdown is now {l}', color=botinfo.root_color)
        await xd.edit(embed=em, view=None)

async def setup(bot):
    await bot.add_cog(raidmode(bot))