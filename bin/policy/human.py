from resources import *
from devcard import *
from policy.policy import CatanPolicy
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

    def init_settle(self, pos):
        print(f"For player {self.player.id}, place a settlement.")
        print(f"Possible initial settlements: {self.player.possible_init_settlements(pos)}")
        settlement = self.input_num()
        return settlement

    def init_road(self, pos, settlement):
        print(f"For player {self.player.id}, place a road.")
        print(f"Possible initial roads: {self.player.possible_init_roads(pos, settlement)}")
        road = self.input_num()
        return road

    def choose_discard(self, pos):
        print(f"Discard {self.player.resources // 2} resources. (wo, br, sh, wh, st)")
        while True:
            owned = self.player.resources
            resources = input().lower().strip().split()
            for resource in resources:
                if resource not in resource_dict:
                    break
                if resource_dict[resource] not in owned:
                    break
                owned.remove(resource_dict[resource])
        return [resource_dict[resource] for resource in resources]

    def choose_robber(self, pos):
        print(f"For player {self.player}, choose where to place the robber.")
        robber = self.input_num()
        return robber

    def take_turn(self, pos):
        print(f"For player {self.player}, choose your options.")
        while True:
            option = input().lower().strip()
            match option:
                case "help":
                    print("help, dev, settle, city, road, resources, trade, end")
                case "dev":
                    print(self.player.dev_cards)
                    dev = input().lower().strip()
                    match dev:
                        case "vp":
                            self.catan.use_dev_card(pos, self.player, DevCard.VP)
                        case "knight":
                            loc = self.input_num()
                            victim = self.input_num()
                            self.catan.use_dev_card(pos, self.player, DevCard.KNIGHT, location=loc, victim=victim)
                        case "plenty":
                            res1 = self.input_res()
                            res2 = self.input_res()
                            self.catan.use_dev_card(pos, self.player, DevCard.PLENTY, first=res1, second=res2)
                        case "road":
                            road1 = self.input_num()
                            road2 = self.input_num()
                            self.catan.use_dev_card(pos, self.player, DevCard.ROAD, road1, road2)
                        case "monopoly":
                            res = self.input_res()
                            self.catan.use_dev_card(pos, self.player, DevCard.MONOPOLY, res=res)
                        case "back":
                            break
                case "settle":
                    settle = self.input_num()
                    self.catan.build_settlement(pos, settle)
                case "city":
                    city = self.input_num()
                    self.catan.build_city(pos, settle)
                case "road":
                    road = self.input_num()
                    self.catan.build_road(pos, road)
                case "trade":
                    give = self.input_res()
                    receive = self.input_res()
                    self.catan.trade_resource(pos, self.player, give, receive)               
                case "resources":
                    print(self.catan.resources)
                case "end":
                    break
