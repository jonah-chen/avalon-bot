import logging
import random

ppQuest = {
    1:  (1,1,1,1,1),
    5:  (2,3,2,3,3),
    6:  (2,3,4,3,4),
    7:  (2,3,3,4,4),
    8:  (3,4,4,5,5),
    9:  (3,4,4,5,5),
    10: (3,4,4,5,5)
}

maxAttempts = 5

roles = ('merlin', 'mordred', 'good', 'good', 'evil', 'good', 'evil', 'good', 'good', 'evil')
good = (True, False, True, True, False, True, False, True, True, False)
evil = (not a for a in good)

acceptEmoji = '\u2705'
rejectEmoji = '\u274C'

class Game:
    def __init__(self, nplayers, channel):
        self.nplayers = nplayers
        self.voteAcceptRequired = (nplayers + 1) // 2
        self.voteRejectRequired = nplayers // 2
        self.players = []
        self.nameMap = dict()
        self.pmMap = dict()
        self.channel = channel

        self.curPlayer = random.randint(0, nplayers-1)
        self.ppQuest = ppQuest[nplayers]
        self.results = []
        self.voteMsg = None

        self.ready = False
        self.over = False
        logging.info('Game created.')

    def _IName(self, idx):
        return self.nameMap[self.players[idx]]
    def _IPM(self, idx):
        return self.pmMap[self.players[idx]]
    
    @property
    def cID(self):
        return self.players[self.curPlayer]
    @property
    def __cName(self):
        return self.nameMap[self.players[self.curPlayer]]
    @property
    def __cPM(self):
        return self.pmMap[self.players[self.curPlayer]]
    @property
    def __questSize(self):
        self.ppQuest[len(self.results)]
    @property
    def merlin(self):
        for id, r in zip(self.players, roles):
            if r == 'merlin':
                return id
        return None
    
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
                await self._Start()
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
        await self._Turn1()

    def _AdvanceTurn(self):
        self.curPlayer = (self.curPlayer + 1) % self.nplayers
    
    async def _Turn1(self):
        await self.Broadcast(f'It is {self.__cName}\'s turn. Please select ' + 
                        f'{self.__questSize} players for the next quest.')
    
    async def SelectPlayers(self, players):
        if len(players) != self.__questSize:
            await self.Broadcast(f'You must select {self.__questSize} players' + 
                        f' for this quest, but you selected {len(players)}.')
            return
        self.voteAccept = 0
        self.voteReject = 0
        self.voteMsg = await self.Broadcast(' '.join(map(lambda p:p.mention, 
            players)) + f'are selected for quest {len(self.results)+1}. ' + 
            f'Please vote {acceptEmoji} to accept or {rejectEmoji} to reject.' +
            f' {self.voteAcceptRequired} accepts are required for the quest ' + 
            f'to begin.')
        self.selectPlayers = players
    
    async def AddVote(self, emoji):
        if emoji == acceptEmoji:
            self.voteAccept += 1
        elif emoji == rejectEmoji:
            self.voteReject += 1

        if self.voteAccept >= self.voteAcceptRequired:
            await self._Turn3()
        if self.voteReject >= self.voteRejectRequired:
            await self.Broadcast('The quest has been rejected by a vote of ' +
                f'{self.voteAccept} - {self.voteReject}.')
            self._AdvanceTurn()
            await self._Turn1()

    async def RemoveVote(self, emoji):
        if emoji == acceptEmoji:
            self.voteAccept -= 1
        if emoji == rejectEmoji:
            self.voteReject -= 1

    async def _Turn3(self):
        await self.Broadcast('The quest has been accepted by a vote of ' +
            f'{self.voteAccept} - {self.voteReject}.')
        await self.Broadcast('The quest has begun. ' + 
            ' '.join(map(lambda p:p.mention, self.selectPlayers)) +
            ' please check your PMs and vote to succeed or fail the quest.')

        self.succeeds = 0
        
        for p in self.selectPlayers:
            # find the position of p based on its id
            idx = self.players.index(p.id)
            if good[idx]:
                self.succeeds += 1
                continue # good players must succeed
            failMsg = await self.Pm(p.id, 'Please vote to succeed or fail the quest.')
            channel = self.pmMap[p.id]
            # get next message from channel
            for attempt in range(maxAttempts):
                msg = await channel.history(limit=1, after=failMsg, oldest_first=False).flatten()
                msg = msg[0].content.lower()
                if msg == 'succeed':
                    self.succeeds += 1
                    break
                if msg == 'fail':
                    break
                
                attemptsLeft = maxAttempts - attempt - 1
                await self.Pm(p.id, 'Please vote to succeed or fail the quest' +
                    f' using "succeed" or "fail". You have {attemptsLeft} ' + 
                    'attempts left otherwise you will vote fail by default.')

        self.results.append((self.succeeds == self.__questSize, self.succeeds))
        if self.results[-1][0]:
            await self.Broadcast('The quest has succeeded!')
        else:
            await self.Broadcast('The quest has failed due to ' 
                f'{self.__questSize - self.succeeds} players voting fail.')
        
        if sum(map(lambda x:x[0], self.results)) >= 3:
            await self.Broadcast('The game has been won by good side. The ' +
                'evil side has one more chance to guess who is merlin!')
            self.over = True
            return
        if sum(map(lambda x:not x[0], self.results)) >= 3:
            await self.Broadcast('The game has been won by evil side. The ' + 
                'game is over. Please start a new game.')
            self = None
            return
    
        self._AdvanceTurn()
        self._Turn1()
