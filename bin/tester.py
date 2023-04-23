from catan import Catan
from random import shuffle
from multiprocessing import Pool
from functools import partial
from statistics import stdev, mean
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


def one_test(setup, i):
    try:
        c = Catan(setup)
        winner, points = c.play_game()
        return setup, winner, points
    except Exception as e:
        # print(repr(e))
        return None, None, None

class Tester:
    def __init__(self, names):
        self.names = names

    def test_setup(self, setup, num):
        single = partial(one_test, setup)

        with Pool(8) as p:
            vals = p.map(single, range(num))

        self.parse_results(vals)

    def parse_results(self, vals):
        winners = {0: 0, 1: 0, 2: 0}
        zero_winner = {1: [], 2: []}
        one_winner = {0: [], 2: []}
        two_winner = {0: [], 1: []}
        for v in vals:
            setup, winner, points = v
            print(setup, winner, points)
            if winner is not None:
                match winner:
                    case 0:
                        winners[0] += 1
                        zero_winner[1].append(points[1][1])
                        zero_winner[2].append(points[2][1])
                    case 1:
                        winners[1] += 1
                        one_winner[0].append(points[0][1])
                        one_winner[2].append(points[2][1])
                    case 2:
                        winners[2] += 1
                        two_winner[0].append(points[0][1])
                        two_winner[1].append(points[1][1])

        print(winners)
        print(f"{self.names[0]} Winner")
        print(f"{self.names[1]}: mean {mean(zero_winner[1])} std {stdev(zero_winner[1])}")
        print(f"{self.names[2]}: mean {mean(zero_winner[2])} std {stdev(zero_winner[2])}")
        print(f"{self.names[1]} Winner")
        print(f"{self.names[0]}: mean {mean(one_winner[0])} std {stdev(one_winner[0])}")
        print(f"{self.names[2]}: mean {mean(one_winner[2])} std {stdev(one_winner[2])}")
        print(f"{self.names[2]} Winner")
        print(f"{self.names[0]}: mean {mean(two_winner[0])} std {stdev(two_winner[0])}")
        print(f"{self.names[1]}: mean {mean(two_winner[1])} std {stdev(two_winner[1])}")
        self.make_graphs(winners, two_winner, one_winner, zero_winner)

    def make_graphs(self, winners, two_winner, one_winner, zero_winner):
        data = [
            zero_winner[1],
            zero_winner[2],
            one_winner[0],
            one_winner[2],
            two_winner[0],
            two_winner[1],
        ]
        names = [
            f"{self.names[1]} Score on {self.names[0]} Victory",
            f"{self.names[2]} Score on {self.names[0]} Victory",
            f"{self.names[0]} Score on {self.names[1]} Victory",
            f"{self.names[2]} Score on {self.names[1]} Victory",
            f"{self.names[0]} Score on {self.names[2]} Victory",
            f"{self.names[1]} Score on {self.names[2]} Victory",
        ]
        files = [
            f"{self.names[1]}_score_{self.names[0]}_vic.png",
            f"{self.names[1]}_score_{self.names[0]}_vic.png",
            f"{self.names[0]}_score_{self.names[1]}_vic.png",
            f"{self.names[2]}_score_{self.names[1]}_vic.png",
            f"{self.names[0]}_score_{self.names[2]}_vic.png",
            f"{self.names[1]}_score_{self.names[2]}_vic.png",
        ]

        for i in range(len(names)):
            plt.figure(i)
            plt.hist(data[i], bins=list(range(2, 10)))
            plt.xlabel('Score')
            plt.ylabel('# of Games')
            plt.title(names[i])
            # Tweak spacing to prevent clipping of ylabel
            plt.subplots_adjust(left=0.15)
            plt.savefig(files[i])

t = Tester(["Baseline", "Heuristic", "Random"])
setup_zero = {

}
setup_one = {

}
setup_two = {

}
t.test_setup([["b", "h", "r"], [setup_zero, setup_one, setup_two]], 1000)
