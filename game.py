import random
import Agents

NUM_CARD = 13

class GameState:
    def __init__(self, numPlayers):
        self.numPlayers = numPlayers
        # [(xa, xb, xc), (ya, yb, yc), (9, 9, 5), (4, 5, 6)]
        self.cardHistory = []
        # [3, 7, 9, 4]
        self.prizeHistory = []
        self.scores = [0 for i in range(numPlayers)]

    def add_card_history(self, cards):
        self.cardHistory.append(cards)

    def add_prize_histories(self, prize):
        self.prizeHistory.extend(prize)

class Game:
    def play(self):
        raise NotImplementedError

    def get_result(self):
        return -1

class DefaultGame(Game):
    def __init__(self, numPlayers, agents):
        self.numPlayers = numPlayers
        self.gameState = GameState(numPlayers)
        self.agents = agents # The first element is the player's agent
        self.prizes = list(range(1, NUM_CARD + 1))
        self.idx = 0
        self.leftover = []
        self.cardBankSets = [set() for i in range(numPlayers)]
        random.shuffle(self.prizes)

    # def restart(self):
    #     self.gameState = GameState(self.numPlayers)
    #     self.prizes = list(range(1, NUM_CARD + 1))
    #     self.idx = 0
    #     self.leftover = []
    #     self.cardBankSets = [set() for i in range(self.numPlayers)]
    #     random.shuffle(self.prizes)

    def play(self):
        while (not self.is_finished()):
            cards = []
            curPrize = self.prizes[self.idx]
            for i in range(self.numPlayers):
                card = self.agents[i].next_move(self.gameState, curPrize, self.leftover)
                if card in self.cardBankSets[i]:
                    raise ("invalid card played by player " + str(i + 1))
                self.cardBankSets[i].add(card)
                cards.append(card)
            self.leftover.append(curPrize)
            self.gameState.add_card_history(tuple(cards))
            self.idx += 1
            maxi = -1
            maxc = -1
            for i, c in enumerate(cards):
                if maxc < c:
                    maxc = c
                    maxi = i
                if maxc == c:
                    # tie
                    self.leftover.append(curPrize)
                    continue
            self.gameState.scores[maxi] += sum(self.leftover)
            self.gameState.add_prize_histories(self.leftover)
            self.leftover = []

    def print_result(self):
        maxs = max(self.gameState.scores)
        for i, s in enumerate(self.gameState.scores):
            if s == maxs:
                print("player " + str(i + 1) + " won")

    def get_result(self):
        maxs = max(self.gameState.scores)
        idx = -1
        for i, s in enumerate(self.gameState.scores):
            if s == maxs:
                if idx != -1:
                    return -1
                idx = i
        return idx

    idx = -1
    def is_finished(self):
        return self.idx >= NUM_CARD

def print_result(dict):
    total = 0.0
    for v in dict.values():
        total += v
    for k, v in dict.items():
        if k == -1:
            print("tie rate: " + str(v / total))
        else:
            print("player " + str(k + 1) + " win rate: " + str(v / total))

result = {i : 0.0 for i in range(2)}
result[-1] = 0.0
for i in range(1000000):
    game = DefaultGame(2, [Agents.RandomAgent(0, 2), Agents.RandomAgent(1, 2)])
    game.play()
    result[game.get_result()] += 1.0
print_result(result)

result = {i : 0.0 for i in range(3)}
result[-1] = 0.0
for i in range(1000000):
    game = DefaultGame(3, [Agents.RandomAgent(0, 3), Agents.RandomAgent(1, 3), Agents.RandomAgent(2, 3)])
    game.play()
    result[game.get_result()] += 1.0
print_result(result)