from discord.ext import commands
import glob

from .utils.formatting import convert_to_codeblock


class Admin(commands.Cog):
    """Commands only admin can use"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx: commands.Context, *, module: str):
        """Loads a module"""
        module = 'cogs.' + module
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, *, module: str):
        """Unloads a module"""
        module = 'cogs.' + module
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx: commands.Context, *, module: str):
        """Reloads a module."""
        module = 'cogs.' + module
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context):
        """Reloads all active modules with admin as last"""
        #TODO: finish

        for module in self.bot.cogs:

            module_name = 'cogs.' + module.lower

            try:
                self.bot.unload_extension(module_name)
                self.bot.load_extension(module_name)
            except Exception as e:
                await ctx.send('\N{PISTOL}')
                await ctx.send('{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx: commands.Context):
        """Displays a page with a table of all modules"""

        all_modules = glob.glob('./cogs/*.py')
        # remove file extension and directory and sort alphabetically
        all_modules = sorted([m[7:-3] for m in all_modules])

        active_modules = list(self.bot.extensions.keys())
        active_modules = [m[5:] for m in active_modules]

        header = 'Module' + ' '*14 + '|' + ' Status' + '\n' 

        lines = []
        for module in all_modules:
            if module in active_modules:
                status = '\N{CHECK MARK}'
            else:
                status = '\N{BALLOT X}'
            lines.append('{:20}|{:>3}\n'.format(module, status))

        table = header + ''.join(lines)

        await ctx.send(convert_to_codeblock(table))


def setup(bot):
    bot.add_cog(Admin(bot))
