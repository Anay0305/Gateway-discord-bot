import discord
from ast import literal_eval
import sqlite3
from discord.ext import commands
import database
import emojis

class autorole(commands.Cog):
  def __init__(self, bot):
      self.bot=bot

  @commands.Cog.listener()
  async def on_member_join(self, user):
      await self.bot.wait_until_ready()
      if not user.guild.me.guild_permissions.manage_roles:
          return
      auto_db = database.fetchone("*", "auto", "guild_id", user.guild.id)
      if auto_db is None:
        return
      try:
          humans = literal_eval(auto_db['humans'])
      except:
          humans = None
      try:
          bots = literal_eval(auto_db['bots'])
      except:
          bots = None
      if not user.bot:
          if humans is not None:
              for i in humans:
                  role = discord.utils.get(user.guild.roles, id=i)
                  if role is None:
                    continue
                  if role.position >= user.guild.me.top_role.position:
                    continue 
                  await user.add_roles(role, reason='Autorole Humans')
      else:
          if bots is not None:
              for i in bots:
                  role = discord.utils.get(user.guild.roles, id=i)
                  if role is None:
                    continue
                  if role.position >= user.guild.me.top_role.position:
                    continue
                  await user.add_roles(role, reason='Autorole Bots')
            
async def setup(bot):
    await bot.add_cog(autorole(bot))