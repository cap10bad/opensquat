from discord.ext import commands
import os
import pymongo
import datetime
from string_utils import split_string

uri = os.getenv('MONGO_CONNECTION')
mongo = pymongo.MongoClient(uri)
db = mongo['boringsec_db']
collection = db['phrases']


async def setup(bot):
    await bot.add_cog(Phrases(bot))

class Phrases(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        required_roles = ["Othermods", "Contributor"]
        try:    
            has_required_role = await commands.has_any_role(*required_roles).predicate(ctx)
            return has_required_role
        except:
            await ctx.send("You don't have the required role to use this command.")
    
    @commands.command()
    async def get(self, ctx):
        lines = ''
        for document in collection.find():
            lines = f'{lines}**{document["partner"]}**\n'
            for keyword in document["keywords"]:
                lines = f'{lines}\t{keyword}\n'
        await ctx.send(lines)

    @commands.command(pass_context=True)
    async def add(self, ctx, *, message=""):
        splits = message.split()

        if len(splits) != 2:
            await ctx.send("add_phrase *partner* *phrase*")
            return

        partner = collection.find_one({"partner": splits[0]})

        if partner is None:
            await ctx.send(f"Adding partner *{splits[0]}*")
            partner = {"partner": splits[0], "keywords": []}
            collection.insert_one(partner)

        if splits[1] in partner["keywords"] or splits[1] == splits[0]:
            await ctx.send(
                f"Phrase *{splits[1]}* already exists for partner *{splits[0]}*")
        else:
            partner["keywords"].append(splits[1])
            new_phrases = "\n\t".join(partner["keywords"])
            await ctx.send(f"Adding phrase *{splits[1]}* to partner *{splits[0]}*\nNew phrase list:\n\t{new_phrases}")
            collection.update_one({"partner": splits[0]},
                                  {"$push": {"keywords": splits[1]}})

    @commands.command(pass_context=True)
    async def remove(self, ctx, *, message=""):
        splits = message.split()

        if len(splits) != 2:
            await ctx.send("remove_phrase *partner* *phrase*")
            return

        partner = collection.find_one({"partner": splits[0]})

        if partner is None:
            await ctx.send(f"No partner *{splits[0]}* found")
            return

        if splits[1] in partner["keywords"] or splits[1] == splits[0]:
            partner["keywords"].remove(splits[1])
            new_phrases = "\n\t".join(partner["keywords"])
            await ctx.send(f"Removing phrase *{splits[1]}* from partner *{splits[0]}*\nNew phrase list:\n\t{new_phrases}")
            collection.update_one({"partner": splits[0]},
                                  {"$pull": {"keywords": splits[1]}})
        else:
            await ctx.send(
                f"No phrase *{splits[1]}* exists for partner *{splits[0]}*")

    @commands.command(pass_context=True)
    async def remove_partner(self, ctx, *, message=""):
        splits = message.split()

        if len(splits) != 1:
            await ctx.send("remove_partner *partner*")
            return

        partner = collection.find_one({"partner": splits[0]})

        if partner is None:
            await ctx.send(f"No partner *{splits[0]}* found")
            return

        collection.delete_one({"partner": splits[0]})
        await ctx.send(f"Removing partner *{splits[0]}*")

        
    @commands.command()
    async def report(self, ctx):
        datestring = datetime.datetime.utcnow().strftime("%y-%m-%d")
        final = f'results-{datestring}.txt'

        with open(final, "r") as f:
            message = f.read()
        f.close()

        if (len(message) > 0):
            for chunk in split_string(message):
                await ctx.send(chunk)