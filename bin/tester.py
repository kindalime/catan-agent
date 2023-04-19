from catan import Catan
from random import shuffle


def one_test(setup):
    setup = setup.copy()
    setup = random.shuffle(setup)
    c = Catan(setup)
    c.play_game()

class Tester:
    def test_setup(self, setup, num):

