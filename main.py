import discord
from discord.ext import commands, timers
from discord.ext.commands import CommandNotFound
import asyncio
import json
import pymongo

with open("cred.json") as json_file:
    credentials = json.load(json_file)

PREFIX = credentials['prefix']

intents = discord.Intents.all()
intents.members = True
intents.reactions = True


class mailModGII(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX,
                         intents=intents
                         )
        self.client = commands.Bot

        self.client.remove_command(self, name='help')
        self.token = credentials['token']
        self.load_extension('cogs.redirectmail')
        self.load_extension('cogs.greeting')
        self.load_extension('cogs.mod')

    async def on_ready(self):

        print('Logged on as', self.user)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        game = discord.Game("Nawaytes")
        await self.client.change_presence(self, status=discord.Status.idle, activity=game)

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        raise error

    def run(self):
        super().run(self.token)


if __name__ == '__main__':
    bot = mailModGII()
    bot.run()
