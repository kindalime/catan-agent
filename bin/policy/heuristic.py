from policy.policy import CatanPolicy
from abc import ABCMeta, abstractmethod
from collections import Counter
from resources import *
from devcard import *

def pick_top_three(data):
    data = Counter(data).most_common(3)
    choice = random.choice(data)
    return choice[0]

class HeuristicPolicy(CatanPolicy):
    def __init__(self, catan, player):
        super().__init__(catan, player)
        self.played_knight = False

    def count_pips(self, pos, cols):
        return {col.id: col.count_pips(pos) for col in cols}

    def init_settle(self, pos):
        if len(self.player.colonies) == 0:
            return self.init_settle_first(pos)
        else:
            return self.init_settle_second(pos)

    def init_settle_first(self, pos):
        # For first initial settles, focus on wood and brick.
        # Wheat is prioritized 3rd, then sheep, and lastly stone for now.

        weighted = {}
        for col in pos.get_colonies(self.player.possible_init_settlements(pos)):
            pips = 0
            for h in pos.get_hexes(col.hexes):
                match h.resource:
                    case Resource.WOOD:
                        pips += 2.5*pip_dict[h.number]
                    case Resource.BRICK:
                        pips += 2.5*pip_dict[h.number]
                    case Resource.WHEAT:
                        pips += 2*pip_dict[h.number]
                    case Resource.SHEEP:
                        pips += 2*pip_dict[h.number]
                    case Resource.STONE:
                        pips += 1*pip_dict[h.number]
            weighted[col.id] = pips
        return pick_top_three(weighted)

    def init_settle_second(self, pos):
        # For first initial settles, focus on wood and brick.
        # Wheat is prioritized 3rd, then sheep, and lastly stone for now.

        curr_resources = pos.get_colony(self.player.colonies[0]).get_resources(pos)

        weighted = {}
        for col in pos.get_colonies(self.player.possible_init_settlements(pos)):
            pips = 0
            for h in pos.get_hexes(col.hexes):
                match h.resource:
                    case Resource.WOOD:
                        if Resource.WOOD not in curr_resources:
                            pips += 3*pip_dict[h.number]
                        else:
                            pips += 1*pip_dict[h.number]
                    case Resource.BRICK:
                        if Resource.BRICK not in curr_resources:
                            pips += 3*pip_dict[h.number]
                        else:
                            pips += 1*pip_dict[h.number]
                    case Resource.WHEAT:
                        if Resource.WHEAT not in curr_resources:
                            pips += 3*pip_dict[h.number]
                        else:
                            pips += 1.25*pip_dict[h.number]
                    case Resource.SHEEP:
                        if Resource.SHEEP not in curr_resources:
                            pips += 3*pip_dict[h.number]
                        else:
                            pips += 1*pip_dict[h.number]
                    case Resource.STONE:
                        pips += 1.5*pip_dict[h.number]
            weighted[col.id] = pips
        return pick_top_three(weighted)

    def init_road(self, pos, settlement):
        # Same as random
        roads = pos.get_colony(settlement).roads
        roads = [r for r in pos.get_roads(roads) if r.owner == -1]
        return random.choice(roads).id

    def choose_discard(self, pos):
        """ Their algorithm in pseudocode:

        get a {resource: total_pips} dict
        discard resources starting from the ones with the most pips
        """
        to_discard = pos.players[self.player.id].resources.total() // 2
        discard = []

        curr_resources = pos.players[self.player.id].resources.copy()
        # If you can make a city, keep those items
        if pos.players[self.player.id].resource_check(city_cost):
            curr_resources.subtract(city_cost)
            # Edge case: can make a city, but have exactly 8 cards
            if pos.players[self.player.id].resources.total() == 8:
                discard.append(Resource.WHEAT)

        # Else if you can make a settlement, keep those items
        elif pos.players[self.player.id].resource_check(settlement_cost):
            curr_resources.subtract(settlement_cost)

        if curr_resources[Resource.STONE] + curr_resources[Resource.WHEAT] \
            > curr_resources[Resource.WOOD] + curr_resources[Resource.BRICK]: 
            discard_order = [Resource.SHEEP, Resource.WOOD, Resource.BRICK, Resource.WHEAT, Resource.STONE]
        else:
            discard_order = [Resource.SHEEP, Resource.WHEAT, Resource.STONE, Resource.WOOD, Resource.BRICK]

        # construct the discard list
        for r in discard_order:
            if len(discard) >= to_discard:
                break
            elif curr_resources[r] + len(discard) < to_discard:
                discard.extend([r] * curr_resources[r])
            else:
                discard.extend([r] * (to_discard - len(discard)))

        if len(discard) != to_discard:
            discard.append(Resource.WHEAT)

        return discard

    def choose_robber(self, pos):
        """ Their algorithm in psuedocode:

        target the player with the most VPs
        always move the robber
        heuristic = -20 for my hex, +4 for their hex, +# of players on hex
        pick randomly from the hexes with the most pips
        """
        points = {p.id: p.points for p in pos.players if p.id != self.player.id}
        targets = [p for p in points if points[p] == max(points.values())]

        def heuristic(h):
            val = 0
            for col in pos.get_colonies(h.colonies):
                if col.owner == self.player.id:
                    val -= 20
                elif col.owner in targets:
                    val += 4
                elif col.owner != -1:
                    val += 1
            return val

        hex_dict = {h.id: heuristic(h) for h in pos.board.hexes}
        top = [h for h in hex_dict if hex_dict[h] == max(hex_dict.values())]
        
        pips = self.count_pips(pos, pos.get_colonies(top))
        location = pick_top_three(pips)
        target_cols = pos.get_colonies(pos.get_hex(location).colonies)
        for col in target_cols:
            if col.owner in targets:
                return col.owner, location

        # fallback if no targets
        for col in target_cols:
            if col.owner not in [-1, self.player.id]:
                return col.owner, location

    def place_settlement(self, pos):
        def choose_location():
            weighted = {}
            for col in pos.get_colonies(self.player.possible_settlements(pos)):
                pips = 0
                for h in pos.get_hexes(col.hexes):
                    match h.resource:
                        case Resource.STONE:
                            pips += 3*pip_dict[h.number]
                        case Resource.WHEAT:
                            pips += 2*pip_dict[h.number]
                        case Resource.WOOD:
                            pips += 1*pip_dict[h.number]
                        case Resource.BRICK:
                            pips += 1*pip_dict[h.number]
                        case Resource.SHEEP:
                            pips += 1*pip_dict[h.number]
                weighted[col.id] = pips
            return pick_top_three(weighted)

        self.catan.build_settlement(pos, self.player, choose_location())
    
    def place_city(self, pos):
        choices = pos.get_colonies(self.player.possible_cities(pos))
        pips = self.count_pips(pos, choices)
        self.catan.build_city(pos, self.player, pick_top_three(pips))

    def place_road(self, pos):
        """ Their algorithm in pseudocode:
        
        if player has longest road:
            20%: extend longest road (random choice)
        elif player is tied for longest road:
            75%: extend longest road (random choice)

        if there are available roads with no opposing building on either side:
            randomly choose one
        else:
            randomly choose from possible roads
        """

        def calculate_road():        
            possible = []
            roads = self.player.possible_roads(pos)
            settles = set(self.player.possible_settlements(pos))
            for road in pos.get_roads(roads):
                # does the road open up access to a new settlement?
                for col in pos.get_colonies(road.colonies):
                    if col.owner == -1 and col.id not in settles:
                        possible.append(road.id)
                        break
            if possible:
                return random.choice(possible)
            else:
                return random.choice(roads)

        road = calculate_road()    
        self.catan.build_road(pos, self.player, road)

    def play_dev(self, pos):
        """ Their algorithm in pseudocode:
        
        play all vp cards only when the total >= 10 (victory)
        
        play knight cards only when:
            you don't have largest army
            you haven't already played a knight card this turn
            9/10 random chance
        pick a random dev card to play
        """

        # VP Cards
        if self.player.points + self.player.dev_cards[DevCard.VP] >= 10:
            for i in range(self.player.dev_cards[DevCard.VP]):
                self.catan.use_dev_card(pos, self.player, DevCard.VP)
                return

        # Knight Card
        if not self.played_knight and pos.largest_army_owner != self.player.id:
            if self.player.dev_cards[DevCard.KNIGHT] > 0 and random.random() < .9:
                self.played_knight = True
                victim, location = self.choose_robber(pos)
                self.catan.use_dev_card(pos, self.player, DevCard.KNIGHT, location=location, victim=victim)
                return

        # the rest of these are the same as random
        dev_cards = counter_to_list(list(self.player.dev_cards.items()))
        random.shuffle(dev_cards)
        for card in dev_cards:
            match card:
                case DevCard.PLENTY:
                    self.catan.use_dev_card(pos, self.player, DevCard.PLENTY, first=Resource.random(), second=Resource.random())
                case DevCard.MONOPOLY:
                    self.catan.use_dev_card(pos, self.player, DevCard.MONOPOLY, res=Resource.random())
                case DevCard.ROAD:
                    choices = self.player.possible_roads(pos)
                    random.shuffle(choices)
                    if len(choices) == 1:
                        self.catan.use_dev_card(pos, self.player, DevCard.ROAD, first=choices[0], second=None)
                    elif len(choices) != 0:
                        self.catan.use_dev_card(pos, self.player, DevCard.ROAD, first=choices[0], second=choices[1])

    def trade_focus(self, pos, cost):
        if resource_check(self.player.resources, cost):
            return None

        needed = cost.copy()
        needed.subtract(self.player.resources)

        # find give resource
        for give in all_resources:
            if give not in cost:
                while self.player.resources[give] >= self.player.trade[give]:
                    # find receive resource
                    still_needed = False
                    for receive in cost:
                        if needed[receive] > 0:
                            self.catan.trade_resource(pos, self.player, give, receive)
                            needed[receive] -= 1
                            still_needed = True
                            break
                    if not still_needed:
                        return

    def trades(self, pos):
        if self.player.resources[Resource.STONE] >= 2 and self.player.resources[Resource.WHEAT] >= 1:
            self.trade_focus(pos, city_cost)
        else:
            self.trade_focus(pos, settlement_cost)

    def take_turn(self, pos):
        """ Their algorithm in pseudocode:
        prioritize the following in order:
        * cities
        * settlements
        * roads (90%)
        * buying dev cards
        * playing dev cards

        """
        self.played_knight = False

        # while it is possible to place settlements, do so
        # print("settlement stage")
        # print(self.player.possible_settlements(pos))
        while self.player.resource_check(settlement_cost) and self.player.possible_settlements(pos) and self.player.settlement_supply > 0:
            self.place_settlement(pos)

        # while it is possible to place roads (90%), do so
        # print("road stage")
        # print(self.player.possible_roads(pos))
        while self.player.resource_check(road_cost) and self.player.possible_roads(pos):
            self.place_road(pos)

        # while it is possible to place cities, do so
        # print("city stage")
        # print(self.player.possible_cities(pos))
        while self.player.resource_check(city_cost) and self.player.possible_cities(pos) and self.player.city_supply > 0:
            self.place_city(pos)

        # while it is possible to buy dev cards, do so
        # print("dev buy stage")
        while not pos.dev_deck.is_empty() and self.player.resource_check(dev_card_cost):
            self.catan.draw_dev_card(pos, self.player)

        # while it is possible to play dev cards, do so
        # print("dev play stage")
        self.play_dev(pos)

        # if you can do any trades, do them
        self.trades(pos)