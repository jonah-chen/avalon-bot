startEmoji = '\U0001F633'
prefix = '!'
__game = None


from nextcord import Intents
from nextcord.ext import commands
import os
from game import Game, good, ppQuest as validNPlayers
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


__intents = Intents.default()
__intents.message_content = True
__client = commands.Bot(command_prefix=prefix, intents=__intents)

@__client.command(help='Start a game with a specified number of players.')
async def start(ctx, msg=''):
    global __game
    try:
        players = int(msg)
    except ValueError:
        await ctx.send(f'"{msg}" is not a number.')
        return
    if players not in validNPlayers:
        await ctx.send(f'{players} is not a valid number of players ' +
            'for the game.')
        return
    if __game:
        await ctx.send('A game is already in progress.')
        return
    
    __game = Game(players, ctx)
    __game.startMsg = await ctx.send(f'Waiting for {players} players to join.')
    await __game.startMsg.add_reaction(startEmoji)
        
@__client.command(help='Force stop the game.')
@commands.has_permissions(kick_members=True)
async def forcestop(ctx):
    global __game
    __game = None
    await ctx.send('A game may have been stopped by force.')
    logging.warning('A game was stopped by force.')
        
@__client.command(help='Select players for a quest.')
async def select(ctx, msg=''):
    global __game
    if not __game or not __game.ready:
        return
    if ctx.author.id != __game.cID:
        await ctx.send('It is not your turn.')
    
    # find the users pinged
    users = ctx.message.mentions
    if not users:
        await ctx.send('You must select at least one user.')
        return
    await __game.SelectPlayers(users)
        
@__client.command(help='Guess the Merlin.')
async def merlin(ctx, msg=''):
    global __game
    game = __game
    if not game or not game.ready or not game.over:
        return
    if ctx.author.id not in game.players:
        return
    if good[game.players.index(ctx.author.id)]:
        return
    
    users = ctx.message.mentions
    if not users or len(users) > 1:
        await ctx.send('There is exactly one merlin.')
        return

    gMerlin = users[0]
    if gMerlin.id == game.merlin:
        await ctx.send(f'{gMerlin.mention} is the merlin! The evil ' +
            'side has won the game.')
    else:
        await ctx.send(f'{gMerlin.mention} is not the merlin! The ' + 
            'good side has won the game.')
    __game = None

        # listener for the checkmark reaction
@__client.event
async def on_reaction_add(reaction, user):
    global __game
    game = __game
    if game and game.startMsg and reaction.message.id ==          \
    game.startMsg.id and reaction.emoji == startEmoji and user.id !=  \
    __client.user.id:
        await game.AddPlayer(user)
    
    if game and game.ready and game.voteMsg and         \
    reaction.message.id == game.voteMsg.id and user.id in         \
    game.players:
        await game.AddVote(reaction.emoji)

            
@__client.event
async def on_reaction_remove(reaction, user):
    global __game
    game = __game
    if game and game.startMsg and reaction.message.id == game.startMsg.id and  \
    reaction.emoji == startEmoji and user.id != __client.user.id:
        game.RemovePlayer(user.name)
    
    if game and game.ready and game.voteMsg and reaction.message.id ==         \
    game.voteMsg.id and user.id in game.players:
        game.RemoveVote(reaction.emoji)


logging.info('Bot is running.')
__client.run(os.environ['AVALON_DISCORD_TOKEN'])
