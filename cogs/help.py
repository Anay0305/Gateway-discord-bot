import discord
from discord import app_commands
from discord.ext import commands
import core.database as database
import datetime
from core.paginators import PaginationView
from core.hpag import HPaginationView
import random
from typing import Optional, List
import core.emojis as emojis
import botinfo

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Get Help with the bot's commands or modules")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help(self, ctx: commands.Context, command: Optional[str]):
        if command is not None:
            cmd = self.bot.get_command(command)
            cog = command
            cog = self.bot.get_cog(cog.lower())
            if cog is not None:
                if cog.qualified_name.capitalize() in emojis.cogs:
                    if cog.qualified_name == "nsfw":
                        if not ctx.channel.is_nsfw():
                            return
                    if cog.qualified_name == "extra":
                        return await self.extra(ctx=ctx)
                    command = cog.qualified_name
                    ls = []
                    for j in cog.walk_commands():
                        ls.append(j.qualified_name)
                    prefix = database.get_guild_prefix(ctx.guild.id)
                    xd = self.bot.main_owner
                    anay = str(xd)
                    pfp = xd.display_avatar.url
                    ls1, hey = [], []
                    for i in sorted(ls):
                        cmd = self.bot.get_command(i)
                        if cmd is not None:
                            if cmd.description is None:
                                cmd.description = "No Description"
                        hey.append(f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n")
                    for i in range(0, len(hey), 10):
                        ls1.append(hey[i: i + 10])
                    em_list = []
                    no = 1
                    lss = emojis.cogs[command.capitalize()]
                    for k in ls1:
                        listem = discord.Embed(title=f"{lss} {command.capitalize()} Commands", color=botinfo.root_color,
                                                description=f"<...> Duty | [...] Optional\n\n{''.join(k)}")
                        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=pfp)
                        em_list.append(listem)
                        no+=1
                    page = PaginationView(embed_list=em_list, ctx=ctx)
                    await page.start(ctx)
                    return
            if isinstance(cmd, discord.ext.commands.core.Group):
                command = cmd.name
                ls = []
                for j in cmd.walk_commands():
                    ls.append(j.qualified_name)
                prefix = database.get_guild_prefix(ctx.guild.id)
                xd = self.bot.main_owner
                anay = str(xd)
                pfp = xd.display_avatar.url
                ls1, hey = [], []
                for i in sorted(ls):
                    cmd = self.bot.get_command(i)
                    if cmd is not None:
                        if cmd.description is None:
                            cmd.description = "No Description"
                    hey.append(f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n")
                for i in range(0, len(hey), 10):
                    ls1.append(hey[i: i + 10])
                em_list = []
                no = 1
                for k in ls1:
                    listem = discord.Embed(title=f"{command.capitalize()} Commands", color=botinfo.root_color,
                                            description=f"<...> Duty | [...] Optional\n\n{''.join(k)}")
                    listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                    listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=pfp)
                    em_list.append(listem)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await page.start(ctx)
                return
            if cmd.cog_name == "nsfw":
                if not ctx.channel.is_nsfw():
                    return
            prefix = database.get_guild_prefix(ctx.guild.id)
            em = discord.Embed(description="> ```[] is Optional argument```\n> ```<> is Required argument```", color=botinfo.root_color)
            if cmd.cog_name:
                em.set_author(name=cmd.cog_name.capitalize(), icon_url=self.bot.user.avatar.url)
            else:
                em.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar.url)
            if cmd.description:
                em.add_field(name="Description", value=cmd.description, inline=False)
            else:
                em.add_field(name="Description", value="No description provided", inline=False)
            if cmd.aliases: 
                em.add_field(name="Aliases", value=f'{" | ".join(cmd.aliases)}', inline=False)
            else:
                em.add_field(name="Aliases", value="No Aliases", inline=False)
            em.add_field(name="Usage", value=f"> {prefix}{cmd.qualified_name} {cmd.signature}", inline=False)
            return await ctx.reply(embed=em, mention_author=False)
        else:
            prefix = database.get_guild_prefix(ctx.guild.id)
            xd = self.bot.main_owner
            anay = str(xd)
            pfp = xd.display_avatar.url
            v = ""
            for i in sorted(emojis.cogs):
                ls = emojis.cogs[i]
                v+=f"{ls} {i.capitalize()}\n"
            help = discord.Embed(title="Overview",
                                    description=f"Prefix for this server is `{prefix}`\nType `{prefix}help <command/module>` to get more info regarding it\n{len(tuple(self.bot.walk_commands())) - 32} Commands",
                                    color=botinfo.root_color)
            help.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
            help.add_field(name=f"Module", value=v)
            help.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
            em_list = []
            em_list.append(help)
            for i in sorted(emojis.cogs):
                x = self.bot.get_cog(i.lower())
                ls = []
                for j in x.walk_commands():
                    ls.append(j.qualified_name)
                ok = ""
                for k in sorted(ls):
                    ok+= f"`{k}`, "
                lss = emojis.cogs[i.capitalize()]
                help_ = discord.Embed(title=f"{lss} {i.capitalize()} Commands", color=botinfo.root_color, description=ok[:-2])
                help_.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
                em_list.append(help_)
            x = round(random.random()*100000)
            no = {}
            count = 1
            for i in emojis.cogs:
                no[i] = count
                count+=1
            database.insert("help", "main, 'no'", (x, 0))
            page = HPaginationView(embed_list=em_list, no=no, cogs=emojis.cogs, i=x, ctx=ctx)
            page.add_item(discord.ui.Button(label="Invite me", url=f"https://discord.com/api/oauth2/authorize?client_id={botinfo.bot_id}&&permissions=8&scope=bot"))
            #page.add_item(discord.ui.Button(label="Support Server", url="{botinfo.support_server}"))
            #page.add_item(discord.ui.Button(label="Vote", url="{botinfo.topgg_link}"))
            await page.start(ctx)

    @help.autocomplete("command")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str) -> List[app_commands.Choice[str]]:
        assert self.bot.help_command
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        help_command = self.bot.help_command.copy()
        help_command.context = ctx
        if not needle:
            return [
                app_commands.Choice(name=cog_name.title(), value=cog_name.lower())
                for cog_name in sorted(emojis.cogs)
            ][:25]
        needle = needle.lower()
        return [
            app_commands.Choice(name=command.qualified_name, value=command.qualified_name)
            for command in await help_command.filter_commands(self.bot.walk_commands(), sort=True)
            if needle in command.qualified_name
        ][:25]

    #@help.command(name="extra", description="Shows the extra's help menu")
    async def extra(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        listem = discord.Embed(color=botinfo.root_color,
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
        listem.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        listem1 = discord.Embed(color=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}nightmode`\n" 
                                                  f"Shows The help menu for nightmode\n\n" 
                                                  f"`{prefix}nightmode enable <perm>`\n" 
                                                  f"Take perms from every role that is below the bot\n\n"
                                                  f"`{prefix}nightmode disable`\n"
                                                  f"Give the role their permissions back\n\n")
        listem1.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem1.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        ls = ["ar", "ar add", "ar remove", "ar show", "ar reset"]
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem2 = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem2.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem2.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        ls = ["mediaonly", "mediaonly add", "mediaonly remove", "mediaonly show"]
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = self.bot.main_owner
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{cmd.qualified_name}`\n{cmd.description}\n\n"
        listem3 = discord.Embed(colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem3.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem3.set_footer(text=f"Made by {str(anay)}" ,  icon_url=anay.avatar.url)
        setupem = discord.Embed(color=botinfo.root_color,
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
                                                 f"`{prefix}setup tag`\n"
                                                 f"Set The Tag for Official role\n\n"
                                                 f"`{prefix}setup stag`\n"
                                                 f"Set The Small Tag for Official role\n\n"
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
        setupem1 = discord.Embed(color=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}official <member>`\n"
                                                 f"{off}\n\n"
                                                 f"`{prefix}applied`\n"
                                                 f"{off} but only if your name has tag\n\n"
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
        em_list.append(listem)
        em_list.append(listem1)
        em_list.append(listem2)
        em_list.append(listem3)
        em_list.append(setupem)
        em_list.append(setupem1)
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)
    
    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        em = discord.Embed(description=f"> [Click To Invite {self.bot.user.name} in Your Server](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&&permissions=8&scope=bot)\n> [Click To Join Support Server]({botinfo.support_server})", color=0x00ffff)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    async def support(self, ctx):
        em = discord.Embed(description=f"> [Click To Invite {self.bot.user.name} in Your Server](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&&permissions=8&scope=bot)\n> [Click To Join Support Server]({botinfo.support_server})", color=0x00ffff)
        await ctx.reply(embed=em, mention_author=False)
        
    #@commands.command()
    async def website(self, ctx):
        em = discord.Embed(description=f"> [Click To Invite {self.bot.user.name} in Your Server](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&&permissions=8&scope=bot)\n> [Click To vote {self.bot.user.name}]({botinfo.topgg_link})\n> [Click To check out Website of the bot](https://gatewaybot.xyz)\n> [Click To Join Support Server]({botinfo.support_server})", color=0x00ffff)
        await ctx.reply(embed=em, mention_author=False)
    
    #@commands.command()
    async def vote(self, ctx):
        em = discord.Embed(description=f"> [Click To Invite {self.bot.user.name} in Your Server](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&&permissions=8&scope=bot)\n> [Click To vote {self.bot.user.name}]({botinfo.topgg_link})\n> [Click To check out Website of the bot](https://gatewaybot.xyz)\n> [Click To Join Support Server]({botinfo.support_server})", color=0x00ffff)
        await ctx.reply(embed=em, mention_author=False)
        
    #@commands.command(aliases=['documentation', 'docs', 'document', 'documents'])
    async def documentations(self, ctx, *, module=None):
        ls = {"general": "https://docs.gatewaybot.xyz/features/#general",
              "mod": "https://docs.gatewaybot.xyz/features/#moderation",
              "moderation": "https://docs.gatewaybot.xyz/features/#moderation",
              "music": "https://docs.gatewaybot.xyz/features/#music",
              "antinuke": "https://docs.gatewaybot.xyz/features/#security",
              "security": "https://docs.gatewaybot.xyz/features/#security",
              "nightmode": "https://docs.gatewaybot.xyz/features/#nightmode",
              "lockrole": "https://docs.gatewaybot.xyz/features/#lockrole",
              "raidmode": "https://docs.gatewaybot.xyz/features/#raidmode",
              "ticket": "https://docs.gatewaybot.xyz/features/#tickets",
              "tickets": "https://docs.gatewaybot.xyz/features/#tickets",
              "logs": "https://docs.gatewaybot.xyz/features/#logging",
              "logging": "https://docs.gatewaybot.xyz/features/#logging",
              "loggings": "https://docs.gatewaybot.xyz/features/#logging",
              "welcome": "https://docs.gatewaybot.xyz/features/#welcome",
              "welcomer": "https://docs.gatewaybot.xyz/features/#welcome",
              "gw": "https://docs.gatewaybot.xyz/features/#giveaway",
              "giveaway": "https://docs.gatewaybot.xyz/features/#giveaway",
              "giveaways": "https://docs.gatewaybot.xyz/features/#giveaway",
              "nsfw": "https://docs.gatewaybot.xyz/features/#nsfw",
              "vc": "https://docs.gatewaybot.xyz/features/#voice",
              "voice": "https://docs.gatewaybot.xyz/features/#voice",
              "invc": "https://docs.gatewaybot.xyz/features/#in-vc-roles",
              "extra": "https://docs.gatewaybot.xyz/features/#extra",
              "setup": "https://docs.gatewaybot.xyz/features/#extra",
              "team": "https://docs.gatewaybot.xyz/team/",
              "cmds": "https://docs.gatewaybot.xyz/commands/",
              "cmd": "https://docs.gatewaybot.xyz/commands/",
              "commands": "https://docs.gatewaybot.xyz/commands/",
              "command": "https://docs.gatewaybot.xyz/commands/",
              "faq": "https://docs.gatewaybot.xyz/faqs/"}
        des = ""
        if module is not None:
            if module.lower() not in ls:
                des = f"> [Click To read the doumentations of {self.bot.user.name}](https://docs.gatewaybot.xyz)\n"
            else:
                des = f"> [Click To read the doumentations of {module.capitalize()}]({ls[module.lower()]})\n"
        else:
            des = f"> [Click To read the doumentations of {self.bot.user.name}](https://docs.gatewaybot.xyz)\n"
        em = discord.Embed(description=des, color=0x00ffff)
        await ctx.reply(embed=em, mention_author=False)

async def setup(bot):
    await bot.add_cog(help(bot))
