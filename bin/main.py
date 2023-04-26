from catan import Catan
import logging

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

baseline_dict = {
    "stone_importance": 3,
    "extend_longest_weight": 1,
    "tie_longest_weight": 1,
    "knight_play_weight": .5
}

# for i in range(100):
#     game = Catan([["b", "h", "r"], [baseline_dict, {}, {}]])
#     winner, scores = game.play_game()
#     print(winner, scores)
game = Catan([["b", "h", "m"], [baseline_dict, {}, {}]], show_display=False)
winner, scores = game.play_game()