import discord
from discord.ext import commands
import os
import random as rnd


HELP_MESSAGE = """\
```css
[Command list]

   say : Make me say something
   tts : Make me say something with text-to-speech turned on
 hello : Hi!
    nb : L-Lewd!
    bj : Play a game of blackjack against me
 anime : Grab the latest anime releases from /r/anime
 manga : Grab the latest manga releases from /r/manga
    db : Commands for editing user base
     $ : See how much money you have left
  give : Give someone money from your bank
         [example] give <amount> <@user>
    rr : Play russian roulette
```
"""


class Users(discord.ext.commands.Cog):
    """Basic commands for users"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='commands')
    async def command(self, ctx):
        """Sends a private message to the sender with all available commands"""
        await ctx.author.send(HELP_MESSAGE)

    @commands.command()
    async def say(self, ctx, *, text: str):
        """Makes the bot say something"""
        if text:
            await ctx.send(''.join(text))

    @commands.command(pass_context=True)
    async def tts(self, ctx, *, text: str):
        """Makes the bot say something with text-to-speech"""
        if text:
            await ctx.send(ctx.message.channel, text, tts=True)

    @commands.command(pass_context=True)
    async def hello(self, ctx, member: discord.Member = None):
        """Replies to the sender with a random greeting"""
        if member is None:
            member = ctx.message.author

        author = member.name
        greeting = rnd.choice(["Kon'nichiwa ", "Moshi moshi "])
        affix = rnd.choice(["-chan", "-sama", "-san", "-kun"])

        await ctx.send(greeting + author + affix)

    @commands.command(name='nb')
    async def nosebleed(self):
        """Sends a random anime nosebleed image to the invoker's channel"""
        path = './cogs/images/'
        
        # find all image file names in images folder
        images = [f for f in os.listdir(path)]
        image_name = rnd.choice(images)

        with open(path + image_name, 'rb') as f:
            await ctx.upload(f)

    @commands.command()
    async def kongou(self):
        """Sends an image of a trash can to the invoker's channel"""
        embed = discord.Embed(title='Kongou')
        embed.set_image(url="http://i.imgur.com/ODfJ5iv.png")

        await ctx.send(embed=embed)

    @commands.command()
    async def bongo(self):
        """Sends a random link of bongo cat from a youtube playlist"""
        with open(os.getcwd() + '/cogs/users/bongo.txt', 'r') as f:
            link = rnd.choice(list(f.readlines()))

        await ctx.send(link)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def presence(self, ctx, *, text: str):
        await self.bot.change_presence(activity=discord.Game(text))
        await ctx.send(f'Changed to {text}')

def setup(bot):
    bot.add_cog(Users(bot))
