import random
from utils import *
from collections import defaultdict
from resources import Resource, pip_dict, all_resources
from errors import BuildError, UpgradeError, TooCloseError, BrokenRoadError

""" Notes on this file's design:
* All references in Road, Colony, and Hex to each other are *ids*
* All references in Board are *pointers* (actual objects)
* This is to make copying all of these objects in the pos easier and less time-consuming
* self.owner is ALSO an id, with -1 meaning nobody owns it
* Additionally, none of these objects store pos data for the above reason
* All functions have arguments (self, pos, player_id, ...) - note player_id and not player
"""

class Road:
    def __init__(self, id):
        self.id = id
        self.owner = -1 # nobody owns this
        self.colonies = []
    
    def add_colonies(self, colonies):
        self.colonies.extend(colonies)

    def check_validity(self, pos, player_id):
        if self.owner != -1:
            raise BuildError(self.id, player_id, self.owner, "road")
        if self.id not in pos.players[player_id].possible_roads(pos):
            raise BrokenRoadError(self.id, player_id)

    def initial_build(self, pos, player_id, settlement, road_id):
        # road must be next to the initial settlement and unowned
        if road_id not in pos.get_colony(settlement).roads:
            raise NotConnectedError(road_id, self.id)
        self.owner = player_id

    def build(self, pos, player):
        self.check_validity(pos, player)
        self.owner = player

class Colony:
    def __init__(self, id):
        self.id = id
        self.owner = -1
        self.roads = []
        self.hexes = []
        self.city = False
        self.harbor = None
        self.harbor_resource = None
    
    def add_roads(self, *roads):
        self.roads.extend(roads)

    def add_hexes(self, *hexes):
        self.hexes.extend(hexes)

    def add_harbor(self, harbor, resource):
        self.harbor = harbor
        self.harbor_resource = resource

    def check_proximity(self, pos):
        for road in pos.get_roads(self.roads):
            for col in pos.get_colonies(road.colonies):
                if col.owner != -1 and col.id != self.id:
                    return False
        return True

    def check_validity(self, pos, player_id):
        if self.owner != -1:
            raise BuildError(self.id, player_id, self.owner, "settlement")
        connect = False
        for road in pos.get_roads(self.roads):
            if road.owner == player_id:
                connect = True
        if not connect:
            raise NotConnectedError(self.id, player_id)
        if not self.check_proximity(pos):
            raise TooCloseError(self.id, player_id)

    def check_upgrade_validity(self, player_id):
        if self.owner != -1 and self.owner != player_id:
            raise BuildError(self.id, player_id, self.owner, "city")
        elif self.city:
            raise UpgradeError(self.id, player_id)

    def initial_build(self, pos, player_id):
        if not self.check_proximity(pos):
            raise TooCloseError(id, player_id)
        self.owner = player_id

    def build(self, pos, player):
        self.check_validity(pos, player)
        self.owner = player

    def upgrade(self, pos, player):
        self.check_upgrade_validity(player)
        self.city = True

    def get_resources(self, pos):
        return [pos.get_hex(h).resource for h in self.hexes if pos.get_hex(h).resource != Resource.DESERT]

    def count_pips(self, pos):
        return sum([pip_dict[pos.get_hex(h).number] for h in self.hexes if pos.get_hex(h).resource != Resource.DESERT])

class Hex:
    def __init__(self, id, resource, number):
        self.id = id
        self.resource = resource
        self.number = number
        self.colonies = []

    def add_colonies(self, colonies):
        self.colonies.extend(colonies)

    def get_resources(self, pos):
        resources = defaultdict(list)

        if self.resource == Resource.DESERT:
            return resources

        for col in pos.get_colonies(self.colonies):
            if col.owner != -1:
                resources[col.owner].append(self.resource)
                if col.city:
                    resources[col.owner].append(self.resource)
        return resources

    def get_players(self, pos):
        players = set()
        for col in pos.get_colonies(self.colonies):
            if col.owner != -1:
                players.add(col.owner)
        return players

class Harbor:
    def __init__(self, id, resource):
        self.id = id
        self.colonies = []
        self.resource = resource
        # Resource.DESERT is a stand-in for 3:1 harbors

    def add_colonies(self, colonies):
        self.colonies.extend(colonies)

class Board:
    def __init__(self):
        self.hexes = self.init_hexes()
        self.colonies = []
        self.roads = []
        self.harbors = []
        self.init_colonies()
        self.init_roads()
        self.init_harbors()

    def create_colony(self, *hexes):
        col = Colony(len(self.colonies))
        self.colonies.append(col)
        col.add_hexes(*hexes)
        hexes = [self.hexes[h] for h in hexes]
        for h in hexes:
            h.add_colonies([col.id])

    def create_road(self, *colonies):
        road = Road(len(self.roads))
        self.roads.append(road)
        road.add_colonies(colonies)
        colonies = [self.colonies[c] for c in colonies]
        for c in colonies:
            c.add_roads(road.id)

    def create_harbor(self, colonies, resource):
        harbor = Harbor(len(self.harbors), resource)
        harbor.add_colonies(colonies)
        for c in colonies:
            self.colonies[c].add_harbor(harbor.id, resource)

    def init_hexes(self):
        dice_values = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        resource_values = [
            (Resource.WOOD, 4),
            (Resource.SHEEP, 4),
            (Resource.WHEAT, 4),
            (Resource.STONE, 3),
            (Resource.BRICK, 3),
        ]
        resource_values = counter_to_list(resource_values)
        random.shuffle(dice_values)
        random.shuffle(resource_values)

        # place the desert in the end of the ID list, which represents the middle of the board
        dice_values.append(7)
        resource_values.append(Resource.DESERT)

        return [Hex(i, resource_values[i], dice_values[i]) for i in range(19)]

    def init_colonies(self):
        # Outer Ring
        for i in range(0, 12, 2):
            self.create_colony(i)
            self.create_colony(i)
            self.create_colony(i, i+1)
            self.create_colony(i+1)
            if i == 10:
                break
            self.create_colony(i+1, i+2)
        self.create_colony(11, 0)

        # Inner Ring
        j = 0
        for i in range(12, 17):
            self.create_colony(i, i+1, j)
            self.create_colony(j+1, i, i+1)
            self.create_colony(i+1, i+2, j+1)
        self.create_colony(10, 11, 17)
        self.create_colony(11, 17, 12)
        self.create_colony(11, 0, 12)

        # Middle Tile
        for i in range(12, 17):
            self.create_colony(18, i, i+1)
        self.create_colony(18, 12, 17)

    def init_roads(self):
        # Outer Ring
        for i in range(0, 29):
            self.create_road(i, i+1)
        self.create_road(29, 0)

        # Outer Ring to Inner Ring
        j = 2
        for i in range(30, 45, 3):
            self.create_road(j, i+1)
            self.create_road(j+2, i+3)
            j += 5
        self.create_road(27, 46)
        self.create_road(29, 30)

        # Inner Ring
        for i in range(30, 47):
            self.create_road(i, i+1)
        self.create_road(30, 47)

        # Inner Ring to Middle Tile
        j = 31
        for i in range(48, 54):
            self.create_road(i, j+1)
            j += 3

        # Middle Tile
        for i in range(48, 53):
            self.create_road(i, i+1)
        self.create_road(53, 48)

    def init_harbors(self):
        harbor_pairs = [
            [0, 1],
            [3, 4],
            [7, 8],
            [10, 11],
            [13, 14],
            [17, 18],
            [20, 21],
            [23, 24],
            [27, 28],
        ]

        resources = all_resources.copy()
        resources.extend([Resource.DESERT, Resource.DESERT, Resource.DESERT, Resource.DESERT])
        random.shuffle(resources)
        for p in range(len(harbor_pairs)):
            self.create_harbor(harbor_pairs[p], resources[p])
