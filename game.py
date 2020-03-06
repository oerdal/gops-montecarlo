import random
import Agents
import numpy as np
import matplotlib.pyplot as plt

NUM_CARD = 13
# a list of all agents
allAgents = [Agents.BracketAgent, Agents.CounterAgent, Agents.Heu1Agent,
              Agents.Heu2Agent, Agents.Heu2AgentAgr, Agents.Heu2AgentCon,
              Agents.HigheshHandAgent, Agents.MatchAgent, Agents.RandomAgent,
              Agents.OneUpAgentCon, Agents.OneUpAgentAgr, Agents.KinglessAgent]
# strategies for convergence analysis
some_strategies = [Agents.KinglessAgent, Agents.MatchAgent, Agents.BracketAgent, Agents.RandomAgent]

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

    # append a tuple of card to the card history
    def add_card_history(self, cards):
        self.cardHistory.append(cards)

    # append a list of prize cards to the prize history
    def add_prize_histories(self, prize):
        self.prizeHistory.extend(prize)

# Base class of Game
class Game:
    # play one round of the game
    def play(self):
        raise NotImplementedError

    # get the index of the player with the highest score
    def get_winner(self):
        return -1


class DefaultGame(Game):
    # key is agent, value is the average rewards won by playing each card
    average_cards_won = {i.__name__:np.zeros(14) for i in allAgents}
    # key is agent, value is the number of rewards won
    claimed_bid = {i.__name__:np.zeros(14) for i in allAgents}
    # key is agent, value is its winning hand
    winning_hand = {i.__name__:np.zeros(14) for i in allAgents}
    winning_times = {i.__name__:0 for i in allAgents}

    def __init__(self, num_players, agents):
        self.numPlayers = num_players # number of players
        self.gameState = GameState(num_players) # current game state
        self.agents = agents # list of game agents representing each player
        self.prizes = list(range(1, NUM_CARD + 1)) # the prize card deck
        self.cardBankSets = [set() for i in range(num_players)]  # used to detect if a player played a duplicate
        self.scores = [0 for i in range(num_players)] # score of each player (agent)
        random.shuffle(self.prizes) # shuffle the prize card deck

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
        agents_reward = {i.__class__.__name__:[] for i in self.agents}
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
            # print(DefaultGame.average_cards_won)
            DefaultGame.average_cards_won[self.agents[maxi].__class__.__name__][maxc] += sum(leftover)
            for i in leftover:
                DefaultGame.claimed_bid[self.agents[maxi].__class__.__name__][i] += 1
            agents_reward[self.agents[maxi].__class__.__name__].extend(leftover)
            # End section
            # print(agents_reward)

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
        winner_idx = self.get_winner()
        winner_name = self.agents[winner_idx].__class__.__name__
        DefaultGame.winning_times[winner_name]+=1
        for r in agents_reward[winner_name]:
            DefaultGame.winning_hand[winner_name][r] += 1

    def get_winner(self):
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

def play_game_and_get_data(game_ctor, agent_ctor, num_players, round_num, if_print=False):
    result = {i: 0.0 for i in range(num_players)}
    result[-1] = 0.0
    win_rate = []
    total = 0
    for i in range(round_num):
        agent_list = []
        for j in range(num_players):
            agent_list.append(agent_ctor[j](j, num_players))
        game = game_ctor(num_players, agent_list)
        game.play()
        total += 1
        result[game.get_winner()] += 1.0
        win_rate.append(result[0] / total)
    for k, v in result.items():
        result[k] = v / total
    if if_print:
        print(game_ctor.stat)
        print_result(result)
    return result, win_rate

# play_game_and_get_data(DefaultGame, [Agents.CounterAgent, Agents.MatchAgent], 2, 10000, True)
# play_game_and_get_data(DefaultGame, [Agents.RandomAgent, Agents.RandomAgent, Agents.RandomAgent], 3, 10000, True)
# play_game_and_get_data(DefaultGame, [Agents.RandomAgent, Agents.BracketAgent], 2, 10000, True)

# win rate matrix
def generateResultMatrix(gameCtor, allAgents, numPlayers, round):
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
            result, win_rate = play_game_and_get_data(DefaultGame, [pa, oa], numPlayers, round)
            outStr += str(result[0]) + "\t"
            outStrTie += str(result[-1]) + "\t"
        print(outStr)
        outStrTie += "\n"
    print(outStrTie)

# convergence analysis
def plotAverateWinRates(times, round):
    plt.figure(0)
    win_rates = {}
    for pa in some_strategies:
        win_rates[pa.__qualname__] = {}
        for oa in some_strategies:
            win_rates[pa.__qualname__][oa.__qualname__] = {}
            for i in range(times):
                result, win_rate = play_game_and_get_data(DefaultGame, [pa, oa], 2, round)
                win_rates[pa.__qualname__][oa.__qualname__][i] = win_rate

    plt.style.use('seaborn-darkgrid')
    palette = plt.get_cmap('Set1')
    fig = plt.figure(figsize=(15, 15))
    x = list(range(round))
    for pi, pa in enumerate(some_strategies):
        for oi, oa in enumerate(some_strategies):
            for k in win_rates[pa.__qualname__][oa.__qualname__]:
                plt.subplot(len(some_strategies), len(some_strategies), pi * 4 + oi + 1)
                plt.plot(x, win_rates[pa.__qualname__][oa.__qualname__][k], marker='', linewidth=1, alpha=0.9, label=k)
                plt.title(pa.__qualname__ + " vs " + oa.__qualname__)
                plt.ylabel("Win Rate")
                plt.xlabel("Step")
    plt.legend(loc=0)

# game stats
def plotStats(dg):
    plt.figure(1)
    key = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    plt.style.use('seaborn-darkgrid')
    palette = plt.get_cmap('Set1')
    fig, axs = plt.subplots(4, 3, sharey=True)
    axs = axs.flatten()
    plt.xlim((1, 13))
    for i, ag in enumerate(allAgents):
        # print(dg.claimed_bid[ag.__name__])
        axs[i].bar(key, dg.claimed_bid[ag.__name__][1:] / 12000, label=ag.__name__)
        axs[i].title.set_text(ag.__name__)
    plt.savefig("prize_won.png")
    plt.show()

    fig, axs = plt.subplots(4, 3, sharey=True)
    axs = axs.flatten()
    plt.xlim((1, 13))
    for i, ag in enumerate(allAgents):
        axs[i].bar(key, dg.average_cards_won[ag.__name__][1:] / 12000, label = ag.__name__)
        axs[i].title.set_text(ag.__name__)
    plt.savefig("prize_won_by_each_card.png")
    plt.show()

    print(dg.winning_times)
    fig, axs = plt.subplots(4, 3, sharey=True)
    axs = axs.flatten()
    plt.xlim((1, 13))
    for i, ag in enumerate(allAgents):
        axs[i].bar(key, dg.winning_hand[ag.__name__][1:] / dg.winning_times[ag.__name__], label = ag.__name__)
        axs[i].title.set_text(ag.__name__)
    plt.savefig("avg_winning_hand.png")

generateResultMatrix(DefaultGame, allAgents, 2, 5000)
plotStats(DefaultGame)
plotAverateWinRates(5, 5000)
plt.show()