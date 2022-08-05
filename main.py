from nextcord import Intents
from nextcord.ext.commands import Bot as _Bot
import os
import constants as K
from game import Game
import logging


valid_nplayers = {1,5,6,7,8,9,10}
start_emoji = '\u2705'

class Bot:
    def __init__(self, __prefix='!'):
        __intents = Intents.default()
        __intents.message_content = True
        self.client = _Bot(command_prefix=__prefix, intents=__intents)

        self.game = None
    
    def main(self):
        @self.client.command()
        async def ping(ctx):
            await ctx.send(':flushed:')

        @self.client.command()
        async def start(ctx, msg=''):
            try:
                players = int(msg)
            except ValueError:
                await ctx.send(f'"{msg}" is not a number.')
                return
            
            if players not in K.valid_nplayers:
                await ctx.send(f'{players} is not a valid number of players for the game.')
                return
            

            self.startMsg = await ctx.send(f'{players} players are ready to play.')
            await self.startMsg.add_reaction(K.start_emoji)
            self.game = Game(players, ctx)

        # listener for the checkmark reaction
        @self.client.event
        async def on_reaction_add(reaction, user):
            if self.startMsg and self.game and reaction.message.id ==          \
            self.startMsg.id and reaction.emoji == K.start_emoji and user.id !=\
            self.client.user.id:
                await self.game.AddPlayer(user)
            
        @self.client.event
        async def on_reaction_remove(reaction, user):
            if self.startMsg and self.game and reaction.message.id ==          \
            self.startMsg.id and reaction.emoji == K.start_emoji and user.id !=\
            self.client.user.id:
                self.game.RemovePlayer(user.name)


        logging.info('Bot is running.')
        self.client.run(os.environ['AVALON_DISCORD_TOKEN'])


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

Bot().main()