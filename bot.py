from discord.ext import tasks
import datetime
import discord

import os
from dotenv import load_dotenv

from string import whitespace

load_dotenv()

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(f'it is currently {datetime.datetime.utcnow()}')

    @tasks.loop(time=datetime.time(13,10))  # task runs daily
    async def my_background_task(self):
        datestring = datetime.datetime.utcnow().strftime("%y-%m-%d")
        final = f'results-{datestring}.txt'

        with open(final, "r") as f:
            message = f.read()

        if(len(message) > 0):
            channelid = int(os.getenv('DISCORD_RESULTS_CHANNEL'))
            channel = self.get_channel(channelid)  # channel ID goes here
            await channel.send(message)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = MyClient(intents=discord.Intents.default())
client.run(os.getenv('DISCORD_TOKEN'))