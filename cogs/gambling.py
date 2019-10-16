from discord.ext import commands
import random
import asyncio
from math import ceil

from .utils import check
from .currency import change_bank


class Gambling:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rr', pass_context=True)
    @check.active_cog('Currency')
    async def russian_roulette(self, ctx, bet: int):
        """Russian roulette with a one in six change of winning
        bet modifier if win is 1.2
        bet modifier if lost is -3

        :param ctx: commands.Context class
        :param bet: amount of money to bet
        """
        member = ctx.message.author.name

        if bet > 100:
            await self.bot.say('You cannot bet over 100')
            return

        try:
            change_bank(ctx, member, bet, '-', warning=True)
        except ValueError:
            await self.bot.say("You don't have enough money")
            return

        msg = await self.bot.say('..'*6 + '\N{PISTOL}')
        await asyncio.sleep(1)

        if random.randint(1, 6) == 1:
            bet = int(ceil(bet * 3))
            await self.bot.edit_message(msg, 'BANG!\N{PISTOL}')
            await self.bot.say('Sadly, your day ended with a bullet in your head, you lose -{}'.format(bet))
            change_bank(ctx, member, bet, '-')
        else:
            to_add = int(ceil(bet * 1.2))
            await self.bot.edit_message(msg, 'CLICK!\N{PISTOL}')
            await self.bot.say('Congratz on surviving, you get +{}'.format(to_add - bet))
            change_bank(ctx, member, to_add, '+')


def setup(bot):
    bot.add_cog(Gambling(bot))