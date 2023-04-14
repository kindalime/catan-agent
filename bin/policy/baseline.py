from policy import CatanPolicy
from abc import ABCMeta, abstractmethod
from collections import Counter
from resource import Resource

def pick_top_three(data):
    data = Counter(data).most_common(3)
    choice = random.choice(data)
    return choice[0]

class BaselinePolicy(CatanPolicy):
    # taken from the "smart heuristic player" from Ashraf and Kim's project, 2018.
    # everything has been implemented except the things related to trading/harbors

    def count_pips(self, pos, cols):
        pips = {col.id:col.count_pips(pos) for col in cols}

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

        for col in pos.get_colonies(pos.board.colonies):
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
            pips = self.count_pips(three_unique)
            if self.player.colonies and Resource.STONE not in self.colonies[0].get_resources(pos):
                for col in three_unique:
                    if Resource.STONE in col.get_resources(pos):
                        pips[col.id] += 3
            return pick_top_three(pips)
        elif three_resources:
            pips = self.count_pips(three_resources)
            return pick_top_three(three_resources)
        elif two_unique:
            pips = self.count_pips(two_unique)
            return pick_top_three(two_unique)
        elif two_resources:
            pips = self.count_pips(two_resources)
            return pick_top_three(two_resources)
        elif others:
            pips = self.count_pips(others)
            return pick_top_three(others)

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
                discard.extend([r[0] * self.player.resources[r[0]]])
            else:
                discard.extend([r[0] * (to_discard - len(discard))])
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
                else:
                    val += 1
            return val

        hex_dict = {h.id: heuristic(h) for h in pos.board.hexes}
        top = [h for h in hex_dict if hex_dict[h] == max(hex_dict.values)]
        
        pips = self.count_pips(pos, top)
        return pick_top_three(pips)

    def place_settlement(self, pos):
        """ Their algorithm in psuedocode:

        if settles connected to resources that the player doesn't own exist:
            return a random choice from the above ^

        return a random choice from the possible choices that have the highest pips           
        """
        # get current resources
        curr_resources = set()
        for die in self.player.dice:
            for r in Resource:
                if self.player.dice[die] > 0:
                    curr_resources.add(r)
        
        possible = self.player.possible_settlements(pos)

        # do settles connected to resources that the player doesn't own exist?
        if len(curr_resources) != 5:
            priority = []
            for settle in possible:
                for r in pos.get_colony(settle).get_resources():
                    if r not in curr_resources:
                        priority.append(settle)
                        break
            if priority:
                pips = self.count_pips(pos, priority)
                return pick_top_three(pips)
        
        # if none of the above exist, fall back to default
        pips = self.count_pips(pos, possible)
        return pick_top_three(pips)
        
    def place_city(self, pos):
        """ Their algorithm in pseudocode:
        
        choose candidates at random from the ones with highest pips
        """

        pips = self.count_pips(pos, self.player.possible_cities(pos))
        return pick_top_three(pips)

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

        # longest road checks

    def play_dev(self, pos):
        """ Their algorithm in pseudocode:
        
        play all vp cards only when the total >= 10 (victory)
        
        play knight cards only when:
            you don't have largest army
            you haven't already played a knight card this turn
            9/10 random chance
        pick a random dev card to play
        """
        pass

    def take_turn(self, pos):
        """ Their algorithm in pseudocode:
        prioritize the following in order:
        * cities
        * settlements
        * roads (90%)
        * buying dev cards
        * playing dev cards

        """
        pass
