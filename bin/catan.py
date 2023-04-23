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
from policy.baseline import BaselinePolicy
from policy.heuristic import HeuristicPolicy
from policy.mcts import MCTSPolicy
from time import sleep
import logging


class Catan:
    def __init__(self, setup, show_display=False):
        self.setup, self.setup_args = setup
        self.player_num = len(self.setup)
        self.display = None
        self.policies = None
        self.show_display = show_display

    def policy_setup(self, pos):
        policies = []
        for i in range(len(self.setup)):
            match self.setup[i]:
                case "h":
                    policies.append(HeuristicPolicy(self, pos.players[i]))
                case "b":
                    policies.append(BaselinePolicy(self, pos.players[i], self.setup_args[i]))
                case "r":
                    policies.append(RandomPolicy(self, pos.players[i]))
                case "m":
                    policies.append(MCTSPolicy(self, pos.players[i], 1000))

        return policies

    def play_game(self):
        pos = self.init_pos()
        self.policies = self.policy_setup(pos)
        pos = self.begin_game(pos)
        while True:
            pos = self.play_turn(pos)
            if pos.terminal:
                break
        scores = [(i, pos.players[i].points) for i in range(self.player_num)]
        logging.info(f"Game Over! Winner: {pos.winner}")
        logging.info(f"Scores: {scores}")
        logging.debug(f"Longest Road: {[(pos.players[i].longest, pos.players[i].endpoints) for i in range(self.player_num)]}")
        if self.show_display:
            self.display.save("image.jpeg")
        return pos.winner, scores

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
        if self.show_display:
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
        # pos = copy.deepcopy(pos)
        logging.info(f"VPs: {[p.points for p in pos.players]}")

        dice = random.randint(1, 6) + random.randint(1, 6) # roll the dice
        logging.info(f"Player {pos.current_turn} turn. Dice roll: {dice}")
        self.gather_resources(pos, dice)

        # ask policy what it wants to do for a specific player
        self.policies[pos.current_turn].take_turn(pos)

        self.end_of_turn(pos)
        return pos

    def gather_resources(self, pos, dice):
        if dice != 7: # gather resources as usual
            for player in pos.players:
                player.collect_resources(pos, dice)
        else: # robber attack!
            self.robber_attack(pos)
        pos.gathered = True

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
        pos.gathered = False

    def robber_attack(self, pos):
        # robber attack - must ask policies for discard, and then do discards
        for i in range(self.player_num):
            logging.debug(f"Robber attack. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")
            if pos.players[i].resources.total() > 7:
                to_discard = self.policies[i].choose_discard(pos)
                pos.players[i].discard_half(to_discard)
                logging.debug(f"Cards discarded. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")

        # then, must ask policy what to do with the robber, and then resolve the robber
        victim, location = self.policies[pos.current_turn].choose_robber(pos)
        self.move_robber(pos, pos.current_turn, victim, location)

    def largest_army(self, pos):
        if pos.players[pos.current_turn].army > pos.largest_army:
            if pos.largest_army_owner != -1:
                pos.players[pos.largest_army_owner].points -= 2
            pos.players[pos.current_turn].points += 2
            pos.largest_army_owner = pos.current_turn
            pos.largest_army = pos.players[pos.current_turn].army
            logging.info(f"New largest army: Player {pos.current_turn} with {pos.largest_army} knights!")
    
    def longest_road(self, pos):
        # calculate longest road for this player only
        player_road = pos.players[pos.current_turn].longest_road(pos)
        if player_road > pos.longest_road:
            if pos.longest_road_owner != -1:
                pos.players[pos.longest_road_owner].points -= 2
            pos.players[pos.current_turn].points += 2
            pos.longest_road_owner = pos.current_turn
            pos.longest_road = player_road
            logging.info(f"New longest road! Player {pos.current_turn} with road length {player_road}!")

    def longest_road_reset(self, pos):
        # calculates longest road for ALL players and resolves according to rules
        # only to be used when a settlement cuts off a road
        logging.info("Longest road reset!")
        if pos.longest_road_owner == -1:
            return
        
        lens = {player.id: player.longest_road(pos) for player in pos.players}
        maxes, val = max_values_dict(lens)
        if val < 5:
            pos.longest_road = 4
            pos.longest_road_owner = -1
            pos.players[pos.longest_road_owner].points -= 2
        else: 
            pos.longest_road = val
            pos.players[pos.longest_road_owner].points -= 2
            if pos.longest_road_owner not in maxes:
                if len(maxes) > 1:
                    pos.longest_road_owner = -1
                else:
                    pos.longest_road_owner = maxes[0]
                    pos.players[pos.longest_road_owner].points += 2

    def build_init_settlement(self, pos, player, id):
        pos.get_colony(id).initial_build(pos, player.id)
        player.colonies.append(id)
        player.points += 1
        player.update_dice(pos, pos.get_colony(id))
        player.update_trade(pos, pos.get_colony(id))
        
        # collect resources, but only on the second settle
        if len(player.colonies) == 2:
            for resource in pos.get_colony(id).get_resources(pos):
                player.resources[resource] += 1 

        if self.show_display:
            self.display.draw_colony(id, player.color)
        logging.debug(f"Init settlement built in {id} for Player {player.id}.")

    def build_init_road(self, pos, player, id, settlement):
        pos.get_road(id).initial_build(pos, player.id, settlement, id)
        player.roads.append(id)

        if self.show_display:
            self.display.draw_road(id, player.color)
        logging.debug(f"Init road built in {id} for Player {player.id}.")

    def build_road(self, pos, player, id, free=False):
        if not free:
            player.resource_gate(road_cost)
            player.resources.subtract(road_cost)

        pos.get_road(id).build(pos, player.id)
        player.roads.append(id)
        pos.road_calc = True

        if self.show_display:
            self.display.draw_road(id, player.color)
        logging.debug(f"Road built in {id}. Player {player.id} resources: {resources_str(player.resources)}")

    def build_settlement(self, pos, player, id):
        player.resource_gate(settlement_cost)
        if player.settlement_supply <= 0:
            raise OutOfSettlementsError(player.id)
        player.resources.subtract(settlement_cost)

        colony = pos.get_colony(id)
        colony.build(pos, player.id)
        player.colonies.append(id)
        player.update_dice(pos, colony)
        player.update_trade(pos, colony)

        player.settlement_supply -= 1
        player.points += 1

        # If our settlement cuts off a road, recalculate all longest roads
        roads = pos.get_roads(pos.get_colony(id).roads)
        owners = [road.owner for road in roads if road.owner != -1]
        most_common = Counter(owners).most_common(1)[0]
        if most_common[1] >= 2 and most_common[0] != player.id:
            pos.road_reset = True
        
        if self.show_display:
            self.display.draw_colony(id, player.color)
        logging.debug(f"Settlement built in {id}. Player {player.id} resources: {resources_str(player.resources)}")

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

        if self.show_display:
            self.display.draw_city(id, player.color)
        logging.debug(f"City built in {id}. Player {player.id} resources: {resources_str(player.resources)}")

    def draw_dev_card(self, pos, player):
        player.resource_gate(dev_card_cost)
        card = pos.draw_dev_card()
        player.resources.subtract(dev_card_cost)
        player.dev_cards[card] += 1
        logging.debug(f"Dev card {DevCard(card).name} drawn. Player {player.id} resources: {resources_str(player.resources)}")

    def use_dev_card(self, pos, player, card, **kwargs):
        if player.dev_cards[card] <= 0:
            raise DontHaveCardError(player.id, card)
        play_card(self, pos, player, card, **kwargs)
        player.dev_cards[card] -= 1
        for i in range(self.player_num):
            logging.debug(f"Dev card used. Player {pos.players[i].id} resources: {resources_str(pos.players[i].resources)}")

    def move_robber(self, pos, player_id, victim_id, location):
        prev_location = pos.robber.location
        location = pos.get_hex(location)
        if victim_id == player_id or victim_id not in location.get_players(pos):
            raise CannotStealError(player_id, victim_id, location.id)
        pos.robber.location = location.id
        logging.info(f"Robber moved from {prev_location} to {location.id}.")

        self.steal_resource(pos, player_id, victim_id)
        # move robber display
        if self.show_display:
            self.display.draw_hex(prev_location)
            self.display.add_robber(location.id)

    def steal_resource(self, pos, player_id, victim_id):
        # steal a resource
        resources = counter_to_list(pos.players[victim_id].resources)
        if resources:
            stolen = random.choice(resources)
            logging.debug(f"Resource stolen from player {victim_id}: {stolen}")
            pos.players[player_id].resources.update([stolen])
            pos.players[victim_id].resources.subtract([stolen])
            logging.debug(f"Player {pos.players[player_id].id} resources: {resources_str(pos.players[player_id].resources)}")
            logging.debug(f"Player {pos.players[victim_id].id} resources: {resources_str(pos.players[victim_id].resources)}")

    def trade_resource(self, pos, player, give, receive):
        if player.trade[give] > player.resources[give]:
            raise ValueError(f"Player {player.id} cannot trade {player.trade[give]} {give}!")
        player.resources[give] -= player.trade[give]
        player.resources[receive] += 1
        logging.debug(f"Player {player.id} traded {player.trade[give]} {give} for 1 {receive}!")
