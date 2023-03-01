from abc import ABCMeta, abstractmethod

class BaselinePolicy(CatanPolicy):
    # All of these functions have a pos and a player (not player_id!) argument
    
    def init_settle(self, pos, player):
        pass

    def choose_discard(self, pos, player):
        pass

    def choose_robber(self, pos, player):
        pass

    def take_turn(self, pos, player):
        pass
