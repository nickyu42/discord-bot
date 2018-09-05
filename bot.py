"""
Simple discord bot using the discord.py library
"""

from discord.ext import commands
import discord
import asyncio
import json
import sys
import traceback
import time

description = """Hello! I am a bot made by /u/nickyu42"""
command_prefix = '<>'

# This tells what extensions to load at startup
initial_extensions = [
    'cogs.admin',
    'cogs.reddit',
    'cogs.blackjack_single'
]


class Bot(commands.Bot):

    def _load_extensions(self):
        """Tries to load all initial extensions"""
        for extension in initial_extensions:
            try:
                print('Loading extension', extension, end=' - ')
                self.load_extension(extension)
                print('Done')
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))

    def _unload_extensions(self):
        """Tries to unload all active extensions"""
        for extension in tuple(self.extensions):
            try:
                self.unload_extension(extension)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to unload extension {}\n{}'.format(extension, exc))

    def _remove_cogs(self):
        for cog in tuple(self.cogs):
            try:
                self.remove_cog(cog)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to remove cog {}\n{}'.format(cog, exc))

    def run(self, *args, **kwargs):
        """
        Overridden version of run method from discord.Client
        which loads a set of extensions before starting the event loop
        """

        try:
            self._load_extensions()
            self.loop.run_until_complete(self.start(*args, **kwargs))

        except KeyboardInterrupt:
            self._unload_extensions()
            self._remove_cogs()
            self.loop.run_until_complete(self.logout())

            # cancel all pending async events
            pending = asyncio.Task.all_tasks(loop=self.loop)
            gathered = asyncio.gather(*pending, loop=self.loop)
            try:
                gathered.cancel()
                self.loop.run_until_complete(gathered)

                gathered.exception()
            except:
                pass

        finally:
            self.loop.close()


bot = Bot(command_prefix=commands.when_mentioned_or(command_prefix), description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print('Username ' + bot.user.name)
    print('ID ' + bot.user.id)

    # Set playing status 
    await bot.change_presence(game=discord.Game(name='Use <>commands'))


@bot.event
async def on_command_error(exception, ctx):
    print('[{0.author.name} | {0.timestamp}] {0.content}'.format(ctx.message))
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
    await bot.send_message(ctx.message.channel, fmt.format(type(exception).__name__, exception))


@bot.event
async def on_message(message):
    if message.author.bot: 
        return

    await bot.process_commands(message)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    try:
        bot.run(credentials['TOKEN'])
    finally:
        sys.exit()
