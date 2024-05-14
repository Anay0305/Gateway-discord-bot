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

async def get_role(ctx: commands.Context, role_info: str):
    if role_info.startswith("<@&") and role_info.endswith(">"):
        try:
            role_id = int(role_info[3:-1])
            role = ctx.guild.get_role(role_id)
            return role
        except ValueError:
            return None
    
    if role_info.isdigit():
        role = ctx.guild.get_role(int(role_info))
        return role
    
    role = discord.utils.get(ctx.guild.roles, name=role_info)
    return role

async def stop_giveaway(self, g_id, data, guild_id, reroll = None):
    if data is None:
        return
    if reroll is None:
      if data["status"] is False:
        return
    else:
      pass
    gw_db = database.fetchone("*", "gwmain", "guild_id", guild_id)
    xd = literal_eval(gw_db["gw"])
    try:
      channel = self.bot.get_channel(data["channel_id"])
      giveaway_message = await channel.fetch_message(int(g_id))
    except:
      if g_id in xd:
        del xd[g_id]
        database.update("gwmain", "gw", f"{xd}", "guild_id", guild_id)
        return
    data['status'] = False
    xd[giveaway_message.id] = data
    database.update("gwmain", "gw", f"{xd}", "guild_id", channel.guild.id)
    req = data['reqrole']
    xd = [user async for user in giveaway_message.reactions[0].users()]
    if req is not None:
        reqrole = self.bot.get_guild(guild_id).get_role(req)
        if reqrole is not None:
            users = []
            for i in reqrole.members:
                if i in xd:
                    users.append(i)
        else:
            users = xd
    else:
        users = xd
    if self.bot.user in users:
        users.pop(users.index(self.bot.user))
    if len(users) < data["winners"]:
        winners_number = len(users)
    else:
        winners_number = data["winners"]
    winners = random.sample(users, winners_number)
    users_mention = []
    for user in winners:
        users_mention.append(user.mention)
    if len(users_mention) == 0:
        x = discord.utils.get(self.bot.users, id=data['host'])
        result_embed = discord.Embed(
            title=f" {data['prize']} ",
            color=botinfo.root_color,
            description=f"Ended <t:{round(datetime.datetime.now().timestamp())}:R> <t:{round(datetime.datetime.now().timestamp())}:f>\nWinners: No one Entered the giveaway\nHosted by {x.mention}")
        result_embed.set_footer(icon_url=self.bot.user.avatar.url, text="Giveaway Ended")
        result_embed.timestamp = datetime.datetime.now()
        await giveaway_message.edit(embed=result_embed)
        v = discord.ui.View()
        v.add_item(discord.ui.Button(label=f"Jump to Giveaway", url=giveaway_message.jump_url))
        await channel.send(f"No one entered the giveaway with the prize `{data['prize']}`", view=v)
    else:
        x = discord.utils.get(self.bot.users, id=data['host'])
        result_embed = discord.Embed(
            title=f" {data['prize']} ",
            color=botinfo.root_color,
            description=f"Ended <t:{round(datetime.datetime.now().timestamp())}:R> <t:{round(datetime.datetime.now().timestamp())}:f>\nWinners: {', '.join(users_mention)}\nHosted by {x.mention}")
        if req is not None:
            if reqrole is not None:
                result_embed.description+=f"\nRequired Role {reqrole.mention}"
        result_embed.set_footer(icon_url=self.bot.user.avatar.url, text="Giveaway Ended")
        await giveaway_message.edit(embed=result_embed)
        em = discord.Embed(description=f"You won the prize `{data['prize']}`.\nContact the giveaway host {x.mention} to claim your reward.", color=botinfo.root_color)
        em.set_footer(icon_url=self.bot.user.avatar.url, text="Giveaway Ended")
        em.timestamp = datetime.datetime.now()
        v = discord.ui.View()
        v.add_item(discord.ui.Button(label=f"Jump to Giveaway", url=giveaway_message.jump_url))
        await channel.send(f'{", ".join(users_mention)}', embed=em, view=v)

class giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_task.start()

    def cog_unload(self):
        self.giveaway_task.cancel()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        await self.bot.wait_until_ready()
        if user.guild is None:
            return
        if not user.guild.me.guild_permissions.manage_messages:
            return
        message_id = reaction.message.id
        gw_db = database.fetchone("*", "gwmain", "guild_id", user.guild.id)
        if gw_db is None:
            return
        xd = literal_eval(gw_db["gw"])
        try:
            if int(message_id) not in xd:
                return
        except:
            return
        if xd[int(message_id)]['status']:
            pass
        else:
            return
        if xd[int(message_id)]['reqrole'] is None:
            return
        else:
            role = user.guild.get_role(xd[int(message_id)]['reqrole'])
            if role is None:
                return
            else:
                if role in user.roles:
                    return
                else:
                    await reaction.remove(user)
                    return


    @tasks.loop(seconds=3)
    async def giveaway_task(self):
        await self.bot.wait_until_ready()
        gw_db = database.fetchall1("*", "gwmain")
        for i, j in gw_db:
            x = literal_eval(j)
            for f in x:
                if int(timeee.time()) > x[f]['end_time']:
                    if x[f]['status']:
                        try:
                            await stop_giveaway(self, f, x[f], guild_id=i)
                        except:
                            continue
    
    @commands.command(aliases=['gcreate'], description="To start a giveaway")
    async def gstart(self, ctx: commands.Context):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        x = discord.Embed(
            title="🎉 New Giveaway!! 🎉",
            description="Please answer the following questions",
            color=botinfo.root_color)
        x.set_footer(icon_url=self.bot.user.avatar.url, text=self.bot.user.name)
        init = await ctx.send(embed=x)

        questions = [
            "What would be the prize of the giveaway?",
            "What would the giveaway channel be like? (Please mention the giveaway channel)",
            "What would be the duration of the giveaway?",
            "How many winners do you want for this Giveaway?",
            "Is there any required role for this giveaway? (Type 'None' if there is no required role)?"
        ]

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        index = 1
        answers = []
        question_message = None
        for question in questions:
            embed = discord.Embed(
                title="Giveaway 🎉",
                description=question,
                color=botinfo.root_color
            ).set_footer(icon_url=self.bot.user.avatar.url, text="Giveaway! | Type 'cancel' to stop.")
            if index == 1:
                question_message = await ctx.send(embed=embed)
            else:
                await question_message.edit(embed=embed)

            try:
                user_response = await self.bot.wait_for("message", timeout=120, check=check)
                await user_response.delete()
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(
                    title="Error",
                    color=botinfo.root_color,
                    description="You took too long to answer this question"
                ))
                await init.delete()
                await question_message.delete()
                return
            else:
                if str(user_response.content).lower() == "cancel":
                    await init.delete()
                    await question_message.delete()
                    return
                answers.append(user_response.content)
                index += 1
        try:
            channel_id = int(answers[1][2:-1])
        except ValueError:
            await ctx.send(f"You didn't mention the channel correctly, do it like {ctx.channel.mention}.")
            await init.delete()
            await question_message.delete()
            return

        try:
            winners = abs(int(answers[3]))
            if winners == 0:
                await ctx.send("You did not enter an postive number.")
                return
        except ValueError:
            await ctx.send("You did not enter an integer.")
            await init.delete()
            await question_message.delete()
            return
        prize = answers[0].title()
        channel = self.bot.get_channel(channel_id)
        converted_time = convert(answers[2])
        if converted_time == -1:
            await ctx.send("You did not enter the correct unit of time (s|m|h|d)")
        elif converted_time == -2:
            await ctx.send("Your time value should be an integer.")
            return
        await init.delete()
        if converted_time < 60:
          return await ctx.reply(f"The time of giveaway must be more than 1 minute")
        reqrole = answers[4]
        if str(reqrole).lower() == "none":
            reqrole = None
        else:
            req = await get_role(ctx, str(reqrole))
            if req is None:
                await ctx.send("You did not passed a valid required role.")
                return
            else:
                reqrole = req.id
        await question_message.delete()
        stamp = datetime.datetime.now() + datetime.timedelta(seconds=converted_time)
        giveaway_embed = discord.Embed(
            title=f" {prize} ",
            color=botinfo.root_color,
            description=f'Ends: <t:{round(stamp.timestamp())}:R> <t:{round(stamp.timestamp())}:f>\n'
                        f'Hosted by {ctx.author.mention}\n'
                        f"{'Winners' if winners > 1 else 'Winner'}: **{winners}**\n")
        if reqrole is not None:
            giveaway_embed.description+=f"Required Role {req.mention}"
        giveaway_embed.set_footer(icon_url=self.bot.user.avatar.url, text=f"Ends at ")
        giveaway_embed.timestamp = datetime.datetime.utcnow() + datetime.timedelta(seconds=converted_time)
        giveaway_message = await channel.send("🎉**New Giveaway**🎉", embed=giveaway_embed)
        await giveaway_message.add_reaction("🎉")
        now = int(timeee.time())
        data = {
            "prize": prize,
            "host": ctx.author.id,
            "winners": winners,
            "end_time": now + converted_time,
            "channel_id": channel.id,
            "g_id": giveaway_message.id,
            "status": True,
            "reqrole": reqrole
        }
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        if gw_db is None:
            xd = {}
            xd[giveaway_message.id] = data
            val = (ctx.guild.id, f"{xd}")
            database.insert("gwmain", "guild_id, gw", val)
        else:
            xd = literal_eval(gw_db["gw"])
            xd[giveaway_message.id] = data
            database.update("gwmain", "gw", f"{xd}", "guild_id", ctx.guild.id)
        await ctx.reply(f"Giveaway started in {channel.mention}")

    @commands.command(description="To quickly start a giveaway")
    async def gquick(self, ctx: commands.Context, time, winner, *, prize):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await ctx.message.delete()
        try:
            winner = int(winner)
        except:
            await ctx.send(f"The parameters you provided are of wrong type, the correct use for example is `{ctx.prefix}gquick 10m 3 Nitro Booster`")
        converted_time = convert(time)
        channel = ctx.channel
        prize = prize.title()
        if converted_time == -1 or converted_time == -2:
            em = discord.Embed(description=f"{emojis.wrong} Provide specific time!", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        if converted_time < 60:
          return await ctx.send(f"The time of giveaway must be more than 1 minute")
        stamp = datetime.datetime.now() + datetime.timedelta(seconds=converted_time)
        giveaway_embed = discord.Embed(
            title=f" {prize} ",
            color=botinfo.root_color,
            description=f'Ends: <t:{round(stamp.timestamp())}:R> <t:{round(stamp.timestamp())}:f>\n'
                        f'Hosted by {ctx.author.mention}\n'
                        f"{'Winners' if winner > 1 else 'Winner'}: **{winner}**\n")
        giveaway_embed.set_footer(icon_url=self.bot.user.avatar.url, text=f"Ends at ")
        giveaway_embed.timestamp = datetime.datetime.utcnow() + datetime.timedelta(seconds=converted_time)
        giveaway_message = await ctx.send("🎉**New Giveaway**🎉", embed=giveaway_embed)
        await giveaway_message.add_reaction("🎉")
        now = int(timeee.time())
        data = {
            "prize": prize,
            "host": ctx.author.id,
            "winners": winner,
            "end_time": now + converted_time,
            "channel_id": channel.id,
            "g_id": giveaway_message.id,
            "status": True,
            "reqrole": None
        }
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        if gw_db is None:
            xd = {}
            xd[giveaway_message.id] = data
            val = (ctx.guild.id, f"{xd}")
            database.insert("gwmain", "guild_id, gw", val)
        else:
            xd = literal_eval(gw_db["gw"])
            xd[giveaway_message.id] = data
            database.update("gwmain", "gw", f"{xd}", "guild_id", ctx.guild.id)

    @commands.command(description="To get the list of all running giveaways in the server")
    @commands.has_permissions(manage_guild=True)
    async def glist(self, ctx: commands.Context):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        em_no = discord.Embed(description="No Giveaway is presently running in this server!", color=botinfo.root_color)
        em_no.set_footer(text=f"{self.bot.user.name} Giveaway", icon_url=self.bot.user.avatar.url)
        if gw_db is None:
            return await ctx.send(embed=em_no)
        xd = literal_eval(gw_db["gw"])
        if len(xd) == 0:
            return await ctx.send(embed=em_no)
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
            des.append(f"`[{'0' + str(count) if count < 10 else count}]` | {xddd[j]['prize']} - [[{xddd[j]['g_id']}]({g_msg.jump_url})] Ends at: <t:{round(j)}:R>")
            count+=1
        if len(des) == 0:
            return await ctx.send(embed=em_no)
        for i in range(0, len(des), 10):
           ls.append(des[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=botinfo.root_color)
           embed.title = f"Giveaways presently running in the server - {count-1}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @commands.command(aliases=['gstop'], description="To end a giveaway")
    async def gend(self, ctx: commands.Context, message_id):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await ctx.message.delete()
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        if gw_db is None:
            return await ctx.send(f"Invalid Giveaway id")
        xd = literal_eval(gw_db["gw"])
        try:
            if int(message_id) not in xd:
                return await ctx.send(f"Invalid Giveaway id")
        except:
            return await ctx.send(f"Invalid Giveaway id")
        if xd[int(message_id)]['status']:
                await stop_giveaway(self, message_id, xd[int(message_id)], ctx.guild.id)
        else:
            return await ctx.send("Giveaway is already ended")

    @commands.command(description="To reroll the winner for giveaway")
    async def greroll(self, ctx: commands.Context, message_id):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        await ctx.message.delete()
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        if gw_db is None:
            return await ctx.send(f"Invalid Giveaway id")
        xd = literal_eval(gw_db["gw"])
        try:
            if int(message_id) not in xd:
                return await ctx.send(f"Invalid Giveaway id")
        except:
            return await ctx.send(f"Invalid Giveaway id")
        if not xd[int(message_id)]['status']:
                await stop_giveaway(self, message_id, xd[int(message_id)], ctx.guild.id, True)
        else:
            return await ctx.send(f"Giveaway is not yet ended")

    @commands.command(description="To cancel a giveaway")
    async def gcancel(self, ctx: commands.Context, message_id):
        check = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveawayrole":
                check = True
                break
        if ctx.author.guild_permissions.manage_guild:
            check = True
        if not check:
            em = discord.Embed(description=f"{emojis.wrong} You must have Manage Guild Permissions or `GiveawayRole` named role in the server", color=botinfo.wrong_color)
            return await ctx.send(embed=em)
        gw_db = database.fetchone("*", "gwmain", "guild_id", ctx.guild.id)
        if gw_db is None:
            return await ctx.send(f"Invalid Giveaway id")
        xd = literal_eval(gw_db["gw"])
        if int(message_id) not in xd:
            return await ctx.send(f"Invalid Giveaway id")
        if not xd[int(message_id)]['status']:
            return await ctx.send("Giveaway is already ended")
        else:
            xd[int(message_id)]['status'] = False
        database.update("gwmain", "gw", f"{xd}", "guild_id", ctx.guild.id)
        await ctx.reply(f"Cancelled the giveaway with prize: `{xd[int(message_id)]['prize']}`")

async def setup(bot):
    await bot.add_cog(giveaway(bot))
