import logging
import random

ppQuest = {
    5:  (2,3,2,3,3),
    6:  (2,3,4,3,4),
    7:  (2,3,3,4,4),
    8:  (3,4,4,5,5),
    9:  (3,4,4,5,5),
    10: (3,4,4,5,5)
}

roles = ('merlin', 'mordred', 'good', 'good', 'evil', 'good', 'evil', 'good', 'good', 'evil')
good = (True, False, True, True, False, True, False, True, True, False)
evil = (not a for a in good)


class Game:
    def __init__(self, nplayers, channel):
        self.nplayers = nplayers
        self.players = []
        self.nameMap = dict()
        self.pmMap = dict()
        self.channel = channel
        self.curPlayer = random.randint(0, nplayers-1)
        self.activeMsg = None

        self.ready = False
        logging.info('Game created.')

    def _AdvanceTurn(self):
        self.curPlayer = (self.curPlayer + 1) % self.nplayers
    
    async def PmBroadcast(self, msg):
        for pm in self.pmMap.values():
            await pm.send(msg)
    async def Pm(self, id, msg):
        if id in self.pmMap:
            await self.pmMap[id].send(msg)
        else:
            logging.warn(f'{id} tried to send a PM, but they were not in the game.')
    async def Broadcast(self, msg):
        await self.channel.send(msg)

    async def AddPlayer(self, user):
        if len(self.players) < self.nplayers:
            channel = user.dm_channel
            if not channel:  # If user has never talked to Eve
                channel = await user.create_dm()
            self.pmMap[user.id] = channel
            self.nameMap[user.id] = user.name
            self.players.append(user.id)

            logging.info(f'{user.name} joined the game.')
            if len(self.players) == self.nplayers:
                self.ready = True
                self._Start()
                return True
        else:
            logging.warn(f'{user.name} tried to join the game, but it was full.')
        return False

    def RemovePlayer(self, id):
        if not self.game.ready and id in self.players:
            self.players.remove(id)
    
    async def _Start(self):
        logging.info('Game started.')
        await self.Broadcast('The game has started, please check your PMs to see your role.')
        random.shuffle(self.players)
        for e, r, id in zip(evil, roles, self.players):
            await self.Pm(id, f'Your role is {r}.')            
            if r == 'merlin':
                for r, _id in zip(roles, self.players):
                    if r == 'evil':
                        await self.Pm(_id, f'{self.nameMap[_id]} is evil.')
            elif e:
                for e, _id in zip(evil, self.players):
                    if e and id != _id:
                        await self.Pm(id, f'{self.nameMap[_id]} is also evil.')
