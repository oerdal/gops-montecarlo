import random
import math


class Agent:
    # you don't have to use all the attributes,
    # but most of them are listed here
    def __init__(self, player_idx, num_players=2):
        self.current_hand = list(range(1, 14))
        self.idx = player_idx
        self.num_players = num_players
        self.score = 0

    # Given the bid on the table, return the card that the agent plays
    # Prize is a number:
    # Ace = 1, 2 = 2, ... J = 11, A = 12 and K = 13
    # game state is an object who's defined in game.py
    # leftover_prize is a list of prize, consisting of the prizes from previous ties
    # it will be empty if the last round was not a tie
    def next_move(self, game_state, prize, leftover_prize=None):
        return 0

    # did_win: did the last move win?
    # cards_played: a list of cards played last round, where the agent played cards_played[self.player_idx]
    # prize: what was the prize that was won? (this could be greater than 13 due to ties)
    def post_res(self, did_win, did_tie, cards_played, prize):
        pass


# RandomAgent just play random card every round

class RandomAgent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        # do additional initialization here
        self.plays = [i for i in range(1, 14)]
        random.shuffle(self.plays)

    def next_move(self, game_state, prize, leftover_prize=None):
        card = self.plays.pop()
        return card


# This agent divides the cards into bracket
# and tries to win the lower 2 cards in the bracket
class BracketAgent(Agent):
    # we don't need any additional init
    def next_move(self, game_state, prize, leftover_prize=None):
        self.current_hand = {
            1: 2,
            2: 3,
            3: 1,
            4: 5,
            5: 6,
            6: 4,
            7: 8,
            8: 9,
            9: 7,
            10: 11,
            11: 12,
            12: 10,
            13: 13
        }
        return self.current_hand[prize]


# This agent always match the prize
class MatchAgent(Agent):
    def next_move(self, game_state, prize, leftover_prize=None):
        return prize


# This agent always play its highest hand
class HigheshHandAgent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.current_hand = list(range(1, 14))

    def next_move(self, game_state, prize, leftover_prize=None):
        return self.current_hand.pop()

# class

# what would be a good strat?
# when I could win with this hand, play the highest hand.
# when I couldn't,
# [0.5402, 1.1563, 1.7082, 2.3073, 2.9388, 3.5464, 3.9714, 4.763, 5.2427, 5.8177, 6.3517, 6.9335]
# these are the expected amount of prize you can win
# class QJKAgent(Agent):
#     def __init__(self, player_idx, num_players=2):

# for the first three rounds, play random cards from the lower 5
# then for the next three rounds, play random cards from the lower 9
# then for the rest 7 rounds, play the highest hand
class Heu1Agent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.first_three = random.sample(range(1, 6), 3)
        for i in range(3):
            self.current_hand.remove(self.first_three[i])
        self.second_three = random.sample(self.current_hand[0:7], 3)
        for i in range(3):
            self.current_hand.remove(self.second_three[i])

    def next_move(self, game_state, prize, leftover_prize=None):
        if self.first_three:
            return self.first_three.pop()
        elif self.second_three:
            return self.second_three.pop()
        else:
            return self.current_hand.pop()

# for the first three < 8 rewards, play random cards from the lower 5
# for the next three < 11 rewards, play random cards from the lower 8
class Heu2Agent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.first_three = random.sample(range(1, 6), 3)
        for i in range(3):
            self.current_hand.remove(self.first_three[i])
        self.second_three = random.sample(self.current_hand[0:6], 3)
        for i in range(3):
            self.current_hand.remove(self.second_three[i])

    def next_move(self, game_state, prize, leftover_prize):
        if prize < 8 and self.first_three:
            return self.first_three.pop()
        elif prize < 11 and self.second_three:
            return self.second_three.pop()
        else:
            return self.current_hand.pop()


# Conservative heu2 variation
class Heu2AgentCon(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.first_three = random.sample(range(1, 6), 3)
        for i in range(3):
            self.current_hand.remove(self.first_three[i])
        self.second_three = random.sample(self.current_hand[0:6], 3)
        for i in range(3):
            self.current_hand.remove(self.second_three[i])

    def next_move(self, game_state, prize, leftover_prize):
        if prize < 8 and self.first_three:
            return self.first_three.pop()
        elif prize < 11 and self.second_three:
            return self.second_three.pop()
        else:
            need_to_win = 91 - self.score
            if (need_to_win * 2) // 7 <= prize <= (need_to_win * 5) // 7:
                return self.current_hand.pop()
            else:
                 return self.current_hand.pop(len(self.current_hand) // 2)

    def post_res(self, did_win, did_tie, cards_played, prize):
        if did_win:
            self.score += sum(prize)


# Aggressive heu2 variation
class Heu2AgentAgr(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.first_three = random.sample(range(1, 6), 3)
        for i in range(3):
            self.current_hand.remove(self.first_three[i])
        self.second_three = random.sample(self.current_hand[0:6], 3)
        for i in range(3):
            self.current_hand.remove(self.second_three[i])
    def next_move(self, game_state, prize, leftover_prize):
        if prize < 8 and self.first_three:
            return self.first_three.pop()
        elif prize < 11 and self.second_three:
            return self.second_three.pop()
        else:
            need_to_win = 91 - self.score
            if (need_to_win * 2) // 7 <= prize <= (need_to_win * 5) // 7:
                return self.current_hand.pop(len(self.current_hand) // 2)
            else:
                 return self.current_hand.pop()

    def post_res(self, did_win, did_tie, cards_played, prize):
        if did_win:
            self.score += sum(prize)

# for the first three rounds, play some mid-range card
# then, classify the strats into three categories
# matching
# +n
# others
class CounterAgent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.first_three = random.sample(self.current_hand[3:9], 3)
        for i in range(3):
            self.current_hand.remove(self.first_three[i])
        self.opponent_category = None
        self.oppo_hist = []

    def next_move(self, game_state, prize, leftover_prize=None):
        if self.first_three:
            return self.first_three.pop()
        else:
            if self.opponent_category == None:
                self.determine_category(game_state, leftover_prize)
            if self.opponent_category == 'm':
                # return smallest available greater than prize + 2
                return self.smallest_available(prize+2)
            elif self.opponent_category == 'p':
                # return smallest available greater than prize + 3
                return self.smallest_available(prize+3)
            else:
                # return like matching
                return self.smallest_available(prize)

    def smallest_available(self, score):
        if score in self.current_hand:
            self.current_hand.remove(score)
            return score
        elif score > 13:
            return self.current_hand.pop(0)
        else:
            return self.smallest_available(score + 1)

    def determine_category(self, gs, leftover):
        temp = []
        temp.extend(gs.prizeHistory)
        temp.extend(leftover)
        diff = [abs(self.oppo_hist[i] - temp[i]) for i in range(3)]
        if diff[0]**2 + diff[1]**2 + diff[2]**2 <= 10:
            self.opponent_category = 'm'
        else:
            md = sum(diff) / 3
            if math.sqrt((diff[0] - md)**2 + (diff[1] - md)**2 + (diff[2] - md)**2) <= 5:
                self.opponent_category = 'p'
            else:
                self.opponent_category = 'n'

    def post_res(self, did_win, did_tie, cards_played, prize):
        self.oppo_hist.append(cards_played[1 if self.idx == 0 else 0])

# narrowly beat out opponent
class OneUpAgentCon(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.current_hand = list(range(1, 14))

    def next_move(self, game_state, prize, leftover_prize=None):
        return self.one_up(prize)

    # return index of card to play
    def one_up(self, score):
        if score + 1 in self.current_hand:
            self.current_hand.remove(score + 1)
            return score + 1
        elif score > 13:
            return self.current_hand.pop(0)
        else:
            return self.one_up(score + 1)

class OneUpAgentAgr(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.current_hand = list(range(1, 14))

    def next_move(self, game_state, prize, leftover_prize=None):
        print(self.current_hand)
        return self.one_up(prize)

    # return index of card to play
    def one_up(self, score):
        if score + 1 in self.current_hand:
            self.current_hand.remove(score + 1)
            return score + 1
        elif score > 13:
            return self.current_hand.pop()
        else:
            return self.one_up(score + 1)            

# This agent gives up the king to win the other top cards
# class KinglessAgent(Agent):
    
