import discord
from discord.ext import commands
from typing import Union
import datetime
import emojis
import botinfo
import typing

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        invoke_without_command=True, aliases=["vc"], description="Shows the help menu for voice commands"
    )
    async def voice(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = self.bot.main_owner
        anay = str(xd)
        pfp = xd.display_avatar.url
        vc = discord.Embed(title=f"{emojis.cogs['Voice']} Voice Commands", colour=botinfo.root_color,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                 f"`{prefix}vc kick <member>`\n"
                                                 f"Disconnects the member from vc\n\n"
                                                 f"`{prefix}vc kickall`\n"
                                                 f"Disconnects all the members in vc\n\n"
                                                 f"`{prefix}vc mute <member>`\n"
                                                 f"Mute a member in vc\n\n"
                                                 f"`{prefix}vc unmute <member>`\n"
                                                 f"Unmute a member in vc\n\n"
                                                 f"`{prefix}vc muteall`\n"
                                                 f"Mute all the members in vc\n\n"
                                                 f"`{prefix}vc unmuteall`\n"
                                                 f"Unmute all the members in vc\n\n"
                                                 f"`{prefix}vc deafen <member>`\n"
                                                 f"Deafen a member in vc\n\n"
                                                 f"`{prefix}vc undeafen <member>`\n"
                                                 f"Undeafen a member in vc\n\n"
                                                 f"`{prefix}vc deafenall`\n"
                                                 f"Deafen all the members in vc\n\n"
                                                 f"`{prefix}vc undeafenall`\n"
                                                 f"Undeafen all the members in vc\n\n"
                                                 f"`{prefix}vc moveall <channel>`\n"
                                                 f"Moves all the members from the vc")
        vc.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        vc.set_footer(text=f"Made by {anay}" ,  icon_url=pfp)
        await ctx.send(embed=vc)

    @voice.command(aliases=["vm"], description="Drags a user into your current voice channel")
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def drag(self , ctx ,  user : typing.Optional[discord.Member] = None ,  channel : typing.Optional[discord.VoiceChannel] = None, to_user : typing.Optional[discord.Member] = None):
        await ctx.defer()
        Rauthor = None
        if ctx.message.reference is not None:
            msg = ctx.message.reference.cached_message
            Rauthor = msg.author
        user = user or Rauthor 
        if channel is None :
            channel2 = None
            if to_user is not None:
                if to_user.voice is None:
                    await ctx.send(f"{to_user} is not in vc.")
                    return
                channel2 = to_user.voice.channel
            channel = channel2 or ctx.author.voice.channel 
            if channel == None:
                await ctx.send("You didn't provide a vc or else you are not in vc")
                return
        data = user.voice
        if data is None :
            await ctx.send(f"{user} is Not in a VC")
        else:
            if not channel.permissions_for(ctx.author).connect:
                await ctx.send(f"You are not allowed to drag user in {channel.mention}")
                return
            await user.move_to(channel)
            await ctx.reply(f"{user.mention} dragged to {channel.mention}")
    
    @voice.command(name="kick", aliases=["dc"], description="Disconnects the member from vc")
    @commands.has_guild_permissions(move_members=True)
    async def vc_kick(self, ctx, *, member: discord.Member):
        if member.voice is None:
            return await ctx.reply(f"{str(member)} Is not connected in any of the voice channel")
        ch = member.voice.channel.mention
        await member.edit(voice_channel=None, reason=f"Disconnected by {str(ctx.author)}")
        return await ctx.reply(f"{str(member)} has been disconnected from {ch}")
    
    @voice.command(name="kickall", aliases=["dcall"], description="Disconnects all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_kickall(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        count=0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            await member.edit(voice_channel=None, reason=f"Disconnected by {str(ctx.author)}")
            count+=1
        return await ctx.reply(f"Disconnected {count} members from {ch}")

    @voice.command(name="mute", description="Mute a member in vc")
    @commands.has_guild_permissions(mute_members=True)
    async def vc_mute(self, ctx, *, member: discord.Member):
        if member.voice is None:
            return await ctx.reply(f"{str(member)} Is not connected in any of the voice channel")
        if member.voice.mute == True:
            return await ctx.reply(f"{str(member)} Is already muted in the voice channel")
        ch = member.voice.channel.mention
        await member.edit(mute=True, reason=f"Muted by {str(ctx.author)}")
        return await ctx.reply(f"{str(member)} has been muted in {ch}")

    @voice.command(name="unmute", description="Unmute a member in vc")
    @commands.has_guild_permissions(mute_members=True)
    async def vc_unmute(self, ctx, *, member: discord.Member):
        if member.voice is None:
            return await ctx.reply(f"{str(member)} Is not connected in any of the voice channel")
        if member.voice.mute == False:
            return await ctx.reply(f"{str(member)} Is already unmuted in the voice channel")
        ch = member.voice.channel.mention
        await member.edit(mute=False, reason=f"Unmuted by {str(ctx.author)}")
        return await ctx.reply(f"{str(member)} has been unmuted in {ch}")
    
    @voice.command(name="muteall", description="Mute all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_muteall(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        count=0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == False:
                await member.edit(mute=True, reason=f"Muted by {str(ctx.author)}")
                count+=1
        return await ctx.reply(f"Muted {count} members in {ch}")

    @voice.command(name="unmuteall", description="Unmute all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_unmuteall(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        count=0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == True:
                await member.edit(mute=False, reason=f"Unmuted by {str(ctx.author)}")
                count+=1
        return await ctx.reply(f"Unmuted {count} members in {ch}")

    @voice.command(name="deafen", description="Deafen a member in vc")
    @commands.has_guild_permissions(deafen_members=True)
    async def vc_deafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            return await ctx.reply(f"{str(member)} Is not connected in any of the voice channel")
        if member.voice.deaf == True:
            return await ctx.reply(f"{str(member)} Is already deafen in the voice channel")
        ch = member.voice.channel.mention
        await member.edit(deafen=True, reason=f"Deafen by {str(ctx.author)}")
        return await ctx.reply(f"{str(member)} has been Deafen in {ch}")

    @voice.command(name="undeafen", description="Undeafen a member in vc")
    @commands.has_guild_permissions(deafen_members=True)
    async def vc_undeafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            return await ctx.reply(f"{str(member)} Is not connected in any of the voice channel")
        if member.voice.deaf == False:
            return await ctx.reply(f"{str(member)} Is already undeafen in the voice channel")
        ch = member.voice.channel.mention
        await member.edit(deafen=False, reason=f"Undeafen by {str(ctx.author)}")
        return await ctx.reply(f"{str(member)} has been undeafen in {ch}")
    
    @voice.command(name="deafenall", description="Deafen all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_deafenall(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        count=0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == False:
                await member.edit(deafen=True, reason=f"Deafen by {str(ctx.author)}")
                count+=1
        return await ctx.reply(f"Deafen {count} members in {ch}")

    @voice.command(name="undeafenall", description="Undeafen all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_undeafenall(self, ctx):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        count=0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == True:
                await member.edit(deafen=False, reason=f"Undeafen by {str(ctx.author)}")
                count+=1
        return await ctx.reply(f"Undeafen {count} members in {ch}")
    
    @voice.command(name="moveall", description="Undeafen all the members in vc")
    @commands.has_guild_permissions(administrator=True)
    async def vc_moveall(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.author.voice is None:
            return await ctx.reply(f"You are not connected in any of the voice channel")
        try:
            ch = ctx.author.voice.channel.mention
            nch = channel.mention
            count = 0
            for member in ctx.author.voice.channel.members:
                await member.edit(voice_channel=channel, reason=f"Moved by {str(ctx.author)}")
                count+=1
            await ctx.reply(f"Moved {count} members from {ch} to {nch}")
        except:
            await ctx.reply("Invalid Voice channel")

async def setup(bot):
    await bot.add_cog(voice(bot))
