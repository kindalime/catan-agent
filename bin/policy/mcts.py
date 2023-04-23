from policy.policy import CatanPolicy
from collections import Counter
from resources import *
from devcard import *
from policy.random import RandomPolicy
from policy.nodecalc import *

import math
import random
import time
import datetime

# MCTS with NO simplifying modifications. Has full access to ALL hidden information.
# Uses the Baseline for estimating what other players will do.

class MCTSPolicy(CatanPolicy):
    def __init__(self, catan, player, runtime):
        super().__init__(catan, player)
        self.runtime = runtime
        self.init_road = None

    def init_settle(self, pos):
        mc = MonteCarlo(self.runtime, pos, self.catan, self.player)
        optimal = mc.run_monte_carlo()
        self.init_road = optimal[1]
        return optimal[0]

    def init_road(self, pos, settlement):
        return self.init_road

    def choose_discard(self, pos):
        mc = MonteCarlo(self.runtime, pos, self.catan, self.player)
        optimal = mc.run_monte_carlo()
        return optimal.action

    def choose_robber(self, pos):
        mc = MonteCarlo(self.runtime, pos, self.catan, self.player)
        optimal = mc.run_monte_carlo()
        return optimal.action

    def take_turn(self, pos):
        mc = MonteCarlo(self.runtime, pos, self.catan, self.player)
        optimal = mc.run_monte_carlo()
        while optimal.action[0] != ["end"]:
            match optimal.action[0]:
                case "city":
                    self.catan.build_city(pos, self.player, optimal.action[1])
                case "settlement":
                    self.catan.build_settlement(pos, self.player, optimal.action[1])
                case "road":
                    self.catan.build_road(pos, self.player, optimal.action[1])
            mc = MonteCarlo(self.runtime, pos, self.catan, self.player)
            optimal = mc.run_monte_carlo()

class MonteCarlo:
    def __init__(self, runtime, state, catan, player):
        self.root = state
        self.runtime = runtime
        self.start_time = time.time()
        self.iterations = 0
        self.nodecalc = NodeCalc(player.id, catan)
        self.states = {self.root: Node(self.root)} # [total views, total payoff]
        self.states[self.root].state = self.nodecalc.find_state(self.root, self.states[self.root])
        self.max_chain = 5

    def turn_diff(self, before, after):
        return (after.turn_count - before.turn_count)/len(before.players)

    def calculate_payoff(self, pos):
        # TODO
        # total_points = 4 * pos.players[i]
        # all_points = sum([])
        return 5

    def run_monte_carlo(self):
        """ Main function that handles the loop of iteration running and then fetches the optimal move. """
        while time.time() - self.start_time < self.runtime: # seconds
            self.run_iteration()
            self.iterations += 1
        # print(f"Iteration complete. Runs: {self.iterations} Time: {datetime.datetime.now()}")
        # self.print_tree()
        return self.return_optimal()

    def run_iteration(self):
        payoff, chain = self.traverse(self.root, [])
        self.update(payoff, chain)

    def traverse(self, state, chain):
        """ Traverse step of the MCTS algorithm. Traverses the existing tree recursively until it
            reaches a terminal node or a leaf node with unexpanded children.
        
            state -- the current state being traversed.
            chain -- the chain of states being traversed, represented as a list starting with the root.
        """ 
        print("traverse begin")
        chain.append(state)
        if state.check_terminal() or self.turn_diff(chain[0], chain[-1]) < self.max_chain:
            return self.calculate_payoff(state), chain
        else:
            if self.states[state][0] == 0: # only simulate upon reaching a new node (w/o children)
                self.expand(state)
                return self.simulate(state), chain
            else:
                child = self.select_child(state)
                payoff, chain = self.traverse(child, chain)
                return payoff, chain

    def expand(self, state):
        """ Expand step of the MCTS algorithm. Creates new nodes with 0 runs/score for every child action.
        
            state -- the current state being expanded.
        """
        print("expand begin")
        children = self.nodecalc.get_children(state)
        self.states.update(children)

    def simulate(self, state):
        """ Simulate step of the MCTS algorithm. Plays random actions until reaching a terminal node.
            Can use the random policy for this. Also does not necessarily reach a terminal node - in that case,
            plays for a certain number of rounds (default 5).

            state -- beginning state being simulated.
        """
        print("simulate begin")
        begin_state = state
        while not state.check_terminal() and self.turn_diff(begin_state, state) < self.max_chain:
            children = self.nodecalc.get_children(state)
            state = random.choice(children)
        return self.calculate_payoff(state)

    def update(self, payoff, chain):
        """ Update step of the MCTS algorithm. Updates states with the given payoff.
        
            payoff -- payoff of the terminal node reached at the end of traverse/simulate. 
            chain -- the chain of states being updated, represented as a list starting with the root.
        """
        print("update begin")
        for state in chain:
            self.states[state].views += 1
            self.states[state].payoff += payoff

    def get_children(self, state):
        print("get_children begin")
        return self.nodecalc.get_children(state, self.states[state]).keys()

    def select_child(self, state):
        """ Function that selects a child for a given state. Picks a random unvisited node (with 0 runs)
            if any exist; otherwise, returns the most optimal node using UCB.

            state -- state that we are selecting the most optimal child for.
        """
        print("select_child begin")
        children = self.get_children(state)
        unvisited = list(filter(lambda x: self.states[x].views == 0, children))
        if unvisited:
            return random.choice(unvisited)

        ucbs = [self.calculate_ucb(child, state) for child in children]
        choices = [idx for idx, value in enumerate(ucbs) if value == max(ucbs)]
        return children[random.choice(choices)]

    def calculate_ucb(self, state, parent_state):
        """ Function that calculates UCB for a given state, according to the formula.

            state -- child state that we are generating the UCB for.
            parent_state -- parent state to the above.
        """
        print("calculate_ucb begin")
        if not parent_state:
            return None

        parent_runs = self.states[parent_state].views
        runs, reward = self.states[state]
        if runs == 0 or parent_runs == 0:
            ucb = None
        else:
            ucb = reward / runs + math.sqrt(2 * math.log(parent_runs) / runs)
        return ucb

    def return_optimal(self):
        """ Function that returns the optimal child at the end of the algorithm by choosing
            which child of the root node was the most visited.
        """
        print("return_optimal begin")
        children = self.get_children(self.root)
        max_runs = max([self.states[child].views for child in children])
        
        choices = []
        for child in children:
            if self.states[child].views == max_runs:
                choices.append(self.states[child].action)
        return random.choice(choices)
