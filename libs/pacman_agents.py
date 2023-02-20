import random
from copy import copy

from libs import PacmanAgent
from libs.layouts import manhattan_distance


class RightTurnAgent(PacmanAgent):
    """
    A Pacman agent that turns right at every opportunity.
    """

    def get_action(self, state):
        actions = self.get_legal_actions(state)
        return actions[0]


class MonCherryAgent(PacmanAgent):
    """
    A Pacman agent that rushes the cherries. Naturally yield decent results.
    """

    def get_action(self, state):
        actions = self.get_legal_actions(state)
        cherries_distance = [manhattan_distance(self.position.coordinates, cherry) for cherry in state.layout.cherries]
        if not cherries_distance:
            return random.choice(actions)
        cherry_position = state.layout.cherries[cherries_distance.index(min(cherries_distance))]
        maze = copy(state.layout.maze)
        from libs.greedy_shortest_path import AStar

        shortest_path_to_cherry = AStar(maze).search((self.position.coordinates[1], self.position.coordinates[0]), (cherry_position[1], cherry_position[0]))
        try:
            next_position = (shortest_path_to_cherry[1][1], shortest_path_to_cherry[1][0])
        except (TypeError, IndexError):
            return random.choice(actions)
        vector = (next_position[0] - self.position.coordinates[0], next_position[1] - self.position.coordinates[1])
        if vector in actions:
            return vector
        else:
            return random.choice(actions)


class ReflexAgent(PacmanAgent):
    """
    Here: implement a reflex agent that chooses an action by evaluating each action available in the current state.
    """

    def get_action(self, state):
        actions = self.get_legal_actions(state)
        return random.choice(actions)
