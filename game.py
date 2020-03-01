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
        self.cardBankSets = [set() for i in range(numPlayers)]
        self.scores = [0 for i in range(numPlayers)]
        random.shuffle(self.prizes)

    # def restart(self):
    #     self.gameState = GameState(self.numPlayers)
    #     self.prizes = list(range(1, NUM_CARD + 1))
    #     self.cardBankSets = [set() for i in range(self.numPlayers)]
    #     random.shuffle(self.prizes)
    def play_round(self, state, prize, leftover):
        cards = []
        for i in range(self.numPlayers):
            card = self.agents[i].next_move(state, prize, leftover)
            if card in self.cardBankSets[i]:
                raise ("invalid card played by player " + str(i + 1))
            self.cardBankSets[i].add(card)
            cards.append(card)
        return cards

    def play(self):
        leftover = []
        round = 0
        while (round < NUM_CARD):
            curPrize = self.prizes[round]
            cards = self.play_round(self.gameState, curPrize, leftover)
            leftover.append(curPrize)
            self.gameState.add_card_history(tuple(cards))
            round += 1
            maxi = -1
            maxc = max(cards)
            # find the highest card played
            for i, c in enumerate(cards):
                if maxc == c:
                    if maxi != -1:
                        # tie
                        maxi = -2
                        break
                    maxi = i
            if maxi == -2:
                continue
            self.scores[maxi] += sum(leftover)
            self.gameState.add_prize_histories(leftover)
            leftover = []

    # def print_result(self):
    #     maxs = max(self.scores)
    #     for i, s in enumerate(self.scores):
    #         if s == maxs:
    #             print("player " + str(i + 1) + " won")

    def get_result(self):
        maxs = max(self.scores)
        pidx = -1
        for i, s in enumerate(self.scores):
            if s == maxs:
                if pidx != -1:
                    return -1
                pidx = i
        return pidx

def print_result(dic):
    total = sum(dic.values())
    for k, v in dic.items():
        if k == -1:
            print("tie rate: " + str(v / total))
        else:
            print("player " + str(k + 1) + " win rate: " + str(v / total))

result = {i : 0.0 for i in range(2)}
result[-1] = 0.0
for i in range(1000):
    game = DefaultGame(2, [Agents.RandomAgent(0, 2), Agents.RandomAgent(1, 2)])
    game.play()
    result[game.get_result()] += 1.0
print_result(result)

result = {i : 0.0 for i in range(3)}
result[-1] = 0.0
for i in range(1000):
    game = DefaultGame(3, [Agents.RandomAgent(0, 3), Agents.RandomAgent(1, 3), Agents.RandomAgent(2, 3)])
    game.play()
    result[game.get_result()] += 1.0
print_result(result)