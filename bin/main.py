from catan import Catan
import logging

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

game = Catan(["h", "r", "r"], show_display=True)
winner, scores = game.play_game()
print(winner, scores)
