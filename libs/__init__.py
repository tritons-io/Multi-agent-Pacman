from copy import deepcopy
from typing import Tuple, Optional, List


def add_tuples(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return a[0] + b[0], a[1] + b[1]


def sub_tuples(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return a[0] - b[0], a[1] - b[1]


def reverse_tuple(a: Tuple[int, int]) -> Tuple[int, int]:
    return -a[0], -a[1]


class BaseClass(object):
    def __deepcopy__(self, memodict):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result


class Position(BaseClass):
    """
    Class used for inanimate objects (like food and bonuses)
    """
    coordinates: Tuple[int, int]

    def __init__(self, coordinates: Tuple[int, int]):
        self.coordinates = coordinates


class ActorPosition(Position):
    """
    Class used for animate objects (like pacman and ghosts)
    """
    direction: Tuple[int, int]  # (1, 0) is right, (-1, 0) is left, (0, 1) is up, (0, -1) is down

    def __init__(self, coordinates: Tuple[int, int], direction: Optional[Tuple[int, int]]):
        super().__init__(coordinates)
        self.direction = direction if direction is not None else (1, 0)

    def get_direction(self):
        if self.direction == (1, 0):
            return 'right'
        elif self.direction == (-1, 0):
            return 'left'
        elif self.direction == (0, 1):
            return 'up'
        elif self.direction == (0, -1):
            return 'down'


class PacmanAgent(BaseClass):
    position: ActorPosition

    def __init__(self, position: Tuple[int, int]):
        self.position = ActorPosition(position, None)

    def get_action(self, state):
        pass

    def get_legal_actions(self, state):
        walls = state.layout.walls
        coordinates = state.pacman.position.coordinates
        actions = []
        if not (coordinates[0] + 1, coordinates[1]) in walls:
            actions.append((1, 0))
        if not (coordinates[0] - 1, coordinates[1]) in walls:
            actions.append((-1, 0))
        if not (coordinates[0], coordinates[1] + 1) in walls:
            actions.append((0, 1))
        if not (coordinates[0], coordinates[1] - 1) in walls:
            actions.append((0, -1))
        return actions

    def evaluation_function(self, state, action):
        pass