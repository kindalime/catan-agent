import random
from utils import *
from errors import CannotStealError

class Robber:
    def __init__(self):
        self.location = 18 # starts in the desert

    def get_resources(self, pos):
        return pos.get_hex(self.location).get_resources()

    def move_robber(self, player_id, victim_id, location):
        if victim_id == player_id or victim_id not in location.get_player_ids():
            raise CannotStealError(player_id, victim_id, location.id)
        self.location = location.id

        # steal a resource
        resources = counter_to_list(self.player_ids[victim_id].resources)
        if resources:
            stolen = random.choice(resources)
            self.player_ids[player_id].resources.update([stolen])
            self.player_ids[victim_id].resources.subtract([stolen])
