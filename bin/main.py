from catan import Catan
import logging

game = Catan(["h", "r", "r"], show_display=True)
winner, scores = game.play_game()
print(winner, scores)
