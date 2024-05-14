import discord
import datetime
from ast import literal_eval
import pytz

async def convert_embed(guild: discord.Guild, member: discord.Member, dic: dict):
    ind = pytz.timezone("Asia/Kolkata")
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    for i in dic:
        if i == 'color':
          continue
        dic[i] = str(dic[i]).replace("$user_name", member.name).replace("$user_username", str(member)).replace("$user_discriminator", f"#{member.discriminator}").replace("$user_id", str(member.id)).replace("$user_avatar", str(member.display_avatar.url)).replace("$user_mention", str(member.mention)).replace("$user_created", f"<t:{round(member.created_at.timestamp())}:F>").replace("$user_joined", f"<t:{round(member.joined_at.timestamp())}:F>").replace("$user_profile", f"https://discord.com/users/{member.id}").replace("$server_name", guild.name).replace("$server_id", str(guild.id)).replace("$membercount_ordinal", ordinal(len(guild.members))).replace("$membercount", str(len(guild.members))).replace("$now", f"{datetime.datetime.now(ind)}")
        if guild.icon:
            dic[i] = str(dic[i]).replace("$server_icon", guild.icon.url)
        else:
            if "$server_icon" in dic[i]:
                dic[i] = str(dic[i]).replace("$server_icon", "")
    for i in dic:
        if i == 'author' or i == 'footer' or i == 'thumbnail' or i == 'fields' or i == 'image':
            dic[i] = literal_eval(dic[i])
    return dic

async def convert_sample_embed(guild: discord.Guild, member: discord.Member, dic: dict):
    ind = pytz.timezone("Asia/Kolkata")
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    for i in dic:
        if i == 'color':
          continue
        dic[i] = str(dic[i]).replace("$membercount_ordinal", f"{ordinal(1)} (This is just an example)").replace("$membercount", f"1 (This is just an example)").replace("$user_name", member.name).replace("$user_username", str(member)).replace("$user_discriminator", f"#{member.discriminator}").replace("$user_id", str(member.id)).replace("$user_avatar", str(member.display_avatar.url)).replace("$user_mention", str(member.mention)).replace("$user_created", f"<t:{round(member.created_at.timestamp())}:F>").replace("$user_joined", f"<t:{round(member.joined_at.timestamp())}:F>").replace("$user_profile", f"https://discord.com/users/{member.id}").replace("$server_name", guild.name).replace("$server_id", str(guild.id)).replace("$now", f"{datetime.datetime.now(ind)}")
        if guild.icon:
            dic[i] = str(dic[i]).replace("$server_icon", guild.icon.url)
        else:
            if "$server_icon" in dic[i]:
                dic[i] = str(dic[i]).replace("$server_icon", "")
    for i in dic:
        if i == 'author' or i == 'footer' or i == 'thumbnail' or i == 'fields' or i == 'image':
            dic[i] = literal_eval(dic[i])
    return dic

async def convert_dict(guild: discord.Guild, member: discord.Member, embed: discord.Embed):
    ind = pytz.timezone("Asia/Kolkata")
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    dic = embed.to_dict()
    for i in dic:
        if i == 'color':
          continue
        if i == 'timestamp':
            dic[i] = "$now"
        if guild.icon:
            dic[i] = str(dic[i]).replace(guild.icon.url, "$server_icon")
        dic[i] = str(dic[i]).replace(f"{ordinal(1)} (This is just an example)", "$membercount_ordinal").replace(f"1 (This is just an example)", "$membercount").replace(str(member), "$user_username").replace(member.name, "$user_name").replace(f"#{member.discriminator}", "$user_discriminator").replace(str(member.display_avatar.url), "$user_avatar").replace("$user_profile", f"https://discord.com/users/{member.id}").replace(str(member.id), "$user_id").replace(str(member.mention), "$user_mention").replace(f"<t:{round(member.created_at.timestamp())}:F>", "$user_created").replace(f"<t:{round(member.joined_at.timestamp())}:F>", "$user_joined").replace("$user_profile", f"https://discord.com/users/{member.id}").replace(guild.name, "$server_name").replace(str(guild.id), "$server_id")
    for i in dic:
        if i == 'author' or i == 'footer' or i == 'thumbnail' or i == 'fields' or i == 'image':
            dic[i] = literal_eval(dic[i])
    return dic