import discord
from discord.ext import commands 
import sqlite3

from .utils import check


def change_bank(ctx, name: str, amount: int, modifier: str, warning=False):
    """Global method or changing someones bank value

    :param ctx: commands.Context class
    :param name: str name of user to change bank
    :param amount: str amount of money to add or remove
    :param modifier: str either + or -
    :param warning: bool To raise an exception if the user doesn't have enough money or not

    """
    if not amount or modifier not in ('+', '-'):
        raise Exception('Modifier not valid')

    obj = ctx.bot.cogs['Currency']

    if warning and obj.in_bank(name) - amount < 0:
        raise ValueError("{} does not have enough money".format(name))

    if modifier is '+':
        obj.add_money(name, amount)
    else:
        obj.remove_money(name, amount)


class Currency:
    """Allows for connecting with a user database

    User base format
    +---------+-----------------------------------+
    | Column  |           Description             |
    +---------+-----------------------------------+
    |  id     | Discord ID: INT                   |
    +---------+-----------------------------------+
    |  name   | Discord name: STRING              |
    +---------+-----------------------------------+
    |  money  | Amount of money: INT              |
    +---------+-----------------------------------+
    |  daily  | Date of last daily bonus claimed  |
    |         | format                            |
    +---------+-----------------------------------+

    """
    _columns = ['id', 'name', 'money', 'daily']
    # TODO: add daily to table Users

    def __init__(self, bot):
        self.bot = bot
        self.con = sqlite3.connect('users.db')
        self.cur = self.con.cursor()

    def __unload(self):
        if self.con:
            self.con.close()

    def _add_member(self, discord_id, name):
        """Add a new member to the user base
        :param discord_id: discord user.id INT
        :param name: discord user name

        :return: raises exception on failure
        """
        fs = "INSERT INTO Users (Id, Name) VALUES ({0}, '{1}')"
        fs = fs.format(discord_id, name)

        try:
            self.cur.execute(fs)

        except sqlite3.IntegrityError as e:
            # rollback changes if error occurs
            if self.con:
                self.con.rollback()

            raise e

    @property
    def _members(self):
        self.cur.execute('SELECT name FROM Users')
        members = [t[0] for t in self.cur.fetchall()]

        return members

    def get_rows(self, column, value):
        """Grabs all rows where column=value

        :param column: selector column
        :param value: the value to search for in given column

        :return: list of dict with columns as keys with corresponding values,
                 otherwise returns empty list if the requested columns doesn't exist
                 or there isn't a column with the given value
        """
        if column not in self._columns:
            return []

        cmd = 'SELECT * FROM Users where {0}=({1})'

        # add quotation marks if value is a string
        if type(value) is str:
            self.cur.execute(cmd.format(column, "'" + value + "'"))
        else:
            self.cur.execute(cmd.format(column, value))

        rows = self.cur.fetchall()

        if rows:
            all_rows = [dict(zip(self._columns, row)) for row in rows]
            return all_rows
        else:
            return []

    def get_data(self, name):
        """Grabs all values from given user

        :return: dict with columns as keys with values
                 return empty list does not exist
        """
        cmd = "SELECT * FROM Users where name='{}'"
        self.cur.execute(cmd.format(name))

        row = self.cur.fetchone()

        if row:
            return dict(zip(self._columns, row))
        else:
            return []

    def in_bank(self, name):
        """Get how much money is left

        :param name: discord member name
        :return: int money left
        """
        self.cur.execute("SELECT money FROM Users WHERE name='{}'".format(name))
        return self.cur.fetchone()[0]

    def add_money(self, name, amount):
        in_bank = self.in_bank(name)
        new_value = in_bank + int(amount)

        to_execute = "UPDATE Users SET money={0} WHERE name='{1}'".format(new_value, name)
        self.cur.execute(to_execute)

        self.con.commit()

    def remove_money(self, name, amount):
        in_bank = self.in_bank(name)

        if in_bank - amount < 0:
            new_value = 0
        else:
            new_value = in_bank - int(amount)

        to_execute = "UPDATE Users SET money={0} WHERE name='{1}'".format(new_value, name)
        self.cur.execute(to_execute)

        self.con.commit()

    @commands.group(name='db')
    async def database(self):
        pass

    @database.command()
    @check.is_owner()
    async def execute(self, *, cmd: str):
        """Method executes given sql command"""
        try:
            self.cur.execute(cmd)
            self.con.commit()
            await self.bot.say('\N{CHECK MARK}')
        except sqlite3.Error as e:
            # if error occurs revert changes
            if self.con:
                self.con.rollback()

            await self.bot.say('{}: {}'.format(type(e).__name__, e))

    @database.command(hidden=True)
    @check.is_owner()
    async def members(self):
        """Return all members in the user base"""
        await self.bot.say('\n'.join(self._members))

    @database.command(pass_context=True, hidden=True)
    @check.is_owner()
    async def add_members(self, ctx):
        """Add all members from the invokers server to the user base"""
        message = ctx.message

        # exit if command was called from a direct message
        if message.channel.is_private:
            return

        self.cur.execute('SELECT Name FROM Users')
        existing_members = [n[0] for n in self.cur.fetchall()]

        for member in message.server.members:
            name = member.name

            if name not in existing_members and not member.bot:
                try:
                    self._add_member(member.id, name)
                    await self.bot.say('Successfully added {} to the user base'.format(name))

                except Exception as e:
                    await self.bot.say('{}: Failed to add {} to the user base'.format(e, name))

        self.con.commit()

    @commands.command(pass_context=True)
    async def give(self, ctx, amount: int, member: discord.Member = None):
        """Removes an amount of money from the invoker's bank
        and gives it to the given member

        If command is invoked by owner, then no money will be subtracted

        :param amount: amount of money to give
        :param member: discord member class, receiver
        """

        giver = ctx.message.author.name
        receiver = member.name
        member_mention = '<@{}>'.format(member.id)

        if receiver not in self._members:
            await self.bot.say('{} is not in the user base, or does not exist'.format(member))
            return

        # if giver is owner, no money is subtracted
        if check.is_owner_check(ctx.message):
            self.add_money(receiver, amount)
            await self.bot.say("{} has received {} from {}".format(member_mention, amount, giver))
        else:
            in_bank = self.in_bank(giver)
            if in_bank - int(amount) < 0:
                await self.bot.say("You don't have enough money")
            else:
                self.remove_money(giver, amount)
                self.add_money(receiver, amount)
                await self.bot.say("{}, has received {} from {}".format(member_mention, amount, giver))

    @commands.command(pass_context=True, name='$')
    async def _get_money(self, ctx):
        """Tells the invoker how much money he has in bank"""
        member_mention = '<@{}>'.format(ctx.message.author.id)
        in_bank = self.in_bank(ctx.message.author.name)

        await self.bot.say('{} you have {}'.format(member_mention, in_bank))


def setup(bot):
    bot.add_cog(Currency(bot))