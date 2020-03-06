import random
import Agents

NUM_CARD = 13


class GameState:
    def __init__(self, num_players):
        # Number of players
        self.numPlayers = num_players
        # List of tuple of cards. Each tuple represents a round.
        # Let c_x_y be the card played by the player x at round y,
        # then the cardHistory of a 3-player game after the second
        # round is
        #       [(c_0_1, c_1_1, c2_1), (c_0_2, c_1_2, c_2_2)]
        self.cardHistory = []
        # List of prize cards. The list contains prize cards
        # that are *CLAIMED* by some player. If a tie happens, the
        # prize card is not added for now, but will be added in
        # the correct order when a winner appears in the later rounds.
        # Let p_x be the prize card of round x.
        #       [(p_1, p_2, p_3)]
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
    stat = {}

    def __init__(self, num_players, agents):
        self.numPlayers = num_players
        self.gameState = GameState(num_players)
        self.agents = agents
        self.prizes = list(range(1, NUM_CARD + 1))
        self.cardBankSets = [set() for i in range(num_players)]  # used to detect if a player played a duplicate
        self.scores = [0 for i in range(num_players)]
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
        round_num = 0
        while round_num < NUM_CARD:
            cur_prize = self.prizes[round_num]
            cards = self.play_round(self.gameState, cur_prize, leftover)
            leftover.append(cur_prize)
            self.gameState.add_card_history(tuple(cards))
            round_num += 1
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
                # tie, so we send the signal to the agents
                for i, a in enumerate(self.agents):
                    self.agents[i].post_res(False, True, cards, leftover)
                continue

            # This section updates the stat
            if self.agents[maxi].__class__.__name__ + str(maxi) not in DefaultGame.stat:
                DefaultGame.stat[self.agents[maxi].__class__.__name__ + str(maxi)] = {}
                DefaultGame.stat[self.agents[maxi].__class__.__name__ + str(maxi)][maxc] = sum(leftover)
            else:
                DefaultGame.stat[self.agents[maxi].__class__.__name__ + str(maxi)][maxc] = sum(leftover) \
                    if maxc not in DefaultGame.stat[self.agents[maxi].__class__.__name__ + str(maxi)] \
                    else DefaultGame.stat[self.agents[maxi].__class__.__name__ + str(maxi)][maxc] + sum(leftover)
            # End section

            # This section sends the result of the round to the agents
            # for each update if the agent want to do additional calculation
            for i, a in enumerate(self.agents):
                if i == maxi:
                    a.post_res(True, False, cards, leftover)
                else:
                    a.post_res(False, False, cards, leftover)
            # End section

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


def play_game_and_print_result(game_ctor, agent_ctor, num_players, round_num):
    result = {i: 0.0 for i in range(num_players)}
    result[-1] = 0.0
    for i in range(round_num):
        agent_list = []
        for j in range(num_players):
            agent_list.append(agent_ctor[j](j, num_players))
        game = game_ctor(num_players, agent_list)
        game.play()
        result[game.get_result()] += 1.0
    print(game_ctor.stat)
    print_result(result)

def play_game_and_get_result(game_ctor, agent_ctor, num_players, round_num):
    result = {i: 0.0 for i in range(num_players)}
    result[-1] = 0.0
    for i in range(round_num):
        agent_list = []
        for j in range(num_players):
            agent_list.append(agent_ctor[j](j, num_players))
        game = game_ctor(num_players, agent_list)
        game.play()
        result[game.get_result()] += 1.0
    total = sum(result.values())
    for k, v in result.items():
        result[k] = v / total
    return result


# play_game_and_print_result(DefaultGame, [Agents.CounterAgent, Agents.MatchAgent], 2, 10000)
# play_game_and_print_result(DefaultGame, [Agents.RandomAgent, Agents.RandomAgent, Agents.RandomAgent], 3, 10000)
# play_game_and_print_result(DefaultGame, [Agents.RandomAgent, Agents.BracketAgent], 2, 10000)

allAgents = [Agents.BracketAgent, Agents.CounterAgent, Agents.Heu1Agent,
              Agents.Heu2Agent, Agents.Heu2AgentAgr, Agents.Heu2AgentCon,
              Agents.HigheshHandAgent, Agents.MatchAgent, Agents.RandomAgent,
              Agents.OneUpAgentCon, Agents.OneUpAgentAgr, Agents.KinglessAgent]
# allAgents = [Agents.BracketAgent, Agents.CounterAgent]

outStr = "\t"
outStrTie = "\n\t"
print("Default game with 2 players (name in column is the agent name of the player)")
for pi, pa in enumerate(allAgents):
    outStr += pa.__qualname__ + "\t"
    outStrTie += pa.__qualname__ + "\t"
print(outStr)
outStrTie += "\n"
for pi, pa in enumerate(allAgents):
    outStr = pa.__qualname__ + "\t"
    outStrTie += pa.__qualname__ + "\t"
    for oi, oa in enumerate(allAgents):
        result = play_game_and_get_result(DefaultGame, [pa, oa], 2, 1000)
        outStr += str(result[0]) + "\t"
        outStrTie += str(result[-1]) + "\t"
    print(outStr)
    outStrTie += "\n"

print(outStrTie)
