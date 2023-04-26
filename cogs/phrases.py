from discord.ext import commands
import os
import pymongo

uri = os.getenv('MONGO_CONNECTION')
mongo = pymongo.MongoClient(uri)
db = mongo['boringsec_db']
collection = db['phrases']


async def setup(bot):
    await bot.add_cog(Phrases(bot))


class Phrases(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_phrases(self, ctx):
        lines = ''
        for document in collection.find():
            lines = f'{lines}**{document["partner"]}**\n'
            for keyword in document["keywords"]:
                lines = f'{lines}\t{keyword}\n'
        await ctx.send(lines)

    @commands.command(pass_context=True)
    async def add_phrase(self, ctx, *, message=""):
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
    async def remove_phrase(self, ctx, *, message=""):
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
