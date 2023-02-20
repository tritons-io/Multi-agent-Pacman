import logging
import string

from copy import deepcopy
from typing import Tuple, Dict

from libs import add_tuples, sub_tuples, BaseClass
from libs.ghost_agents import GhostAgent, BlinkyAgent, PinkyAgent, InkyAgent, ClydeAgent
from libs.layouts import Layout
from libs.pacman_agents import PacmanAgent

LETTERS = string.ascii_uppercase
TIME_PENALTY = 1  # Number of points lost each round


def import_class_by_name(module_name, class_name):
    """
    Dynamically import a class from a module. Used to import agents from the command line.
    """
    module = __import__(module_name, globals(), locals(), [class_name])
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        logging.error(f'Class "{class_name}" not found in module "{module_name}"')
        raise e


class PacmanState(BaseClass):
    turn: int = 0
    layout: Layout

    ghosts: Dict[str, GhostAgent] = {}

    pacman: PacmanAgent

    score: int = 0
    game_over: bool = False
    clipping_bug: bool

    def copy(self):
        """
        If the ghosts are not copied, all the states will have the same ghosts, messing up the position when calculating
         the successors states.
        """
        result = deepcopy(self)
        result.ghosts = deepcopy(self.ghosts)
        return result

    def __init__(self, layout, pacman_agent: str, clipping_bug: bool = False, ghost_agent=None):
        self.clipping_bug = clipping_bug
        self.layout = layout
        ghost_agent_class = import_class_by_name('libs.ghost_agents', ghost_agent)
        if self.layout.blinky != (-1, -1):
            if ghost_agent:
                self.ghosts['blinky'] = deepcopy(ghost_agent_class(self.layout.blinky))
            else:
                self.ghosts['blinky'] = deepcopy(BlinkyAgent(self.layout.blinky))
        if self.layout.pinky != (-1, -1):
            if ghost_agent:
                self.ghosts['pinky'] = deepcopy(ghost_agent_class(self.layout.pinky))
            else:
                self.ghosts['pinky'] = deepcopy(PinkyAgent(self.layout.pinky))
        if self.layout.inky != (-1, -1):
            if ghost_agent:
                self.ghosts['inky'] = deepcopy(ghost_agent_class(self.layout.inky))
            else:
                self.ghosts['inky'] = deepcopy(InkyAgent(self.layout.inky))
        if self.layout.clyde != (-1, -1):
            if ghost_agent:
                self.ghosts['clyde'] = deepcopy(ghost_agent_class(self.layout.clyde))
            else:
                self.ghosts['clyde'] = deepcopy(ClydeAgent(self.layout.clyde))

        self.pacman = import_class_by_name('libs.pacman_agents', pacman_agent)(self.layout.pacman)

    def set_ghost_position(self, ghost_name: str, position: Tuple[int, int]):
        self.ghosts[ghost_name].position.coordinates = position

    def set_pacman_position(self, position: Tuple[int, int]):
        self.pacman.position.coordinates = position

    def compute_pacman_position(self, keyboard_input=False):
        """
        Compute the new position of pacman, taking into account the portals and the keyboard input.
        """
        for portal in self.layout.portals:
            if self.pacman.position.coordinates == self.layout.portals[portal][0]:
                self.pacman.position.coordinates = self.layout.portals[portal][1]

            elif self.pacman.position.coordinates == self.layout.portals[portal][1]:
                self.pacman.position.coordinates = self.layout.portals[portal][0]

        if not keyboard_input:
            self.pacman.position.direction = self.pacman.get_action(self)
        if self.pacman.position.direction not in self.pacman.get_legal_actions(self):
            logging.error(f'Pacman tried to move in an illegal direction: {self.pacman.position.direction}')
            raise ValueError
        self.pacman.position.coordinates = add_tuples(self.pacman.position.coordinates, self.pacman.position.direction)

    def update(self, with_pacman: bool = True, keyboard_input=False):
        """
        Update the state of the game, moving the ghosts and pacman.
        """
        if with_pacman:
            self.compute_pacman_position(keyboard_input=keyboard_input)

        for index, name in enumerate(self.ghosts):
            if not self.ghosts[name].disable_clip:
                self.ghosts[name].position.direction = self.ghosts[name].get_action(self)
            self.ghosts[name].position.coordinates = add_tuples(self.ghosts[name].position.coordinates, self.ghosts[name].position.direction)
            for portal in self.layout.portals:
                if self.ghosts[name].disable_clip:
                    self.ghosts[name].disable_clip = False
                    continue
                if self.ghosts[name].position.coordinates == self.layout.portals[portal][0]:
                    before_portal = sub_tuples(self.layout.portals[portal][1], self.ghosts[name].position.direction)
                    self.set_ghost_position(name, before_portal)
                    self.ghosts[name].disable_clip = True
                elif self.ghosts[name].position.coordinates == self.layout.portals[portal][1]:
                    before_portal = sub_tuples(self.layout.portals[portal][0], self.ghosts[name].position.direction)
                    self.set_ghost_position(name, before_portal)
                    self.ghosts[name].disable_clip = True
            if self.ghosts[name].dead or self.ghosts[name].scared:
                self.ghosts[name].respawn_tick()
        self.turn += 1
        return self.compute_score()

    def generate_successor(self, pacman_action: Tuple[int, int]):
        next_state = self.copy()
        next_state.pacman.position.coordinates = add_tuples(next_state.pacman.position.coordinates, pacman_action)
        next_state.update(with_pacman=False)
        return next_state

    def predict_pacman_position(self, steps: int):
        """
        Fast and unreliable way to predict the position of pacman after a certain number of steps. Used to calculate the
        target position for the Pinky agent.
        """
        next_state = self.copy()
        if steps != 0:
            current_position = next_state.pacman.position.coordinates
            next_state.pacman.position.coordinates = add_tuples(next_state.pacman.position.coordinates, self.pacman.position.direction)
            if next_state.pacman.position.coordinates in next_state.layout.walls:
                if add_tuples(current_position, (1, 0)) not in next_state.layout.walls:
                    next_state.pacman.position.direction = (1, 0)
                    next_state.pacman.position.coordinates = add_tuples(current_position, (1, 0))
                    return next_state.predict_pacman_position(steps=steps-1)
                elif add_tuples(current_position, (-1, 0)) not in next_state.layout.walls:
                    next_state.pacman.position.direction = (-1, 0)
                    next_state.pacman.position.coordinates = add_tuples(current_position, (-1, 0))
                    return next_state.predict_pacman_position(steps=steps-1)
                elif add_tuples(current_position, (0, 1)) not in next_state.layout.walls:
                    next_state.pacman.position.direction = (0, 1)
                    next_state.pacman.position.coordinates = add_tuples(current_position, (0, 1))
                    return next_state.predict_pacman_position(steps=steps-1)
                elif add_tuples(current_position, (0, -1)) not in next_state.layout.walls:
                    next_state.pacman.position.direction = (0, -1)
                    next_state.pacman.position.coordinates = add_tuples(current_position, (0, -1))
                    return next_state.predict_pacman_position(steps=steps-1)
        return next_state

    def get_ghosts_bounty(self):
        """
        Compute the bounty for eating the ghosts.

        The rule is when pacman eats a ghost, he gets 200 points times the number of ghosts that are currently in the
        respawning state.
        """
        return (len(list(filter(lambda x: self.ghosts[x].dead > 0, self.ghosts))) + 1) * 200

    def pacman_just_crossed_ghost(self, ghost):
        if self.clipping_bug:
            return False
        pacman_prev = sub_tuples(self.pacman.position.coordinates, self.pacman.position.direction)
        ghost_prev = sub_tuples(ghost.position.coordinates, ghost.position.direction)
        if ghost_prev == self.pacman.position.coordinates and pacman_prev == ghost.position.coordinates:
            return True

    def compute_score(self):
        """
        Compute the score of the game and check for victory or defeat.

        Also sets the scared and dead states of the ghosts, based on whether they collide with pacman and if pacman eats
        a cherry.

        Victory is achieved when all the food is eaten.
        """
        ghost_bounty = self.get_ghosts_bounty()
        self.score -= TIME_PENALTY
        if self.pacman.position.coordinates in self.layout.food:
            self.score += 10
            self.layout.food.remove(self.pacman.position.coordinates)
        if self.pacman.position.coordinates in self.layout.cherries:
            self.score += 50
            for index, name in enumerate(self.ghosts):
                self.ghosts[name].scared = True
            self.layout.cherries.remove(self.pacman.position.coordinates)
        for index, name in enumerate(self.ghosts):
            if self.ghosts[name].position.coordinates == self.pacman.position.coordinates or \
                    self.pacman_just_crossed_ghost(self.ghosts[name]):
                if self.ghosts[name].scared:
                    self.score += ghost_bounty
                    self.ghosts[name].set_respawn()
                    ghost_bounty = self.get_ghosts_bounty()
                else:
                    self.score -= 500
                    logging.info(f"Pacman died! Final score: {self.score}")
                    self.game_over = True
        if len(self.layout.food) == 0:
            self.score += 500
            logging.info(f"Pacman won! Final score: {self.score}")
            self.game_over = True
        return self.game_over

