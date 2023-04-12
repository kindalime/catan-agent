import pygame
from math import sqrt
from resources import Resource

# six hexagon sides to x/y coords, to be used as offsets
hex_shifts = [ 
    [sqrt(3)/2, -.5],
    [sqrt(3)/2, .5],
    [0, 1],
    [-sqrt(3)/2, .5],
    [-sqrt(3)/2, -.5],
    [0, -1],
    [sqrt(3)/2, -.5], # repeat of 0, makes logic simpler
]


class Display:
    """
    Class that does all of the drawing and displaying through the pygame board.
    Whenever the board state changes, commands are sent to this class, which changes the display.
    Class contains dicts for every item class in board.py (Hex, Colony, Road) that maps IDs to polygon coords.
    Then, whenever the game state changes, those coords are used to draw on top of the existing board.
    """

    def __init__(self, board):
        self.window = self.pygame_init()
        self.board = board
        self.hex_dict = self.hex_dict_init()
        self.col_dict = self.colony_dict_init()
        self.road_dict = self.road_dict_init(self.col_dict, board.roads)
        self.board_init()

    def pygame_init(self):
        # start up pygame stuff
        pygame.init()
        window = pygame.display.set_mode((1000, 1000))
        window.fill((255, 255, 255))
        pygame.display.update()
        return window

    # Below three functions mirror the init functions present in the Board class.
    # Present in this class and not that class to separate all pygame functionality.
    def hex_dict_init(self):
        return {
            0: [500-200*sqrt(3)/2, 200],
            1: [500,200],
            2: [500+200*sqrt(3)/2, 200],
            3: [500+300*sqrt(3)/2, 350],
            4: [500+400*sqrt(3)/2, 500],
            5: [500+300*sqrt(3)/2, 650],
            6: [500+200*sqrt(3)/2, 800],
            7: [500,800],
            8: [500-200*sqrt(3)/2, 800],
            9: [500-300*sqrt(3)/2, 650],
            10: [500-400*sqrt(3)/2, 500],
            11: [500-300*sqrt(3)/2, 350],
            12: [500-100*sqrt(3)/2, 350],
            13: [500+100*sqrt(3)/2, 350],
            14: [500+200*sqrt(3)/2, 500],
            15: [500+100*sqrt(3)/2, 650],
            16: [500-100*sqrt(3)/2, 650],
            17: [500-200*sqrt(3)/2, 500],
            18: [500, 500]
        }

    def colony_dict_init(self):
        colonies = {}

        def shift(col, coords, offset):
            colonies[col] = coords.copy()
            coords[0] += offset[0]*100
            coords[1] += offset[1]*100
            return col + 1, coords

        # Outer Ring
        col = 0
        coords = [500 - 150*sqrt(3), 150] # coordinate of colony 0, assuming a 1000px * 1000px canvas
        # each side of the hexagon lattice
        for i in range(6):
            for j in range(2):
                col, coords = shift(col, coords, hex_shifts[i])
                col, coords = shift(col, coords, hex_shifts[i+1])
            col, coords = shift(col, coords, hex_shifts[i])

        # Inner Ring
        coords = [500 - 100*sqrt(3), 300]
        colonies[col] = coords.copy()
        # each side of the hexagon lattice again
        for i in range(6):
            col, coords = shift(col, coords, hex_shifts[i])
            col, coords = shift(col, coords, hex_shifts[i+1])
            col, coords = shift(col, coords, hex_shifts[i])

        # Middle Tile
        coords = [500, 400]
        colonies[col] = coords.copy()
        for i in range(6):
            col, coords = shift(col, coords, hex_shifts[i+1])
        return colonies

    def road_dict_init(self, col_dict, road_objs):
        def endpoints(col1, col2):
            col1 = col_dict[col1]
            col2 = col_dict[col2]

            delta_x = col2[0] - col1[0]
            delta_y = col2[1] - col1[1]
            
            new_col1 = [col1[0] + .15*delta_x, col1[1] + .15*delta_y]
            new_col2 = [col2[0] - .15*delta_x, col2[1] - .15*delta_y]
            return new_col1, new_col2

        roads = {}
        # we know roads are between two existing colonies
        # no need to redo work - already know these connections as well as colony coords
        for road in road_objs:
            roads[road.id] = endpoints(*road.colonies)
        return roads

    def add_robber(self, hex_id):
        coords = self.hex_dict[hex_id]
        # write a big "X" on the hex's number
        pygame.draw.line(self.window, "red", [coords[0]-20, coords[1]-20], [coords[0]+20, coords[1]+20], width=7)
        pygame.draw.line(self.window, "red", [coords[0]+20, coords[1]-20], [coords[0]-20, coords[1]+20], width=7)
        pygame.display.update()

    def draw_colony(self, col_id, color):
        coords = self.col_dict[col_id]
        pygame.draw.circle(self.window, color, coords, 10)
        pygame.display.update()

    def draw_city(self, col_id, color):
        coords = self.col_dict[col_id]
        pygame.draw.circle(self.window, color, coords, 20)
        pygame.display.update()

    def draw_road(self, road_id, color):
        coords = self.road_dict[road_id]
        pygame.draw.line(self.window, color, coords[0], coords[1], width=10)
        pygame.display.update()

    def draw_hex(self, hex_id):
        # also doubles as robber removal - just rewrite the entire hex for now
        resource = self.board.hexes[hex_id].resource
        color_dict = {
            Resource.DESERT: "lightgoldenrod1",
            Resource.WOOD: "springgreen4",
            Resource.BRICK: "sienna3",
            Resource.SHEEP: "cadetblue3",
            Resource.WHEAT: "darkgoldenrod1",
            Resource.STONE: "lightslategray",
        }

        coords = self.hex_dict[hex_id]
        hex_coords = [[coords[0] + hex_shifts[i][0]*90, coords[1] + hex_shifts[i][1]*90] for i in range(6)]
        pygame.draw.polygon(self.window, color_dict[resource], hex_coords)

        # draw the number
        if resource != Resource.DESERT:
            font = pygame.font.Font('freesansbold.ttf', 40)
            text = font.render(str(self.board.hexes[hex_id].number), True, 'black', 'white')
            rect = text.get_rect()
            rect.center = coords
            self.window.blit(text, rect)
        pygame.display.update()

    def board_init(self):
        for i in self.hex_dict:
            self.draw_hex(i)
        
        for i in self.col_dict:
            self.draw_colony(i, "black")

        for i in self.road_dict:
            self.draw_road(i, "black")
