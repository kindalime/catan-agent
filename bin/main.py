from catan import Catan
import logging

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

for i in range(100):
    game = Catan(["b", "h", "r"])
    winner, scores = game.play_game()
    print(winner, scores)
