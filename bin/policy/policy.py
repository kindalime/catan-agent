from abc import ABCMeta, abstractmethod

class CatanPolicy(metaclass=ABCMeta):
    def __init__(self, catan, player):
        self.catan = catan
        self.player = player

    # All of these functions have a pos and a player (not player_id!) argument

    @abstractmethod
    def init_settle(self, pos):
        pass

    @abstractmethod
    def choose_discard(self, pos):
        # Return the resources to discard
        pass

    @abstractmethod
    def choose_robber(self, pos):
        pass

    @abstractmethod
    def take_turn(self, pos):
        pass
