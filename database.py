import sqlite3

async def create_tables():
    with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "main" (
                "xd"	INTEGER DEFAULT 77,
                "nopre"	TEXT DEFAULT [1141685323299045517],
                "bperm"	TEXT DEFAULT [1141685323299045517],
                PRIMARY KEY("xd")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "count" (
                "xd" INTEGER DEFAULT 1,
                "guild_count"	TEXT DEFAULT "{}",
                "cmd_count"	TEXT DEFAULT "{}",
                "user_count"	TEXT DEFAULT "{}",
                PRIMARY KEY("xd")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "noprefix" (
                "user_id"	INTEGER,
                "servers"	TEXT,
                "main"	INTEGER DEFAULT 0,
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "afk" (
                "user_id"	INTEGER,
                "afkk"	TEXT DEFAULT '{}',
                "globally" INTEGER DEFAULT 0,
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "warn" (
                "guild_id"	INTEGER,
                "data"	TEXT DEFAULT '{}',
                "count"	TEXT DEFAULT '[]',
                "autopunish" TEXT DEFAULT '{}',
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "bl" (
                "main"  INTEGER DEFAULT 1,
                "user_ids"	TEXT DEFAULT '[]',
                PRIMARY KEY("main")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prefixes(
                "guild_id" INTEGER,
                "prefix" TEXT DEFAULT "-",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "titles" (
                "user_id"	INTEGER,
                "title"	TEXT,
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "badges" (
                "user_id"	INTEGER,
                "PARTNER"	INTEGER DEFAULT 0,
                "SUPPORTER"	INTEGER DEFAULT 0,
                "OWNER"	INTEGER DEFAULT 0,
                "DEVELOPER"	INTEGER DEFAULT 0,
                "STAFF"	INTEGER DEFAULT 0,
                "ADMIN"	INTEGER DEFAULT 0,
                "MOD"	INTEGER DEFAULT 0,
                "SPECIAL"	INTEGER DEFAULT 0,
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles(
                "guild_id"	INTEGER,
                "role"	INTEGER DEFAULT 0,
                "official"	INTEGER DEFAULT 0,
                "vip"	INTEGER DEFAULT 0,
                "guest"	INTEGER DEFAULT 0,
                "girls"	INTEGER DEFAULT 0,
                "tag"	TEXT,
                "friend"	INTEGER DEFAULT 0,
                "custom"	TEXT DEFAULT "{}",
                "ar"	INTEGER DEFAULT 0,
                "stag"	TEXT,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imp(
                    "guild_id"	INTEGER,
                "cmd" TEXT DEFAULT 0,
                "admin" TEXT DEFAULT 0,
                "kick" TEXT DEFAULT 0,
                "ban" TEXT DEFAULT 0,
                "mgn" TEXT DEFAULT 0,
                "mgnch" TEXT DEFAULT 0,
                "mgnro" TEXT DEFAULT 0,
                "mention" TEXT DEFAULT 0,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfp(
                "guild_id"	INTEGER,
                "channel_id" INTEGER,
                "type" TEXT,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo(
                    "user_id"	INTEGER,
                "todo" TEXT DEFAULT "[]",
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "help" (
                "main"  INTEGER DEFAULT 1,
                "no" INTEGER,
                PRIMARY KEY("main")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto(
                "guild_id" INTEGER,
                "humans" TEXT,
                "bots" TEXT,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS welcome(
                    "guild_id"	INTEGER,
                "channel_id"	INTEGER,
                "msg"	TEXT DEFAULT 'Hey $user_mention',
                "emdata"	TEXT DEFAULT "{'footer': {'text': 'Welcome'}, 'color': 3092790, 'type': 'rich', 'description': 'Hey $user_mention', 'title': 'Welcome to $server_name'}",
                "embed"	INTEGER DEFAULT 0,
                "ping"	INTEGER DEFAULT 0,
                "autodel"  INTEGER DEFAULT 0,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto(
                "guild_id" INTEGER,
                "humans" TEXT,
                "bots" TEXT,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS punish(
                "guild_id" INTEGER,
                "PUNISHMENT" TEXT DEFAULT "BAN",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lockr(
                "guild_id" INTEGER,
                "role_id" TEXT DEFAULT "[]",
                "bypass_uid" TEXT DEFAULT "[]",
                "bypass_rid" TEXT DEFAULT "[]",
                "m_list" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raidmode(
                "guild_id" INTEGER,
                "toggle" INTEGER DEFAULT 0,
                "time" INTEGER DEFAULT 10,
                "max" INTEGER DEFAULT 15,
                "PUNISHMENT" TEXT DEFAULT "KICK",
                "lock" INTEGER DEFAULT 0,
                "lockdown" INTEGER DEFAULT 1,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "gwmain" (
                "guild_id"  INTEGER,
                "gw" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "invc" (
                "guild_id"  INTEGER,
                "vc" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "bot" (
                "bot_id"  INTEGER,
                "totaltime" INTEGER DEFAULT 0,
                "server" TEXT DEFAULT "{}",
                "user" TEXT DEFAULT "{}",
                PRIMARY KEY("bot_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "setup" (
                "guild_id"  INTEGER,
                "channel_id" INTEGER,
                "msg_id" INTEGER,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "247" (
                "guild_id"  INTEGER,
                "channel_id" INTEGER,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "pl" (
                "user_id"  INTEGER,
                "pl" TEXT DEFAULT "{}",
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "user" (
                "user_id"  INTEGER,
                "totaltime" INTEGER DEFAULT 0,
                "server" TEXT DEFAULT "{}",
                "friend" TEXT DEFAULT "{}",
                "artist" TEXT DEFAULT "{}",
                "track", TEXT DEFAULT "{}",
                PRIMARY KEY("user_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "ignore" (
                "guild_id"  INTEGER,
                "cmd" TEXT DEFAULT "[]",
                "channel" TEXT DEFAULT "[]",
                "user" TEXT DEFAULT "[]",
                "role" TEXT DEFAULT "[]",
                "module" TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "bypass" (
                "guild_id"  INTEGER,
                "bypass_users" TEXT DEFAULT "{}",
                "bypass_roles" TEXT DEFAULT "{}",
                "bypass_channels" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "srmain" (
                "guild_id"  INTEGER,
                "data_button" TEXT DEFAULT "[]",
                "data_dropdown" TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "messages_db" (
                "guild_id"  INTEGER,
                "messages" TEXT DEFAULT "{}",
                "daily_messages" TEXT DEFAULT "{}",
                "bl_channels" TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "logs" (
                "guild_id"	INTEGER,
                "mod"	INTEGER,
                "role"	INTEGER,
                "channel"	INTEGER,
                "server"	INTEGER,
                "member"	INTEGER,
                "message"	INTEGER,
                "antinuke"	INTEGER,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS toggle(
                "guild_id" INTEGER,
                "BAN" INTEGER DEFAULT 0,
                "BOT" INTEGER DEFAULT 0,
                "KICK" INTEGER DEFAULT 0,
                "ROLE CREATE" INTEGER DEFAULT 0,
                "ROLE DELETE" INTEGER DEFAULT 0,
                "ROLE UPDATE" INTEGER DEFAULT 0,
                "CHANNEL CREATE" INTEGER DEFAULT 0,
                "CHANNEL DELETE" INTEGER DEFAULT 0,
                "CHANNEL UPDATE" INTEGER DEFAULT 0,
                "MEMBER UPDATE" INTEGER DEFAULT 0,
                "GUILD UPDATE" INTEGER DEFAULT 0,
                "WEBHOOK" INTEGER DEFAULT 0,
                "ALL" INTEGER DEFAULT 0,
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wl(
                "guild_id" INTEGER,
                "BAN" TEXT DEFAULT "[]",
                "BOT" TEXT DEFAULT "[]",
                "KICK" TEXT DEFAULT "[]",
                "ROLE CREATE" TEXT DEFAULT "[]",
                "ROLE DELETE" TEXT DEFAULT "[]",
                "ROLE UPDATE" TEXT DEFAULT "[]",
                "CHANNEL CREATE" TEXT DEFAULT "[]",
                "CHANNEL DELETE" TEXT DEFAULT "[]",
                "CHANNEL UPDATE" TEXT DEFAULT "[]",
                "MEMBER UPDATE" TEXT DEFAULT "[]",
                "GUILD UPDATE" TEXT DEFAULT "[]",
                "WEBHOOK" TEXT DEFAULT "[]",
                "ALL" TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS punish(
                "guild_id" INTEGER,
                "PUNISHMENT" TEXT DEFAULT "BAN",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lockr(
                "guild_id" INTEGER,
                "role_id" TEXT DEFAULT "[]",
                "bypass_uid" TEXT DEFAULT "[]",
                "bypass_rid" TEXT DEFAULT "[]",
                "m_list" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lockrpos(
                "guild_id" INTEGER,
                "enable" INTEGER DEFAULT 0,
                "channel_id" INTEGERE DEFAULT 0,
                "roles_pos" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "sticky_msg" (
                "guild_id"	INTEGER,
                "data"	TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "media_only" (
                "guild_id"	INTEGER,
                "channels"	TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "autoresponder" (
                "guild_id"	INTEGER,
                "data"	TEXT DEFAULT "{}",
                "ignore_channels"	TEXT DEFAULT "[]",
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "panel" (
                "guild_id"  INTEGER,
                "channel_id" INTEGER,
                "msg_id" INTEGER,
                "opencategory" INTEGER,
                "closedcategory" INTEGER,
                "claimedrole" INTEGER,
                "supportrole" INTEGER,
                "pingrole" INTEGER,
                "name" TEXT,
                "msg" TEXT DEFAULT '\nTo create a ticket interact with the button below 📩',
                PRIMARY KEY("guild_id")
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "ticket" (
                "guild_id"  INTEGER,
                "name" TEXT,
                "count" INTEGER DEFAULT 0000,
                "opendata" TEXT DEFAULT "{}",
                "closeddata" TEXT DEFAULT "{}",
                PRIMARY KEY("guild_id")
        )
        ''')
    db.commit()
    cursor.close()
    db.close()

def get_guild_prefix(guild_id):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM prefixes WHERE guild_id = {guild_id}")
        res = cursor.fetchone()
    cursor.close()
    db.close()
    return res["prefix"]

def fetchone(xx, table_name, q, value):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"SELECT {xx} FROM {table_name} WHERE {q} = ?"
        val = (value,)
        cursor.execute(query, val)
        res = cursor.fetchone()
    cursor.close()
    db.close()
    return res

def fetchone1(xx, table_name):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"SELECT {xx} FROM {table_name}"
        cursor.execute(query)
        res = cursor.fetchone()
    cursor.close()
    db.close()
    return res

def fetchall(xx, table_name, q, value):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"SELECT {xx} FROM {table_name} WHERE {q} = ?"
        val = (value,)
        cursor.execute(query, val)
        res = cursor.fetchall()
    cursor.close()
    db.close()
    return res

def fetchall1(xx, table_name):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"SELECT {xx} FROM {table_name}"
        cursor.execute(query)
        res = cursor.fetchall()
    cursor.close()
    db.close()
    return res

def insert(table_name, q, value):
    x = '?, '*(len(value))
    x = x.strip()
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"INSERT OR IGNORE INTO {table_name}({q}) VALUES({x[:-1]})"
        cursor.execute(query, value)
    db.commit()
    cursor.close()
    db.close()
    return True

def update(table_name, q, value, u_key, u_val):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"UPDATE {table_name} SET '{q}' = ? WHERE {u_key} = ?"
        val = (value, u_val,)
        cursor.execute(query, val)
    db.commit()
    cursor.close()
    db.close()
    return True

def update_bulk(table_name, dic: dict, u_key, u_val):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
    for i in dic:
        query = f"UPDATE {table_name} SET '{i}' = ? WHERE {u_key} = ?"
        val = (dic[i], u_val,)
        cursor.execute(query, val)
    db.commit()
    cursor.close()
    db.close()
    return True

def delete(table_name, q, value):
    with sqlite3.connect('database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = f"DELETE FROM {table_name} WHERE {q} = ?"
        val = (value,)
        cursor.execute(query, val)
        res = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()
    return True