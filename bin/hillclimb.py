import random
from tester import Tester
from numpy import arange

class HillClimb:
    def __init__(self, mini, maxi, step, curr, runs):
        self.mini = mini
        self.maxi = maxi
        self.step = step
        self.curr = curr
        self.curr_score = 0
        self.visited = []
        self.runs = runs

    def score(self, setup):
        test_setup = [["b", "b", "h"], [setup, self.curr, {}]]
        tester = Tester(["Neighbor", "Current", "Builder"])
        _, winners, _, _, _ = tester.test_setup(test_setup, self.runs)
        return winners[0] / sum([winners[i] for i in winners])

    def new_neighbor(self, old, key, val):
        new = old.copy()
        new[key] += val
        return new

    def generate_neighbors(self):
        possible = [self.curr.copy()]
        for i in self.curr:
            new = []
            for p in possible:
                if p[i] + self.step[i] <= self.maxi[i]:
                    new.append(self.new_neighbor(p, i, self.step[i]))
                if p[i] - self.step[i] >= self.mini[i]:
                    new.append(self.new_neighbor(p, i, -self.step[i]))
            possible.extend(new)
        return [p for p in possible if p not in self.visited and p != self.curr]

    def hill_climb(self):
        while True:
            neighbors = self.generate_neighbors()
            neighbor_scores = [self.score(neighbor) for neighbor in neighbors]
            best_score = max(neighbor_scores)
            if not neighbors or best_score <= self.curr_score:
                return self.curr, self.curr_score
            else:
                self.curr_score = best_score
                self.curr = neighbors[neighbor_scores.index(best_score)]
                self.visited.extend(neighbors)

if __name__ == "__main__":
    mini = {
        "stone_importance": 1,
        "extend_longest_weight": 0,
        "tie_longest_weight": 0,
        "knight_play_weight": 0
    }
    maxi = {
        "stone_importance": 5,
        "extend_longest_weight": 1,
        "tie_longest_weight": 1,
        "knight_play_weight": 1
    }
    step = {
        "stone_importance": 1,
        "extend_longest_weight": .05,
        "tie_longest_weight": .05,
        "knight_play_weight": .05
    }
    curr = {
        "stone_importance": random.choice(range(1, 6)),
        "extend_longest_weight": random.choice(arange(0, 1.05, .05)),
        "tie_longest_weight": random.choice(arange(0, 1.05, .05)),
        "knight_play_weight": random.choice(arange(0, 1.05, .05)),
    }
    runs = 10000
    h = HillClimb(mini, maxi, step, curr, runs)
    optimal = h.hill_climb()
    print(optimal)
