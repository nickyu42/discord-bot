import discord
from discord.ext import commands
import praw
import random as rnd


class Stream:
    """Represents a submission stream from a
    given subreddit
    """
    def __init__(self, bot, subreddit, channel):
        self.bot = bot
        self.subreddit = subreddit
        self.channel = channel

    def process_subsmission(self, submission):
        pass

    async def stream_task(self):
        for submission in self.subreddit.stream.submission():
            message = self.process_subsmission(submission)
            await self.bot.send_message(self.channel, message)


class Reddit:
    """Commands for grabbing data from reddit"""

    def __init__(self, bot):
        self.bot = bot
        self.r = praw.Reddit('waifu_bot')
        self.streams = {}

    @commands.command()
    async def anime(self):
        """Returns any new anime releases from /r/anime
        to the sender's channel
        """
        subreddit = self.r.subreddit('anime')
        l = []

        for submission in subreddit.hot(limit=20):
            if submission.title.startswith('[Spoilers]'):
                name = ' '.join(submission.title.split(' ')[1:-1])
                l.append(name)

        await self.bot.say('\n'.join(l))

    @commands.command()
    async def manga(self):
        """Returns any new manga releases from /r/manga
        to the sender's channel
        """
        subreddit = self.r.subreddit('manga')
        l = []

        for submission in subreddit.hot(limit=10):
            if submission.title.startswith('[DISC]'):
                name = ' '.join(submission.title.split(' ')[1:])
                l.append(name)

        await self.bot.say('\n'.join(l))

    @commands.command()
    async def moe(self):
        """Returns an image url from a random moe subreddit"""
        subreddit = rnd.choice(['headpats', 'animeponytails', 'cutelittlefangs'])
        post = self.r.subreddit(subreddit).random()
        
        embed = discord.Embed(title='Link', url=post.url)
        embed.set_image(url=post.url)
                 
        await self.bot.say(embed=embed)
        
    @commands.command()
    async def maki(self):
        post = self.r.subreddit('onetrueidol').random()
           
        embed = discord.Embed(title='Maki', url=post.url)
        embed.set_image(url=post.url)
        
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Reddit(bot))
