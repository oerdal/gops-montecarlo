import random


class Agent:
    def __init__(self, player_idx, num_players=2):
        self.current_hand = None
        self.idx = player_idx
        self.num_players = num_players
        self.score = 0

    # Given the bid on the table, return the card that the agent plays
    # Ace = 1, 2 = 2, ... J = 11, A = 12 and K = 13
    # leftover_prize is a list
    def next_move(self, game_state, prize, leftover_prize=None):
        return 0

    # return the score the player got
    def get_score(self):
        return self.score

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

class BracketAgent(Agent):
    # we don't need any additional init
    def next_move(self, game_state, prize, leftover_prize=None):
        plays = {
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
        return plays[prize]

class MatchAgent(Agent):
    def next_move(self, game_state, prize, leftover_prize=None):
        return prize

class HigheshHandAgent(Agent):
    def __init__(self, player_idx, num_players=2):
        super().__init__(player_idx, num_players)
        self.hand = list(range(1, 14))
    def next_move(self, game_state, prize, leftover_prize=None):
        return self.hand.pop()