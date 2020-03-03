import random


class Agent:
    # you don't have to use all the attributes,
    # but most of them are listed here
    def __init__(self, player_idx, num_players=2):
        self.current_hand = None
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