class NodeCalc:
    def __init__(self, id, catan):
        self.id = id # can't use for any state variables!
        self.catan = catan

    def init_settle(self, pos, node):
        children = []
        for settle in pos.player[self.id].possible_init_settlements(pos):
            settle_child = copy.deepcopy(pos)
            self.catan.build_init_settlement(settle_child, self.id, settle)
            for road in pos.player[self.id].possible_init_roads(pos, settle):
                road_child = copy.deepcopy(settle_child)
                self.catan.build_init_road(road_child, self.id, road, settle)
                children.append(road_child)
        return children

    def init_settle_one(self, pos, node):
        children = self.init_settle(pos, node)
        nodes = {}
        for child in children:
            child_node = self.init_settle_one_play(child, node)
            nodes[child] = child_node
        return nodes

    def init_settle_one_play(self, pos, node):
        for i in range(self.id+1, self.catan.player_num):
            curr_player = (pos.current_turn + i) % self.catan.player_num
            col = self.catan.policies[curr_player].init_settle(pos)
            self.catan.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.catan.policies[curr_player].init_road(pos, col)
            self.catan.build_init_road(pos, pos.players[curr_player], road, col)

        for i in range(self.player_num-1, self.id-1, -1):
            curr_player = (pos.current_turn + i) % self.catan.player_num
            col = self.catan.policies[curr_player].init_settle(pos)
            self.catan.build_init_settlement(pos, pos.players[curr_player], col)

            road = self.catan.policies[curr_player].init_road(pos, col)
            self.catan.build_init_road(pos, pos.players[curr_player], road, col)

        node = copy.copy(node)
        node.state = State.INIT_SETTLE_TWO
        return node

    def init_settle_two(self, pos, node):
        children = self.init_settle(pos, node)
        nodes = {}
        for child in children:
            child_node = self.init_settle_two_play(child, node)
            nodes[child] = child_node
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

    def dev_card(self, pos, node):
        children = []
        combos = get_all_combos(pos.players[self.id].dev_cards)
        for combo in combos:
            combo = Counter(combo)

            child = copy.deepcopy(pos)
            for i in range(len(combo[DevCard.VP])):
                self.dev_card_vp(child)
            new_children = [child]

            for i in range(len(combo[DevCard.ROAD])):
                new_children = merge_list([self.dev_card_road(c) for c in new_children])

            for i in range(len(combo[DevCard.PLENTY])):
                new_children = merge_list([self.dev_card_plenty(c) for c in new_children])

            for i in range(len(combo[DevCard.MONOPOLY])):
                new_children = merge_list([self.dev_card_monopoly(c) for c in new_children])

            for i in range(len(combo[DevCard.KNIGHT])):
                new_children = merge_list([self.dev_card_knight(c) for c in new_children])

            children.extend(new_children)

        nodes = {}
        for child in children:
            child_node = self.dev_card_children_play(pos, node)
            nodes[child] = child_node
        return children

    def dev_card_children_play(pos, node):
        # doesn't play anything - goes directly to building stage
        node = copy.copy(node)
        node.state = State.BUILDING
        return node

    def dev_card_vp(self, pos):
        self.catan.use_dev_card(pos, pos.players[self.id], DevCard.VP)

    def dev_card_road(self, pos): # max 2
        # Max 2 roads. Copied from above.
        queue = deque([pos, 0, ()])
        visited = set()

        # Get all possible 2-road combinations.
        while queue:
            node = queue.popleft()
            if node[2] not in visited:
                if node[1] < 2:
                    visited.add(node[2])
                    possible_roads = pos.players[self.id].possible_roads(roads)
                    for r in possible_roads:
                        new_pos = copy.deepcopy(p)
                        self.catan.build_road(new_pos, pos.players[self.id], r)
                        queue.append([new_pos, node[1] + 1, node[2] + (r)])

        # Play the dev card for each combo
        children = []
        for c in list(visited):
            child = copy.deepcopy(pos)
            if len(c) == 1:
                self.catan.use_dev_card(child, pos.players[self.id], DevCard.ROAD, first=c[0], second=None)
            elif len(c) == 2:
                self.catan.use_dev_card(child, pos.players[self.id], DevCard.ROAD, first=c[0], second=c[1])
            children.append(child)
        return children

    def dev_card_plenty(self, pos): # max 2
        combos = itertools.combinations_with_replacement(all_resources, 2)
        children = []
        for c in combos:
            child = copy.deepcopy(pos)
            self.catan.use_dev_card(child, pos.players[self.id], DevCard.PLENTY, first=c[0], second=c[1])
            children.append(child)
        return children

    def dev_card_monopoly(self, pos): # max 2
        children = []
        for c in all_resources:
            child = copy.deepcopy(pos)
            self.catan.use_dev_card(child, pos.players[self.id], DevCard.MONOPOLY, first=c[0], second=c[1])
            children.append(child)
        return children

    def dev_card_knight(self, pos):
        combos = pos.players[self.id].possible_robber(pos)
        children = []
        for c in combos:
            child = copy.deepcopy(pos)
            self.catan.use_dev_card(child, pos.players[self.id], DevCard.KNIGHT, victim=c[0], location=c[1])
            children.append(child)
        return children

    def building(self, pos, node):
        combos = self.get_action_combos(pos)
        building_children = []
        for combo in combos:
            children = [pos]
            if combo["road"] > 0:
                new_children = []
                for child in children:
                    new_children.extend(self.road_children(child, combo["road"]))
                children = new_children

            if combo["settlement"] > 0:
                new_children = []
                for child in children:
                    new_children.extend(self.settlement_children(child, combo["settlement"]))
                children = new_children

            if combo["city"] > 0:
                new_children = []
                for child in children:
                    new_children.extend(self.city_children(child, combo["city"]))
                children = new_children

            if combo["dev"] > 0:
                for child in children:
                    self.dev_children(child, combo["dev"])

        nodes = {}
        for child in children:
            child_node = self.building_play(child, node)
            nodes[child] = child_node
        return children

    def get_action_combos(self, pos):
        # Given our resources, what actions can we do?
        resources = pos.players[self.id].resources.copy()
        combos = [[resources, empty_actions()]]
        actions = [
            ["city", city_cost],
            ["settlement", settlement_cost],
            ["dev", dev_card_cost],
            ["road", road_cost]
        ]
        
        for action in actions:
            new_combos = []
            for combo in combos:
                curr_resources = combo[0].copy()
                curr_actions = combo[1].copy()
                while resource_check(curr_resources, action[1]):
                    curr_resources.subtract(action[1])
                    curr_actions[actions[0]] += 1
                    new_combos.append([curr_resources.copy(), curr_actions.copy()])
            combos.extend(new_combos)

        return [combo[1] for combo in combos]

    def road_children(self, pos, possible):
        children = []
        # [pos, depth, (road IDs)]
        queue = deque([pos, 0, ()])
        visited = set()

        while queue: # Need to update roads after every road placed. BFS
            node = queue.popleft()
            if node[2] not in visited:
                children.append(node[0])
                visited.add(node[2])
                
                if node[1] < possible:
                    possible_roads = pos.players[self.id].possible_roads(roads)
                    for r in possible_roads:
                        new_pos = copy.deepcopy(pos)
                        self.catan.build_road(new_pos, pos.players[self.id], r)
                        queue.append([new_pos, node[1] + 1, node[2] + (r)])

        return children

    def settlement_children(self, pos, possible):
        children = []
        # [pos, depth, (settlement IDs)]
        queue = deque([pos, 0, ()])
        visited = set()

        while queue:
            node = queue.popleft()
            if node[2] not in visited:
                children.append(node[0])
                visited.add(node[2])
                
                if node[1] < possible:
                    possible_settlements = pos.players[self.id].possible_settlements(settlements)
                    for s in possible_settlements:
                        child = copy.deepcopy(pos)
                        self.catan.build_settlement(child, pos.players[self.id], s)
                        queue.append([child, node[1] + 1, node[2] + (s)])

        return children

    def city_children(self, pos, possible):
        actions = pos.players[self.id].possible_cities(pos)
        combos = itertools.combinations(actions, max(len(actions), possible))
        children = []
        for p in actions:
            for c in combos:
                child = copy.deepcopy(pos)
                self.catan.build_city(child, pos.players[self.id], c)
            children.append(child)
        return children

    def dev_children(self, pos, possible):
        for p in possible:
            self.catan.draw_dev_card(pos, self.id)
        return pos

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
        for c in combos:
            child = copy.deepcopy(pos)
            child.players[i].discard_half(c)
            children.append(child)
        return children

    def other_discard(self, pos, node):
        children = self.discard(pos)
        nodes = {}
        for child in children:
            child_node = self.play_other_turn(child, node)
            nodes[child] = child_node
        return children

    def my_discard(self, pos, node):
        children = self.discard(pos)
        nodes = {}
        for child in children:
            for robber_child in self.robber_attack(child):
                child_node = self.my_discard_play(child, node)
                nodes[robber_child] = child_node
        return children

    def my_discard_play(pos, node):
        # doesn't play anything - goes directly to building stage
        node = copy.copy(node)
        node.state = State.DEV_CARD
        return node

    def other_dice(pos, node):
        nodes = {}
        pos.gathered = True

        for i in range(2, 13):
            child = copy.deepcopy(pos)
            if dice != 7: 
                # gather resources as usual
                for player in pos.players:
                    player.collect_resources(child, dice)
                # play the turn
                child_node = self.play_other_turn(child, node)
                child_node.dice = i
                nodes[child] = child_node

        # Dice = 7
        self.other_player_discard(pos)
        child_node = copy.copy(node)
        if pos.players[self.id].resources.total() > 7:
            child_node.state = State.OTHER_DISCARD
        else:
            child_node = self.play_other_turn(child, node)
        child_node.dice = 7
        nodes[child] = child_node

        return nodes

    def my_dice(pos, node):
        nodes = {}
        pos.gathered = True

        for i in range(2, 13):
            child = copy.deepcopy(pos)
            if dice != 7: 
                # gather resources as usual
                for player in pos.players:
                    player.collect_resources(child, dice)
                # set to dev
                child_node = copy.copy(node)
                child_node.state = DEV_CARD
                child_node.dice = i
                nodes[child] = child_node

        # Dice = 7
        self.other_player_discard(pos)
        child_node = copy.copy(node)
        if pos.players[self.id].resources.total() > 7:
            child_node.state = State.MY_DISCARD
        else:
            child_node = self.play_other_turn(child, node)
        child_node.dice = 7
        nodes[child] = child_node

        return nodes

    def other_player_discard(self, pos):
        # Tell other players to discard their cards.
        for i in range(self.catan.player_num):
            if i != self.id and pos.players[i].resources.total() > 7:
                to_discard = self.catan.policies[i].choose_discard(pos)
                pos.players[i].discard_half(to_discard)

    def robber_attack(self, pos):
        # robber attack - must ask policies for discard, and then do discards
        if pos.current_turn == player.id: # create new children
            new_children = []
            for child in children:
                new_children.append(self.robber_children(child))
            children = merge_list(new_children)
        else:
            for child in children: # in-place edits
                self.move_robber(child, child.current_turn, victim, location)
                # then, must ask policy what to do with the robber, and then resolve the robber
                victim, location = self.catan.policies[child.current_turn].choose_robber(child)
        return children