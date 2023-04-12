import random
from utils import *
from errors import CannotStealError

class Robber:
    def __init__(self):
        self.location = 18 # starts in the desert

    def get_resources(self, pos):
        return pos.get_hex(self.location).get_resources(pos)
