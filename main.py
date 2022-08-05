startEmoji = '\U0001F633'


from nextcord import Intents
from nextcord.ext import commands
import os
from game import Game, good, ppQuest as validNPlayers
import logging

class Bot:
    def __init__(self, __prefix='!'):
        __intents = Intents.default()
        __intents.message_content = True
        self.client = commands.Bot(command_prefix=__prefix, intents=__intents)
        self.game = None
    
    def main(self):
        @self.client.command(help='Start a game with a specified number of players.')
        async def start(ctx, msg=''):
            try:
                players = int(msg)
            except ValueError:
                await ctx.send(f'"{msg}" is not a number.')
                return
            if players not in validNPlayers:
                await ctx.send(f'{players} is not a valid number of players ' +
                    'for the game.')
                return
            if self.game:
                await ctx.send('A game is already in progress.')
                return
            
            self.startMsg = await ctx.send(f'Waiting for {players} players to join.')
            await self.startMsg.add_reaction(startEmoji)
            self.game = Game(players, ctx)
        
        @self.client.command(help='Force stop the game.')
        @commands.has_permissions(kick_members=True)
        async def forcestop(ctx):
            self.game = None
            await ctx.send('A game may have been stopped by force.')
            logging.warning('A game was stopped by force.')
        
        @self.client.command(help='Select players for a quest.')
        async def select(ctx, msg=''):
            if not self.game or not self.game.ready:
                return
            if ctx.author.id != self.game.cID:
                await ctx.send('It is not your turn.')
            
            # find the users pinged
            users = ctx.message.mentions
            if not users:
                await ctx.send('You must select at least one user.')
                return
            await self.game.SelectPlayers(users)
        
        @self.client.command(help='Guess the Merlin.')
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
            
            if self.game and self.game.ready and self.game.voteMsg and         \
            reaction.message.id == self.game.voteMsg.id and user.id in         \
            self.game.players:
                await self.game.AddVote(reaction.emoji)

            
        @self.client.event
        async def on_reaction_remove(reaction, user):
            if self.startMsg and self.game and reaction.message.id ==          \
            self.startMsg.id and reaction.emoji == start_emoji and user.id !=  \
            self.client.user.id:
                self.game.RemovePlayer(user.name)
            
            if self.game and self.game.ready and self.game.voteMsg and         \
            reaction.message.id == self.game.voteMsg.id and user.id in         \
            self.game.players:
                self.game.RemoveVote(reaction.emoji)


        logging.info('Bot is running.')
        self.client.run(os.environ['AVALON_DISCORD_TOKEN'])


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
Bot().main()
