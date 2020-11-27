import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio
import math

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class RedirectMail(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:RedirectMail ready")

    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.guild:
            if col_serverinfo.find_one() is None:
                return
            else:
                server_owner = col_serverinfo.find_one()['guild_owner']

            if message.author == self.client.user:
                return

            print(f'author : {message.author}')
            print(f'message: {message.content}')

            mutual_servers = []
            page = 0
            all_server = self.client.guilds
            for server in all_server:
                guild_id = server.id
                guild = self.client.get_guild(guild_id)
                for member in guild.members:
                    if message.author.id == member.id:
                        mutual_servers.append(guild.id)
                        continue
            embed = discord.Embed(title="Select a server",
                                  color=0x26d953,
                                  description=f'choose a server that you will send a message to the moderators\n'
                                              f'page {page + 1}/{math.ceil(len(mutual_servers) / 3)}'
                                  )
            emj = [':one:', ':two:', ':three:']
            num_emj = ['\U000023ea',
                       '1\N{variation selector-16}\N{combining enclosing keycap}',
                       '2\N{variation selector-16}\N{combining enclosing keycap}',
                       '3\N{variation selector-16}\N{combining enclosing keycap}',
                       '\U000023e9',
                       ]
            count = 0
            guild_list = []

            if len(mutual_servers) <= 3:
                guild_itter = mutual_servers[0:len(mutual_servers)]
            else:
                guild_itter = mutual_servers[3 ** page:3 ** page + 3]

            for guild_id in guild_itter:
                guild_list.append(guild_id)
                guild = self.client.get_guild(guild_id)
                guild_name = guild.name
                guild_member = len(guild.members)
                embed.add_field(name=f'{emj[count]} {guild_name}',
                                value=f'ID : {guild_id}\n'
                                      f'member : {guild_member}',
                                inline=False
                                )
                count += 1
            pass

            print(mutual_servers)
            wait_msg = await message.author.send(embed=embed)
            if page != 0:
                await wait_msg.add_reaction('\U000023ea')
            for x in range(0, count):
                await wait_msg.add_reaction(num_emj[x + 1])
            if (len(mutual_servers) / 3) > (page + 1):
                await wait_msg.add_reaction('\U000023e9')

            def check(reaction, user):
                return str(reaction.emoji) in num_emj and message.author == user

            loop = True
            while loop:
                try:
                    # Timeout parameter is optional but sometimes can be useful
                    reaction, user = await self.client.wait_for('reaction_add', timeout=30, check=check)
                    # Will wait until a user reacts with the specified checks then continue on with the code
                    index = num_emj.index(str(reaction))
                    if index in range(1, 3):
                        target_guild = self.client.get_guild(guild_list[index - 1])
                        target_user = self.client.get_user(target_guild.owner.id)
                        clock = datetime.now()
                        date = datetime.today()
                        current_time = clock.strftime('%H:%M:%S')
                        current_date = date.strftime('%d/%m/%Y')
                        embed = discord.Embed(
                            title=f' ',
                            description=message.content,
                            colour=discord.Colour.blue()
                        )
                        embed.set_footer(text=f"sender : {message.author} \n"
                                              f"server : {target_guild.name}\n"
                                              f"Discord ID : {message.author.id}\n"
                                              f"{current_date}.{current_time}")
                        embed.set_author(name=message.author.name,
                                         icon_url=message.author.avatar_url)
                        await target_user.send(embed=embed)
                        await wait_msg.edit(f"your message has been sent to : "
                                            f"{str(reaction)} {target_guild.name}",
                                            embed=None)
                        print(f'index : {target_guild.owner.id}')
                        # await wait_msg.edit(content='Message success',embed=None)
                        loop = False
                    elif index == 0:
                        if page != 0:
                            pass
                    elif index == 4:
                        pass

                except asyncio.TimeoutError:

                    # when wait_for reaches specified timeout duration (in this example it is 30 seconds)
                    await wait_msg.edit(content='Time out', embed=None)
                    await wait_msg.delete()
                    loop = False

            return


def setup(client):
    client.add_cog(RedirectMail(client))
