from policy.policy import CatanPolicy
from collections import Counter
from resources import *
from devcard import *

import math
import random
import time
import datetime
from enum import Enum

# MCTS with NO simplifying modifications. Has full access to ALL hidden information.
# Uses the Baseline for estimating what other players will do.
    
class Node:
    def __init__(self, pos, depth=None, state=None):
        self.views = 0
        self.payoff = 0

        if not state:
            self.state = self.find_state()
        else:
            self.state = state

        if not depth:
            self.depth = pos.current_turn # TODO: change
        else:
            self.depth = depth

    def find_state(self):
        pass


def mcts_policy(time):
    """ Wrapper function that returns a class method call. """
    def fun(state):
        mc = MonteCarlo(time, state)
        return mc.run_monte_carlo()
    return fun

class MonteCarlo:
    def __init__(self, runtime, state, catan, player):
        self.root = state
        self.runtime = runtime
        self.start_time = time.time()
        self.states = {self.root: Node(self.root)} # [total views, total payoff]
        self.iterations = 0
        super().__init__(catan, player)

    def run_monte_carlo(self):
        """ Main function that handles the loop of iteration running and then fetches the optimal move. """
        while time.time() - self.start_time < self.runtime:
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
        chain.append(state)
        if state.is_terminal():
            return state.payoff(), chain
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
        for action in state.get_actions():
            child = state.successor(action)
            self.states[child] = [0, 0]

    def simulate(self, state):
        """ Simulate step of the MCTS algorithm. Plays random actions until reaching a terminal node.

            state -- beginning state being simulated.
        """
        while not state.is_terminal():
            action = random.choice(state.get_actions())
            state = state.successor(action)
        return state.payoff()

    def update(self, payoff, chain):
        """ Update step of the MCTS algorithm. Updates states with the given payoff.
        
            payoff -- payoff of the terminal node reached at the end of traverse/simulate. 
            chain -- the chain of states being updated, represented as a list starting with the root.
        """

        for state in chain:
            self.states[state][0] += 1
            self.states[state][1] += payoff

    def get_children(self, state):
        return [state.successor(action) for action in state.get_actions()]

    def select_child(self, state):
        """ Function that selects a child for a given state. Picks a random unvisited node (with 0 runs)
            if any exist; otherwise, returns the most optimal node using UCB.

            state -- state that we are selecting the most optimal child for.
        """

        children = self.get_children(state)
        unvisited = list(filter(lambda x: self.states[x][0] == 0, children))
        if unvisited:
            return random.choice(unvisited)

        # For player 0, max ucb: else, min ucb
        ucbs = [self.calculate_ucb(child, state) for child in children]
        if state.actor() == 0:
            choices = [idx for idx, value in enumerate(ucbs) if value == max(ucbs)]
        else:
            choices = [idx for idx, value in enumerate(ucbs) if value == min(ucbs)]
        return children[random.choice(choices)]

    def calculate_ucb(self, state, parent_state):
        """ Function that calculates UCB for a given state, according to the formula.

            state -- child state that we are generating the UCB for.
            parent_state -- parent state to the above.
        """

        if not parent_state:
            return None

        parent_runs = self.states[parent_state][0]
        runs, reward = self.states[state]
        if runs == 0 or parent_runs == 0:
            ucb = None
        else:
            if parent_state.actor() == 0:
                ucb = reward / runs + math.sqrt(2 * math.log(parent_runs) / runs)
            else:
                ucb = reward / runs - math.sqrt(2 * math.log(parent_runs) / runs)
        return ucb

    def return_optimal(self):
        """ Function that returns the optimal child at the end of the algorithm by choosing
            which child of the root node was the most visited.
        """

        children = self.get_children(self.root)
        max_runs = max([self.states[child][0] for child in children])
        
        choices = []
        for action in self.root.get_actions():
            child = self.root.successor(action)
            if self.states[child][0] == max_runs:
                choices.append(action)
        return random.choice(choices)

    def print_node(self, state, depth, parent_runs):
        if self.states[state][0] == 0:
            string = f"New node, Player: {state.actor()}, Actions: {len(state.get_actions())}, Terminal: {state.is_terminal()}"
            print("-" * depth + string)
        else:
            runs, reward = self.states[state]
            string = f"Runs: {runs}, Reward: {reward/runs}, UCB: {self.calculate_ucb(state, None)}, Player: {state.actor()}, Actions: {len(state.get_actions())}, Terminal: {state.is_terminal()}"
            print("-" * depth + string)
            if not state.is_terminal():
                for child in self.get_children(state):
                    self.print_node(child, depth + 1, runs)

    def print_tree(self):
        print("//////////////////////////////////")
        self.print_node(self.root, 0, 0)
