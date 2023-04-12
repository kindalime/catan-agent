import random
from enum import Enum
from collections import Counter

class Resource(Enum):
    DESERT = 0
    WOOD = 1
    BRICK = 2
    SHEEP = 3
    WHEAT = 4
    STONE = 5

    @classmethod
    def random(self):
        return random.choice(list(self.__members__.values()))

# TODO: CHANGE THIS
def empty_resources():
    return Counter({
        Resource.WOOD: 1,
        Resource.BRICK: 1,
        Resource.SHEEP: 1,
        Resource.WHEAT: 1,
        Resource.STONE: 1,
    })

road_cost = Counter({
    Resource.WOOD: 1,
    Resource.BRICK: 1,
})

settlement_cost = Counter({
    Resource.WOOD: 1,
    Resource.BRICK: 1,
    Resource.SHEEP: 1,
    Resource.WHEAT: 1,
})

city_cost = Counter({
    Resource.WHEAT: 2,
    Resource.STONE: 3,
})

dev_card_cost = Counter({
    Resource.SHEEP: 1,
    Resource.WHEAT: 1,
    Resource.STONE: 1,
})
