from nextcord import Intents
from nextcord.ext.commands import Bot as _Bot
import os
from game import Game, good
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
            
            if players not in valid_nplayers:
                await ctx.send(f'{players} is not a valid number of players for the game.')
                return
            

            self.startMsg = await ctx.send(f'{players} players are ready to play.')
            await self.startMsg.add_reaction(start_emoji)
            self.game = Game(players, ctx)
        
        @self.client.command()
        async def select(ctx, msg=''):
            if not self.game or not self.game.ready:
                return
            if ctx.author.id != self.game.cID:
                return
            
            # find the users pinged
            users = ctx.message.mentions
            if not users:
                await ctx.send('You must ping at least one user.')
                return
            # send the users a message
            msg = f'{ctx.author.mention} has selected {", ".join(map(lambda u:u.mention, users))}.'
            await self.game.Broadcast(msg)
        
        @self.client.command()
        async def merlin(ctx, msg=''):
            if not self.game or not self.game.ready or not self.game.over:
                return
            if ctx.author.id not in self.game.players:
                return
            if good[self[self.game.players.index(ctx.author.id)]]:
                return
            
            users = ctx.message.mentions
            if not users or len(users) > 1:
                await ctx.send('There is exactly one merlin.')
                return

            gMerlin = users[0]
            if gMerlin.id == self.game.merlin:
                await ctx.send(f'{gMerlin.mention} is the merlin! The evil ' +
                    'side has won the game.')
            else:
                await ctx.send(f'{gMerlin.mention} is not the merlin! The ' + 
                    'good side has won the game.')
            self.game = None

        # listener for the checkmark reaction
        @self.client.event
        async def on_reaction_add(reaction, user):
            if self.startMsg and self.game and reaction.message.id ==          \
            self.startMsg.id and reaction.emoji == start_emoji and user.id !=  \
            self.client.user.id:
                await self.game.AddPlayer(user)
            
            if self.game and self.game.ready and reaction.message.id ==        \
            self.game.voteMsg.id and user.id in self.game.players:
                await self.game.AddVote(reaction.emoji)

            
        @self.client.event
        async def on_reaction_remove(reaction, user):
            if self.startMsg and self.game and reaction.message.id ==          \
            self.startMsg.id and reaction.emoji == start_emoji and user.id !=  \
            self.client.user.id:
                self.game.RemovePlayer(user.name)
            
            if self.game and self.game.ready and reaction.message.id ==        \
            self.game.voteMsg.id and user.id in self.game.players:
                self.game.RemoveVote(reaction.emoji)


        logging.info('Bot is running.')
        self.client.run(os.environ['AVALON_DISCORD_TOKEN'])


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

Bot().main()