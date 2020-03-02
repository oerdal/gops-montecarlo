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

def play_game_and_print_result(gameCtor, AgentCtor, numPlayers, round):
    result = {i: 0.0 for i in range(numPlayers)}
    result[-1] = 0.0
    for i in range(round):
        agentLst = []
        for j in range(numPlayers):
            agentLst.append(AgentCtor[j](i, numPlayers))
        game = gameCtor(numPlayers, agentLst)
        game.play()
        result[game.get_result()] += 1.0
    print_result(result)


play_game_and_print_result(DefaultGame, [Agents.RandomAgent, Agents.RandomAgent], 2, 10000)
play_game_and_print_result(DefaultGame, [Agents.RandomAgent, Agents.RandomAgent, Agents.RandomAgent], 3, 10000)
play_game_and_print_result(DefaultGame, [Agents.RandomAgent, Agents.BracketAgent], 2, 10000)