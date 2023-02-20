from typing import List, Tuple, Dict, Optional

from libs import BaseClass


def manhattan_distance(position1: Tuple[int, int], position2: Tuple[int, int]):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])


class Layout(BaseClass):
    maze: List[List[int]] = []
    walls: List[Tuple[int, int]]
    portals: Dict[int, Tuple[Tuple[int, int], Optional[Tuple[int, int]]]] = {}

    food: List[Tuple[int, int]]
    cherries: List[Tuple[int, int]]

    pacman: Tuple[int, int]

    blinky: Tuple[int, int] = (-1, -1)
    pinky: Tuple[int, int] = (-1, -1)
    inky: Tuple[int, int] = (-1, -1)
    clyde: Tuple[int, int] = (-1, -1)

    initial_food_count: int

    def __init__(self, layout_text: str):
        self.walls = []
        self.food = []
        self.cherries = []

        ghosts_table = ['b', 'p', 'i', 'c']

        for y, line in enumerate(layout_text.splitlines()):
            self.maze.append([])
            for x, char in enumerate(line):
                if char == '%':
                    self.maze[y].append(1)
                    self.walls.append((x, y))
                else:
                    self.maze[y].append(0)
                if char == ' ':
                    continue
                elif char == '.':
                    self.food.append((x, y))
                elif char == 'o':
                    self.cherries.append((x, y))
                elif char == 'P':
                    self.pacman = (x, y)
                elif char == 'G':
                    self.set_ghost_start(ghosts_table.pop(0), (x, y))
                elif char in ghosts_table:
                    self.set_ghost_start(char, (x, y))
                else:
                    try:
                        if 0 <= int(char) <= 9:
                            self.add_to_portal(int(char), (x, y))
                    except ValueError:
                        continue
        self.initial_food_count = len(self.food)

    def add_to_portal(self, portal: int, position: Tuple[int, int]):
        if portal in self.portals.keys():
            self.portals[portal] = (self.portals[portal][0], position)
        else:
            self.portals[portal] = (position, None)

    def set_ghost_start(self, ghost_vowel: str, position: Tuple[int, int]):
        if ghost_vowel == 'b':
            self.blinky = position
        elif ghost_vowel == 'p':
            self.pinky = position
        elif ghost_vowel == 'i':
            self.inky = position
        elif ghost_vowel == 'c':
            self.clyde = position

    def get_dimensions(self):
        return max(x for x, y in self.walls) + 1, max(y for x, y in self.walls) + 1
