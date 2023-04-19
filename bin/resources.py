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

all_resources = [Resource.BRICK, Resource.SHEEP, Resource.STONE, Resource.WOOD, Resource.WHEAT]

def resources_str(data):
    return f"Wood: {data[Resource.WOOD]}, Brick: {data[Resource.BRICK]}, Sheep: {data[Resource.SHEEP]}, Wheat: {data[Resource.WHEAT]}, Stone: {data[Resource.STONE]}"

def empty_resources():
    return Counter({
        Resource.WOOD: 0,
        Resource.BRICK: 0,
        Resource.SHEEP: 0,
        Resource.WHEAT: 0,
        Resource.STONE: 0,
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

def resource_check(resources, cost):
    for resource in cost:
        if cost[resource] > resources[resource]:
            return False
    return True

def resource_gate(resources, cost):
    for resource in cost:
        if cost[resource] > resources[resource]:
            raise NotEnoughResourcesError(self.id, resource, cost[resource], resources[resource])

pip_dict = {
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    8: 5,
    9: 4,
    10: 3,
    11: 2,
    12: 1,
}