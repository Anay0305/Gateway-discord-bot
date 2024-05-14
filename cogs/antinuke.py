from re import I
import discord
import datetime
from discord.ext import commands, tasks
from ast import literal_eval
import sqlite3
import botinfo
import database
import emojis
import asyncio
from paginators import PaginationView, PaginatorView

def check_lockrole_bypass(role: discord.Role, guild: discord.Guild, user: discord.Member):
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        rl_db = cursor.execute("SELECT * FROM  lockr WHERE guild_id = ?", (guild.id,)).fetchone()
    if rl_db is None:
        cursor.close()  
        db.close()
        return True
    try:
        if rl_db is not None:
            if rl_db["role_id"] == "[]":
                return True
            else:
                if role.id in literal_eval(rl_db["role_id"]):
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    checkk = False
                    if user.id == guild.owner.id:
                        checkk = True
                    elif user.id in u_id:
                        checkk = True
                    else:
                        for i in user.roles:
                            if i.id in r_id:
                                checkk = True
                                break
                    return checkk
                else:
                    return True
    except:
        return True
    

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
      
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [1141685323299045517, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

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

def wll(anti_db, user_id, type):
    if anti_db is None:
        return False
    if anti_db[type] is None:
        return False
    if user_id in literal_eval(anti_db[type]):
        return True
    else:
        return False
    
def wl(guild_id, user_id, type):
    query = "SELECT * FROM  wl WHERE guild_id = ?"
    val = (guild_id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        anti_db = cursor.fetchone()
    if anti_db is None:
        return False
    if anti_db[type] is None:
        return False
    if user_id in literal_eval(anti_db[type]):
        return True
    else:
        return False

def punishh(anti_db):
    if anti_db['PUNISHMENT'] == "KICK":
        return False
    else:
        return True

def punish(guild_id):
    query = "SELECT * FROM  punish WHERE guild_id = ?"
    val = (guild_id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        anti_db = cursor.fetchone()
    if anti_db['PUNISHMENT'] == "KICK":
        return False
    else:
        return True

def check(guild_id, type):
    query = "SELECT * FROM  toggle WHERE guild_id = ?"
    val = (guild_id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        anti_db = cursor.fetchone()
    if anti_db is None:
        return False
    if anti_db[type] == 0:
        return False
    else:
        return True

def toggle(guild, type, icon, prefix):
    query = "SELECT * FROM  toggle WHERE guild_id = ?"
    val = (guild.id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        anti_db = cursor.fetchone()
    if anti_db is None or anti_db['ALL'] == 0:
        em = discord.Embed(description=f"First enable the security for {guild.name} by using `{prefix}antinuke enable`", color=botinfo.root_color)
        return em
    else:
        if anti_db[type] == 0:
            c = 1
        else:
            c = 0
        sql1 = (f"UPDATE toggle SET '{type}' = ? WHERE guild_id = ?")
        val1 = (c, guild.id)
        cursor.execute(sql1,val1)
    db.commit()
    query = "SELECT * FROM  wl WHERE guild_id = ?"
    val = (guild.id,)
    with sqlite3.connect('./database.sqlite3') as db1:
        db1.row_factory = sqlite3.Row
        cursor1 = db1.cursor()
        cursor1.execute(query, val)
        anti_db1 = cursor1.fetchone()
    des = ""
    ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
    for i in sorted(ls):
        if anti_db[i] == 1:
            des += f"**Anti {i.capitalize()}:** {emojis.disable_no}{emojis.enable_yes}\n"
        else:
            des += f"**Anti {i.capitalize()}:** {emojis.enable_no}{emojis.disable_yes}\n"
    embed = discord.Embed(color=botinfo.root_color)
    embed.set_author(name=f"{str(guild.me.name)} Security", icon_url=icon)
    embed.title = f"{guild.name} Security Settings"
    try:
            ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
            ls1 = []
            c = 0
            for i in ls:
                for j in literal_eval(anti_db1[i]):
                    if j not in ls1:
                        x = discord.utils.get(guild.members, id=j)
                        if x is None:
                            continue
                        ls1.append(j)
                        c+=1
            if c != 0:
                wl = len(ls1)
    except:
        wl = 0
    embed.description = f"Move my role above for more protection.\n\nPunishments:\n\n{des}\nWhitelisted {wl} Users\nTo Change Punishment type `{prefix}antinuke punishment <type>`\nThere are two types of punishments Ban or Kick\nTo Enable or disable event type `{prefix}antinuke anti <event>`"
    query = "SELECT * FROM  punish WHERE guild_id = ?"
    val = (guild.id,)
    with sqlite3.connect('./database.sqlite3') as db2:
        db2.row_factory = sqlite3.Row
        cursor2 = db2.cursor()
        cursor2.execute(query, val)
        anti_db2 = cursor2.fetchone()
    if anti_db2 is None:
            sql = (f"INSERT INTO punish(guild_id) VALUES(?)")
            val = (guild.id,)
            cursor.execute(sql,val)
            punishment = "Ban"
    else:
        punishment = anti_db2['PUNISHMENT'].capitalize()
    embed.set_footer(text=f"Current Punishment is {punishment}", icon_url=icon)
    db.commit()
    cursor.close()
    db.close()
    db1.commit()
    cursor1.close()
    db1.close()
    db2.commit()
    cursor2.close()
    db2.close()
    return embed


class whitelistMenu(discord.ui.Select):
    def __init__(self, ctx: commands.Context, user : discord.Member):
        options = [
            discord.SelectOption(label='Anti Ban', value="BAN"),
            discord.SelectOption(label='Anti Bot', value="BOT"),
            discord.SelectOption(label='Anti Channel Create', value="CHANNEL CREATE"),
            discord.SelectOption(label='Anti Channel Delete', value="CHANNEL DELETE"),
            discord.SelectOption(label='Anti Channel Update', value="CHANNEL UPDATE"),
            discord.SelectOption(label='Anti Guild Update', value="GUILD UPDATE"),
            discord.SelectOption(label='Anti Kick', value="KICK"),
            discord.SelectOption(label='Anti Member Update', value="MEMBER UPDATE"),
            discord.SelectOption(label='Anti Role Create', value="ROLE CREATE"),
            discord.SelectOption(label='Anti Role Delete', value="ROLE DELETE"),
            discord.SelectOption(label='Anti Role Update', value="ROLE UPDATE"),
            discord.SelectOption(label='Anti Webhook', value="WEBHOOK"),
        ]
        super().__init__(placeholder="Select specific events for whitelisting the user",
            min_values=1,
            max_values=12,
            options=options,
        )
        self.ctx = ctx
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (self.ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        des= ""
        for i in self.values:
                if anti_db[i] is None:
                    human = [self.user.id]
                    sql = (f"UPDATE wl SET '{i}' = ? WHERE guild_id = ?")
                    val = (f"{human}", self.ctx.guild.id)
                    cursor.execute(sql, val)
                    des += f"Anti {i.title()}, "
                    pass
                if self.user.id in literal_eval(anti_db[i]):
                    pass
                else:
                    human = literal_eval(anti_db[i])
                    human.append(self.user.id)
                    sql = (f"UPDATE wl SET '{i}' = ? WHERE guild_id = ?")
                    val = (f"{human}", self.ctx.guild.id)
                    cursor.execute(sql, val)
                    des += f"Anti {i.title()}, "
        db.commit()
        cursor.close()
        db.close()
        if des == "":
            em = discord.Embed(description=f'{self.user.mention} is Already a Whitelisted User for the events you passed', color=botinfo.root_color)
        else:
            em = discord.Embed(description=f"{self.user.mention} was successfully added in whitelisted users for {des[:-2]} events", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()
        self.stop()

class wlMenu(discord.ui.View):
    def __init__(self, ctx: commands.Context, user : discord.Member):
        super().__init__(timeout=60)
        self.add_item(whitelistMenu(ctx, user))
        self.ctx = ctx
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [1141685323299045517, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
    

    @discord.ui.button(label="Whitelist the user from all the events", style=discord.ButtonStyle.blurple)
    async def _wl(self, interaction, button):
        user = self.user
        ctx = self.ctx
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        c=0
        for i in ls:
          if anti_db is not None:
            if user.id in literal_eval(anti_db[i]):
                c=+1
        if c == 12:
              em = discord.Embed(description=f'{user.mention} is Already a Whitelisted User', color=botinfo.root_color)
              await ctx.reply(embed=em, mention_author=False)
              await interaction.message.delete()
              self.stop()
        if anti_db is None:
              sql = (f"INSERT INTO wl(guild_id) VALUES(?, ?)")
              val = (ctx.guild.id,)
              cursor.execute(sql, val)
        db.commit()
        for i in ls:
              human = literal_eval(anti_db[i])
              human.append(user.id)
              sql = (f"UPDATE wl SET '{i}' = ? WHERE guild_id = ?")
              val = (f"{human}", ctx.guild.id)
              cursor.execute(sql, val)
        db.commit()
        em = discord.Embed(description=f"{user.mention} was successfully added in whitelisted users", color=botinfo.root_color)
        await ctx.reply(embed=em)
        cursor.close()
        db.close()
        await interaction.message.delete()
        self.stop()

class whitelistedMenu(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        options = [
            discord.SelectOption(label='Anti Ban', value="BAN"),
            discord.SelectOption(label='Anti Bot', value="BOT"),
            discord.SelectOption(label='Anti Channel Create', value="CHANNEL CREATE"),
            discord.SelectOption(label='Anti Channel Delete', value="CHANNEL DELETE"),
            discord.SelectOption(label='Anti Channel Update', value="CHANNEL UPDATE"),
            discord.SelectOption(label='Anti Guild Update', value="GUILD UPDATE"),
            discord.SelectOption(label='Anti Kick', value="KICK"),
            discord.SelectOption(label='Anti Member Update', value="MEMBER UPDATE"),
            discord.SelectOption(label='Anti Role Create', value="ROLE CREATE"),
            discord.SelectOption(label='Anti Role Delete', value="ROLE DELETE"),
            discord.SelectOption(label='Anti Role Update', value="ROLE UPDATE"),
            discord.SelectOption(label='Anti Webhook', value="WEBHOOK"),
        ]
        super().__init__(placeholder="Select specific event to see the whitelisted user",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        ctx = self.ctx
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (self.ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        db.commit()
        cursor.close()
        db.close()
        ls = []
        lss = []
        count = 1
        for i in literal_eval(anti_db[self.values[0]]):
            u = discord.utils.get(ctx.guild.members, id = i)
            if u is None:
                continue
            lss.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.mention} `[{u.id}]`")
            count += 1
        if count == 1:
            em = discord.Embed(description=f'There are no whitelisted users for Anti {self.values[0].capitalize()}', color=botinfo.root_color)
            await ctx.reply(embed=em, mention_author=False)
            await interaction.message.delete()
            self.stop()
        for i in range(0, len(lss), 10):
            ls.append(lss[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Whitelisted users of Anti {self.values[0].capitalize()} in {ctx.guild.name} - {count-1}"
            embed.description = "\n".join(k)
            embed.set_footer(text=f"{ctx.guild.me.name} • Page {no}/{len(ls)}", icon_url=ctx.guild.me.display_avatar.url)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)
        await interaction.message.delete()
        self.stop()

class wldMenu(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=60)
        self.add_item(whitelistedMenu(ctx))
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [1141685323299045517, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
    

    @discord.ui.button(label="Whitelisted users", style=discord.ButtonStyle.blurple)
    async def _wld(self, interaction, button):
        ctx = self.ctx
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        db.commit()
        cursor.close()
        db.close()
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        ls1 = []
        c = 0
        for i in ls:
            for j in literal_eval(anti_db[i]):
                if j not in ls1:
                    ls1.append(j)
                    c+=1
        if c == 0:
            em = discord.Embed(description=f'There are no whitelisted users', color=botinfo.root_color)
            await ctx.reply(embed=em, mention_author=False)
            await interaction.message.delete()
            self.stop()
        ls = []
        lss = []
        count = 1
        for i in ls1:
            u = discord.utils.get(ctx.guild.members, id = i)
            if u is None:
                continue
            lss.append(f"`[{'0' + str(count) if count < 10 else count}]` | {u.mention} `[{u.id}]`")
            count += 1
        for i in range(0, len(lss), 10):
            ls.append(lss[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"List of Whitelisted users in {ctx.guild.name} - {count-1}"
            embed.description = "\n".join(k)
            em_list.append(embed)
            no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)
        await interaction.message.delete()
        self.stop()

class unwhitelistMenu(discord.ui.Select):
    def __init__(self, ctx: commands.Context, user : discord.Member):
        options = [
            discord.SelectOption(label='Anti Ban', value="BAN"),
            discord.SelectOption(label='Anti Bot', value="BOT"),
            discord.SelectOption(label='Anti Channel Create', value="CHANNEL CREATE"),
            discord.SelectOption(label='Anti Channel Delete', value="CHANNEL DELETE"),
            discord.SelectOption(label='Anti Channel Update', value="CHANNEL UPDATE"),
            discord.SelectOption(label='Anti Guild Update', value="GUILD UPDATE"),
            discord.SelectOption(label='Anti Kick', value="KICK"),
            discord.SelectOption(label='Anti Member Update', value="MEMBER UPDATE"),
            discord.SelectOption(label='Anti Role Create', value="ROLE CREATE"),
            discord.SelectOption(label='Anti Role Delete', value="ROLE DELETE"),
            discord.SelectOption(label='Anti Role Update', value="ROLE UPDATE"),
            discord.SelectOption(label='Anti Webhook', value="WEBHOOK"),
        ]
        super().__init__(placeholder="Select specific events for blacklisting the user",
            min_values=1,
            max_values=12,
            options=options,
        )
        self.ctx = ctx
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (self.ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        des= ""
        for i in self.values:
                if anti_db[i] is None:
                    pass
                if self.user.id not in literal_eval(anti_db[i]):
                    continue
                else:
                    human = literal_eval(anti_db[i])
                    human.remove(self.user.id)
                    sql = (f"UPDATE wl SET '{i}' = ? WHERE guild_id = ?")
                    val = (f"{human}", self.ctx.guild.id)
                    cursor.execute(sql, val)
                    des += f"Anti {i.title()}, "
        db.commit()
        cursor.close()
        db.close()
        if des == "":
            em = discord.Embed(description=f'{self.user.mention} is Already a Blacklisted User for the events you passed', color=botinfo.root_color)
        else:
            em = discord.Embed(description=f"{self.user.mention} was successfully added in Blacklisted users for {des[:-2]} events", color=botinfo.root_color)
        await self.ctx.reply(embed=em)
        await interaction.message.delete()
        self.stop()

class uwlMenu(discord.ui.View):
    def __init__(self, ctx: commands.Context, user : discord.Member):
        super().__init__(timeout=60)
        self.add_item(unwhitelistMenu(ctx, user))
        self.ctx = ctx
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [1141685323299045517, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Blacklists the user from all the events", style=discord.ButtonStyle.blurple)
    async def _uwl(self, interaction, button):
        user = self.user
        ctx = self.ctx
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        if anti_db is None:
                em = discord.Embed(description=f'{user.mention} is Already a Blacklisted User', color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)
                await interaction.message.delete()
                self.stop()
                return
        if user.id not in literal_eval(anti_db["BAN"]) and user.id not in literal_eval(anti_db["BOT"]) and user.id not in literal_eval(anti_db["KICK"]) and user.id not in literal_eval(anti_db["GUILD UPDATE"]) and user.id not in literal_eval(anti_db["ROLE CREATE"]) and user.id not in literal_eval(anti_db["ROLE DELETE"]) and user.id not in literal_eval(anti_db["ROLE UPDATE"]) and user.id not in literal_eval(anti_db["CHANNEL CREATE"]) and user.id not in literal_eval(anti_db["CHANNEL DELETE"]) and user.id not in literal_eval(anti_db["CHANNEL UPDATE"]) and user.id not in literal_eval(anti_db["MEMBER UPDATE"]) and user.id not in literal_eval(anti_db["WEBHOOK"]):
                em = discord.Embed(description=f'{user.mention} is Already a Blacklisted User', color=botinfo.root_color)
                await ctx.reply(embed=em, mention_author=False)
                await interaction.message.delete()
                self.stop()
                return
        else:
            for i in ls:
                human = literal_eval(anti_db[i])
                human.remove(user.id)
                sql = (f"UPDATE wl SET '{i}' = ? WHERE guild_id = ?")
                val = (f"{human}", ctx.guild.id)
                cursor.execute(sql, val)
        db.commit()
        em = discord.Embed(description=f"{user.mention} was successfully added in Blacklisted users", color=botinfo.root_color)
        await ctx.reply(embed=em)
        cursor.close()
        db.close()
        await interaction.message.delete()
        self.stop()

class antinuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_check = []
        #self.autoroleposlock.start()

    def cog_unload(self):
        #self.autoroleposlock.cancel()
        pass

    @tasks.loop(seconds=5)
    async def autoroleposlock(self):
        await self.bot.wait_until_ready()
        rpos_db = database.fetchall1("*", "lockrpos")
        for i, j, k, l in rpos_db:
            if j == 0:
                continue
            guild = discord.utils.get(self.bot.guilds, id=i)
            if guild is None:
                continue
            if not guild.me.guild_permissions.manage_roles:
                continue
            if guild.id in self.role_check:
                self.role_check.remove(guild.id)
                continue
            before_role_pos = literal_eval(l)
            after_role_pos = {}
            if len(before_role_pos) == 0:
                continue
            check = False
            for role in guild.roles[1:]:
                after_role_pos[role.id] = role.position
                if role.position != before_role_pos[role.id]:
                    check = True
            if not check:
                continue
            xx = {}
            reverted = []
            for i in before_role_pos:
                r = guild.get_role(i)
                if r is None:
                    continue
                if r.position < guild.me.top_role.position and before_role_pos[i] < guild.me.top_role.position:
                    reverted.append(r.id)
                    xx[r] = before_role_pos[i]
            try:
                await guild.edit_role_positions(xx, reason=f"{self.bot.user.name} | Locked Role Position Recovery")
            except:
                reverted = []
            new_role_pos = {}
            for i in guild.roles[1:]:
                new_role_pos[i.id] = i.position
            database.update("lockrpos", "roles_pos", f"{new_role_pos}", "guild_id", f"{guild.id}")
            ch = guild.get_channel(k)
            if ch is None:
                continue
            else:
                ls, todo = [], []
                count = 1
                for i in before_role_pos:
                    if before_role_pos[i] == after_role_pos[i]:
                        continue
                    r = guild.get_role(i)
                    if i in reverted:
                        todo.append(f"`[{'0' + str(count) if count < 10 else count}]` | {r.mention}'s Postion was changed `{before_role_pos[i]} -> {after_role_pos[i]}`, **I changed it back to {before_role_pos[i]}**")
                    else:
                        todo.append(f"`[{'0' + str(count) if count < 10 else count}]` | {r.mention}'s Postion was changed `{before_role_pos[i]} -> {after_role_pos[i]}`, **I couldn't change it back to {before_role_pos[i]}**")
                    count += 1
                for i in range(0, len(todo), 20):
                    ls.append(todo[i: i + 20])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=botinfo.root_color)
                    embed.title = f"Role Position Updated"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                await ch.send(embeds=em_list)

    @commands.group(
        invoke_without_command=True, description="Shows the help menu for Antinuke commands"
    )
    async def antinuke(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=1141685323299045517)
        ls = ["antinuke", "antinuke anti", "antinuke punishment", "antinuke enable", "antinuke disable", "antinuke whitelist", "antinuke unwhitelist", "antinuke whitelisted", "antinuke config"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Antinuke']} Security Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    @antinuke.command(description="Shows the current settings for Security of the server")
    @commands.has_guild_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
                em = discord.Embed(description=f"{botinfo.wrong}You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  toggle WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if anti_db is None or anti_db['ALL'] == 0:
            embed = discord.Embed(color=botinfo.root_color)
            embed.set_author(name=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
            embed.title = f"{ctx.guild.name} Security Settings"
            embed.description = f"The Security system is disabled\nTo enable Security `{ctx.prefix}antinuke enable`"
            embed.set_footer(text=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
            return await ctx.send(embed=embed)
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            anti_db1 = cursor1.fetchone()
        if anti_db1 is None:
                sql = (f"INSERT INTO wl(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
        db.commit()
        des = ""
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        for i in sorted(ls):
            if anti_db[i] == 1:
                des += f"**Anti {i.capitalize()}:** {emojis.disable_no}{emojis.enable_yes}\n"
            else:
                des += f"**Anti {i.capitalize()}:** {emojis.enable_no}{emojis.disable_yes}\n"
        embed = discord.Embed(color=botinfo.root_color)
        embed.set_author(name=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
        embed.title = f"{ctx.guild.name} Security Settings"
        wl = 0
        try:
            ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
            ls1 = []
            c = 0
            for i in ls:
                for j in literal_eval(anti_db1[i]):
                    if j not in ls1:
                        x = discord.utils.get(ctx.guild.members, id=j)
                        if x is None:
                            continue
                        ls1.append(j)
                        c+=1
            if c != 0:
                wl = c
            else:
                wl = 0
        except:
            wl = 0
        embed.description = f"Move my role above for more protection.\n\nPunishments:\n\n{des}\nWhitelisted {wl} Users\nTo Change Punishment type `{ctx.prefix}antinuke punishment <type>`\nThere are two types of punishments Ban or Kick\nTo Enable or disable event type `{ctx.prefix}antinuke anti <event>`"
        query = "SELECT * FROM  punish WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db2:
            db2.row_factory = sqlite3.Row
            cursor2 = db2.cursor()
            cursor2.execute(query, val)
            anti_db2 = cursor2.fetchone()
        if anti_db2 is None:
                sql = (f"INSERT INTO punish(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
                punishment = "Ban"
        else:
            punishment = anti_db2['PUNISHMENT'].capitalize()
        embed.set_footer(text=f"Current Punishment is {punishment}", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()
        db1.commit()
        cursor1.close()
        db1.close()
        db2.commit()
        cursor2.close()
        db2.close()
    
    @antinuke.command(aliases=['on'], description="Enables the antinuke for the server")
    @commands.has_guild_permissions(administrator=True)
    async def enable(self, ctx):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            em = discord.Embed(description=f"{botinfo.wrong}Only owner of the server can run this command", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        query = "SELECT * FROM  toggle WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if anti_db is None:
                sql = (f"INSERT OR REPLACE INTO toggle(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        for i in ls:
                sql1 = (f"UPDATE toggle SET '{i}' = ? WHERE guild_id = ?")
                val1 = (1, ctx.guild.id,)
                cursor.execute(sql1,val1)
        sql1 = (f"UPDATE toggle SET 'ALL' = ? WHERE guild_id = ?")
        val1 = (1, ctx.guild.id,)
        cursor.execute(sql1,val1)
        db.commit()
        query = "SELECT * FROM  toggle WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            anti_db1 = cursor1.fetchone()
        if anti_db1 is None:
                sql = (f"INSERT INTO wl(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
        db.commit()
        des = ""
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        for i in sorted(ls):
            if anti_db[i] == 1:
                des += f"**Anti {i.capitalize()}:** {emojis.disable_no}{emojis.enable_yes}\n"
            else:
                des += f"**Anti {i.capitalize()}:** {emojis.enable_no}{emojis.disable_yes}\n"
        embed = discord.Embed(color=botinfo.root_color)
        embed.set_author(name=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
        embed.title = f"{ctx.guild.name} Security Settings"
        wl = 0
        try:
            ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
            ls1 = []
            c = 0
            for i in ls:
                for j in literal_eval(anti_db1[i]):
                    if j not in ls1:
                        ls1.append(j)
                        c+=1
            if c != 0:
                wl = c
            else:
                wl = 0
        except:
            wl = 0
        embed.description = f"Move my role above for more protection.\n\nPunishments:\n\n{des}\nWhitelisted {wl} Users\nTo Change Punishment type `{ctx.prefix}antinuke punishment <type>`\nThere are two types of punishments Ban or Kick\nTo Enable or disable event type `{ctx.prefix}antinuke anti <event>`"
        query = "SELECT * FROM  punish WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db2:
            db2.row_factory = sqlite3.Row
            cursor2 = db2.cursor()
            cursor2.execute(query, val)
            anti_db2 = cursor2.fetchone()
        if anti_db2 is None:
                sql = (f"INSERT INTO punish(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
                punishment = "Ban"
        else:
            punishment = anti_db2['PUNISHMENT'].capitalize()
        embed.set_footer(text=f"Current Punishment is {punishment}", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()
    
    @antinuke.command(aliases=['off'], description="Disables the antinuke for the server")
    @commands.has_guild_permissions(administrator=True)
    async def disable(self, ctx):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            em = discord.Embed(description=f"{botinfo.wrong}Only owner of the server can run this command", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        query = "SELECT * FROM  toggle WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if anti_db is None:
                sql = (f"INSERT OR REPLACE INTO toggle(guild_id) VALUES(?)")
                val = (ctx.guild.id,)
                cursor.execute(sql,val)
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        for i in ls:
                sql1 = (f"UPDATE toggle SET '{i}' = ? WHERE guild_id = ?")
                val1 = (0, ctx.guild.id)
                cursor.execute(sql1,val1)
        sql1 = (f"UPDATE toggle SET 'ALL' = ? WHERE guild_id = ?")
        val1 = (0, ctx.guild.id,)
        cursor.execute(sql1,val1)
        db.commit()
        cursor.close()
        db.close()
        query = "SELECT * FROM  toggle WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        des = ""
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        for i in sorted(ls):
            if anti_db[i] == 1:
                des += f"**Anti {i.capitalize()}:** {emojis.disable_no}{emojis.enable_yes}\n"
            else:
                des += f"**Anti {i.capitalize()}:** {emojis.enable_no}{emojis.disable_yes}\n"
        embed = discord.Embed(color=botinfo.root_color)
        embed.set_author(name=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
        embed.title = f"{ctx.guild.name} Security Settings"
        embed.description = f"Disabled the Security system\nTo enable Security `{ctx.prefix}antinuke enable`"
        embed.set_footer(text=f"{self.bot.user.name} Security", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @antinuke.command(description="Enable or disbales a specific event in Security")
    @commands.has_guild_permissions(administrator=True)
    async def anti(self, ctx, *, event):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            em = discord.Embed(description=f"{botinfo.wrong}Only owner of the server can run this command", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        ls = ["BAN", "KICK", "BOT", "GUILD UPDATE", "ROLE CREATE", "ROLE DELETE", "ROLE UPDATE", "CHANNEL CREATE", "CHANNEL DELETE", "CHANNEL UPDATE", "MEMBER UPDATE", "WEBHOOK"]
        if event.upper() not in ls:
            return await ctx.reply("Please provide a valid event")
        em = toggle(ctx.guild, event.upper(), self.bot.user.avatar.url, ctx.prefix)
        return await ctx.reply(embed=em)
    
    @antinuke.command(description="To change the punishment for antinuke")
    @commands.has_guild_permissions(administrator=True)
    async def punishment(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
                em = discord.Embed(description=f"{botinfo.wrong}You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  punish WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if not check(ctx.guild.id, 'all'):
              em = discord.Embed(description=f'First enable antinuke in order to change the punishment', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
        v = xddd(ctx)
        xd = await ctx.reply(embed=discord.Embed(description="Select the punishment for antinuke", color=botinfo.root_color), view=v)
        await v.wait()
        if anti_db['PUNISHMENT'] == v.value.upper():
            em = discord.Embed(description=f'Punishment is already set to {v.value.capitalize()}', color=botinfo.root_color)
            await xd.delete()
            return await ctx.reply(embed=em)
        else:
            pass
        if anti_db is None:
            sql = (f"INSERT INTO punish(guild_id, PUNISHMENT) VALUES(?, ?)")
            val = (ctx.guild.id, f'{v.value.upper()}')
            cursor.execute(sql, val)
        else:
            sql = (f"UPDATE punish SET 'PUNISHMENT' = ? WHERE guild_id = ?")
            val = (f'{v.value.upper()}', ctx.guild.id,)
            cursor.execute(sql, val)
        db.commit()
        em = discord.Embed(description=f'Punishment is set to {v.value.capitalize()}', color=botinfo.root_color)
        await xd.edit(embed=em, view=None)
        cursor.close()
        db.close()

    @antinuke.command(aliases=['wl'], description="To add a whitelisted user for Security")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def whitelist(self, ctx, *,user: discord.Member):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
                em = discord.Embed(description=f"{botinfo.wrong}You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if anti_db is None:
              sql = (f"INSERT INTO wl(guild_id) VALUES(?)")
              val = (ctx.guild.id,)
              cursor.execute(sql, val)
              db.commit()
              cursor.close()
              db.close()
        if not check(ctx.guild.id, 'ALL'):
              em = discord.Embed(description=f'First enable antinuke in order to whitelist a user', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
        view = wlMenu(ctx, user)
        em = discord.Embed(description=f"Select the options given to whitelist {user.mention}", color=botinfo.root_color)
        m = await ctx.reply(embed=em, view=view)
        await view.wait()

    @antinuke.command(aliases=['bl', 'uwl', 'unwhitelist'], description="To remove a whitelisted user from Security")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def blacklist(self, ctx, *,user: discord.Member):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
                em = discord.Embed(description=f"{botinfo.wrong}You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        if not check(ctx.guild.id, 'ALL'):
              em = discord.Embed(description=f'First enable antinuke in order to blacklist a user', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
        view = uwlMenu(ctx, user)
        em = discord.Embed(description=f"Select the options given to Blacklist {user.mention}", color=botinfo.root_color)
        m = await ctx.reply(embed=em, view=view)
        await view.wait()

    @antinuke.command(aliases=['wld'], description="Shows the whitelisted user from bot's antinuke")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def whitelisted(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in  [1141685323299045517, 979353019235840000]:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
                em = discord.Embed(description=f"{botinfo.wrong}You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  wl WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            anti_db = cursor.fetchone()
        if anti_db is None or not check(ctx.guild.id, 'ALL'):
                em = discord.Embed(description=f'First enable antinuke in order to check the whitelisted users', color=botinfo.root_color)
                return await ctx.reply(embed=em, mention_author=False)
        view = wldMenu(ctx)
        em = discord.Embed(description=f"Select the options given to see the whitelisted users", color=botinfo.root_color)
        m = await ctx.reply(embed=em, view=view)
        await view.wait()
    
    @commands.group(
        invoke_without_command=True, aliases=['lockr'], description="Shows the help menu for lockrole commands"
    )
    async def lockrole(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=1141685323299045517)
        ls = ["lockrole", "lockrole add", "lockrole remove", "lockrole wluser add", "lockrole wluser remove", "lockrole wlrole add", "lockrole wlrole remove", "lockrole config"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Antinuke']} Lockrole Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    @lockrole.command(name="config", description="Shows the settings for locked roles in the server")
    @commands.has_guild_permissions(administrator=True)
    async def r_config(self, ctx: commands.Context):
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There are no locked roles for this server", color=botinfo.root_color))
        if rl_db['role_id'] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There are no locked roles for this server", color=botinfo.root_color))
        em = discord.Embed(title=f"Locked Roles settings for the server", color=botinfo.root_color)
        br_id = literal_eval(rl_db['role_id'])
        lr = []
        for i in br_id:
            r = discord.utils.get(ctx.guild.roles, id=i)
            try:
                lr.append(r.mention)
            except:
                pass
        if len(lr) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"There are no locked roles for this server", color=botinfo.root_color))
        em.add_field(name="Locked Roles:", value="\n".join(lr), inline=False)
        u_id = literal_eval(rl_db['bypass_uid'])
        um = []
        for i in u_id:
            u = discord.utils.get(ctx.guild.members, id=i)
            if u is not None:
                um.append(u.mention)
            else:
                pass
        if len(um) == 0:
            em.add_field(name="Whitelisted Users", value="No Users are whitelisted", inline=False)
        else:
            em.add_field(name="Whitelisted Users", value="\n".join(um), inline=False)
        r_id = literal_eval(rl_db['bypass_rid'])
        rm = []
        for r in r_id:
            ru = discord.utils.get(ctx.guild.roles, id=r)
            if ru is not None:
                rm.append(ru.mention)
            else:
                pass
        if len(rm) == 0:
            em.add_field(name="Whitelisted Roles", value="No Roles are whitelisted", inline=False)
        else:
            em.add_field(name="Whitelisted Roles", value="\n".join(rm), inline=False)
        await ctx.reply(embed=em)

    @lockrole.command(name="add", description="Locks a role")
    @commands.has_guild_permissions(administrator=True)
    async def r_add(self, ctx: commands.Context, *, role: discord.Role):
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.")
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can lock a role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        m_ids = []
        for i in role.members:
            m_ids.append(i.id)
        if rl_db is None:
            x = {}
            x[role.id] = m_ids
            sql = (f"INSERT INTO lockr(guild_id, role_id, m_list) VALUES(?, ?, ?)")
            val = (ctx.guild.id, f"[{role.id}]", f"{x}")
            cursor.execute(sql, val)
        else:
            xd = literal_eval(rl_db["role_id"])
            x = literal_eval(rl_db["m_list"])
            if role.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Locked", color=botinfo.root_color))
            xd.append(role.id)
            x[role.id] = m_ids
            sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
            val = (f"{x}", ctx.guild.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully Locked the role {role.mention}", color=botinfo.right_color))

    @lockrole.command(name="remove", description="Unlocks a role")
    @commands.has_guild_permissions(administrator=True)
    async def r_remove(self, ctx: commands.Context, *, role: discord.Role):
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can unlock a role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Unlocked", color=botinfo.root_color))
        else:
            xd = literal_eval(rl_db["role_id"])
            x = literal_eval(rl_db["m_list"])
            if role.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Unlocked", color=botinfo.root_color))
            xd.remove(role.id)
            del x[role.id]
            sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
            val = (f"{x}", ctx.guild.id)
            cursor.execute(sql, val)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully Unlocked the role {role.mention}", color=botinfo.right_color))

    @lockrole.command(name="show", description="Shows Users locked in the role")
    @commands.has_guild_permissions(administrator=True)
    async def r_show(self, ctx: commands.Context, *, role: discord.Role):
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        cursor.close()
        db.close()
        no_em = discord.Embed(description=f"{role.mention} is not a locked role.", color=botinfo.root_color).set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if rl_db is None:
            return await ctx.reply(embed=no_em)
        else:
            br_id = literal_eval(rl_db["role_id"])
            if role.id not in br_id:
                cursor.close()
                db.close()
                return await ctx.reply(embed=no_em)
            else:
                x = literal_eval(rl_db["m_list"])[role.id]
                init = await ctx.reply(f"{emojis.loading} Processing the command...", mention_author=False)
                ls, lock_users = [], []
                count = 1
                for i in x:
                    member = discord.utils.get(ctx.guild.members, id=i)
                    lock_users.append(f"`[{'0' + str(count) if count < 10 else count}]` | {member} [{member.mention}]")
                    count += 1
                for i in range(0, len(lock_users), 10):
                    ls.append(lock_users[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=botinfo.root_color)
                    embed.title = f"Locked Users in {role.name} - {count-1}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await init.delete()
                await page.start(ctx)

    @lockrole.group(invoke_without_command=True, description="Shows The help menu for lockrole wluser")
    async def wluser(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = discord.utils.get(self.bot.users, id=1141685323299045517)
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}lockrole wluser`\n" 
                                                  f"Shows The help menu for lockrole wluser\n\n" 
                                                  f"`{prefix}lockrole wluser add <user>`\n" 
                                                  f"Adds a whitelisted user for locked roles\n\n"
                                                  f"`{prefix}lockrole wluser remove <user>`\n"
                                                  f"Removes a whitelisted user for locked roles\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)
    
    @wluser.command(name="add", description="Adds a whitelisted user for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def uwl_add(self, ctx: commands.Context, *, user: discord.Member):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can add a whitelisted user for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted User", color=botinfo.root_color))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted User", color=botinfo.root_color))
        else:
            xd = literal_eval(rl_db["bypass_uid"])
            if user.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is already whitelisted for locked roles", color=botinfo.root_color))
            xd.append(user.id)
            sql = (f"UPDATE lockr SET bypass_uid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully whitelisted {user.mention} for locked roles", color=botinfo.right_color))

    @wluser.command(name="remove", description="Removes a whitelisted user for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def uwl_remove(self, ctx: commands.Context, *, user: discord.Member):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can remove a whitelisted user for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=botinfo.root_color))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=botinfo.root_color))
        else:
            xd = literal_eval(rl_db["bypass_uid"])
            if user.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=botinfo.root_color))
            xd.remove(user.id)
            sql = (f"UPDATE lockr SET bypass_uid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully unwhitelisted {user.mention} for locked roles", color=botinfo.right_color))
    

    @lockrole.group(invoke_without_command=True, description="Shows The help menu for lockrole wlrole")
    async def wlrole(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = discord.utils.get(self.bot.users, id=1141685323299045517)
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}lockrole wlrole`\n" 
                                                  f"Shows The help menu for lockrole wlrole\n\n" 
                                                  f"`{prefix}lockrole wlrole add <user>`\n" 
                                                  f"Adds a whitelisted role for locked roles\n\n"
                                                  f"`{prefix}lockrole wluser remove <user>`\n"
                                                  f"Removes a whitelisted role for locked roles\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)
    
    @wlrole.command(name="add", description="Adds a whitelisted role for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def rwl_add(self, ctx: commands.Context, *, role: discord.Role):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can add a whitelisted role for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted role", color=botinfo.root_color))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted role", color=botinfo.root_color))
        else:
            xd = literal_eval(rl_db["bypass_rid"])
            if role.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already whitelisted for locked roles", color=botinfo.root_color))
            xd.append(role.id)
            sql = (f"UPDATE lockr SET bypass_rid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully whitelisted {role.mention} for locked roles", color=botinfo.right_color))

    @wlrole.command(name="remove", description="Removes a whitelisted role for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def rwl_remove(self, ctx: commands.Context, *, role: discord.Role):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can remove a whitelisted role for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=botinfo.root_color))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=botinfo.root_color))
        else:
            xd = literal_eval(rl_db["bypass_rid"])
            if role.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=botinfo.root_color))
            xd.remove(role.id)
            sql = (f"UPDATE lockr SET bypass_rid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully unwhitelisted {role.mention} for locked roles", color=botinfo.right_color))

    
    #@commands.group(invoke_without_command=True, aliases=['lockrp', 'lockrpos'], description="Shows the help menu for lockrolepos commands")
    async def lockrolepos(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=1141685323299045517)
        ls = ["lockrole", "lockrolepos enable", "lockrolepos disable", "lockrolepos config"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"{emojis.cogs['Antinuke']} Lockrolepos Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    #@lockrolepos.command(name="config", description="Shows the settings for Role Locked Positions in the server")
    #@commands.has_guild_permissions(administrator=True)
    async def rpos_config(self, ctx: commands.Context):
        query = "SELECT * FROM  lockrpos WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"Role Lock Position is disabled", color=botinfo.wrong_color))
        if rl_db['enable'] == 0:
            return await ctx.reply(embed=discord.Embed(description=f"Role Lock Position is disabled", color=botinfo.wrong_color))
        br_id = literal_eval(rl_db['roles_pos'])
        sort = {}
        for i in br_id:
            sort[br_id[i]] = i
        ls, count = [], 1
        joinpos = []
        for _t in reversed(sorted(sort)):
            r = discord.utils.get(ctx.guild.roles, id=sort[_t])
            if r is not None:
                joinpos.append(f"`[{'0' + str(_t) if count < 10 else _t}]` | {r.mention}")
            count += 1
        for i in range(0, len(joinpos), 20):
           ls.append(joinpos[i: i + 20])
        em_list = []
        no = 1
        ch = ctx.guild.get_channel(rl_db['channel_id'])
        for k in ls:
            embed =discord.Embed(color=botinfo.root_color)
            embed.title = f"Role Lock Position settings for the server"
            embed.description = "\n".join(k)  
            if ch is not None:
                embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)+1}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
            no+=1
        embed =discord.Embed(color=botinfo.root_color)
        embed.title = f"Role Lock Position settings for the server"
        if ch is not None:
            embed.add_field(name=f"Channel for loggings of updated Role Positions:", value=ch.mention, inline=True)
            embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)+1}", icon_url=self.bot.user.display_avatar.url)
            em_list.append(embed)
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    #@lockrolepos.command(name="enable", description="Enables Role Lock Position")
    #@commands.has_guild_permissions(administrator=True)
    async def rpos_add(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can Lock The position of Roles")
        query = "SELECT * FROM  lockrpos WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            if channel is None:
                cursor.close()
                db.close()
                return await ctx.reply(f"Please provide me a channel to log the changes in the position of Roles of the server.")
            xd = {}
            for i in ctx.guild.roles[1:]:
                xd[i.id] = i.position
            sql = (f"INSERT INTO lockrpos(guild_id, enable, channel_id, roles_pos) VALUES(?, ?, ?, ?)")
            val = (ctx.guild.id, 1, channel.id, f"{xd}")
            cursor.execute(sql, val)
        else:
            if rl_db['enable'] == 1:
                return await ctx.reply(embed=discord.Embed(description=f"Roles Position are already Locked", color=botinfo.root_color))
            if channel is not None:
                sql = (f"UPDATE lockrpos SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                cursor.execute(sql, val)
            else:
                c = ctx.guild.get_channel(rl_db['channel_id'])
                if c is None:
                    cursor.close()
                    db.close()
                    return await ctx.reply(f"Please provide me a channel to log the changes in the position of Roles of the server.")
            xd = {}
            for i in ctx.guild.roles[1:]:
                xd[i.id] = i.position
            sql = (f"UPDATE lockrpos SET enable = ? WHERE guild_id = ?")
            val = (1, ctx.guild.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE lockrpos SET roles_pos = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully Locked the Role Positions of the server", color=botinfo.right_color))

    #@lockrolepos.command(name="disable", description="Disables Role Lock Position")
    #@commands.has_guild_permissions(administrator=True)
    async def rpos_remove(self, ctx: commands.Context):
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in  [1141685323299045517, 979353019235840000]:
            return await ctx.reply("Only guild owner can disable Role Lock Position")
        query = "SELECT * FROM  lockrpos WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            cursor.close()
            db.close()
            return await ctx.reply(embed=discord.Embed(description=f"Role Lock Position is already disabled", color=botinfo.root_color))
        else:
            if rl_db['enable'] == 0:
                cursor.close()
                db.close()
                return await ctx.reply(embed=discord.Embed(description=f"Role Lock Position is already disabled", color=botinfo.root_color))
            sql = (f"UPDATE lockrpos SET enable = ? WHERE guild_id = ?")
            val = (0, ctx.guild.id)
            cursor.execute(sql, val)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successfully Disabled Role Lock Position", color=botinfo.right_color))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member,
                               after: discord.Member) -> None:
        await self.bot.wait_until_ready()
        guild = after.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_roles:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
            rl_db = cursor.execute("SELECT * FROM  lockr WHERE guild_id = ?", (guild.id,)).fetchone()
        if toggle_db is None and rl_db is None:
            cursor.close()
            db.close()
            return
        try:
            if toggle is not None:
                if not toggle_db['MEMBER UPDATE']:
                    c1 = False
                else:
                    c1 = True
        except:
            c1 = False
        try:
            if rl_db is not None:
                if rl_db["role_id"] == "[]":
                    c2 = False
                else:
                    c2 = True
        except:
            c2 = False
        if not c1 and not c2:
            cursor.close()
            db.close()
            return
        async for entry in after.guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.member_role_update):
            if (entry.reason == "The role is locked" or entry.reason == f"{self.bot.user.name} | Recovery") and entry.user.id == self.bot.user.id:
                cursor.close()
                db.close()
                return
            hm = []
            if toggle_db is not None:
                if toggle_db['MEMBER UPDATE']:
                    IGNORE = wll(wl_db, entry.user.id, "MEMBER UPDATE")
                    if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        pass
                    else:
                        punishment = punishh(punish_db)
                        for role in after.roles:
                            if role not in before.roles:
                                if role.permissions.administrator or role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_channels or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.mention_everyone:
                                    if entry.user.top_role.position < guild.me.top_role.position:
                                        if guild.me.guild_permissions.ban_members and punishment:
                                            await guild.ban(entry.user,
                                                        reason=f"{self.bot.user.name} | Anti Member Role Update")
                                        if guild.me.guild_permissions.kick_members and not punishment:
                                            await guild.kick(entry.user,
                                                        reason=f"{self.bot.user.name} | Anti Member Role Update")
                                    if guild.me.guild_permissions.manage_roles:
                                        if role.is_assignable():
                                            hm.append(role.id)
                                            await after.remove_roles(role, reason=f"{self.bot.user.name} | Anti Member Role Recovery")
            if rl_db is not None:
                if rl_db["role_id"] != "[]":
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    checkk = False
                    if entry.user.id == self.bot.user.id:
                        checkk = True
                    elif entry.user.id == guild.owner.id:
                        checkk = True
                    elif entry.user.id in u_id:
                        checkk = True
                    else:
                        for i in entry.user.roles:
                            if i.id in r_id:
                                checkk = True
                                break
                    br_id = literal_eval(rl_db["role_id"])
                    xxx = []
                    for i in after.roles:
                        if i not in before.roles:
                            if i.id in br_id:
                                xxx.append(i.id)
                                if not checkk:
                                    if i.id not in hm:
                                        await after.remove_roles(i, reason=f"The role is locked")
                                else:
                                    x = literal_eval(rl_db["m_list"])
                                    h = x[i.id]
                                    if after.id not in h:
                                        h.append(after.id)
                                    x[i.id] = h
                                    sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                                    val = (f"{x}", after.guild.id)
                                    cursor.execute(sql, val)
                    for i in before.roles:
                        if i not in after.roles:
                            if i.id in br_id:
                                if not checkk and i.id not in xxx:
                                    await after.add_roles(i, reason=f"The role is locked")
                                else:
                                    x = literal_eval(rl_db["m_list"])
                                    h = x[i.id]
                                    if after.id in h:
                                        h.remove(after.id)
                                    x[i.id] = h
                                    sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                                    val = (f"{x}", after.guild.id)
                                    cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user) -> None:
        await self.bot.wait_until_ready()

        if not guild:
            return
        if user.id == self.bot.user.id:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['BAN']:
            return
        async for entry in guild.audit_logs(limit=1,
                                            after=datetime.datetime.now() -
                                            datetime.timedelta(minutes=2),
                                            action=discord.AuditLogAction.ban):
            if entry.user.id == self.bot.user.id:
                return
            if user.id != entry.target.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "BAN")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Ban")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Ban")
                if guild.me.guild_permissions.ban_members:
                    await guild.unban(entry.target.id, reason=f"{self.bot.user.name} | Anti Ban Recovery")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        await self.bot.wait_until_ready()
        if member.id == self.bot.user.id:
            return

        guild = member.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['KICK']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.kick):
            if entry.user.id == self.bot.user.id:
                return
            if member.id != entry.target.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "KICK")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Kick")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Kick")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.bot.wait_until_ready()

        guild = member.guild
        if member.id == self.bot.user.id or not member.bot:
            return
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['BOT']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.bot_add):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "BOT")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            punishment = punishh(punish_db)
            if entry.user.top_role.position < guild.me.top_role.position:
                if guild.me.guild_permissions.ban_members and punishment:
                    await guild.ban(entry.user,
                                reason=f"{self.bot.user.name} | Anti Bot")
                if guild.me.guild_permissions.kick_members and not punishment:
                    await guild.kick(entry.user,
                                reason=f"{self.bot.user.name} | Anti Bot")
            if guild.me.guild_permissions.kick_members:
                await member.ban(reason=f"{self.bot.user.name} | Anti Bot Recovery")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel) -> None:
        await self.bot.wait_until_ready()

        guild = channel.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_channels:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['CHANNEL CREATE']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.channel_create):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "CHANNEL CREATE")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Create")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Create")
                
                if guild.me.guild_permissions.manage_channels:
                    await channel.delete(reason=f"{self.bot.user.name} | Anti Channel Create Recovery")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel) -> None:
        await self.bot.wait_until_ready()

        guild = channel.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_channels:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['CHANNEL DELETE']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.channel_delete):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "CHANNEL DELETE")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Delete")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Delete")
                if guild.me.guild_permissions.manage_channels:
                    await channel.clone(reason=f"{self.bot.user.name} | Anti Channel Delete Recovery")

    @commands.Cog.listener()
    async def on_guild_channel_update(
            self, before: discord.abc.GuildChannel,
            after: discord.abc.GuildChannel) -> None:
        await self.bot.wait_until_ready()

        name = before.name
        over = before.overwrites
        guild = after.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_channels:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['CHANNEL UPDATE']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.channel_update):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "CHANNEL UPDATE")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Update")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Channel Update")
                if guild.me.guild_permissions.manage_channels:
                    await after.edit(name=f"{name}", overwrites=over, reason=f"{self.bot.user.name} | Anti Channel Update Recovery")

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild,
                              after: discord.Guild) -> None:
        await self.bot.wait_until_ready()

        guild = after
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_guild:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['GUILD UPDATE']:
            return
        async for entry in after.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.guild_update):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "GUILD UPDATE")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Server Update")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Server Update")
                if guild.me.guild_permissions.manage_guild:
                    if 'COMMUNITY' in before.features:
                        com = True
                    else:
                        com = False
                    await after.edit(name=before.name, description=before.description, icon=before.icon, banner=before.banner, community=com, rules_channel=before.rules_channel, public_updates_channel=before.public_updates_channel, verification_level=before.verification_level, discoverable='DISCOVERABLE' in before.features,
                                    reason=f"{self.bot.user.name} | Anti Server Update Recovery")
                    if before.rules_channel != after.rules_channel:
                        if after.rules_channel:
                            await after.rules_channel.delete()
                    if before.public_updates_channel != after.public_updates_channel:
                        if after.public_updates_channel:
                            await after.public_updates_channel.delete()

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel) -> None:
        await self.bot.wait_until_ready()

        guild = channel.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_webhooks:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None:
            return
        if not toggle_db['WEBHOOK']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.webhook_create):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "WEBHOOK")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Webhook")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Webhook")
                if guild.me.guild_permissions.manage_webhooks:
                    webhooks = await guild.webhooks()
                    for webhook in webhooks:
                        if webhook.id == entry.target.id:
                            await webhook.delete(reason=f"{self.bot.user.name} | Anti Webhook Recovery")
                            break

    @commands.Cog.listener()
    async def on_guild_role_create(self, role) -> None:
        await self.bot.wait_until_ready()

        guild = role.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_roles:
            return
        if guild.id not in self.role_check:
            self.role_check.append(guild.id)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
            rposl_db = cursor.execute("SELECT * FROM  lockrpos WHERE guild_id = ?", (guild.id,)).fetchone()
        if rposl_db is not None:
            if rposl_db['enable'] == 1:
                xd = {}
                for i in guild.roles[1:]:
                    xd[i.id] = i.position
                sql = (f"UPDATE lockrpos SET roles_pos = ? WHERE guild_id = ?")
                val = (f"{xd}", guild.id)
                cursor.execute(sql, val)
                db.commit()
        if toggle_db is None:
            return
        if not toggle_db['ROLE CREATE']:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.role_create):
            if entry.user.id == self.bot.user.id:
                return
            IGNORE = wll(wl_db, entry.user.id, "ROLE CREATE")
            if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                return
            else:
                punishment = punishh(punish_db)
                if entry.user.top_role.position < guild.me.top_role.position:
                    if guild.me.guild_permissions.ban_members and punishment:
                        await guild.ban(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Role Create")
                    if guild.me.guild_permissions.kick_members and not punishment:
                        await guild.kick(entry.user,
                                    reason=f"{self.bot.user.name} | Anti Role Create")
                if guild.me.guild_permissions.manage_roles:
                    await role.delete(reason=f"{self.bot.user.name} | Anti Role Create Recovery")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role) -> None:
        await self.bot.wait_until_ready()

        guild = role.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_roles:
            return
        if guild.id not in self.role_check:
            self.role_check.append(guild.id)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
            rl_db = cursor.execute("SELECT * FROM  lockr WHERE guild_id = ?", (guild.id,)).fetchone()
            rposl_db = cursor.execute("SELECT * FROM  lockrpos WHERE guild_id = ?", (guild.id,)).fetchone()
        if rposl_db is not None:
            if rposl_db['enable'] == 1:
                xd = {}
                for i in guild.roles[1:]:
                    xd[i.id] = i.position
                sql = (f"UPDATE lockrpos SET roles_pos = ? WHERE guild_id = ?")
                val = (f"{xd}", guild.id)
                cursor.execute(sql, val)
                db.commit()
        if toggle_db is None and rl_db is None:
            cursor.close()
            db.close()
            return
        if not toggle_db['ROLE DELETE']:
            if rl_db is not None:
                if rl_db["role_id"] == "[]":
                    cursor.close()
                    db.close()
                    return
                else:
                    br_id = literal_eval(rl_db["role_id"])
                    if role.id not in br_id:
                        cursor.close()
                        db.close()
                        return
        try:
            if toggle is not None:
                if not toggle_db['MEMBER UPDATE']:
                    c1 = False
                else:
                    c1 = True
        except:
            c1 = False
        try:
            if rl_db is not None:
                if rl_db["role_id"] == "[]":
                    c2 = False
                else:
                    br_id = literal_eval(rl_db["role_id"])
                    if role.id not in br_id:
                        c2 = False
                    else:
                        c2 = True
        except:
            c2 = False
        if not c1 and not c2:
            cursor.close()
            db.close()
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.role_delete):
            if entry.user.id == self.bot.user.id:
                cursor.close()
                db.close()
                return
            rrr = None
            if toggle_db is not None:
                if toggle_db['ROLE CREATE']:
                    IGNORE = wll(wl_db, entry.user.id, "ROLE DELETE")
                    if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        pass
                    else:
                        punishment = punishh(punish_db)
                        if entry.user.top_role.position < guild.me.top_role.position:
                            if guild.me.guild_permissions.ban_members and punishment:
                                await guild.ban(entry.user,
                                            reason=f"{self.bot.user.name} | Anti Role Delete")
                            if guild.me.guild_permissions.kick_members and not punishment:
                                await guild.kick(entry.user,
                                            reason=f"{self.bot.user.name} | Anti Role Delete")
                        if guild.me.guild_permissions.manage_roles:
                            rrr = await guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable ,reason=f"{self.bot.user.name} | Anti Role Delete Recovery")
            if rl_db is not None:
                if rl_db["role_id"] != "[]":
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    br_id = literal_eval(rl_db["role_id"])
                    if role.id not in br_id:
                        cursor.close()
                        db.close()
                        pass
                    else:
                        checkk = False
                        if entry.user.id in u_id or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                            checkk = True
                        else:
                            for i in entry.user.roles:
                                if i.id in r_id:
                                    checkk = True
                                    break
                        if not checkk:
                            br_id.remove(role.id)
                        else:
                            br_id = literal_eval(rl_db["role_id"])
                            x = literal_eval(rl_db['m_list'])
                            del x[role.id]
                            br_id.remove(role.id)
                            sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
                            val = (f"{br_id}", guild.id)
                            cursor.execute(sql, val)
                            sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                            val = (f"{x}", guild.id)
                            cursor.execute(sql, val)
                            db.commit()
                            cursor.close()
                            db.close()
                        if not check and guild.me.guild_permissions.manage_roles:
                            if rrr is None:
                                rrr = await guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable ,reason=f"{self.bot.user.name} | Locked Role Recovery")
                        x = literal_eval(rl_db['m_list'])
                        h = x[role.id]
                        del x[role.id]
                        if rrr is not None:
                            x[rrr.id] = h
                            br_id.append(rrr.id)
                        sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
                        val = (f"{br_id}", guild.id)
                        cursor.execute(sql, val)
                        sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                        val = (f"{x}", guild.id)
                        cursor.execute(sql, val)
                        db.commit()
                        cursor.close()
                        db.close()
                        if guild.me.guild_permissions.manage_roles and rrr is not None:
                            for i in h:
                                u = discord.utils.get(guild.members, id=i)
                                await u.add_roles(rrr, reason=f"{self.bot.user.name} | Locked Role Recovery")
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            rposl_db = cursor.execute("SELECT * FROM  lockrpos WHERE guild_id = ?", (guild.id,)).fetchone()
        if rposl_db is not None:
            if rposl_db['enable'] == 1:
                xd = {}
                for i in guild.roles[1:]:
                    xd[i.id] = i.position
                sql = (f"UPDATE lockrpos SET roles_pos = ? WHERE guild_id = ?")
                val = (f"{xd}", guild.id)
                cursor.execute(sql, val)
                db.commit()
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role,
                                   after: discord.Role) -> None:
        await self.bot.wait_until_ready()
        guild = after.guild
        name = before.name
        colour = before.colour
        perm = before.permissions
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log and not guild.me.guild_permissions.kick_members and not guild.me.guild_permissions.ban_members and not guild.me.guild_permissions.manage_roles:
            return
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            wl_db = cursor.execute("SELECT * FROM  wl WHERE guild_id = ?", (guild.id,)).fetchone()
            toggle_db = cursor.execute("SELECT * FROM  toggle WHERE guild_id = ?", (guild.id,)).fetchone()
            punish_db = cursor.execute("SELECT * FROM  punish WHERE guild_id = ?", (guild.id,)).fetchone()
            rl_db = cursor.execute("SELECT * FROM  lockr WHERE guild_id = ?", (guild.id,)).fetchone()
        cursor.close()
        db.close()
        if toggle_db is None and rl_db is None:
            return
        if toggle_db is not None:
            if toggle_db['ROLE UPDATE']:
                async for entry in guild.audit_logs(
                        limit=1,
                        after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                        action=discord.AuditLogAction.role_update):
                    if entry.user.id == self.bot.user.id:
                        return
                    IGNORE = wll(wl_db, entry.user.id, "ROLE UPDATE")
                    if IGNORE or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        return
                    else:
                        punishment = punishh(punish_db)
                        if entry.user.top_role.position < guild.me.top_role.position:
                            if guild.me.guild_permissions.ban_members and punishment:
                                await guild.ban(entry.user,
                                            reason=f"{self.bot.user.name} | Anti Role Update")
                            if guild.me.guild_permissions.kick_members and not punishment:
                                await guild.kick(entry.user,
                                            reason=f"{self.bot.user.name} | Anti Role Update")
                        if guild.me.guild_permissions.manage_roles and after.position < guild.me.top_role.position:
                                await after.edit(name=name, colour=colour, permissions=perm, hoist=before.hoist, mentionable=before.mentionable, reason=f"{self.bot.user.name} | Anti Role Update Recovery")
        elif rl_db is not None:
            if rl_db["role_id"] != "[]":
                u_id = literal_eval(rl_db["bypass_uid"])
                r_id = literal_eval(rl_db["bypass_rid"])
                br_id = literal_eval(rl_db["role_id"])
                if after.id not in br_id:
                    return
                async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.role_update):
                    if entry.user.id in u_id or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        return
                    else:
                        for i in entry.user.roles:
                            if i.id in r_id:
                                return
                    await after.edit(name=name, colour=colour, permissions=perm, hoist=before.hoist, mentionable=before.mentionable, reason=f"{self.bot.user.name} | Locked Role Update Recovery")

async def setup(bot):
	await bot.add_cog(antinuke(bot))