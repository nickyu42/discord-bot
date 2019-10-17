"""
Simple discord bot using the discord.py library
"""

import asyncio
import json
import traceback
import logging

import discord
from discord.ext import commands

DESCRIPTION = 'I am Holo the Wise Wolf, and I am a very proud wolf'
COMMAND_PREFIX = '<>'

# This tells what extensions to load at startup
INITIAL_EXTENSIONS = [
    'cogs.admin'
]


def setup_logging(filename: str) -> logging.Logger:
    """
    Initialize logging to an output file
    :param filename: name of the output file
    :return: own logger
    """
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    # Log discord to given filename
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(filename=filename, encoding='utf-8', mode='w')
    handler.setFormatter(formatter)
    discord_logger.addHandler(handler)

    # Log bot to stdout
    logger = logging.getLogger('bot')
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class Bot(commands.Bot):

    def _load_extensions(self):
        """
        Tries to load all initial extensions
        """
        for extension in INITIAL_EXTENSIONS:
            try:
                log.info('Loading extension %s', extension)
                self.load_extension(extension)
                log.info('Done %s', extension)
            except Exception as ex:
                exc = '{}: {}'.format(type(ex).__name__, ex)
                log.warning('Failed to load extension %s\n%s', extension, exc)

    def _unload_extensions(self):
        """
        Tries to unload all active extensions
        """
        for extension in tuple(self.extensions):
            try:
                self.unload_extension(extension)
            except Exception as ex:
                exc = '{}: {}'.format(type(e).__name__, ex)
                log.warning('Failed to unload extension %s\n%s', extension, exc)

    def _remove_cogs(self):
        """
        Remove all loaded cogs
        """
        for cog in tuple(self.cogs):
            try:
                self.remove_cog(cog)
            except Exception as ex:
                exc = '{}: {}'.format(type(ex).__name__, ex)
                log.warning('Failed to remove cog %s\n%s', cog, exc)

    def _cleanup_tasks(self):
        """
        Cancel all async tasks
        """
        pending = asyncio.Task.all_tasks(loop=self.loop)

        tasks = {t for t in pending if not t.done()}

        if not tasks:
            return

        gathered = asyncio.gather(*tasks, loop=self.loop, return_exceptions=True)
        gathered.cancel()
        self.loop.run_until_complete(gathered)
        log.info('Finished cleaning up pending tasks')

        for task in tasks:
            if not task.cancelled() and task.exception() is not None:
                self.loop.call_exception_handler({
                    'message': 'Unhandled exception during Client.run shutdown.',
                    'exception': task.exception(),
                    'task': task
                })

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
            self.loop.run_until_complete(self.logout())
            self._cleanup_tasks()

        finally:
            self.loop.close()


bot = Bot(command_prefix=commands.when_mentioned_or(COMMAND_PREFIX), description=DESCRIPTION)


@bot.event
async def on_ready():
    log.info('Logged in as %s with id=%s', bot.user.name, bot.user.id)

    # Set playing status 
    await bot.change_presence(status=discord.Game(name='Use <>commands'))


@bot.event
async def on_command_error(exception, ctx: commands.Context):
    log.error('[{0.author.name} | {0.timestamp}] {0.content}'.format(ctx.message))
    log.error(traceback.format_exception(type(exception), exception, exception.__traceback__))

    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
    await ctx.send(fmt.format(type(exception).__name__, exception))


@bot.event
async def on_message(message):
    if message.author.bot: 
        return

    await bot.process_commands(message)


def load_credentials():
    """
    Load credentials file
    :return: dict of json object
    """
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    log = setup_logging('discord.log')
    webhook = discord.Webhook.from_url(credentials['WEBHOOK'], adapter=discord.RequestsWebhookAdapter())

    try:
        bot.run(credentials['TOKEN'])
    except Exception as ex:
        webhook.send(str(ex), username='Holo')
    finally:
        webhook.send('Server closed', username='Holo')
