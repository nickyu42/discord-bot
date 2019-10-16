"""
Functions meant to be used as decorators that perform certain checks
before the wrapped function is executed
"""
import discord
from discord.ext import commands


def is_owner_check(message):
    return message.author.id == '282191364614127616'


def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


def active_cog_check(bot, cog):
    return True if cog in bot.cogs else False


def active_cog(cog):
    def wrapper():
        return commands.check(lambda ctx: active_cog_check(ctx.bot, cog))
    return wrapper()

