from nextcord import Intents
from nextcord.ext.commands import Bot
import os

__intents = Intents.default()
__intents.message_content = True
__client = Bot(command_prefix='!', intents=__intents)

def __start(ctx,):





__client.run(os.environ['AVALON_DISCORD_TOKEN'])
