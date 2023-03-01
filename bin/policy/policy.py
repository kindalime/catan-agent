from abc import ABCMeta, abstractmethod

class CatanPolicy(metaclass=ABCMeta):
    # All of these functions have a pos and a player (not player_id!) argument
    
    @abstractmethod
    def init_settle(self, pos, player):
        pass

    @abstractmethod
    def choose_discard(self, pos, player):
        pass

    @abstractmethod
    def choose_robber(self, pos, player):
        pass

    @abstractmethod
    def take_turn(self, pos, player):
        pass
