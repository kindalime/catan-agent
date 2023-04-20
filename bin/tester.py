from catan import Catan
from random import shuffle
from multiprocessing import Pool
from functools import partial
from statistics import stdev, mean
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


def one_test(setup, i):
    try:
        setup = setup.copy()
        shuffle(setup)
        c = Catan(setup)
        winner, points = c.play_game()
        return setup, winner, points
    except:
        return None, None, None

class Tester:
    def test_setup(self, setup, num):
        single = partial(one_test, setup)

        with Pool(8) as p:
            vals = p.map(single, range(num))

        self.parse_results(vals)

    def parse_results(self, vals):
        winners = {"h": 0, "b": 0, "r": 0}
        random_winner = {"b": [], "h": []}
        heuristic_winner = {"b": [], "r": []}
        baseline_winner = {"h": [], "r": []}
        for v in vals:
            setup, winner, points = v
            if winner:
                winner = setup[winner]

                match winner:
                    case "h":
                        winners["h"] += 1
                        heuristic_winner["b"].append(points[setup.index("b")][1])
                        heuristic_winner["r"].append(points[setup.index("r")][1])
                    case "b":
                        winners["b"] += 1
                        baseline_winner["h"].append(points[setup.index("h")][1])
                        baseline_winner["r"].append(points[setup.index("r")][1])
                    case "r":
                        winners["r"] += 1
                        random_winner["b"].append(points[setup.index("b")][1])
                        random_winner["h"].append(points[setup.index("h")][1])

        print(winners)
        print("Heuristic Winner")
        print(f"Baseline: mean {mean(heuristic_winner['b'])} std {stdev(heuristic_winner['b'])}")
        print(f"Random: mean {mean(heuristic_winner['r'])} std {stdev(heuristic_winner['r'])}")
        print("Baseline Winner")
        print(f"Heuristic: mean {mean(baseline_winner['h'])} std {stdev(baseline_winner['h'])}")
        print(f"Random: mean {mean(baseline_winner['r'])} std {stdev(baseline_winner['r'])}")
        print("Random Winner")
        print(f"Heuristic: mean {mean(random_winner['h'])} std {stdev(random_winner['h'])}")
        print(f"Baseline: mean {mean(random_winner['b'])} std {stdev(random_winner['b'])}")
        self.make_graphs(winners, random_winner, heuristic_winner, baseline_winner)

    def make_graphs(self, winners, random_winner, heuristic_winner, baseline_winner):
        data = [
            baseline_winner['h'],
            baseline_winner['r'],
            heuristic_winner['b'],
            heuristic_winner['r'],
            random_winner['h'],
            random_winner['b'],
        ]
        names = [
            "Heuristic Score on Baseline Victory",
            "Random Score on Baseline Victory",
            "Baseline Score on Heuristic Victory",
            "Random Score on Heuristic Victory",
            "Heuristic Score on Random Victory",
            "Baseline Score on Random Victory",
        ]
        files = [
            "hscore_bvic.png",
            "rscore_bvic.png",
            "bscore_hvic.png",
            "rscore_hvic.png",
            "hscore_rvic.png",
            "bscore_rvic.png",
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

t = Tester()
t.test_setup(["h", "b", "r"], 10000)
