from ..resources import *
from ..devcard import *
from policy import CatanPolicy
from abc import ABCMeta, abstractmethod

resource_dict = {
    "wo": Resource.WOOD,
    "br": Resource.BRICK,
    "sh": Resource.SHEEP,
    "wh": Resource.WHEAT,
    "st": Resource.STONE,
}

class HumanPolicy(CatanPolicy):
    def input_num(self):
        while True:
            num = input().strip()
            if num.isnumeric():
                return int(num)
            print("Error: invalid number input!")
    
    def input_res(self):
        while True:
            res = input().strip()
            if res in resource_dict:
                return resource_dict[res]
            print("Error: invalid resource input!")

    def init_settle(self, pos, player):
        print(f"For player {player}, place a settlement.")
        settlement = self.input_num()
        print(f"For player {player}, place a road.")
        road = self.input_num()
        return settlement, road

    def choose_discard(self, pos, player):
        print(f"Discard {player.resources // 2} resources. (wo, br, sh, wh, st)")
        while True:
            owned = player.resources
            resources = input().lower().strip().split()
            for resource in resources:
                if resource not in resource_dict:
                    break
                if resource_dict[resource] not in owned:
                    break
                owned.remove(resource_dict[resource])
        return [resource_dict[resource] for resource in resources]

    def choose_robber(self, pos, player):
        print(f"For player {player}, choose where to place the robber.")
        robber = self.input_num()
        return robber

    def take_turn(self, pos, player):
        print(f"For player {player}, choose your options.")
        while True:
            option = input().lower().strip()
            match option:
                case "help":
                    print("help, dev, settle, city, road, resources, end")
                case "dev":
                    print(player.dev_cards)
                    dev = input().lower().strip()
                    match dev:
                        case "vp":
                            player.use_dev_card(player, DevCard.VP)
                        case "knight":
                            loc = self.input_num()
                            victim = self.input_num()
                            player.use_dev_card(player, DevCard.KNIGHT, location=loc, victim=victim)
                        case "plenty":
                            res1 = self.input_res()
                            res2 = self.input_res()
                            player.use_dev_card(player, DevCard.PLENTY, first=res1, second=res2)
                        case "road":
                            road1 = self.input_num()
                            road2 = self.input_num()
                            player.use_dev_card(player, DevCard.ROAD, road1, road2)
                        case "monopoly":
                            res = self.input_res()
                            player.use_dev_card(player, DevCard.MONOPOLY, res=res)
                        case "back":
                            break
                case "settle":
                    settle = self.input_num()
                    player.build_settlement(settle)
                case "city":
                    city = self.input_num()
                    player.build_city(settle)
                case "road":
                    road = self.input_num()
                    player.build_road(road)
                case "resources":
                    print(player.resources)
                case "end":
                    break
