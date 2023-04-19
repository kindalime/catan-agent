import random
from enum import Enum

from utils import *
from resources import *
from policy.policy import CatanPolicy
from devcard import *
from time import sleep

class Option(Enum):
    SETTLEMENT = 0
    CITY = 1
    ROAD = 2
    DEV = 3

class RandomPolicy(CatanPolicy):
    def init_settle(self, pos):
        possible = self.player.possible_init_settlements(pos)
        return random.choice(possible)
        # Find any unowned, valid settle spot
        # while True:
        #     spot = random.randrange(54)
        #     if pos.get_colony(spot).owner == -1 and pos.get_colony(spot).check_proximity(pos):
        #         break
        # return spot

    def init_road(self, pos, settlement):
        # Find any possible road connected to that spot
        roads = pos.get_colony(settlement).roads
        roads = [r for r in pos.get_roads(roads) if r.owner == -1]
        return random.choice(roads).id

    def choose_discard(self, pos):
        resources = counter_to_list(self.player.resources)
        random.shuffle(resources)
        return resources[:len(resources) // 2] # half rounding down

    def choose_robber(self, pos):
        while True:            
            # If the hex blocks 2+ other settlements (and possibly this self.player)
            # OR 1+ other settlements and NOT this self.player, select this hex
            # First requirement used to avoid possible inf loops w/ 3 self.players
            while True:
                spot = random.randrange(len(pos.board.hexes)-1) # doesn't include the desert
                settles = 0
                self.players_blocked = []
                blocked = False
                for col in pos.get_colonies(pos.get_hex(spot).colonies):
                    if col.owner == self.player.id:
                        blocked = True
                    elif col.owner != -1:
                        settles += 1
                        self.players_blocked.append(col.owner)
                if settles >= 2 or (settles >= 1 and not blocked):
                    break

            return random.choice(self.players_blocked), spot

    def option_settlement(self, pos):
        choices = self.player.possible_settlements(pos)
        if choices and self.player.resource_check(settlement_cost) and self.player.settlement_supply > 0:
            self.catan.build_settlement(pos, self.player, random.choice(choices))

    def option_city(self, pos):
        choices = self.player.possible_cities(pos)
        if choices and self.player.resource_check(city_cost) and self.player.city_supply > 0:
            self.catan.build_city(pos, self.player, random.choice(choices))

    def option_road(self, pos):
        choices = self.player.possible_roads(pos)
        if choices and self.player.resource_check(road_cost):
            self.catan.build_road(pos, self.player, random.choice(choices))

    def option_dev(self, pos):
        if not pos.dev_deck.is_empty() and self.player.resource_check(dev_card_cost):
            self.catan.draw_dev_card(pos, self.player)

    def play_dev_card(self, pos, card_type):
        match card_type:
            case DevCard.KNIGHT:
                victim, spot = self.choose_robber(pos)
                self.catan.use_dev_card(pos, self.player, card_type, location=spot, victim=victim)
            case DevCard.VP:
                self.catan.use_dev_card(pos, self.player, card_type)
            case DevCard.PLENTY:
                self.catan.use_dev_card(pos, self.player, card_type, first=Resource.random(), second=Resource.random())
            case DevCard.MONOPOLY:
                self.catan.use_dev_card(pos, self.player, card_type, res=Resource.random())
            case DevCard.ROAD:
                choices = self.player.possible_roads(pos)
                random.shuffle(choices)
                if len(choices) == 1:
                    self.catan.use_dev_card(pos, self.player, card_type, first=choices[0], second=None)
                elif len(choices) != 0:
                    self.catan.use_dev_card(pos, self.player, card_type, first=choices[0], second=choices[1])
            case None:
                raise ValueError("Incorrect dev card!")

    def take_turn(self, pos):
        # for each dev card: 33% chance to play every turn
        dev_cards = counter_to_list(list(self.player.dev_cards.items()))
        random.shuffle(dev_cards)
        for card in dev_cards:
            if random.random() < 2/3:
                self.play_dev_card(pos, card)
        
        # possible choices: settlements, cities, roads, dev cards, chosen in random order
        # this algorithm does AT MOST one settlement, one city, two roads, two dev cards a turn
        options = [Option.SETTLEMENT, Option.CITY, Option.ROAD, Option.ROAD, Option.DEV, Option.DEV]
        option_dict = {
            Option.SETTLEMENT: self.option_settlement,
            Option.CITY: self.option_city,
            Option.ROAD: self.option_road,
            Option.DEV: self.option_dev,
        }
        
        random.shuffle(options)
        for option in options:
            option_dict[option](pos)
