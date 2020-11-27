from discord.ext import commands
import pymongo
import json
import asyncio

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class GreetingMessage(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bot_owner = col_botinfo.find_one()['owner_bot']

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:greeting ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("new member join")
        if col_serverinfo.find_one()['greeting'] is False:
            return
        print("new member join 2")
        greet_str = col_serverinfo.find_one({'guild':member.guild.id})['greeting_message']
        print(member.guild.id)
        if greet_str is None:
            return
        await member.send(greet_str)

    @commands.command(name="start")
    async def cmd_start_greeting_message(self, ctx):
        if ctx.author.id not in [self.bot_owner, ctx.guild.owner.id]:
            return
        if col_serverinfo.find_one({"guild":ctx.guild.id})['greeting'] is True:
            await ctx.send("the command has started", delete_after=5)
            return

        approve_message = await ctx.send("are you sure you want to start the welcome message privately", delete_after=5)
        await approve_message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        await approve_message.add_reaction('\U0000274e')
        col_greeting_msg.insert_one({
            "approve_message": approve_message.id,
            "channel_id": ctx.channel.id
        })
        await asyncio.sleep(5)
        col_greeting_msg.delete_one({'approve_message':approve_message.id})

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return
        user_id = payload.user_id
        message_id = payload.message_id
        guild_id = payload.guild_id
        guild = self.client.get_guild(guild_id)
        emoji = payload.emoji.name
        accept_emoji = '\U00002705'
        start_approval = col_greeting_msg.find_one({"approve_message": message_id})

        if start_approval is not None and user_id in [self.bot_owner, guild.owner.id]:
            channel = self.client.get_channel(start_approval['channel_id'])
            print(emoji.encode('utf-8'))
            if emoji == accept_emoji:
                col_greeting_msg.delete_one({"approve_message": message_id})
                col_serverinfo.update_one({"guild": guild.id}, {"$set": {"greeting": True}})
                await channel.send('the greeting message has started', delete_after=5)
                print("approve")


def setup(client):
    client.add_cog(GreetingMessage(client))
