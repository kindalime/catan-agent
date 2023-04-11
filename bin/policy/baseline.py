from policy import CatanPolicy
from abc import ABCMeta, abstractmethod

class BaselinePolicy(CatanPolicy):
    # taken from the "smart heuristic player" from Ashraf and Kim's project, 2018.
    # everything has been implemented except the things related to trading/harbors

    def init_settle(self, pos, player):
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
        pass

    def choose_discard(self, pos, player):
        """ Their algorithm in pseudocode:

        get a {resource: total_pips} dict
        discard resources starting from the ones with the most pips
        """
        pass

    def choose_robber(self, pos, player):
        """ Their algorithm in psuedocode:

        target the player with the most VPs
        always move the robber
        heuristic = -20 for my hex, +4 for their hex, + # of players on hex
        pick randomly from the hexes with the most pips
        """
        pass

    def take_turn(self, pos, player):
        """ Their algorithm in pseudocode:
        prioritize the following in order:
        * cities
        * settlements
        * roads (90%)
        * buying dev cards
        * playing dev cards

        """
        pass

    def place_settlement(self, pos, player):
        """ Their algorithm in psuedocode:

        if settles connected to resources that the player doesn't own exist:
            return a random choice from the above ^

        return a random choice from the possible choices that have the highest pips           
        """
        pass

    def place_city(self, pos, player):
        """ Their algorithm in pseudocode:
        
        choose candidates at random from the ones with highest pips
        """
        pass

    def place_road(self, pos, player):
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

    def play_dev(self, pos, player):
        """ Their algorithm in pseudocode:
        
        play all vp cards only when the total >= 10 (victory)
        
        play knight cards only when:
            you don't have largest army
            you haven't already played a knight card this turn
            9/10 random chance
        pick a random dev card to play
        """
        pass