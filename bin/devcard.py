import random
from utils import *
from enum import Enum
from collections import Counter

class DevCard:
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

### All dev cards accept a pos and a player (NOT player_id)

def vp_card(catan, pos, player, **kwargs):
    player.points += 1

def road_card(catan, pos, player, **kwargs):
    pos.get_road(kwargs[first]).build(player)
    if second is not None:
        pos.get_road(kwargs[second]).build(player)    

def knight_card(catan, pos, player, **kwargs):
    catan.move_robber(kwargs[location], kwargs[victim])
    player.army += 1
    pos.army_calc = True

def plenty_card(catan, pos, player, **kwargs):
    player[kwargs[first]] += 1
    player[kwargs[second]] += 1

def monopoly_card(catan, pos, player, **kwargs):
    for player in pos.players:
        if player.id != player:
            player.resources[kwargs[res]] += player.resources[kwargs[res]]
            player.resources[kwargs[res]] == 0

def play_card(catan, pos, player, card, **kwargs):
    cards = {
        DevCard.KNIGHT: knight_card,
        DevCard.VP: vp_card,
        DevCard.PLENTY: plenty_card,
        DevCard.MONOPOLY: monopoly_card,
        DevCard.ROAD: road_card,
    }
    cards[card](catan, pos, player, **kwargs)
