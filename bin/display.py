import pygame
from math import sqrt
from resource import Resource

# six hexagon sides to x/y coords, to be used as offsets
hex_shifts = [ 
    [sqrt(3), -.5],
    [sqrt(3), .5],
    [0, 1],
    [-sqrt(3), .5],
    [-sqrt(3), -.5],
    [0, -1],
    [sqrt(3), -.5], # repeat of 0, makes logic simpler
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
        self.road_dict = self.road_dict_init(self.col_dict, roads)
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
            0: [500-200*sqrt(3), 200],
            1: [500,200],
            2: [500+200*sqrt(3), 200],
            3: [500+300*sqrt(3), 350],
            4: [500+400*sqrt(3), 500],
            5: [500+300*sqrt(3), 650],
            6: [500+200*sqrt(3), 800],
            7: [500,800],
            8: [500-200*sqrt(3), 800],
            9: [500-300*sqrt(3), 650],
            10: [500-400*sqrt(3), 500],
            11: [500-300*sqrt(3), 350],
            12: [500-100*sqrt(3), 350],
            13: [500+100*sqrt(3), 350],
            14: [500+200*sqrt(3), 500],
            15: [500+100*sqrt(3), 650],
            16: [500-100*sqrt(3), 650],
            17: [500-200*sqrt(3), 500],
            18: [500, 500]
        }

    def colony_dict_init(self):
        colonies = {}

        def shift(col, coords, offset):
            colonies[col] = coords
            coords[0] += offset[0]*100
            coords[1] += offset[1]*100
            return col + 1, coords

        # Outer Ring
        col = 0
        coords = [500 - 100*sqrt(3), 150] # coordinate of colony 0, assuming a 1000px * 1000px canvas
        # each side of the hexagon lattice
        for i in range(6):
            for i in range(2):
                col, coords = shift(col, coords, hex_shifts[i])
                col, coords = shift(col, coords, hex_shifts[i+1])
            col, coords = shift(col, coords, hex_shifts[i])

        # Inner Ring
        coords = [500-100*sqrt(3), 250]
        colonies[col] = coords
        # each side of the hexagon lattice again
        for i in range(6):
            col, coords = shift(col, coords, hex_shifts[i])
            col, coords = shift(col, coords, hex_shifts[i+1])
            col, coords = shift(col, coords, hex_shifts[i])

        # Middle Tile
        coords = [500, 400]
        colonies[col] = coords
        for i in range(6):
            col, coords = shift(col, coords, hex_shifts[i+1])
        return colonies

    def road_dict_init(self, col_dict, road_objs):
        def endpoints(col1, col2):
            delta_x = col2[0] - col1[0]
            delta_y = col2[1] - col1[1]
            
            new_col1 = [col1[0] + .2*delta_x, col1[1] + .2*delta_y]
            new_col2 = [col2[0] - .2*delta_x, col1[1] - .2*delta_y]
            return new_col1, new_col2

        roads = {}
        # we know roads are between two existing colonies
        # no need to redo work - already know these connections as well as colony coords
        for road in road_objs:
            roads[road.id] = self.endpoints(*road.colonies)
        return roads

    def add_robber(self, hex_id):
        coords = self.hex_dict[hex_id]
        # write a big "X" on the hex's number
        pygame.draw.line(self.window, "red", [coords[0]-40, coords[1]-40], [coords[0]+40, coords[1]+40], width=5)
        pygame.draw.line(self.window, "red", [coords[0]+40, coords[1]-40], [coords[0]-40, coords[1]+40], width=5)
        pygame.display.update()

    def draw_colony(self, col_id, color):
        coords = self.col_dict[col_id]
        pygame.draw.circle(self.window, color, coords, 10)
        pygame.display.update()

    def draw_city(self, col_id, color):
        coords = self.col_dict[col_id]
        pygame.draw.circle(self.window, color, coords, 10)
        pygame.display.update()

    def draw_road(self, road_id, color):
        coords = self.road_dict[road_id]
        pygame.draw.line(self.window, color, coords[0], coords[1], width=20)
        pygame.display.update()

    def draw_hex(self, hex_id):
        # also doubles as robber removal - just rewrite the entire hex for now
        resource = self.board.get_hex(hex_id).resource
        color_dict = {
            Resource.DESERT: "lightgoldenrod",
            Resource.WOOD: "springgreen4",
            Resource.BRICK: "sienna3",
            Resource.SHEEP: "azure1",
            Resource.WHEAT: "darkgoldenrod1",
            Resource.STONE: "lightslategray",
        }

        coords = self.hex_dict[hex_id]
        hex_coords = [[coords[0] + hex_shifts[i][0], coords[1] + hex_shifts[i][1]*80] for i in range(6)]
        pygame.draw.polygon(self.window, color_dict[resource], hex_coords)

        # draw the number
        if resource != Resource.DESERT:
            font = pygame.font.Font('freesansbold.ttf', 40)
            text = font.render(str(self.board.get_hex(hex_id).number), True, 'black', 'white')
            rect = text.get_rect()
            rect.center = coords
            pygame.display.update()

    def board_init(self):
        for i in self.hex_dict():
            draw_hex()
        
        for i in self.colony_dict():
            draw_colony("black")

        for i in self.road_dict():
            draw_city("black")
