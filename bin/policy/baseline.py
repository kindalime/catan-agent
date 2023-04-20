from policy.policy import CatanPolicy
from abc import ABCMeta, abstractmethod
from collections import Counter
from resources import *
from devcard import *

def pick_top_three(data):
    data = Counter(data).most_common(3)
    choice = random.choice(data)
    return choice[0]

class BaselinePolicy(CatanPolicy):
    # taken from the "smart heuristic player" from Ashraf and Kim's project, 2018.
    # everything has been implemented except the things related to trading/harbors

    def __init__(self, catan, player):
        super().__init__(catan, player)
        self.played_knight = False

    def count_pips(self, pos, cols):
        return {col.id: col.count_pips(pos) for col in cols}

    def init_settle(self, pos):
        """ Their algorithm in pseudocode:
        
        get all vertices (colonies) and their info
        also, get information on resources currently controlled

        if settles w/ 3 unique resources exist:
            for every settle with 3 unique resources:
                add up the sum of its pips
                if this is the 2nd settle and player doesn't have stone:
                    if this settle has stone:
                        add 3 to pips
            return a random choice from top 3 pip totals

        if settles connected to 3 resource hexes exist:
            return a random choice

        if settles connected to 2 resource hexes and a port exist:
            if settles where the port is 2:1 AND the player has 1+ of that resource exist:
                candidates = those settles
            elif settles where the port is 3:1 exist:
                candidates = those settles

            if candidates has settles where the 2 resources are different:
                filter candidates to the above ^

            filter candidates to only the ones with the highest pips

            return a random choice from candidates

        if settles connected to 2 resource hexes exist:
            return a random choice

        return a random choice
        """
        three_unique = []
        three_resources = []
        two_unique = []
        two_resources = []
        others = []

        for col in pos.get_colonies(self.player.possible_init_settlements(pos)):
            resources = col.get_resources(pos)
            if len(resources) == 3:
                if len(set(resources)) == 3:
                    three_unique.append(col)
                else:
                    three_resources.append(col)
            elif len(resources) == 2:
                if len(set(resources)) == 2:
                    two_unique.append(col)
                else:
                    two_resources.append(col)
            else:
                others.append(col)
        
        if three_unique:
            pips = self.count_pips(pos, three_unique)
            if self.player.colonies and Resource.STONE not in pos.get_colony(self.player.colonies[0]).get_resources(pos):
                for col in three_unique:
                    if Resource.STONE in col.get_resources(pos):
                        pips[col.id] += 3
            return pick_top_three(pips)
        elif three_resources:
            pips = self.count_pips(pos, three_resources)
            return pick_top_three(pips)
        elif two_unique:
            pips = self.count_pips(pos, two_unique)
            return pick_top_three(pips)
        elif two_resources:
            pips = self.count_pips(pos, two_resources)
            return pick_top_three(pips)
        elif others:
            pips = self.count_pips(pos, others)
            return pick_top_three(pips)

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
        to_discard = self.player.resources.total() // 2
        discard = []

        # find out most common resources
        resources = {
            Resource.WOOD: 0,
            Resource.BRICK: 0,
            Resource.SHEEP: 0,
            Resource.WHEAT: 0,
            Resource.STONE: 0,
        }
        for col in pos.get_colonies(self.player.colonies):
            for h in pos.get_hexes(col.hexes):
                if h.resource != Resource.DESERT:
                    resources[h.resource] += h.number
        resources = Counter(resources).most_common()

        # construct the discard list
        for r in resources:
            if len(discard) >= to_discard:
                break
            elif self.player.resources[r[0]] + len(discard) < to_discard:
                discard.extend([r[0]] * self.player.resources[r[0]])
            else:
                discard.extend([r[0]] * (to_discard - len(discard)))
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
        """ Their algorithm in psuedocode:

        if settles connected to resources that the player doesn't own exist:
            return a random choice from the above ^

        return a random choice from the possible choices that have the highest pips           
        """
            
        def choose_location():
            # get current resources
            curr_resources = set()
            for die in self.player.dice:
                for r in Resource:
                    if self.player.dice[die][r] > 0:
                        curr_resources.add(r)
            
            possible = pos.get_colonies(self.player.possible_settlements(pos))

            # do settles connected to resources that the player doesn't own exist?
            if len(curr_resources) != 5:
                priority = []
                for settle in possible:
                    for r in settle.get_resources(pos):
                        if r not in curr_resources:
                            priority.append(settle)
                            break
                if priority:
                    pips = self.count_pips(pos, priority)
                    return pick_top_three(pips)
            
            # if none of the above exist, fall back to default
            pips = self.count_pips(pos, possible)
            return pick_top_three(pips)

        self.catan.build_settlement(pos, self.player, choose_location())
    
    def place_city(self, pos):
        """ Their algorithm in pseudocode:
        
        choose candidates at random from the ones with highest pips
        """
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

        # find possible endpoints to extend - want to extend to vertices w/o 2+ roads to extend longest road
        def extend_longest_road():
            possible = []
            for endpoint in pos.get_roads(self.player.endpoints):
                for col in pos.get_colonies(endpoint.colonies):
                    if col.owner in [-1, self.player.id]:
                        possible_col = True
                        for road in pos.get_roads(col.roads):
                            if road.id != endpoint and road.owner == self.player.id:
                                possible_col = False
                                break
                        if possible_col:
                            possible.extend(col.roads)
            return possible

        def calculate_road():
            if pos.longest_road_owner == self.player:
                if random.random() < .2: # 20% check
                    possible = extend_longest_road()
                    if possible:
                        return random.choice(possible)
            elif pos.longest_road_owner != -1 and pos.longest_road == self.player.longest:
                if random.random() < .75: # 75% check
                    possible = extend_longest_road()
                    if possible:
                        return random.choice(possible)
            
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

        # while it is possible to place cities, do so
        # print("city stage")
        # print(self.player.possible_cities(pos))
        while self.player.resource_check(city_cost) and self.player.possible_cities(pos) and self.player.city_supply > 0:
            self.place_city(pos)

        # while it is possible to place settlements, do so
        # print("settlement stage")
        # print(self.player.possible_settlements(pos))
        while self.player.resource_check(settlement_cost) and self.player.possible_settlements(pos) and self.player.settlement_supply > 0:
            self.place_settlement(pos)

        # while it is possible to place roads (90%), do so
        # print("road stage")
        # print(self.player.possible_roads(pos))
        while self.player.resource_check(road_cost) and self.player.possible_roads(pos):
            if random.random() < .9:
                self.place_road(pos)
            else:
                break

        # while it is possible to buy dev cards, do so
        # print("dev buy stage")
        while not pos.dev_deck.is_empty() and self.player.resource_check(dev_card_cost):
            self.catan.draw_dev_card(pos, self.player)

        # while it is possible to play dev cards, do so
        # print("dev play stage")
        self.play_dev(pos)
