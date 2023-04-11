import copy
import random
from utils import *

from player import Player
from board import Board
from devcard import DevelopmentDeck
from robber import Robber
from position import Position
from display import Display

from policy.human import HumanPolicy


class Catan:
    def __init__(self, player_num):
        self.player_num = player_num
        self.first_player = random.randint(0, player_num-1)
        self.display = Display
        self.policies = self.policy_setup()

    def policy_setup(self):
        return [HumanPolicy(), HumanPolicy(), HumanPolicy()]

    def play_game(self, pos):
        self.begin_game()
        while not pos.is_terminal():
            pos = self.play_turn()

    def init_pos(self):
        players = [Player(num) for num in range(player_num)]
        board = Board()
        dev_deck = DevelopmentDeck()
        robber = Robber()
        current_turn = self.first_player
        turn_count = 0
        return Position(board, players, dev_deck, robber, current_turn, turn_count)

    def begin_game(self):
        # initial settlement playing
        pos = init_pos()
        for i in range(self.player_num):
            pos = self.policies[(self.first_player + i) % self.player_num].init_settle(pos)

        for i in range(self.player_num-1, -1, -1):
            pos = self.policies[(self.first_player + i) % self.player_num].init_settle(pos)
        return pos

    def play_turn(self, pos):
        pos = copy(pos)

        dice = random.randint(1, 6) + random.randint(1, 6) # roll the dice
        print(f"Dice roll: {dice}")
        if dice != 7: # gather resources as usual
            for player in pos.players:
                player.collect_resources(dice)
        else: # robber attack!
            self.robber_attack(pos)

        # ask policy what it wants to do for a specific player
        pos = self.policies[pos.current_turn].take_turn(pos, pos.get_player(pos.current_turn))

        self.end_of_turn(pos)
        return pos

    def end_of_turn(self, pos):
        if pos.army_calc:
            self.largest_army(pos)
        if pos.road_reset:
            self.longest_road_reset(pos)
        elif pos.road_calc:
            self.longest_road_calc(pos)

        # reset variables
        pos.army_calc = False
        pos.road_reset = False
        pos.road_calc = False

        # increment turns
        pos.current_turn = (pos.current_turn + 1) % self.player_num
        pos.turn_count += 1

    def robber_attack(self, pos):
        # robber attack - must ask policies for discard, and then do discards
        for i in range(self.player_num):
            if pos.player[i].resources.total() > 7:
                to_discard = self.policies[i].choose_discard(pos, pos.player[i])
                pos.player[i].discard(to_discard)

        # then, must ask policy what to do with the robber, and then resolve the robber
        victim, location = self.policies[i].choose_robber(pos, pos.player[i])
        self.robber.move_robber(pos, pos.player, victim, location)

    def largest_army(self, pos):
        if pos.players[pos.current_turn].army > pos.largest_army:
            pos.players[pos.largest_army_owner].points -= 2
            pos.players[pos.current_turn].points += 2
            pos.largest_army_owner = current_turn
    
    def longest_road(self, pos):
        # calculate longest road for this player only
        player_road = pos.players[pos.current_turn].longest_road(pos)
        if player_road > pos.longest_road:
            pos.players[pos.longest_road_owner].points -= 2
            pos.players[pos.current_turn].points += 2
            pos.longest_road_owner = current_turn

    def longest_road_reset(self, pos):
        # calculates longest road for ALL players and resolves according to rules
        # only to be used when a settlement cuts off a road
        if pos.longest_road_owner == -1:
            return

        lens = {player.id: player.longest_road(pos) for player in pos.players}
        maxes, val = max_values_dict(lens)
        if val < 5:
            pos.longest_road = 4
            pos.longest_road_owner = -1
            pos.players[pos.longest_road_owner] -= 2
        else: 
            pos.longest_road = val
            if pos.longest_road_owner not in maxes:
                pos.players[pos.longest_road_owner] -= 2
                if len(maxes) > 1:
                    pos.longest_road_owner = -1
                else:
                    pos.longest_road_owner = maxes[0]
                    pos.players[pos.longest_road_owner] += 2

    def build_init_settlement(self, pos, player, id):
        pos.get_settlement(id).initial_build(player.id, pos)
        player.colonies.append(id)
        player.points += 1
        
        # collect resources, but only on the second settle
        if len(player.colonies) == 2:
            for resource in pos.get_colony(id).get_resources(pos):
                player.resources[resource] += 1 

        self.display.draw_settlement(id, player.color)

    def build_road(self, pos, player, id):
        player.resource_check(road_cost)
        pos.get_road(id).build(player.id)
        player.roads.append(id)
        pos.road_calc = True
        
        self.display.draw_road(id, player.color)

    def build_init_road(self, pos, player, id, settlement):
        pos.get_road(id).initial_build(player.id, pos, settlement)
        player.roads.append(id)
        player.points += 1

        self.display.draw_road(id, player.color)``

    def build_settlement(self, pos, player, id):
        player.resource_check(settlement_cost)
        if player.settlement_supply <= 0:
            raise OutOfSettlementsError(player.id)

        colony = pos.get_colony(id)
        colony.build(player.id)
        player.colonies.append(id)

        player.resources.update(colony.get_resources())
        player.resources.subtract(settlement_cost)
        player.settlement_supply -= 1
        player.points += 1

        # If our settlement cuts off a road, recalculate all longest roads
        roads = pos.get_roads(pos.get_colony(id).roads)
        owners = [road.owner for road in roads if road.owner != -1]
        most_common = Counter(owners).most_common(1)[0]
        if most_common[1] >= 2 and most_common[0] != player.id:
            pos.road_reset = True
        
        self.display.draw_settlement(id, player.color)

    def build_city(self, pos, player, id):
        player.resource_check(city_cost)
        if player.city_supply <= 0:
            raise OutOfCitiesError(player.id)

        colony = pos.get_colony(id)
        colony.upgrade(player.id)
        player.resources.update(colony.get_resources())
        player.resources.subtract(city_cost)
        player.settlement_supply += 1
        player.city_supply -= 1
        player.points += 1

        self.display.draw_city(id, player.color)

    def draw_dev_card(self, pos, player):
        player.resource_check(dev_card_cost)
        card = pos.draw_dev_card()
        player.dev_cards[card] += 1
    
    def use_dev_card(self, pos, player, card, **kwargs):
        if player.dev_cards[card] <= 0:
            raise DontHaveCardError(player.id, card)
        play_card(self, player, card, **kwargs)
        player.dev_cards[card] -= 1

    def move_robber(self, pos, player_id, victim_id, location):
        prev_location = pos.robber.location
        location = pos.get_hex(location)
        if victim_id == player_id or victim_id not in location.get_player_ids():
            raise CannotStealError(player_id, victim_id, location.id)
        pos.robber.location = location.id

        # steal a resource
        resources = counter_to_list(self.players[victim_id].resources)
        if resources:
            stolen = random.choice(resources)
            self.players[player_id].resources.update([stolen])
            self.players[victim_id].resources.subtract([stolen])

        # move robber display
        self.display.draw_hex(prev_location)
        self.display.add_robber(location.id)