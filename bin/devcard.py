import random
from utils import *
from enum import Enum
from collections import Counter
import logging

class DevCard(Enum):
    NONE = 0
    VP = 1
    ROAD = 2
    KNIGHT = 3
    PLENTY = 4
    MONOPOLY = 5

def empty_deck():
    return Counter({
        DevCard.KNIGHT: 0,
        DevCard.VP: 0,
        DevCard.PLENTY: 0,
        DevCard.MONOPOLY: 0,
        DevCard.ROAD: 0,
    })


class DevelopmentDeck:
    def __init__(self):
        self.deck = self.init_deck()

    def init_deck(self):
        deck = [
            (DevCard.KNIGHT, 14),
            (DevCard.VP, 5),
            (DevCard.PLENTY, 2),
            (DevCard.MONOPOLY, 2),
            (DevCard.ROAD, 2),
        ]
        deck = counter_to_list(deck)
        random.shuffle(deck)
        return deck

    def draw(self):
        if not self.deck:
            raise OutOfCardsError()
        else:
            return self.deck.pop()

    def is_empty(self):
        return not self.deck

### All dev cards accept a pos and a player (NOT player_id)

def vp_card(catan, pos, player, **kwargs):
    logging.info(f"Player {player.id} plays VP dev card for one points.")
    player.points += 1

def road_card(catan, pos, player, **kwargs):
    logging.info(f"Player {player.id} plays road dev card for roads {kwargs}")
    catan.build_road(pos, player, kwargs['first'], free=True)
    if kwargs['second'] is not None:
        catan.build_road(pos, player, kwargs['second'], free=True)

def knight_card(catan, pos, player, **kwargs):
    logging.info(f"Player {player.id} plays knight dev card on location {kwargs['location']} and steals from {kwargs['victim']}")
    catan.move_robber(pos, player.id, kwargs['victim'], kwargs['location'])
    player.army += 1
    pos.army_calc = True

def plenty_card(catan, pos, player, **kwargs):
    logging.info(f"Player {player.id} plays plenty dev card for resources {kwargs['first']}, {kwargs['second']}.")
    player.resources[kwargs['first']] += 1
    player.resources[kwargs['second']] += 1

def monopoly_card(catan, pos, player, **kwargs):
    logging.info(f"Player {player.id} plays monopoly dev card for resource {kwargs['res']}")
    for player in pos.players:
        if player.id != player:
            player.resources[kwargs['res']] += player.resources[kwargs['res']]
            player.resources[kwargs['res']] == 0

def play_card(catan, pos, player, card, **kwargs):
    cards = {
        DevCard.KNIGHT: knight_card,
        DevCard.VP: vp_card,
        DevCard.PLENTY: plenty_card,
        DevCard.MONOPOLY: monopoly_card,
        DevCard.ROAD: road_card,
    }
    cards[card](catan, pos, player, **kwargs)
