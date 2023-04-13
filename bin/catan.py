import copy
import random

from utils import *
from resources import *
from errors import CannotStealError

from player import Player
from board import Board
from devcard import *
from robber import Robber
from position import Position
from display import Display

from policy.human import HumanPolicy
from policy.random import RandomPolicy
from time import sleep


class Catan:
    def __init__(self, player_num):
        self.player_num = player_num
        self.display = None
        self.policies = None

    def policy_setup(self, pos):
        # TODO: change
        return [
            RandomPolicy(self, pos.players[0]),
            RandomPolicy(self, pos.players[1]),
            RandomPolicy(self, pos.players[2]),
        ]

    def play_game(self):
        pos = self.init_pos()
        self.policies = self.policy_setup(pos)
        pos = self.begin_game(pos)
        while True:
            pos = self.play_turn(pos)
            if pos.terminal:
                break
        print(f"Game Over! Winner: {pos.winner}")
        print(f"Scores: {[(i, pos.players[i].points) for i in range(self.player_num)]}")
        return pos.winner

    def init_pos(self):
        players = [Player(num) for num in range(self.player_num)]
        board = Board()
        dev_deck = DevelopmentDeck()
        robber = Robber()
        current_turn = random.randint(0, self.player_num-1)
        turn_count = 0
        return Position(board, players, dev_deck, robber, current_turn, turn_count)

    def begin_game(self, pos):
        # initial settlement/road placing
        self.display = Display(pos.board)
        for i in range(self.player_num):
            curr_player = (pos.current_turn + i) % self.player_num
            col = self.policies[curr_player].init_settle(pos)
            self.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.policies[curr_player].init_road(pos, col)
            self.build_init_road(pos, pos.players[curr_player], road, col)

        for i in range(self.player_num-1, -1, -1):
            curr_player = (pos.current_turn + i) % self.player_num
            col = self.policies[curr_player].init_settle(pos)
            self.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.policies[curr_player].init_road(pos, col)
            self.build_init_road(pos, pos.players[curr_player], road, col)
        return pos

    def play_turn(self, pos):
        pos = copy.copy(pos)

        dice = random.randint(1, 6) + random.randint(1, 6) # roll the dice
        print(f"Player {pos.current_turn} turn. Dice roll: {dice}")
        if dice != 7: # gather resources as usual
            for player in pos.players:
                player.collect_resources(pos, dice)
        else: # robber attack!
            self.robber_attack(pos)

        # ask policy what it wants to do for a specific player
        self.policies[pos.current_turn].take_turn(pos)

        self.end_of_turn(pos)
        return pos

    def end_of_turn(self, pos):
        if pos.army_calc:
            self.largest_army(pos)
        if pos.road_reset:
            self.longest_road_reset(pos)
        elif pos.road_calc:
            self.longest_road(pos)

        # reset variables
        pos.army_calc = False
        pos.road_reset = False
        pos.road_calc = False

        # check if the current player has won
        pos.check_terminal()

        # increment turns
        pos.current_turn = (pos.current_turn + 1) % self.player_num
        pos.turn_count += 1

    def robber_attack(self, pos):
        # robber attack - must ask policies for discard, and then do discards
        for i in range(self.player_num):
            print(f"DEBUG: Robber attack. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")
            if pos.players[i].resources.total() > 7:
                to_discard = self.policies[i].choose_discard(pos)
                pos.players[i].discard_half(to_discard)
                print(f"DEBUG: Cards discarded. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")

        # then, must ask policy what to do with the robber, and then resolve the robber
        victim, location = self.policies[pos.current_turn].choose_robber(pos)
        self.move_robber(pos, pos.current_turn, victim, location)

    def largest_army(self, pos):
        if pos.players[pos.current_turn].army > pos.largest_army:
            pos.players[pos.largest_army_owner].points -= 2
            pos.players[pos.current_turn].points += 2
            pos.largest_army_owner = pos.current_turn
    
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
        pos.get_colony(id).initial_build(pos, player.id)
        player.colonies.append(id)
        player.points += 1
        player.update_dice(pos, pos.get_colony(id))
        
        # collect resources, but only on the second settle
        if len(player.colonies) == 2:
            for resource in pos.get_colony(id).get_resources(pos):
                player.resources[resource] += 1 

        self.display.draw_colony(id, player.color)

    def build_init_road(self, pos, player, id, settlement):
        pos.get_road(id).initial_build(pos, player.id, settlement, id)
        player.roads.append(id)
        player.points += 1

        self.display.draw_road(id, player.color)

    def build_road(self, pos, player, id):
        player.resource_gate(road_cost)
        player.resources.subtract(road_cost)

        pos.get_road(id).build(pos, player.id)
        player.roads.append(id)
        pos.road_calc = True

        self.display.draw_road(id, player.color)
        print(f"DEBUG: Road built. Player {player.id} resources: {resources_str(player.resources)}")

    def build_settlement(self, pos, player, id):
        player.resource_gate(settlement_cost)
        if player.settlement_supply <= 0:
            raise OutOfSettlementsError(player.id)
        player.resources.subtract(settlement_cost)

        colony = pos.get_colony(id)
        colony.build(pos, player.id)
        player.colonies.append(id)
        player.update_dice(pos, colony)

        player.settlement_supply -= 1
        player.points += 1

        # If our settlement cuts off a road, recalculate all longest roads
        roads = pos.get_roads(pos.get_colony(id).roads)
        owners = [road.owner for road in roads if road.owner != -1]
        most_common = Counter(owners).most_common(1)[0]
        if most_common[1] >= 2 and most_common[0] != player.id:
            pos.road_reset = True
        
        self.display.draw_colony(id, player.color)
        print(f"DEBUG: Settlement built. Player {player.id} resources: {resources_str(player.resources)}")

    def build_city(self, pos, player, id):
        player.resource_gate(city_cost)
        if player.city_supply <= 0:
            raise OutOfCitiesError(player.id)
        player.resources.subtract(city_cost)

        colony = pos.get_colony(id)
        colony.upgrade(pos, player.id)
        player.update_dice(pos, colony)

        player.settlement_supply += 1
        player.city_supply -= 1
        player.points += 1

        self.display.draw_city(id, player.color)
        print(f"DEBUG: City built. Player {player.id} resources: {resources_str(player.resources)}")

    def draw_dev_card(self, pos, player):
        player.resource_gate(dev_card_cost)
        card = pos.draw_dev_card()
        player.resources.subtract(dev_card_cost)
        player.dev_cards[card] += 1
        print(f"DEBUG: Dev card drawn. Player {player.id} resources: {resources_str(player.resources)}")

    def use_dev_card(self, pos, player, card, **kwargs):
        if player.dev_cards[card] <= 0:
            raise DontHaveCardError(player.id, card)
        play_card(self, pos, player, card, **kwargs)
        player.dev_cards[card] -= 1
        for i in range(self.player_num):
            print(f"DEBUG: Dev card used. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")

    def move_robber(self, pos, player_id, victim_id, location):
        prev_location = pos.robber.location
        location = pos.get_hex(location)
        if victim_id == player_id or victim_id not in location.get_players(pos):
            raise CannotStealError(player_id, victim_id, location.id)
        pos.robber.location = location.id
        print(f"Robber moved from {prev_location} to {location.id}.")

        # steal a resource
        resources = counter_to_list(pos.players[victim_id].resources)
        if resources:
            stolen = random.choice(resources)
            print(f"DEBUG: Resource stolen from player {victim_id}: {stolen}")
            pos.players[player_id].resources.update([stolen])
            pos.players[victim_id].resources.subtract([stolen])
            print(f"DEBUG: Player {pos.players[player_id].id} resources: {resources_str(pos.players[player_id].resources)}")
            print(f"DEBUG: Player {pos.players[victim_id].id} resources: {resources_str(pos.players[victim_id].resources)}")

        # move robber display
        self.display.draw_hex(prev_location)
        self.display.add_robber(location.id)