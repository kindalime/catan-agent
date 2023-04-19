from catan import Catan
from random import shuffle
from multiprocessing import Pool
from functools import partial

def one_test(setup, i):
    try:
        setup = setup.copy()
        shuffle(setup)
        c = Catan(setup)
        winner, points = c.play_game()
        return winner, points
    except:
        return None, None

class Tester:
    def test_setup(self, setup, num):
        single = partial(one_test, setup)

        with Pool(8) as p:
            vals = p.map(single, range(num))
        for val in vals:
            print(val)


t = Tester()
t.test_setup(["h", "b", "r"], 100)