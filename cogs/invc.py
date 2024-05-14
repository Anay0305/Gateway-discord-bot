import discord
import datetime
from discord.ext import commands, tasks
from ast import literal_eval
import database
import io
import emojis
from paginators import PaginationView, PaginatorView
import botinfo

class enablemenu(discord.ui.Select):
    def __init__(self, ctx: commands.Context, role: discord.Role):
        options = []
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        c = 0
        for i in x:
            if x[i] is None:
                xx = discord.utils.get(ctx.guild.channels, id=i)
                options.append(discord.SelectOption(label=f"{xx.name}", value=i))
                c = c+1
        super().__init__(placeholder="Select voice channels",
            min_values=1,
            max_values=c,
            options=options,
        )
        self.ctx = ctx
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        ctx = self.ctx
        role = self.role
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        des= ""
        for i in self.values:
            if x[int(i)] is None:
                x[int(i)] = role.id
                xx = discord.utils.get(ctx.guild.channels, id=int(i))
                des += f"{xx.mention}, "
        database.update("invc", "vc", f"{x}", "guild_id", ctx.guild.id)
        em = discord.Embed(description=f"{role.mention} is now invc role for {des[:-2]}", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()

class enableview(discord.ui.View):
    def __init__(self, ctx: commands.Context, role: discord.Role):
        super().__init__(timeout=60)
        self.add_item(enablemenu(ctx, role))
        self.ctx = ctx
        self.role = role
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="All Voice Channels", style=discord.ButtonStyle.blurple)
    async def _enable(self, interaction, button):
        ctx = self.ctx
        role = self.role
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        des= ""
        for i in x:
                x[i] = role.id
                xx = discord.utils.get(ctx.guild.channels, id=i)
                des += f"{xx.mention}, "
        database.update("invc", "vc", f"{x}", "guild_id", ctx.guild.id)
        em = discord.Embed(description=f"{role.mention} is now invc role for {des[:-2]}", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()

class disablemenu(discord.ui.Select):
    def __init__(self, ctx: commands.Context, role: discord.Role=None):
        options = []
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        c = 0
        for i in x:
            if x[i] is not None:
                if role is None:
                    xx = discord.utils.get(ctx.guild.channels, id=i)
                    options.append(discord.SelectOption(label=f"{xx.name}", value=i))
                    c +=1
                else:
                    if x[i] == role.id:
                        xx = discord.utils.get(ctx.guild.channels, id=i)
                        options.append(discord.SelectOption(label=f"{xx.name}", value=i))
                        c +=1
        super().__init__(placeholder="Select voice channels",
            min_values=1,
            max_values=c,
            options=options,
        )
        self.ctx = ctx
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        ctx = self.ctx
        role = self.role
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        des= ""
        for i in self.values:
            if x[int(i)] is not None:
                if role is None:
                    x[int(i)] = None
                    xx = discord.utils.get(ctx.guild.channels, id=int(i))
                    des += f"{xx.mention}, "
                else:
                    if x[int(i)] == role.id:
                        x[int(i)] = None
                        xx = discord.utils.get(ctx.guild.channels, id=int(i))
                        des += f"{xx.mention}, "
        database.update("invc", "vc", f"{x}", "guild_id", ctx.guild.id)
        if role is not None:
            em = discord.Embed(description=f"{role.mention} is now removed from invc role for {des[:-2]}", color=botinfo.root_color)
        else:
            em = discord.Embed(description=f"All invc roles are now removed from {des[:-2]}", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()

class disableview(discord.ui.View):
    def __init__(self, ctx: commands.Context, role: discord.Role=None):
        super().__init__()
        self.add_item(disablemenu(ctx, role))
        self.ctx = ctx
        self.role = role

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="All Voice Channels", style=discord.ButtonStyle.blurple)
    async def _disable(self, interaction, button):
        ctx = self.ctx
        role = self.role
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        x = literal_eval(log_db['vc'])
        des= ""
        for i in x:
            if x[i] is not None:
                if role is None:
                    x[i] = None
                    xx = discord.utils.get(ctx.guild.channels, id=i)
                    des += f"{xx.mention}, "
                else:
                    if x[i] == role.id:
                        x[i] = None
                        xx = discord.utils.get(ctx.guild.channels, id=i)
                        des += f"{xx.mention}, "
        database.update("invc", "vc", f"{x}", "guild_id", ctx.guild.id)
        if role is not None:
            em = discord.Embed(description=f"{role.mention} is now removed from invc role for {des[:-2]}", color=botinfo.root_color)
        else:
            em = discord.Embed(description=f"All invc roles are now removed in the server", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()

class invc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="invc",
        invoke_without_command=True, description="Shows the invc's help menu"
    )
    async def invc(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        ls = ["invc", "invc enable", "invc disable", "invc config"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            if cmd.description is None:
                cmd.description = "No Description"
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Invc']} Invc Role Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    @invc.command(name="config",description="Shows the current invc role settings")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        em = discord.Embed(title="Invc Role setting for the server", color=botinfo.root_color)
        x = literal_eval(log_db['vc'])
        c = 0
        for i in x:
            if x[i] is not None:
                cc = discord.utils.get(ctx.guild.channels, id=i)
                r = discord.utils.get(ctx.guild.roles, id=x[i])
                if r is None:
                    rr = "The role is deleted"
                else:
                    rr = r.mention
                em.add_field(name=f"{cc.name}:", value=f"{rr}", inline=True)
                c+=1
        if c==0:
            em.description = "No Invc Role is setup in this server"
        em.set_footer(text=f"Invc Role system", icon_url=self.bot.user.display_avatar.url)
        await ctx.reply(embed=em)

    @invc.command(name="enable", aliases=['on'], description="Enable the logs for the server")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, *, role: discord.Role):
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.")
        if role.permissions.administrator or role.permissions.manage_roles or role.permissions.ban_members or role.permissions.kick_members or role.permissions.manage_guild or role.permissions.manage_channels or role.permissions.mention_everyone or role.permissions.manage_webhooks:
            return await ctx.reply("The Role has dangerous permissions so it cant be used as a invc role.")
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        ls = literal_eval(log_db['vc'])
        c = 0
        for i in ls:
            if ls[i] is None:
                c+=1
        if c == 0:
            return await ctx.reply(f"All Voice Channels have a invc role already enabled")
        view = enableview(ctx, role)
        em = discord.Embed(description=f"Which Voice channel should have {role.mention} as invc role?", color=botinfo.root_color)
        m = await ctx.reply(embed=em, view=view)
        await view.wait()
    
    @invc.command(name="disable", aliases=['off'], description="Disable the logs for the server")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, *, role: discord.Role=None):
        if role is not None:
            if role.is_bot_managed() or role.is_premium_subscriber():
                return await ctx.reply("It is a integrated role. Please provide a different role")
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        log_db = database.fetchone("*", "invc", "guild_id", ctx.guild.id)
        ls = literal_eval(log_db['vc'])
        c = 0
        for i in ls:
            if ls[i] is not None:
                if role is not None:
                    if ls[i] == role.id:
                        c+=1
                else:
                    c+=1
        if c == 0:
            if role is not None:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not invc role for any of the Voice Channel", color=botinfo.root_color))
            else:
                return await ctx.reply(f"Invc role system for All Voice Channels are already disabled")
        if role is not None:
            view = disableview(ctx, role)
        else:
            view = disableview(ctx)
        if role is not None:
            em = discord.Embed(description=f"Which Voice channel should not have {role.mention} as invc role?", color=botinfo.root_color)
        else:
            em = discord.Embed(description=f"Which Voice channel should not have any invc role?", color=botinfo.root_color)
        m = await ctx.reply(embed=em, view=view)
        await view.wait()
    

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        await self.bot.wait_until_ready()
        log_db = database.fetchone("*", "invc", "guild_id", channel.guild.id)
        ls = literal_eval(log_db['vc'])
        if isinstance(channel, discord.VoiceChannel):
            ls[channel.id] = None
        database.update("invc", "vc", f"{ls}", "guild_id", channel.guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        await self.bot.wait_until_ready()
        log_db = database.fetchone("*", "invc", "guild_id", channel.guild.id)
        if log_db is None:
            return
        ls = literal_eval(log_db['vc'])
        if isinstance(channel, discord.VoiceChannel):
            if channel.id in ls:
                del ls[channel.id]
        database.update("invc", "vc", f"{ls}", "guild_id", channel.guild.id)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        await self.bot.wait_until_ready()
        log_db = database.fetchone("*", "invc", "guild_id", role.guild.id)
        if log_db is None:
            return
        ls = literal_eval(log_db['vc'])
        for i in ls:
            if ls[i] == role.id:
                ls[i] = None
        database.update("invc", "vc", f"{ls}", "guild_id", role.guild.id)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await self.bot.wait_until_ready()
        guild = member.guild
        if not guild.me.guild_permissions.manage_roles:
          return
        log_db = database.fetchone("*", "invc", "guild_id", guild.id)
        if log_db is None:
            return
        ls = literal_eval(log_db['vc'])
        if before.channel:
            if before.channel.id in ls:
                r = discord.utils.get(guild.roles, id=ls[before.channel.id])
                if r is not None:
                  if r.position < guild.me.top_role.position:
                    await member.remove_roles(r, reason=f"{self.bot.user.name} | INVC ROLE")
        if after.channel:
            if after.channel.id in ls:
                r = discord.utils.get(guild.roles, id=ls[after.channel.id])
                if r is not None:
                  if r.position < guild.me.top_role.position:
                    await member.add_roles(r, reason=f"{self.bot.user.name} | INVC ROLE")
                

async def setup(bot):
	await bot.add_cog(invc(bot))
