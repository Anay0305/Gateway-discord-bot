import discord
from discord.ext import commands
from discord import *
import database
import random
from ast import literal_eval
from embed import *
from converter import *
import botinfo
import emojis

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
      
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in botinfo.main_devs:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True
      
class HumansOrBots(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None 

    @discord.ui.button(label="Humans", custom_id='humans', style=discord.ButtonStyle.green)
    async def _human(self, interaction, button):
        self.value = 'humans'
        self.stop()

    @discord.ui.button(label="Bots", custom_id='bots', style=discord.ButtonStyle.green)
    async def _bot(self, interaction, button):
        self.value = 'bots'
        self.stop()

    @discord.ui.button(label="Both", custom_id='both', style=discord.ButtonStyle.blurple)
    async def _both(self, interaction, button):
        self.value = 'both'
        self.stop()

    @discord.ui.button(label="Cancel", emoji=f"{emojis.wrong} ", custom_id='cancel', style=discord.ButtonStyle.danger)
    async def _cancel(self, interaction, button):
        self.value = 'cancel'
        self.stop()
class YesOrNo(BasicView):
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

class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    

    @discord.ui.button(label="Enable", custom_id='on', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'on'
        self.stop()

    @discord.ui.button(label="Disable", custom_id='off', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'off'
        self.stop()

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

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def _send(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        embed = await getembed(self.ctx.guild, self.ctx.author, self.id, True)
        embed = await convert_dict(self.ctx.guild, self.ctx.author, discord.Embed.from_dict(embed))
        welcome_db = database.fetchone("embed", "welcome", "guild_id", self.ctx.guild.id)
        if welcome_db is not None:
            database.update("welcome", "emdata", f"{embed}", "guild_id", self.ctx.guild.id)
        em = discord.Embed(color=botinfo.root_color)
        em.description = f"Successfully updated the welcome embed"
        await interaction.message.edit(content=None, embed=em, view=None)
        await delembed(self.id)
        self.stop()

    @discord.ui.button(label="Userinfo Template", style=discord.ButtonStyle.grey)
    async def _ui(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        ui = {'footer': {'text': 'You are $membercount_ordinal member of the server', 'icon_url': '$server_icon'}, 'thumbnail': {'url': '$server_icon'}, 'author': {'name': '$user_username', 'icon_url': '$user_avatar'}, 'color': 3092790, 'timestamp': '$now', 'type': 'rich', 'description': 'Account Created $user_created\nUser Joined $user_joined\nWe hope you enjoy your stay here', 'title': 'Welcome to $server_name'}
        uii = await convert_sample_embed(self.ctx.guild, self.ctx.author, ui)
        uii = discord.Embed.from_dict(uii)
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
        uii.footer.text = f"You are {ordinal(len(self.ctx.guild.members))} member of the server"
        v = YesOrNo(self.ctx)
        await interaction.message.edit(content="Do you want to continue with this template?", embed=uii, view=v)
        await v.wait()
        if v.value is None:
          await interaction.delete_original_response()
          self.stop()
        if v.value == "No":
          pass
        else:
          uii.footer.text = 'You are $membercount_ordinal member of the server'
          await updateembed(self.id, uii.to_dict())
        em = await getembed(self.ctx.guild, self.ctx.author, self.id)
        em = await convert_sample_embed(self.ctx.guild, self.ctx.author, em)
        em = discord.Embed.from_dict(em)
        await interaction.message.edit(content="This is a sample of welcome embed you have updated till now", embed=em, view=self)

    @discord.ui.button(label="Keywords", style=discord.ButtonStyle.blurple)
    async def _keywords(self, interaction: discord.Interaction, button):
        em = discord.Embed(title="Here are some keywords, which you can use in your welcome embed.", description="```$user_name - displays username.\n$user_username - display users username with his discriminator.\n$user_discriminator - display users discriminator.\n$user_id - display users ID.\n$user_avatar - display users avatar.\n$user_mention - mentions the user.\n$user_created - displays the timestamp of when the user id was created.\n$user_joined - displays the timestamp of when the user joined the server.\n$user_profile - direct link for the user's profile\n$server_name - displays server name.\n$server_id - displays server ID.\n$server_icon - displays server icon.\n$membercount - show the member count of the server.\n$membercount_ordinal - same as membercount but includes ordinal number (st, th, rd).\n\n```", color=botinfo.root_color)
        em.set_author(name="Welcome Keywords", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=em, ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def _cancel(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        em = discord.Embed(color=botinfo.root_color)
        em.description = f"Cancelled the command"
        await interaction.edit_original_response(content=None, embed=em, view=None)
        await delembed(self.id)
        self.stop()

def convert(date):
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
        return val * time_dic[unit]
    else:
        return val * time_dic[unit]

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, user):
        await self.bot.wait_until_ready()
        raid_db = database.fetchone("*", "raidmode", "guild_id", user.guild.id)
        if raid_db is not None:
          if raid_db['lock'] == 1:
              return
        welcome_db = database.fetchone("*", "welcome", "guild_id", user.guild.id)
        if welcome_db is None:
            return
        channel_id = welcome_db['channel_id']
        channel = self.bot.get_channel(channel_id)
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
        member = user
        guild = member.guild
        msg = str(welcome_db['msg']).replace("$user_name", member.name).replace("$user_username", str(member)).replace("$user_discriminator", f"#{member.discriminator}").replace("$user_id", str(member.id)).replace("$user_avatar", str(member.display_avatar.url)).replace("$user_mention", str(member.mention)).replace("$user_created", f"<t:{round(member.created_at.timestamp())}:R>").replace("$user_joined", f"<t:{round(member.joined_at.timestamp())}:R>").replace("$server_name", guild.name).replace("$server_id", str(guild.id)).replace("$membercount_ordinal", ordinal(len(guild.members))).replace("$membercount", str(len(guild.members)))
        data = literal_eval(welcome_db['emdata'])
        ping = welcome_db['ping']
        emb = welcome_db['embed']
        auto = welcome_db["autodel"] or None
        if emb == 1:
            embed = await convert_embed(user.guild, user, data)
            embed = discord.Embed.from_dict(embed)
            if ping == 1:
                if user.mention in msg:
                    c = False
                else:
                    c = True
                await channel.send(msg, embed=embed, delete_after=auto)
                if c:
                    await channel.send(f"{user.mention}", delete_after=1)
            if ping == 0:
                await channel.send(embed=embed, delete_after=auto)
        else:
            await channel.send(msg, delete_after=auto)

    @commands.group(invoke_without_command=True, description="Shows the help menu for welcome")
    async def welcome(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        general = discord.Embed(title=f"{emojis.cogs['Welcome']} Welcome Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}welcome`\n"
                                                 f"THis Command Will Show This Page\n\n"
                                                 f"`{prefix}welcome channel <channel>`\n"
                                                 f"Set the Welcome Channel\n\n"
                                                 f"`{prefix}welcome embed <on/off>`\n"
                                                 f"Toggle embed For Welcomer\n\n"
                                                 f"`{prefix}welcome ping <on/off>`\n"
                                                 f"Toggle embed ping For Welcomer\n\n"
                                                 f"`{prefix}welcome message/msg <message>`\n"
                                                 f"Sets the Description for Welcome Message\n\n"
                                                 f"`{prefix}welcome embed edit`\n"
                                                 f"To customize welcome embed\n\n"
                                                 f"`{prefix}welcome autodel <seconds>`\n"
                                                 f"Set the Welcome to automatically delete after x Seconds\n\n"
                                                 f"`{prefix}welcome test`\n"
                                                 f"Test the welcome message how it will look like\n\n"
                                                 f"`{prefix}welcome config`\n"
                                                 f"Shows The current Welcome Settings For the server\n\n" 
                                                 f"`{prefix}welcome reset`\n" 
                                                 f"Resets the Welcome Settings For the server\n\n")
        general.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        general.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=general)
    
    @welcome.command(name="test", description="Tests your current welcome settings")
    @commands.has_permissions(administrator=True)
    async def test(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        channel_id = welcome_db['channel_id']
        channel = self.bot.get_channel(channel_id)
        member = ctx.author
        guild = ctx.guild
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
        msg = str(welcome_db['msg']).replace("$user_name", member.name).replace("$user_username", str(member)).replace("$user_discriminator", f"#{member.discriminator}").replace("$user_id", str(member.id)).replace("$user_avatar", str(member.display_avatar.url)).replace("$user_mention", str(member.mention)).replace("$user_created", f"<t:{round(member.created_at.timestamp())}:R>").replace("$user_joined", f"<t:{round(member.joined_at.timestamp())}:R>").replace("$server_name", guild.name).replace("$server_id", str(guild.id)).replace("$membercount_ordinal", ordinal(len(guild.members))).replace("$membercount", str(len(guild.members)))
        data = literal_eval(welcome_db['emdata'])
        ping = welcome_db['ping']
        emb = welcome_db['embed']
        auto = welcome_db["autodel"] or None
        if emb == 1:
          embed = await convert_embed(ctx.guild, ctx.author, data)
          embed = discord.Embed.from_dict(embed)
          if ping == 1:
            if ctx.author.mention in msg:
              c = False
            else:
              c = True
            await channel.send(msg, embed=embed, delete_after=auto)
            if c:
              await channel.send(f"{ctx.author.mention}", delete_after=1)
          if ping == 0:
            await channel.send(embed=embed, delete_after=auto)
        else:
          await channel.send(msg, delete_after=auto)

    @welcome.command(name="channel", aliases=['enable'], description="Sets the channel for welcome")
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        channel = channel or ctx.channel
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
            val = (ctx.guild.id, channel.id)
            database.insert("welcome", "guild_id, channel_id", val)
        else:
            database.update("welcome", "channel_id", channel.id, "guild_id", ctx.guild.id)
        await ctx.send(f'Welcome Channel set to **{channel.mention}**')

    @welcome.group(invoke_without_command=True, name="embed", description="Toggles the embed for welcome")
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        view = OnOrOff(ctx)
        em = discord.Embed(description="Click the button below to Enable or Disable the Embed", color=botinfo.root_color)
        hm = await ctx.reply(embed=em, mention_author=False, view=view)
        await view.wait()
        if view.value == 'on':
          if welcome_db is not None:
            await hm.delete()
            if welcome_db['embed'] == 1:
              em = discord.Embed(description="Embed is Already Enabled", color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            database.update("welcome", "embed", 1, "guild_id", ctx.guild.id)
            await ctx.reply(embed=discord.Embed(description=f'Embed is Enabled', color=botinfo.root_color), mention_author=False)
        if view.value == 'off':
          if welcome_db is not None:
            await hm.delete()
            if welcome_db['embed'] == 0:
              em = discord.Embed(description="Embed is Already Disabled", color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            database.update("welcome", "embed", 0, "guild_id", ctx.guild.id)
            await ctx.reply(embed=discord.Embed(description=f'Embed is Disabled', color=botinfo.root_color), mention_author=False)

    @welcome.command(name="ping", description="Toggles the ping for Welcome")
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        view = OnOrOff(ctx)
        em = discord.Embed(description="Click the button below to Enable or Disable the Ping", color=botinfo.root_color)
        hm = await ctx.reply(embed=em, mention_author=False, view=view)
        await view.wait()
        if view.value == 'on':
          if welcome_db is not None:
            await hm.delete()
            if welcome_db['ping'] == 1:
              em = discord.Embed(description="Ping is Already Enabled", color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            database.update("welcome", "ping", 1, "guild_id", ctx.guild.id)
            await ctx.reply(embed=discord.Embed(description=f'Ping is Enabled', color=botinfo.root_color), mention_author=False)
        if view.value == 'off':
          if welcome_db is not None:
            await hm.delete()
            if welcome_db['ping'] == 0:
              em = discord.Embed(description="Ping is Already Disabled", color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            database.update("welcome", "ping", 0, "guild_id", ctx.guild.id)
            await ctx.reply(embed=discord.Embed(description=f'Ping is Disabled', color=botinfo.root_color), mention_author=False)

    @welcome.command(name="keywords", aliases=["keyword"], description="Shows the keyword to use for setting the message")
    async def keywords(self, ctx):
      em = discord.Embed(title="Here are some keywords, which you can use in your welcome embed.", description="```$user_name - displays username.\n$user_username - display users username with his discriminator.\n$user_discriminator - display users discriminator.\n$user_id - display users ID.\n$user_avatar - display users avatar.\n$user_mention - mentions the user.\n$user_created - displays the timestamp of when the user id was created.\n$user_joined - displays the timestamp of when the user joined the server.\n$user_profile - direct link for the user's profile\n$server_name - displays server name.\n$server_id - displays server ID.\n$server_icon - displays server icon.\n$membercount - show the member count of the server.\n$membercount_ordinal - same as membercount but includes ordinal number (st, th, rd).\n\n```", color=botinfo.root_color)
      em.set_author(name="Welcome Keywords", icon_url=self.bot.user.avatar.url)
      await ctx.reply(embed=em)

    @welcome.command(name="message", aliases=["msg"], description="Setup the message for welcome")
    @commands.has_permissions(administrator=True)
    async def message(self, ctx, *, message=None):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        if message is None:
          em = discord.Embed(title="Here are some keywords, which you can use in your welcome message.", description="**Send your welcome message in this channel now.**\n\n```$user_name - displays username.\n$user_username - display users username with his discriminator.\n$user_discriminator - display users discriminator.\n$user_id - display users ID.\n$user_avatar - display users avatar.\n$user_mention - mentions the user.\n$user_created - displays the timestamp of when the user id was created.\n$user_joined - displays the timestamp of when the user joined the server.\n$server_name - displays server name.\n$server_id - displays server ID.\n$server_icon - displays server icon.\n$membercount - show the member count of the server.\n$membercount_ordinal - same as membercount but includes ordinal number (st, th, rd).\n\n```", color=botinfo.root_color)
          em.set_author(name="Welcome Message Setup")
          em.set_footer(text="Type cancel to stop the command")
          await ctx.send(embed=em)
          def message_check(m):
              return (
                  m.author.id == ctx.author.id
                  and ctx.channel == m.channel
              )
          mssgg = await self.bot.wait_for("message", check=message_check)
          if mssgg.content.lower() == "cancel":
              return await ctx.send("Cancelled the changes")
          mssg = mssgg.content
        else:
          mssg = message
        if welcome_db is not None:
            database.update("welcome", "msg", mssg, "guild_id", ctx.guild.id)
            await ctx.send(f'I Set The Welcome Message')
    
    @embed.command(name="edit", aliases=['custom'], description="To customize welcome embed")
    @commands.has_permissions(administrator=True)
    async def edit(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        data = literal_eval(welcome_db['emdata'])
        em = await convert_sample_embed(ctx.guild, ctx.author, data)
        x = round(random.random()*100000)
        await updateembed(x, em)
        v = embedSend(self.bot, ctx, x)
        await ctx.reply("This is a sample of welcome embed you have updated till now", embed=discord.Embed.from_dict(em), view=v)
        await v.wait()

    @welcome.command(name="autodel", description="Sets the time for deleting the welcome message")
    @commands.has_permissions(administrator=True)
    async def autodel(self, ctx, *, time):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        t = convert(time)
        if t == -1 or t == -2:
            em = discord.Embed(description=f"{emojis.wrong} Provide specific time!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if welcome_db is not None:
            database.update("welcome", "autodel", int(t), "guild_id", ctx.guild.id)
            await ctx.send(f'I Set The autodel timer')
            
    @welcome.command(name="config", description="Shows the current Welcome settings")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx: commands.Context):
        welcome_db = database.fetchone("*", "welcome", "guild_id", ctx.guild.id)
        if welcome_db is None:
          return await ctx.reply(f'First setup Your welcome channel by Running `{ctx.prefix}welcome channel #channel/id`')
        channel = welcome_db['channel_id']
        msg = welcome_db['msg']
        ping = welcome_db['ping']
        emb = welcome_db['embed']
        auto = welcome_db["autodel"] or None
        if emb == 1:
          emb = "Enabled"
        else:
          emb = "Disabled"
        if ping == 1:
          ping = "Enabled"
        else:
          ping = "Disabled"
        embed = discord.Embed(title=f"Welcome Settings For {ctx.guild.name}", color=botinfo.root_color)
        embed.add_field(name="Welcome Channel:", value=f"<#{channel}>")
        embed.add_field(name="Welcome Message:", value=msg)
        embed.add_field(name="Welcome Embed:", value=emb)
        embed.add_field(name="Welcome Ping:", value=ping)
        embed.add_field(name="Welcome Autodel:", value=auto)
        await ctx.send(embed=embed)
            
    @welcome.command(name="reset", aliases=['disable'], description="Resets the welcome settings for the server")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        database.delete("welcome", "guild_id", ctx.guild.id)
        await ctx.send(f"{ctx.author.mention} I Reset The Welcome settings for : {ctx.guild.name}")
    
    @commands.group(aliases=["autoroles"], invoke_without_command=True)
    async def autorole(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}autorole`\n"
                                                 f"This Command Will Show This Page\n\n"
                                                 f"`{prefix}autorole humans add <role>`\n"
                                                 f"Adds the role in Autorole humans list\n\n"
                                                 f"`{prefix}autorole humans remove <role>`\n"
                                                 f"Removes the role from Autorole humans list\n\n"
                                                 f"`{prefix}autorole bot add <role>`\n"
                                                 f"Adds the role in Autorole Bot list\n\n"
                                                 f"`{prefix}autorole bot remove <role>`\n"
                                                 f"Removes the role from Autorole Bot list\n\n"
                                                 f"`{prefix}autorole config`\n"
                                                 f"Shows the current Autorole settings\n\n"
                                                 f"`{prefix}autorole reset`\n"
                                                 f"Resets the autorole settings\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @autorole.command(name="config")
    @commands.has_permissions(administrator=True)
    async def _config(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        auto_db = database.fetchone("*", "auto", "guild_id", ctx.guild.id)
        if auto_db['humans'] is None:
          human = "No Roles"
        elif auto_db['humans'] == '[]':
          human = "No Roles"
        else:
          human = literal_eval(auto_db['humans'])
        if auto_db['bots'] is None:
          bot = "No Roles"
        elif auto_db['bots'] == '[]':
          bot = "No Roles"
        else:
          bot = literal_eval(auto_db['bots'])
        em = discord.Embed(title=f'Autorole settings for {ctx.guild.name}', color=botinfo.root_color)
        if human != 'No Roles':
          count = 0
          humann = ""
          for i in range(len(human)):
            humann+= f"<@&{human[count]}>\n"
            count+=1
          em.add_field(name="Autorole Humans:", value=humann)
        else:
          em.add_field(name="Autorole Humans:", value=human)
        if bot != 'No Roles':
          count1 = 0
          bott = ""
          for i in range(len(bot)):
            bott+= f"<@&{bot[count1]}>\n"
            count1+=1
          em.add_field(name="Autorole Bots:", value=bott)
        else:
          em.add_field(name="Autorole Bots:", value=bot)
        em.set_footer(text=f"{self.bot.user.name} Autorole", icon_url=self.bot.user.display_avatar.url)
        return await ctx.reply(embed=em, mention_author=False)

    @autorole.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def _reset(self, ctx):
        if ctx.guild.owner.id == ctx.author.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
        view = HumansOrBots(ctx)
        em = discord.Embed(description="Are you sure you want to reset the Autoroles settings?", color=botinfo.root_color)
        hm = await ctx.reply(embed=em, mention_author=False, view=view)
        await view.wait()
        if view.value == 'humans':
          await hm.delete()
          database.update("auto", "humans", f'[]', "guild_id", ctx.guild.id)
          em = discord.Embed(description="I Cleared the settings for Autoroles humans", color=botinfo.root_color)
          em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
          await ctx.reply(embed=em, mention_author=False)
        if view.value == 'bots':
          await hm.delete()
          database.update("auto", "bots", f'[]', "guild_id", ctx.guild.id)
          em = discord.Embed(description="I Cleared the settings for Autoroles bots", color=botinfo.root_color)
          em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
          await ctx.reply(embed=em, mention_author=False)
        if view.value == 'both':
          await hm.delete()
          dic = {
             'humans': f'[]',
             'bots': f'[]'
          }
          database.update_bulk("auto", dic, "guild_id", ctx.guild.id)
          em = discord.Embed(description="I Cleared the settings for Autoroles", color=botinfo.root_color)
          em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
          await ctx.reply(embed=em, mention_author=False)
        if view.value == 'cancel':
            await hm.delete()
            em = discord.Embed(description="Canceled The Command", color=botinfo.wrong_color)
            return await ctx.reply(embed=em, mention_author=False)

    @autorole.group(aliases=['human'], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def humans(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}autorole humans`\n"
                                                 f"This Command Will Show This Page\n\n"
                                                 f"`{prefix}autorole humans add <role>`\n"
                                                 f"Adds the role in Autorole humans list\n\n"
                                                 f"`{prefix}autorole humans remove <role>`\n"
                                                 f"Removes the role from Autorole humans list\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @humans.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.reply(embed=em, mention_author=False)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if role.permissions.administrator:
                em = discord.Embed(description=f"You cannot add A role having Administrator perms in autorole", color=botinfo.root_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            auto_db = database.fetchone("*", "auto", "guild_id", ctx.guild.id)
            if auto_db['humans'] is not None:
             if role.id in literal_eval(auto_db['humans']):
              em = discord.Embed(description=f'{role.mention} is Already in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            if auto_db['humans'] is None:
              database.update("auto", "humans", f'[{role.id}]', "guild_id", ctx.guild.id)
            else:
              human = literal_eval(auto_db['humans'])
              human.append(role.id)
              database.update("auto", "humans", f"{human}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Added {role.mention} To Autorole humans list", color=botinfo.root_color)
            em.set_footer(text=f"{self.bot.user.name} Autoroles", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=em, mention_author=False)

    @humans.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.reply(embed=em, mention_author=False)
            auto_db = database.fetchone("*", "auto", "guild_id", ctx.guild.id)
            if auto_db['humans'] is not None:
             if role.id not in literal_eval(auto_db['humans']):
              em = discord.Embed(description=f'{role.mention} is not in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            if auto_db['humans'] is None:
              em = discord.Embed(description=f'{role.mention} is not in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            else:
              human = literal_eval(auto_db['humans'])
              human.remove(role.id)
              database.update("auto", "humans", f"{human}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Removed {role.mention} from Autorole humans list", color=botinfo.root_color)
            em.set_footer(text=f"{self.bot.user.name} Autoroles", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=em, mention_author=False)

    @autorole.group(aliases=['bot'], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def bots(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}autorole bots`\n"
                                                 f"This Command Will Show This Page\n\n"
                                                 f"`{prefix}autorole bots add <role>`\n"
                                                 f"Adds the role in Autorole Bots list\n\n"
                                                 f"`{prefix}autorole bots remove <role>`\n"
                                                 f"Removes the role from Autorole Bots list\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=listem)

    @bots.command(name="add")
    @commands.has_permissions(administrator=True)
    async def _add(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.reply(embed=em, mention_author=False)
            if role.position >= ctx.guild.me.top_role.position:
                em = discord.Embed(description=f"{role.mention} is above my top role, move my role above the {role.mention} and run the command again", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            if not role.is_assignable():
                em = discord.Embed(description=f"{role.mention} can't be assigned to any user by the bot Please try again with different role.", color=botinfo.wrong_color)
                return await ctx.reply(embed=em, mention_author=False)
            auto_db = database.fetchone("*", "auto", "guild_id", ctx.guild.id)
            if auto_db['bots'] is not None:
             if role.id in literal_eval(auto_db['bots']):
              em = discord.Embed(description=f'{role.mention} is Already in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            if auto_db['bots'] is None:
              database.update("auto", "bots", f"[{role.id}]", "guild_id", ctx.guild.id)
            else:
              bot = literal_eval(auto_db['bots'])
              bot.append(role.id)
              database.update("auto", "bots", f"{bot}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Added {role.mention} To Autorole Bots list", color=botinfo.root_color)
            em.set_footer(text=f"{self.bot.user.name} Autoroles", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=em, mention_author=False)

    @bots.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def _remove(self, ctx, *,role: discord.Role):
            if ctx.guild.owner.id == ctx.author.id:
                pass
            else:
                if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in botinfo.main_devs:
                    em = discord.Embed(description=f"{emojis.wrong} You must Have Higher Role than Bot To run This Command", color=botinfo.wrong_color)
                    return await ctx.reply(embed=em, mention_author=False)
            auto_db = database.fetchone("*", "auto", "guild_id", ctx.guild.id)
            if auto_db['bots'] is not None:
             if role.id not in literal_eval(auto_db['bots']):
              em = discord.Embed(description=f'{role.mention} is not in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            if auto_db['bots'] is None:
              em = discord.Embed(description=f'{role.mention} is not in Autorole List', color=botinfo.root_color)
              return await ctx.reply(embed=em, mention_author=False)
            else:
              bot = literal_eval(auto_db['bot'])
              bot.remove(role.id)
              database.update("auto", "bots", f"{bot}", "guild_id", ctx.guild.id)
            em = discord.Embed(description=f"Removed {role.mention} from Autorole Bot list", color=botinfo.root_color)
            em.set_footer(text=f"{self.bot.user.name} Autoroles", icon_url=self.bot.user.display_avatar.url)
            await ctx.reply(embed=em, mention_author=False)

async def setup(bot):
    await bot.add_cog(welcome(bot))