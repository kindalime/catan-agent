import copy
from resources import *
from utils import *
from enum import Enum

class State(Enum):
    INIT_SETTLE_ONE = 1
    INIT_SETTLE_TWO = 2
    MY_DICE = 3
    OTHER_DICE = 4
    DEV_CARD = 5
    BUILDING = 6
    MY_DISCARD = 7
    OTHER_DISCARD = 8
    MY_ROBBER = 9


class Node:
    def __init__(self, pos, depth=None, state=None):
        self.views = 0
        self.payoff = 0
        self.action = None # previous action done to get to this node.
        self.state = state

        if not depth:
            self.depth = pos.current_turn # TODO: change
        else:
            self.depth = depth

    def __str__(self):
        return f"Node with {self.views} views, {self.payoff} payoff, {self.state} state, {self.depth} depth."

class NodeCalc:
    def __init__(self, id, catan):
        self.id = id # can't use for any state variables!
        self.catan = catan

    def get_player(self, pos):
        return pos.players[self.id]

    def find_state(self, pos, node):
        if len(pos.players[self.id].colonies) == 0:
            return State.INIT_SETTLE_ONE

        if len(pos.players[self.id].colonies) == 1:
            return State.INIT_SETTLE_TWO

        if not pos.gathered:
            if pos.current_turn == self.id:
                return State.MY_DISCARD
            else:
                return State.OTHER_DISCARD

        return State.BUILDING

    def get_children(self, pos, node):
        if node.state == None:
            node.state = self.find_state(pos, node)

        match node.state:
            case State.INIT_SETTLE_ONE:
                return self.init_settle_one(pos, node)
            case State.INIT_SETTLE_TWO:
                return self.init_settle_two(pos, node)
            case State.MY_DICE:
                return self.my_dice(pos, node)
            case State.OTHER_DICE:
                return self.other_dice(pos, node)
            # case State.DEV_CARD:
            #     return self.dev_card(pos, node)
            case State.BUILDING:
                return self.building(pos, node)
            case State.MY_DISCARD:
                return self.my_discard(pos, node)
            case State.OTHER_DISCARD:
                return self.other_discard(pos, node)
            case State.STEAL:
                return self.steal(pos, node)
            case _:
                raise ValueError("Bad node state!")

    def init_settle(self, pos, node):
        children = []
        actions = []
        for settle in self.get_player(pos).possible_init_settlements(pos):
            settle_child = copy.deepcopy(pos)
            self.catan.build_init_settlement(settle_child, self.get_player(pos), settle)
            for road in settle_child.players[self.id].possible_init_roads(settle_child, settle):
                road_child = copy.deepcopy(settle_child)
                self.catan.build_init_road(road_child, settle_child.players[self.id], road, settle)
                children.append(road_child)
                actions.append([settle, road])
        return children, actions

    def init_settle_one(self, pos, node):
        children, actions = self.init_settle(pos, node)
        nodes = {}
        for i in range(len(children)):
            child_node = self.init_settle_one_play(children[i], node)
            child_node.action = actions[i]
            nodes[children[i]] = child_node
        return nodes

    def init_settle_one_play(self, pos, node):
        for i in range(self.id+1, self.catan.player_num):
            curr_player = (pos.current_turn + i) % self.catan.player_num
            col = self.catan.policies[curr_player].init_settle(pos)
            self.catan.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.catan.policies[curr_player].init_road(pos, col)
            self.catan.build_init_road(pos, pos.players[curr_player], road, col)

        for i in range(self.catan.player_num-1, self.id-1, -1):
            curr_player = (pos.current_turn + i) % self.catan.player_num
            col = self.catan.policies[curr_player].init_settle(pos)
            self.catan.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.catan.policies[curr_player].init_road(pos, col)
            self.catan.build_init_road(pos, pos.players[curr_player], road, col)

        node = copy.copy(node)
        node.state = State.INIT_SETTLE_TWO
        return node

    def init_settle_two(self, pos, node):
        children, actions = self.init_settle(pos, node)
        nodes = {}
        for i in range(len(children)):
            child_node = self.init_settle_two_play(children[i], node)
            child_node.action = actions[i]
            nodes[children[i]] = child_node
        return nodes

    def init_settle_two_play(self, pos, node):
        for i in range(self.id-1, -1, -1):
            curr_player = (pos.current_turn + i) % self.catan.player_num
            col = self.catan.policies[curr_player].init_settle(pos)
            self.catan.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.catan.policies[curr_player].init_road(pos, col)
            self.catan.build_init_road(pos, pos.players[curr_player], road, col)

        node = copy.copy(node)
        if node.current_turn == self.id:
            node.state = State.MY_DICE
        else:
            node.state = State.OTHER_DICE
        return node

    # def dev_card(self, pos, node):
    #     children = []
    #     combos = get_all_combos(pos.players[self.id].dev_cards)
    #     for combo in combos:
    #         combo = Counter(combo)

    #         child = copy.deepcopy(pos)
    #         for i in range(len(combo[DevCard.VP])):
    #             self.dev_card_vp(child)
    #         new_children = [child]

    #         for i in range(len(combo[DevCard.ROAD])):
    #             new_children = merge_list([self.dev_card_road(c) for c in new_children])

    #         for i in range(len(combo[DevCard.PLENTY])):
    #             new_children = merge_list([self.dev_card_plenty(c) for c in new_children])

    #         for i in range(len(combo[DevCard.MONOPOLY])):
    #             new_children = merge_list([self.dev_card_monopoly(c) for c in new_children])

    #         for i in range(len(combo[DevCard.KNIGHT])):
    #             new_children = merge_list([self.dev_card_knight(c) for c in new_children])

    #         children.extend(new_children)

    #     nodes = {}
    #     for child in children:
    #         child_node = self.dev_card_children_play(pos, node)
    #         nodes[child] = child_node
    #     return children

    # def dev_card_children_play(pos, node):
    #     # doesn't play anything - goes directly to building stage
    #     node = copy.copy(node)
    #     node.state = State.BUILDING
    #     return node

    # def dev_card_vp(self, pos):
    #     self.catan.use_dev_card(pos, pos.players[self.id], DevCard.VP)

    # def dev_card_road(self, pos): # max 2
    #     # Max 2 roads. Copied from above.
    #     queue = deque([pos, 0, ()])
    #     visited = set()

    #     # Get all possible 2-road combinations.
    #     while queue:
    #         node = queue.popleft()
    #         if node[2] not in visited:
    #             if node[1] < 2:
    #                 visited.add(node[2])
    #                 possible_roads = pos.players[self.id].possible_roads(roads)
    #                 for r in possible_roads:
    #                     new_pos = copy.deepcopy(p)
    #                     self.catan.build_road(new_pos, pos.players[self.id], r, free=True)
    #                     queue.append([new_pos, node[1] + 1, node[2] + (r)])

    #     # Play the dev card for each combo
    #     children = []
    #     for c in list(visited):
    #         child = copy.deepcopy(pos)
    #         if len(c) == 1:
    #             self.catan.use_dev_card(child, child.players[self.id], DevCard.ROAD, first=c[0], second=None)
    #         elif len(c) == 2:
    #             self.catan.use_dev_card(child, child.players[self.id], DevCard.ROAD, first=c[0], second=c[1])
    #         children.append(child)
    #     return children

    # def dev_card_plenty(self, pos): # max 2
    #     combos = itertools.combinations_with_replacement(all_resources, 2)
    #     children = []
    #     for c in combos:
    #         child = copy.deepcopy(pos)
    #         self.catan.use_dev_card(child, child.players[self.id], DevCard.PLENTY, first=c[0], second=c[1])
    #         children.append(child)
    #     return children

    # def dev_card_monopoly(self, pos): # max 2
    #     children = []
    #     for c in all_resources:
    #         child = copy.deepcopy(pos)
    #         self.catan.use_dev_card(child, child.players[self.id], DevCard.MONOPOLY, first=c[0], second=c[1])
    #         children.append(child)
    #     return children

    # def dev_card_knight(self, pos):
    #     combos = pos.players[self.id].possible_robber(pos)
    #     children = []
    #     for c in combos:
    #         child = copy.deepcopy(pos)
    #         self.catan.use_dev_card(child, child.players[self.id], DevCard.KNIGHT, victim=c[0], location=c[1])
    #         children.append(child)
    #     return children

    # def building(self, pos, node):
    #     building_children = []
    #     for combo in combos:
    #         children = [pos]
    #         if combo["road"] > 0:
    #             new_children = []
    #             for child in children:
    #                 new_children.extend(self.road_children(child, combo["road"]))
    #             children = new_children

    #         if combo["settlement"] > 0:
    #             new_children = []
    #             for child in children:
    #                 new_children.extend(self.settlement_children(child, combo["settlement"]))
    #             children = new_children

    #         if combo["city"] > 0:
    #             new_children = []
    #             for child in children:
    #                 new_children.extend(self.city_children(child, combo["city"]))
    #             children = new_children

    #         if combo["dev"] > 0:
    #             for child in children:
    #                 self.dev_children(child, combo["dev"])

    #     nodes = {}
    #     for child in children:
    #         child_node = self.building_play(child, node)
    #         nodes[child] = child_node
    #     return children

    def building(self, pos, node):
        children = {}
        if pos.players[self.id].resource_check(city_cost):
            for city in pos.players[self.id].possible_cities(pos):
                child = copy.deepcopy(pos)
                new_node = copy.copy(node)
                self.catan.build_city(child, pos.players[self.id], city)
                new_node.action = ["city", city]
                children[child] = new_node

        if pos.players[self.id].resource_check(road_cost):
            for road in pos.players[self.id].possible_roads(pos):
                child = copy.deepcopy(pos)
                new_node = copy.copy(node)
                self.catan.build_road(child, pos.players[self.id], road)
                new_node.action = ["road", road]
                children[child] = new_node
            
        if pos.players[self.id].resource_check(settlement_cost):
            for settle in pos.players[self.id].possible_settlements(pos):
                child = copy.deepcopy(pos)
                new_node = copy.copy(node)
                self.catan.build_settle(child, pos.players[self.id], settle)
                new_node.action = ["settle", settle]
                children[child] = node
        
        # add the node for doing nothing and ending turn
        end_child = copy.deepcopy(pos)
        end_node = copy.copy(node)
        end_node.action = ["end", None]
        self.building_play(end_state, end_node)
        children[end_child] = end_node
        return children


    # def get_action_combos(self, pos):
    #     # Given our resources, what actions can we do?
    #     resources = pos.players[self.id].resources.copy()
    #     combos = [[resources, empty_actions()]]
    #     actions = [
    #         ["city", city_cost],
    #         ["settlement", settlement_cost],
    #         ["dev", dev_card_cost],
    #         ["road", road_cost]
    #     ]
        
    #     for action in actions:
    #         new_combos = []
    #         for combo in combos:
    #             curr_resources = combo[0].copy()
    #             curr_actions = combo[1].copy()
    #             while resource_check(curr_resources, action[1]):
    #                 curr_resources.subtract(action[1])
    #                 curr_actions[actions[0]] += 1
    #                 new_combos.append([curr_resources.copy(), curr_actions.copy()])
    #         combos.extend(new_combos)

    #     return [combo[1] for combo in combos]

    # def road_children(self, pos, possible):
    #     children = []
    #     # [pos, depth, (road IDs)]
    #     queue = deque([pos, 0, ()])
    #     visited = set()

    #     while queue: # Need to update roads after every road placed. BFS
    #         node = queue.popleft()
    #         if node[2] not in visited:
    #             visited.add(node[2])
                
    #             if node[1] < possible:
    #                 possible_roads = pos.players[self.id].possible_roads(roads)
    #                 for r in possible_roads:
    #                     child = copy.deepcopy(pos)
    #                     self.catan.build_road(child, pos.players[self.id], r)
    #                     queue.append([child, node[1] + 1, node[2] + (r)])
    #             elif node[1] == possible:
    #                 children.append(node[0])

    #     return children

    # def settlement_children(self, pos, possible):
    #     children = []
    #     # [pos, depth, (settlement IDs)]
    #     queue = deque([pos, 0, ()])
    #     visited = set()

    #     while queue:
    #         node = queue.popleft()
    #         if node[2] not in visited:
    #             children.append(node[0])
    #             visited.add(node[2])
                
    #             if node[1] < possible:
    #                 possible_settlements = pos.players[self.id].possible_settlements(settlements)
    #                 for s in possible_settlements:
    #                     child = copy.deepcopy(pos)
    #                     self.catan.build_settlement(child, child.players[self.id], s)
    #                     queue.append([child, node[1] + 1, node[2] + (s)])
    #             elif node[1] == possible:
    #                 children.append(node[0])

    #     return children

    # def city_children(self, pos, possible):
    #     actions = pos.players[self.id].possible_cities(pos)
    #     combos = itertools.combinations(actions, max(len(actions), possible))
    #     children = []
    #     for combo in combos:
    #         child = copy.deepcopy(pos)
    #         for city in combo:
    #             self.catan.build_city(child, child.players[self.id], c)
    #     children.append(child)
    #     return children

    # def dev_children(self, pos, possible):
    #     for p in possible:
    #         self.catan.draw_dev_card(pos, self.id)
    #     return pos

    def building_play(self, pos, node):
        # After building phase, the turn is over. Next node is a random node.
        node = copy.copy(node)
        self.catan.end_of_turn(pos)
        node.state = State.OTHER_DICE
        return node

    def play_other_turn(self, pos, node):
        # ask policy what it wants to do for a specific player
        self.catan.policies[pos.current_turn].take_turn(pos)
        self.catan.end_of_turn(pos)
        
        if pos.current_turn == self.id:
            node.state = State.MY_DICE
        else:
            node.state = State.OTHER_DICE
        return node

    def discard(self, pos):
        resources = pos.players[self.id].resources
        combos = unique_combinations(resources, resources.total() // 2)
        children = []
        discards = []
        for c in combos:
            child = copy.deepcopy(pos)
            child.players[self.id].discard_half(c)
            children.append(child)
            discards.append(c)
        return children, discards

    def other_discard(self, pos, node):
        children, discards = self.discard(pos)
        nodes = {}
        for i in range(len(children)):
            child_node = self.play_other_turn(children[i], node)
            nodes[children[i]] = child_node
            nodes.action = discards[i]
        return nodes

    def my_discard(self, pos, node):
        children, discards = self.discard(pos)
        nodes = {}
        for i in range(len(children)):
            child_node = self.my_discard_play(children[i], node)
            nodes[robber_child] = child_node
            nodes.action = discards[i]
        return nodes

    def my_discard_play(pos, node):
        # doesn't play anything - goes directly to my robber stage
        node = copy.copy(node)
        node.state = State.MY_ROBBER
        return node

    def my_robber(self, pos, node):
        children, actions = self.robber_children(pos)
        nodes = {}
        for i in range(len(children)):
            child_node = self.my_robber_play(children[i], node)
            nodes[robber_child] = child_node
            nodes.action = discards[i]
        return nodes

    def my_robber_play(pos, node):
        # doesn't play anything - goes directly to build stage
        node = copy.copy(node)
        node.state = State.BUILDING
        return node

    def other_dice(pos, node):
        nodes = {}
        pos.gathered = True

        for dice in range(2, 13):
            child = copy.deepcopy(pos)
            if dice != 7: 
                # gather resources as usual
                for player in child.players:
                    player.collect_resources(child, dice)
                # play the turn
                child_node = self.play_other_turn(child, node)
                child_node.dice = dice
                nodes[child] = child_node

        # Dice = 7
        child = copy.deepcopy(pos)
        self.other_player_discard(child)
        child_node = copy.copy(node)
        print(child.players[self.id].resources.total())
        if child.players[self.id].resources.total() > 7:
            child_node.state = State.OTHER_DISCARD
        else:
            child_node = self.play_other_turn(child, child_node)
        child_node.dice = 7
        nodes[child] = child_node

        return nodes

    def my_dice(pos, node):
        nodes = {}
        pos.gathered = True

        for dice in range(2, 13):
            child = copy.deepcopy(pos)
            if dice != 7: 
                # gather resources as usual
                for player in child.players:
                    player.collect_resources(child, dice)
                # set to dev
                child_node = copy.copy(node)
                child_node.state = State.BUILDING
                child_node.dice = dice
                nodes[child] = child_node

        # Dice = 7
        child = copy.deepcopy(pos)
        self.other_player_discard(child)
        child_node = copy.copy(node)
        print(child.players[self.id].resources.total())
        if child.players[self.id].resources.total() > 7:
            child_node.state = State.MY_DISCARD
        else:
            child_node.state = State.BUILDING
        child_node.dice = 7
        nodes[child] = child_node

        return nodes

    def other_player_discard(self, pos):
        # Tell other players to discard their cards.
        for i in range(self.catan.player_num):
            if i != self.id and pos.players[i].resources.total() > 7:
                to_discard = self.catan.policies[i].choose_discard(pos)
                pos.players[i].discard_half(to_discard)

    # def robber_attack(self, pos):
    #     # robber attack - must ask policies for discard, and then do discards
    #     if pos.current_turn == player.id: # create new children
    #         children = self.robber_children(child)
    #     else:
    #         # then, must ask policy what to do with the robber, and then resolve the robber
    #         victim, location = self.catan.policies[pos.current_turn].choose_robber(pos)
    #         self.catan.move_robber(pos, pos.current_turn, victim, location)
    #     return children

    def robber_children(self, pos):
        children = []
        actions = []
        for h in pos.board.hexes:
            players = h.get_players()
            if self.id in players:
                continue

            for p in players:
                child = copy.deepcopy(pos)
                self.catan.move_robber(child, pos.current_turn, p, h.id)
                children.append(child)
                actions.append(p, h.id)
        return children, actions
