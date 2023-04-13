from resources import *
from errors import *
from devcard import empty_deck, play_card
from utils import player_colors

class Player:
    def __init__(self, id):
        self.id = id
        self.roads = [] # ids
        self.colonies = [] # ids
        self.dice = {i: empty_resources() for i in range(2, 13)}
        self.resources = empty_resources()
        self.dev_cards = empty_deck()
        self.points = 0
        self.army = 0
        self.settlement_supply = 5
        self.city_supply = 4
        self.color = player_colors[self.id]

    def possible_init_settlements(self, pos):
        # loop through *all* settlements and get valid placements
        possible = []
        for col in pos.board.colonies:
            if col.owner == -1 and col.check_proximity(pos):
                possible.append(col.id)
        return possible

    def possible_init_roads(self, pos, settlement):
        return pos.get_colony(settlement).roads

    def possible_settlements(self, pos):
        # get all colonies this player has access to from roads
        colonies = []
        for road in pos.get_roads(self.roads):
            colonies.extend(road.colonies)
        colonies = set(colonies)

        # then, check if the colonies are within two of another colony
        possible = []
        for col in pos.get_colonies(colonies):
            if col.owner == -1:
                if col.check_proximity(pos):
                    possible.append(col.id)
        return possible

    def possible_cities(self, pos):
        # get all settlements this player owns, and then filter
        return [col.id for col in pos.get_colonies(self.colonies) if not col.city]

    def possible_roads(self, pos):
        # get all road connections to roads this player owns
        roads = []
        for road in pos.get_roads(self.roads):
            for col in pos.get_colonies(road.colonies):
                # edge case: can't build roads past another player's colony
                if col.owner in [-1, self.id]:
                    roads.extend(col.roads)
        roads = list(set(roads))

        # filter and return all empty roads
        return [road.id for road in pos.get_roads(roads) if road.owner == -1]

    def update_dice(self, pos, colony):
        for h in colony.hexes:
            h = pos.get_hex(h)
            if h.resource != Resource.DESERT:
                self.dice[h.number][h.resource] += 1

    def collect_resources(self, pos, die):
        print(f"DEBUG: Player {self.id} collects resources: {resources_str(self.dice[die])}")
        self.resources.update(self.dice[die])
        robber_resources = pos.robber.get_resources(pos)
        if self.id in robber_resources and pos.get_hex(pos.robber.location).number == die:
            self.resources.subtract(robber_resources[self.id])
            print(f"DEBUG: Robber takes: {robber_resources[self.id]}")
        print(f"DEBUG: Player {self.id} resources: {resources_str(self.resources)}")

    def resource_gate(self, resources):
        for resource in resources:
            if resources[resource] > self.resources[resource]:
                raise NotEnoughResourcesError(self.id, resource, resources[resource], self.resources[resource])

    def resource_check(self, resources):
        for resource in resources:
            if resources[resource] > self.resources[resource]:
                return False
        return True

    def discard_half(self, to_discard):
        to_discard = Counter(to_discard)
        if self.resources.total() <= 7:
            raise DoNotDiscardError(self.id)
        if to_discard.total() != self.resources.total() // 2:
            raise DiscardAmountWrongError(self.id, to_discard.total(), self.resources.total())
        self.resources.subtract(to_discard)

    def longest_road(self, pos):
        # longest path algorithm for an undirected cyclic disconnected graph
        # use settlements as "nodes" and roads as "edges"
        # settlements block if owned by someone else, but not if they're unowned
        # get all of the "start positions" and then run dfs.
        endpoints = []
        for road in pos.get_roads(self.roads):
            connected = 0
            for colony in pos.get_colonies(road.colonies):
                for r in pos.get_roads(colony.roads):
                    if r.id != road.id and r.owner == road.owner:
                        connected += 1
            if connected == 1:
                endpoints.append(road)

        def dfs_helper(pos, curr, visited, depth):
            # get same-owner children
            visited.add(curr.id)
            max_depth = 0
            for colony in pos.get_colonies(curr.colonies):
                for road in pos.get_roads(colony.roads):
                    if road.id not in visited and road.owner == self.id:
                        max_depth = max(max_depth, dfs_helper(pos, road, visited, depth+1))
            return max_depth

        def dfs(endpoints):
            visited = set()
            max_depth = 0
            for end in endpoints:
                max_depth = max(dfs_helper(pos, end, visited, 0))
            return max_depth

        return dfs(endpoints)
        
    def print_dice(self):
        for number in self.dice:
            print(number, self.dice[number])
