import discord
from discord.ext import commands
import os
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
import datetime
import re
from ast import literal_eval
import botinfo
import asyncio
import wavelink
import core.database as database
from cogs.extra import by_channel, by_cmd, by_module, by_role, get_prefix
from core.premium import check_upgraded

botinfo.starttime = datetime.datetime.now(datetime.UTC)

async def add_count(ctx, user, guild, cmd_name):
    user_columns = database.fetchone("*", "count", "xd", 1)
    if user_columns is None:
        c = {}
        c[user.id] = 1
        cc = {}
        cc[guild.id] = 1
        ccc = {}
        ccc[cmd_name] = 1
        database.insert("count", "xd, 'user_count', 'guild_count', 'cmd_count'", (1, f"{c}", f"{cc}", f"{ccc}",))
    else:
        c = literal_eval(user_columns['user_count'])
        if user.id in c:
            c[user.id] = c[user.id] + 1
        else:
            c[user.id] = 1
        c = {k: v for k, v in reversed(sorted(c.items(), key=lambda item: item[1]))}
        database.update("count", 'user_count', f"{c}", "xd", 1)
        cc = literal_eval(user_columns['guild_count'])
        if guild.id in cc:
            cc[guild.id] = cc[guild.id] + 1
        else:
            cc[guild.id] = 1
        cc = {k: v for k, v in reversed(sorted(cc.items(), key=lambda item: item[1]))}
        database.update("count", 'guild_count', f"{cc}", "xd", 1)
        ccc = literal_eval(user_columns['cmd_count'])
        if cmd_name in ccc:
            ccc[cmd_name] = ccc[cmd_name] + 1
        else:
            ccc[cmd_name] = 1
        ccc = {k: v for k, v in reversed(sorted(ccc.items(), key=lambda item: item[1]))}
        database.update("count", 'cmd_count', f"{ccc}", "xd", 1)

async def get_pre(bot, ctx):
    if ctx.guild is None:
        return commands.when_mentioned_or(f"-")(bot, ctx)
    res = database.get_guild_prefix(ctx.guild.id)
    if res:
      prefix = str(res[0])
    if not res:
      prefix = '-'
    try:
        res1 = database.fetchone("*", "noprefix", "user_id", ctx.author.id)
        if res1 is not None:
            if res1['servers'] is not None:
                no_prefix = literal_eval(res1['servers'])
                if ctx.guild.id in no_prefix:
                    return commands.when_mentioned_or(f"{prefix}", "")(bot, ctx)
            if res1['main'] is not None:
                if res1['main'] == 1:
                    return commands.when_mentioned_or(f"{prefix}", "")(bot, ctx)
    except:
        pass
    return commands.when_mentioned_or(prefix)(bot,ctx)

intents = discord.Intents.all()
class Bot(commands.AutoShardedBot):
    def __init__(self, get_pre, intents) -> None:
        super().__init__(command_prefix = get_pre, case_insensitive=True, intents=intents, shard_count=2)

    async def setup_hook(self) -> None:
        nodes: list[wavelink.Node] = [wavelink.Node(uri=botinfo.wavelink_uri, password=botinfo.wavelink_pass)]
        self.wavelink = nodes[0]
        await wavelink.Pool.connect(nodes=nodes, client=self)
        initial_extensions = ['jishaku']

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                initial_extensions.append("cogs." + filename[:-3])

        for extension in initial_extensions:
            await self.load_extension(extension)
        await database.create_tables()
        await self.tree.sync()

bot = Bot(get_pre, intents)
ownerids = botinfo.main_devs
bot.owner_ids = ownerids
bot.remove_command("help")

@bot.event
async def on_ready():
    bot.main_owner = discord.utils.get(bot.users, id=979353019235840000)
    #bot.topggpy = topgg.client.DBLClient(bot=bot, token=botinfo.dbltoken, autopost=True, post_shard_count=False, autopost_interval=900)

@bot.event
async def on_autopost_success():
    print(f"Posted server count ({bot.topggpy.guild_count})")

@bot.event
async def process_commands(message: discord.Message) -> None:
    if message.author.bot:
        return
    s_id = message.guild.shard_id
    sh = bot.get_shard(s_id)
    if sh.is_ws_ratelimited() and check:
            webhook = discord.SyncWebhook.from_url(botinfo.webhook_ratelimit_logs)
            webhook.send("The bot is being ratelimited", username=f"{str(bot.user)} | Ratelimit Logs", avatar_url=bot.user.avatar.url)
    ctx = await bot.get_context(message)
    ig_db = database.fetchone("*", "ignore", "guild_id", message.guild.id)
    if ig_db is None:
      if ctx.command:
        if not ctx.command.qualified_name.startswith("jishaku"):
            await add_count(ctx, ctx.author, ctx.guild, cmd_name=ctx.command.qualified_name)
        await bot.invoke(ctx)
    else:
        xd = literal_eval(ig_db['cmd'])
        xdd = literal_eval(ig_db['module'])
        if ctx.command:
            if check_upgraded(ctx.guild.id):
                if str(ctx.command.cog_name.lower()) == "music":
                    cmd_name = str(ctx.command.name)
                    if cmd_name == "247" or cmd_name == "msetup":
                        pass
                    else:
                        s_db = database.fetchone("*", "setup", "guild_id", ctx.guild.id)
                        c = None
                        if s_db is None:
                            check = False
                        else:
                            try:
                                c = bot.get_channel(s_db['channel_id'])
                                if c is None:
                                    check = False
                                else:
                                    msg: discord.Message = await c.fetch_message(s_db['msg_id'])
                                    if msg is None:
                                        check = False
                                    else:
                                        check = True
                                check = check and ctx.channel.id == s_db['channel_id']
                            except:
                                check = False
                        if not check and c is not None:
                            return await ctx.reply(f"You can only use the music commands of the bot in {c.mention}.")
            c_cmd = await by_cmd(ctx, message.author, ctx.command.qualified_name)
            c_module = await by_module(ctx, message.author, str(ctx.command.cog_name.lower()))
            if ctx.command.qualified_name in xd and not c_cmd:
                s = str(ctx.command.qualified_name.capitalize())
                em = discord.Embed(description=f"{s} command is disabled for this server", color=botinfo.root_color).set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
                return await ctx.reply(embed=em, delete_after=3)
            elif str(ctx.command.cog_name.lower()) in xdd and not c_module:
                s = str(ctx.command.cog_name.capitalize())
                em = discord.Embed(description=f"{s} module is disabled for this server", color=botinfo.root_color).set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
                return await ctx.reply(embed=em, delete_after=3)
            else:
              if not ctx.command.qualified_name.startswith("jishaku"):
                await add_count(ctx, ctx.author, ctx.guild, cmd_name=ctx.command.qualified_name)
              await bot.invoke(ctx)

@bot.event
async def on_message(message: discord.Message) -> None:
    await bot.wait_until_ready()
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != bot.user.id:
            webhook = discord.SyncWebhook.from_url(botinfo.webhook_dm_logs)
            if message.author.avatar:
                webhook.send(f"{message.content}", username=f"{str(message.author)} | Dm Logs", avatar_url=message.author.avatar.url)
            else:
                webhook.send(f"{message.content}", username=f"{str(message.author)} | Dm Logs")
        return
    if not message.guild.me.guild_permissions.read_messages:
        return
    if not message.guild.me.guild_permissions.read_message_history:
        return
    if not message.guild.me.guild_permissions.view_channel:
        return
    if not message.guild.me.guild_permissions.send_messages:
        return
    ctx = await bot.get_context(message)
    bl_db = database.fetchone("*", "bl_guilds", "main", 1)
    if bl_db is not None:
        bl_db = literal_eval(bl_db["guild_ids"])
        if ctx.guild.id in bl_db:
            return
    bl_db = database.fetchone("*", "bl", "main", 1)
    if bl_db is not None:
        bl_db = literal_eval(bl_db["user_ids"])
        if ctx.author.id in bl_db:
            return
    if re.fullmatch(rf"<@!?{bot.user.id}>", message.content) and not ctx.author.bot:
        prefix = database.get_guild_prefix(message.guild.id)
        emb = discord.Embed(description=f"Hey {message.author.mention} My Prefix is `{prefix}`\nTo view all my modules do `{prefix}help` or </help:1063005466914979900>.\nFor module related help use `{prefix}help <module name>` or </help:1063005466914979900> `<module name>`", color=botinfo.root_color)
        page = discord.ui.View()
        page.add_item(discord.ui.Button(label="Invite me", url=f"https://discord.com/api/oauth2/authorize?client_id={botinfo.bot_id}&&permissions=8&scope=bot"))
        page.add_item(discord.ui.Button(label="Support Server", url=f"{botinfo.support_server}"))
        #page.add_item(discord.ui.Button(label="Vote", url=f"{botinfo.topgg_link}"))
        await ctx.reply(embed=emb, mention_author=False, view=page, delete_after=10)
    ig_db = database.fetchone("*", "ignore", "guild_id", message.guild.id)
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
    if message.author.id == bot.user.id:
        return
    try:
        if bot.mesaagecreate:
            return await bot.process_commands(message)
    except:
        pass
    s_db = database.fetchone("*", "setup", "guild_id", message.guild.id)
    if s_db is None:
        return await bot.process_commands(message)
    elif message.channel.id != s_db['channel_id']:
        return await bot.process_commands(message)
    else:
        pre = await get_prefix(message)
        check = False
        content = message.content
        prefix = None
        for k in pre:
            if content.startswith(k):
                content = content.replace(k, "").strip()
                check = True
                prefix = k
        s = ""
        for i in content:
            if i == " ":
                break
            s+=i
        cmd = bot.get_command(s)
        if cmd is None:
            if check and prefix != "":
                message.content = f"<@{message.guild.me.id}> {content}"
            else:
                message.content = f"<@{message.guild.me.id}> play {message.content}"
        else:
            if cmd.cog_name != "music":
                return await ctx.send(f"{message.author.mention} You can only runs command from music module, no other command can be runned in this channel.", delete_after=15)
            if check:
                message.content = prefix + content
            else:
                message.content = f"<@{message.guild.me.id}> {message.content}"
        await bot.process_commands(message)
        try:
            await message.delete()
        except:
            pass
        await asyncio.sleep(60)
        async for msg in message.channel.history(limit=100):
            if msg.id == s_db['msg_id'] or len(msg.components) != 0:
                pass
            else:
                try:
                    await msg.delete()
                except:
                    pass

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    await bot.wait_until_ready()
    if after.content == before.content:
        return
    message = after
    ctx = await bot.get_context(message)
    bl_db = database.fetchone("*", "bl_guilds", "main", 1)
    if bl_db is not None:
        bl_db = literal_eval(bl_db["guild_ids"])
        if ctx.guild.id in bl_db:
            return
    bl_db = database.fetchone("*", "bl", "main", 1)
    if bl_db is not None:
        bl_db = literal_eval(bl_db["user_ids"])
        if ctx.author.id in bl_db:
            return
    ig_db = database.fetchone("*", "ignore", "guild_id", message.guild.id)
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
    await bot.process_commands(after)

bot.run(botinfo.gateway_token)