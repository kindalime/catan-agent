from resources import *
from errors import *
from dev_card import empty_deck, play_card

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
            if col.owner != -1:
                if col.check_proximity():
                    possible.append(col.id)
        return possible

    def possible_cities(self, pos):
        # get all settlements this player owns, and then filter
        return [col.id for col in pos.get_colonies(self.colonies) if col.city]

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

    def collect_resources(self, pos, die):
        self.resources.update(self.dice[die])
        robber_resources = pos.robber.get_resources()
        if self.id in robber_resources:
            self.resources.subtract(robber_resources[self.id])

    def resource_check(self, resources):
        for resource in resources:
            if resources[resource] > self.resources[resource]:
                raise NotEnoughResourcesError(self.id, resource, resources[resource], self.resources[resource])

    def build_init_settlement(self, pos, id):
        pos.get_settlement(id).initial_build(self.id, pos)
        self.colonies.append(id)
        self.points += 1
        
        # collect resources, but only on the second settle
        if len(self.colonies) == 2:
            for resource in pos.get_colony(id).get_resources(pos):
                self.resources[resource] += 1 

    def build_init_road(self, pos, id, settlement):
        pos.get_road(id).initial_build(self.id, pos, settlement)
        self.roads.append(id)
        self.points += 1

    def build_road(self, pos, id):
        self.resource_check(road_cost)
        pos.get_road(id).build(self.id)
        self.roads.append(id)
        pos.road_calc = True
        
    def build_settlement(self, pos, id):
        self.resource_check(settlement_cost)
        if self.settlement_supply <= 0:
            raise OutOfSettlementsError(self.id)

        colony = pos.get_colony(id)
        colony.build(self.id)
        self.colonies.append(id)

        self.resources.update(colony.get_resources())
        self.resources.subtract(settlement_cost)
        self.settlement_supply -= 1
        self.points += 1

        # If our settlement cuts off a road, recalculate all longest roads
        roads = pos.get_roads(pos.get_colony(id).roads)
        owners = [road.owner for road in roads if road.owner != -1]
        most_common = Counter(owners).most_common(1)[0]
        if most_common[1] >= 2 and most_common[0] != self.id:
            pos.road_reset = True

    def build_city(self, pos, id):
        self.resource_check(city_cost)
        if self.city_supply <= 0:
            raise OutOfCitiesError(self.id)

        colony = pos.get_colony(id)
        colony.upgrade(self.id)
        self.resources.update(colony.get_resources())
        self.resources.subtract(city_cost)
        self.settlement_supply += 1
        self.city_supply -= 1
        self.points += 1

    def draw_dev_card(self, pos):
        self.resource_check(dev_card_cost)
        card = pos.draw_dev_card()
        self.dev_cards[card] += 1
    
    def use_dev_card(self, pos, card, **kwargs):
        if self.dev_cards[card] <= 0:
            raise DontHaveCardError(self.id, card)
        play_card(self.id, pos, card, **kwargs)
        self.dev_cards[card] -= 1

    def discard_half(self, to_discard):
        if self.resources.total() <= 7:
            raise DoNotDiscardError(self.id)
        if to_discard.total() != self.resources.total() // 2:
            raise DiscardAmountWrongError(self.id, to_discard.total(), self.resources.total())
        self.resources.subtract(to_discard)

    def longest_road(self, pos):
        # longest path algorithm for an undirected cyclic disconnected graph
        # use settlements as "nodes" and roads as "edges"
        # settlements block if owned by someone else, but not if they're unowned
        # TODO: ask prof. glenn about this!
        pass
