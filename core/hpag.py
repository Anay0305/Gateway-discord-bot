from discord.ext import commands
import discord
import sqlite3
import core.emojis as emojis
import botinfo

def change_page(id, c: int):
    query = "SELECT * FROM  'help' WHERE main = ?"
    val = (id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        log_db = cursor.fetchone()
    sql = (f"UPDATE 'help' SET 'no' = ? WHERE main = ?")
    val = (c, id)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()
    return

def get_page(id):
    query = "SELECT * FROM  'help' WHERE main = ?"
    val = (id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        log_db = cursor.fetchone()
    return log_db['no']

class helpdrop(discord.ui.Select):
    def __init__(self, view: discord.ui.View, embed_list: list, no:dict, cogs: dict, i: int, ctx):
        self.embed_list = embed_list
        self.v = view
        self.id = i
        options = []
        options.append(discord.SelectOption(label=f'Index', value=0, description=f'Shows You Index', emoji=emojis.help_index))
        for i in cogs:
            options.append(discord.SelectOption(label=f'{i} Commands', value=no[i], description=f'Show You {i} Commands', emoji=f'{cogs[i]}'))

        super().__init__(placeholder="Select Module To Get Help For That Module.",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        id = self.id
        change_page(id, int(self.values[0]))
        if get_page(id) <= 0:  # if we are on first page,
            change_page(id, 0)  # we disabled `first` and `previous`
            self.v.first.disabled = True
            self.v.previous.disabled = True
        else:
            self.v.first.disabled = False
            self.v.previous.disabled = False

        if get_page(id) >= len(self.embed_list) - 1:
            change_page(id, len(self.embed_list) - 1)
            self.v._last.disabled = True
            self.v.next.disabled = True
        else:
            self.v._last.disabled = False
            self.v.next.disabled = False
        await HPaginationView.callback(self.v, interaction=interaction, c=get_page(id), em_list = self.embed_list)

class HPaginationView(discord.ui.View):

    def __init__(self, embed_list: list, no:dict, cogs: dict, i: int, ctx, links: list=None):
        super().__init__(timeout=90)
        self.add_item(helpdrop(self, embed_list, no, cogs, i, ctx))
        self.embed_list = embed_list
        self.id = i
        self.ctx = ctx
        self.links = links
        self.view = None
        self.message = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user == interaction.user or interaction.user.id in botinfo.main_devs:
            return True
        await interaction.response.send_message(
            f"Only **{self.user}** can interact. Run the command if you want to.",
            ephemeral=True,
        )
        return False

    async def callback(self, interaction: discord.Interaction, c: int, em_list: list):
        await interaction.response.edit_message(
            embed=em_list[c], view=self
        )

    async def on_timeout(self) -> None:
        query = "SELECT * FROM  'help' WHERE main = ?"
        val = (self.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            log_db = cursor.fetchone()
        sql = (f"DELETE FROM 'help' WHERE main = ?")
        val = (self.id,)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

    @discord.ui.button(label="≪", style=discord.ButtonStyle.blurple, disabled=True)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        id = self.id
        change_page(id, 0)

        self.previous.disabled = True
        button.disabled = True

        if len(self.embed_list) >= 1:
            self.next.disabled = False
            self._last.disabled = False
        else:
            self.next.disabled = True
            self._last.disabled = True

        await interaction.response.edit_message(
            embed=self.embed_list[get_page(id)], view=self
        )
        self.view = get_page(id)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green, disabled=True)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        id = self.id
        change_page(id, get_page(id) - 1)

        if len(self.embed_list) >= 1:  # if list consists of 2 pages, if,
            self._last.disabled = (
                False  # then `last` and `next` need not to be disabled
            )
            self.next.disabled = False
        else:
            self._last.disabled = True  # else it should be disabled
            self.next.disabled = True  # because why not

        if get_page(id) <= 0:  # if we are on first page,
            change_page(id, 0)  # we disabled `first` and `previous`
            self.first.disabled = True
            button.disabled = True
        else:
            self.first.disabled = False
            button.disabled = False


        await interaction.response.edit_message(
            embed=self.embed_list[get_page(id)], view=self
        )
        self.view = get_page(id)


    @discord.ui.button(emoji="<a:Cross:937350485919289364>", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        query = "SELECT * FROM  'help' WHERE main = ?"
        val = (self.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            log_db = cursor.fetchone()
        sql = (f"DELETE FROM 'help' WHERE main = ?")
        val = (self.id,)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await interaction.message.delete()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        id = self.id
        change_page(id,get_page(id)+1)

        if get_page(id) >= len(self.embed_list) - 1:
            change_page(id, len(self.embed_list) - 1)
            button.disabled = True
            self._last.disabled = True

        if len(self.embed_list) >= 1:
            self.first.disabled = False
            self.previous.disabled = False
        else:
            self.previous.disabled = True
            self.first.disabled = True

        await interaction.response.edit_message(
            embed=self.embed_list[get_page(id)], view=self
        )
        self.view = get_page(id)

    @discord.ui.button(label="≫", style=discord.ButtonStyle.blurple, disabled=False)
    async def _last(self, interaction: discord.Interaction, button: discord.ui.Button):
        id = self.id
        change_page(id,len(self.embed_list) - 1)

        button.disabled = True
        self.next.disabled = True

        if len(self.embed_list) >= 1:
            self.first.disabled = False
            self.previous.disabled = False
        else:
            self.first.disabled = True
            self.previous.disabled = True

        await interaction.response.edit_message(
            embed=self.embed_list[get_page(id)], view=self
        )
        self.view = get_page(id)

    async def start(self, ctx: commands.Context, interaction: discord.Interaction=None):
        if len(self.embed_list) != 1:
            if ctx.author.id in ctx.bot.owner_ids:
                if interaction is not None:
                    self.message = await interaction.response.send_message(content="Hey Developer, How can I help you today?", embed=self.embed_list[0], view=self, ephemeral=True)
                else:
                    self.message = await ctx.send(content="Hey Developer, How can I help you today?", embed=self.embed_list[0], view=self)
            else:
                if interaction is not None:
                    self.message = await interaction.response.send_message(embed=self.embed_list[0], view=self, ephemeral=True)
                else:
                    self.message = await ctx.send(embed=self.embed_list[0], view=self)
            self.user = ctx.author
            await self.wait()
            return self.message
        else:
            if interaction is not None:
                self.message = await interaction.response.send_message(embed=self.embed_list[0], ephemeral=True)
            else:
                self.message = await ctx.send(embed=self.embed_list[0])
            self.user = ctx.author
            return self.message