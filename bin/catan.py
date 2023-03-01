import copy
import random
from utils import *

from player import Player
from board import Board
from devcard import DevelopmentDeck
from robber import Robber
from position import Position

class Catan:
    def __init__(self, player_num):
        self.player_num = player_num
        self.first_player = random.randint(0, player_num-1)
        self.policies = []
        self.pos = None

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

    def play_turn(self):
        pos = copy(self.pos)

        dice = random.randint(1, 6) + random.randint(1, 6) # roll the dice
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
        pos.robber.move_robber(pos)

    def play_game(self):
        self.begin_game()
        while not self.pos.is_terminal():
            self.pos = self.play_turn()

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
