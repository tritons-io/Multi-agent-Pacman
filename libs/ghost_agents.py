import random
from copy import deepcopy, copy
from typing import Tuple


from libs import ActorPosition, BaseClass, reverse_tuple, add_tuples
from libs.greedy_shortest_path import AStar
from libs.layouts import manhattan_distance


class GhostAgent(BaseClass):
    name: str
    initial_position: ActorPosition
    position: ActorPosition
    scared: bool = False
    dead: bool = False
    previous_action: Tuple[int, int] = (0, 0)
    disable_clip: bool = False
    fleeing_since: int = 0
    key: str

    def __init__(self, position: Tuple[int, int]):
        position = ActorPosition(position, (1, 0))
        self.initial_position = deepcopy(position)
        self.position = position

    def set_respawn(self):
        self.dead = True

    def respawn_tick(self):
        if self.position.coordinates == self.initial_position.coordinates:
            self.dead = False
            self.scared = False
            self.fleeing_since = 0

    def get_action(self, state):
        if self.dead:
            return self.go_to_coords(state, self.initial_position.coordinates)
        if self.scared:
            if self.fleeing_since > 10:
                return self.go_to_coords(state, self.initial_position.coordinates)
            self.fleeing_since += 1
            return self.flee_pacman(state)
        if self.disable_clip:
            return self.previous_action

    def flee_pacman(self, state):
        """
        The ghost should flee from Pacman.
        :param state: the game state
        :return: the action that will move the ghost away from Pacman
        """
        pacman_position = state.pacman.position.coordinates
        ghost_position = self.position.coordinates
        actions = self.get_legal_actions(state)
        distances = []
        for action in actions:
            distances.append(manhattan_distance(add_tuples(ghost_position, action), pacman_position))
        return actions[distances.index(max(distances))]

    def get_legal_actions(self, state):
        """
        A ghost can only move in cardinal directions.
        A ghost cannot move backwards.
        A ghost cannot move through a wall.
        A ghost cannot move through a ghost.
        A ghost can only advance one step at a time.

        :return: list of legal actions
        """
        walls = state.layout.walls
        coordinates = self.position.coordinates
        direction = self.position.direction
        actions = []
        if not (coordinates[0] + 1, coordinates[1]) in walls and direction != (-1, 0):
            actions.append((1, 0))
        if not (coordinates[0] - 1, coordinates[1]) in walls and direction != (1, 0):
            actions.append((-1, 0))
        if not (coordinates[0], coordinates[1] + 1) in walls and direction != (0, -1):
            actions.append((0, 1))
        if not (coordinates[0], coordinates[1] - 1) in walls and direction != (0, 1):
            actions.append((0, -1))
        if len(actions) == 0:
            actions.append((direction[0] * -1, direction[1] * -1))
        return actions

    def go_to_coords(self, state, coords):
        actions = self.get_legal_actions(state)
        maze = deepcopy(state.layout.maze)
        if self.position.coordinates != self.initial_position.coordinates:
            previous_position = (self.position.coordinates[1] - self.position.direction[1], self.position.coordinates[0] - self.position.direction[0])
            try:
                maze[previous_position[0]][previous_position[1]] = 1
            except IndexError:
                pass
        shortest_path_to_target = AStar(maze).search((self.position.coordinates[1], self.position.coordinates[0]), (coords[1], coords[0]))
        try:
            next_position = (shortest_path_to_target[1][1], shortest_path_to_target[1][0])
        except (TypeError, IndexError):
            return random.choice(actions)
        vector = (next_position[0] - self.position.coordinates[0], next_position[1] - self.position.coordinates[1])
        if vector in actions:
            return vector
        else:
            return random.choice(actions)


class RandomGhostAgent(GhostAgent):
    """
    A ghost agent that chooses a legal action uniformly at random.
    """

    def get_action(self, state):
        action = super().get_action(state)
        if action is not None:
            return action
        actions = self.get_legal_actions(state)
        return random.choice(actions)


class BlinkyAgent(GhostAgent):
    """
    Chaser ghost, starts outside the box and chases pacman immediately.
    """

    def get_action(self, state):
        action = super().get_action(state)
        if action is not None:
            return action
        return self.go_to_coords(state, state.pacman.position.coordinates)


class PinkyAgent(GhostAgent):
    """
    Ghost that tries to get in front of pacman. Starts inside the box but exits immediately.
    """
    start_at_turn = 5

    def get_action(self, state):
        action = super().get_action(state)
        if action is not None:
            return action
        actions = self.get_legal_actions(state)
        if state.turn < self.start_at_turn:
            if self.previous_action == (0, 0):
                self.previous_action = random.choice(actions)
                return self.previous_action
            else:
                self.previous_action = reverse_tuple(self.previous_action)
                return self.previous_action
        way_ahead = state.predict_pacman_position(3)
        return self.go_to_coords(state, way_ahead.pacman.position.coordinates)


class InkyAgent(GhostAgent):
    """
    Ghost setting up ambushes. Starts inside the box and exits after 30 fruit have been eaten.

    Draw a vector from blinky to 2 tiles in front of pacman, then double it. This is the target position for inky.
    """
    needed_food_to_start = 10

    def get_action(self, state):
        action = super().get_action(state)
        if action is not None:
            return action
        actions = self.get_legal_actions(state)
        if state.layout.initial_food_count - len(state.layout.food) < self.needed_food_to_start:
            if self.previous_action == (0, 0):
                self.previous_action = random.choice(actions)
                return self.previous_action
            else:
                self.previous_action = reverse_tuple(self.previous_action)
                return self.previous_action
        return self.go_to_coords(state, state.pacman.position.coordinates)


class ClydeAgent(GhostAgent):
    """
    Hard to predict ghost. Starts inside the box and exits after a third of the fruit have been eaten.

    If clyde is more than 8 tiles away from pacman, he will target him.
    Else, he will flee him
    """

    def get_action(self, state):
        action = super().get_action(state)
        if action is not None:
            return action
        actions = self.get_legal_actions(state)
        if state.layout.initial_food_count - len(state.layout.food) < state.layout.initial_food_count / 3:
            if self.previous_action == (0, 0):
                self.previous_action = random.choice(actions)
                return self.previous_action
            else:
                self.previous_action = reverse_tuple(self.previous_action)
                return self.previous_action
        if manhattan_distance(state.pacman.position.coordinates, self.position.coordinates) > 8:
            return self.go_to_coords(state, state.pacman.position.coordinates)
        else:
            return self.flee_pacman(state)
