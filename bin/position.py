class Position:
    def __init__(self, board, players, dev_deck, robber, current_turn, turn_count):
        self.board = board
        self.players = players
        self.dev_deck = dev_deck
        self.robber = robber
        self.current_turn = current_turn
        self.turn_count = turn_count

        self.largest_army = 2
        self.largest_army_owner = -1
        self.longest_road = 4
        self.longest_road_owner = -1

        # these variables aren't used by anything lower than the Catan game
        self.army_calc = False
        self.road_calc = False
        self.road_reset = False

        self.terminal = False
        self.winner = None

    def check_terminal(self, board):
        for player in self.players:
            if player.points >= 10:
                return True
        return False

    def draw_dev_card(self):
        self.dev_deck.draw()

    def get_road(self, id):
        return self.board.roads[id]

    def get_colony(self, id):
        return self.board.colonies[id]

    def get_hex(self, id):
        return self.board.hexes[id]

    def get_roads(self, ids):
        return [self.get_road(id) for id in ids]

    def get_colonies(self, ids):
        return [self.get_colony(id) for id in ids]

    def get_hexes(self, ids):
        return [self.get_hex(id) for id in ids]

    def get_player(self, id):
        return self.players[id]

    def get_robber(self):
        return self.robber.location

    def check_terminal(self):
        if self.current_turn.points >= 10:
            self.terminal = True
            self.winner = self.current_turn
