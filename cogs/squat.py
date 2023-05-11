from discord.ext import commands
import functools
import asyncio
from concurrent.futures import ThreadPoolExecutor
import searcher
from string_utils import split_string

async def setup(bot):
    await bot.add_cog(Squat(bot))

class Squat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        required_roles = ["Othermods", "Contributor"]
        try:
            has_required_role = await commands.has_any_role(*required_roles
                                                            ).predicate(ctx)
            return has_required_role
        except:
            await ctx.send(
                "You don't have the required role to use this command.")

    def doSearch(self, message):
        results = ''.join(searcher.do([message]))
        print(results)
        return results

    @commands.command(pass_context=True)
    async def search(self, ctx, *, message=""):
        await ctx.send(f"Searching for _{message}_")

        loop = asyncio.get_event_loop()
        matches = await loop.run_in_executor(
            ThreadPoolExecutor(),
            functools.partial(self.doSearch, message))

        if(not matches):
            await ctx.send(f"No matches found for _{message}_")
        else:
            for chunk in split_string(f"Matches for _{message}_\n{matches}"):
                await ctx.send(chunk)