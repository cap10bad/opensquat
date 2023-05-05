import datetime
import os
import discord
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)


@tasks.loop(time=datetime.time(13, 10))
async def my_background_task():
    datestring = datetime.datetime.utcnow().strftime("%y-%m-%d")
    final = f'results-{datestring}.txt'

    with open(final, "r") as f:
        message = f.read()

    if (len(message) > 0):
        channelid = int(os.getenv('DISCORD_RESULTS_CHANNEL'))
        channel = bot.get_channel(channelid)
        await channel.send(message)


@my_background_task.before_loop
async def before_my_task():
    await bot.wait_until_ready()
    print('Finished waiting for bot to be ready!')


@bot.event
async def on_ready():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded Cog: {filename[:-3]}")
        else:
            print("Unable to load pycache folder.")
    await my_background_task.start()


bot.run(os.getenv('DISCORD_TOKEN'))