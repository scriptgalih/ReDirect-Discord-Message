import discord
from discord.ext import commands
from datetime import datetime


class RedirectMail(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:RedirectMail ready")

    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.guild:

            if message.author == self.client.user:
                return

            print(f'author : {message.author}')
            print(f'message: {message.content}')

            user = self.client.get_user(533685396404568104)
            clock = datetime.now()
            date = datetime.today()
            current_time = clock.strftime('%H:%M:%S')
            current_date = date.strftime('%d/%m/%Y')
            embed = discord.Embed(
                title=f'New message',
                description=message.content,
                colour=discord.Colour.blue()
            )
            embed.set_footer(text=f"sender : {message.author} \n"
                                  f"Discord ID : {message.author.id}\n"
                                  f"{current_date} {current_time}")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.set_author(name=self.client.user.name,
                             icon_url=self.client.user.avatar_url)
            await user.send(embed=embed)


def setup(client):
    client.add_cog(RedirectMail(client))
