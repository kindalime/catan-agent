from resources import *
from errors import *
from devcard import empty_deck, play_card
from utils import player_colors
import logging

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
        self.longest = 1
        self.endpoints = None

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

    def possible_robber(self, pos):
        combos = []
        for h in self.pos.board.hexes:
            players = list(h.get_players())
            if self.id not in players and len(players) > 1:
                for p in players:
                    combos.append([players, h.id])
        return combos

    def update_dice(self, pos, colony):
        for h in colony.hexes:
            h = pos.get_hex(h)
            if h.resource != Resource.DESERT:
                self.dice[h.number][h.resource] += 1

    def collect_resources(self, pos, die):
        logging.debug(f"DEBUG: Player {self.id} collects resources: {resources_str(self.dice[die])}")
        self.resources.update(self.dice[die])
        robber_resources = pos.robber.get_resources(pos)
        if self.id in robber_resources and pos.get_hex(pos.robber.location).number == die:
            self.resources.subtract(robber_resources[self.id])
            logging.debug(f"DEBUG: Robber takes: {robber_resources[self.id]}")
        logging.debug(f"DEBUG: Player {self.id} resources: {resources_str(self.resources)}")

    def resource_gate(self, cost):
        resource_gate(self.resources, cost)

    def resource_check(self, cost):
        return resource_check(self.resources, cost)

    def discard_half(self, to_discard):
        to_discard = Counter(to_discard)
        if self.resources.total() <= 7:
            raise DoNotDiscardError(self.id)
        if to_discard.total() != self.resources.total() // 2:
            raise DiscardAmountWrongError(self.id, to_discard.total(), self.resources.total() // 2)
        self.resources.subtract(to_discard)

    def longest_road(self, pos):
        # longest path algorithm for an undirected cyclic disconnected graph
        # use settlements as "nodes" and roads as "edges"
        # settlements block if owned by someone else, but not if they're unowned
        # get all of the "start positions" and then run dfs.

        # TODO: buggy for loops and larger edge cases?
        endpoints = []
        for road in pos.get_roads(self.roads):
            for colony in pos.get_colonies(road.colonies):
                if colony.owner not in [-1, self.id]: # endpoint if cut off by another player's settlement
                    endpoints.append(road)
                    break
                else: # road is an "endpoint" if it is the only road on its vertex
                    connected = 0
                    for r in pos.get_roads(colony.roads):
                        if r.id != road.id and r.owner == self.id:
                            connected += 1
                    if connected == 0:
                        endpoints.append(road)
                        break

        def dfs_helper(pos, curr, visited_roads, visited_cols, depth):
            # get same-owner children
            # print(curr.id, visited_roads, visited_cols, depth)
            visited_roads.add(curr.id)
            max_depth = depth
            max_endpoint = curr.id
            for colony in pos.get_colonies(curr.colonies):
                if colony.id not in visited_cols and colony.owner in [-1, self.id]:
                    visited_cols.add(colony.id)
                    for road in pos.get_roads(colony.roads):
                        if road.id not in visited_roads and road.owner == self.id:
                            new_depth, visited_roads, visited_cols, new_endpoint = dfs_helper(pos, road, visited_roads, visited_cols, depth+1)
                            if new_depth > max_depth:
                                max_depth = new_depth
                                max_endpoint = new_endpoint
            return max_depth, visited_roads, visited_cols, max_endpoint

        def dfs(endpoints):
            max_depth = 0
            max_endpoints = None
            for end in endpoints:
                visited_roads = set()
                visited_cols = set()
                depth, visited_roads, visited_cols, endpoint = dfs_helper(pos, end, visited_roads, visited_cols, 1)
                if depth > max_depth:
                    max_depth = depth
                    max_endpoints = [end.id, endpoint]
            return max_depth, visited_roads, visited_cols, max_endpoints

        max_depth, visited_roads, visited_cols, max_endpoints = dfs(endpoints)

        self.longest = max_depth
        self.endpoints = max_endpoints
        return max_depth
        
    def print_dice(self):
        for number in self.dice:
            print(number, self.dice[number])
