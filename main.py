import argparse
import logging
from copy import copy
import time
from typing import Dict, Tuple

from libs import add_tuples, sub_tuples, reverse_tuple, BaseClass
from libs.animations import ANIMATIONS
from libs.layouts import Layout, manhattan_distance
from libs.pacman_controller import PacmanState
from random import choice

logger = logging.getLogger('root')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('Pacman - %(levelname)s - %(message)s'))
logger.addHandler(handler)

DELAY_BETWEEN_FRAMES = 0.015  # In seconds. Used to slow down the game for better visualization.
FRAME_PER_EPOCH = 16  # Number of frames between each game state update. Every 16 frames, agens take a new action, must be identical to the tile size.
SPRITE_OFFSET = (2, 0)
SPRITE_SIZE = (16, 16)


DISPLAY_COLORS = {  # I'm colorblind, please be gentle
    'blinky': (255, 0, 0),
    'pinky': (252, 181, 255),
    'inky': (0, 255, 255),
    'clyde': (248, 187, 85)
}

parser = argparse.ArgumentParser(
    prog='Multi-Agent Pacman',
    description='Runs an AI sandbox in the Pacman world'
)
parser.add_argument('-n', '--number-of-games', type=int, help='The number of games to play', default=1)
parser.add_argument('-G', '--no-graphics', action='store_true', help='Disable rendering', default=False)
parser.add_argument('-l', '--layout', help='The layout to use', default='layouts/original.lay')
parser.add_argument('-a', '--agent', help='The agent to use, must be a class in pacman_agents.py', default='RightTurnAgent')
parser.add_argument('-g', '--ghost-agent', help='If set, uses this agent for all ghosts', default=None)
parser.add_argument('-C', '--clipping-bug', action='store_true', help='Enable the clipping bug', default=False)

parser.add_argument('--log-level', help='The log level to use: DEBUG, INFO, WARNING, ERROR, CRITICAL', default='INFO')
# parser.add_argument('-K', '--keyboard', action='store_true', help='Use the keyboard to control Pacman', default=False)
args = parser.parse_args()

logger.setLevel(args.log_level)

run_pygame = not args.no_graphics
# keyboard_input = args.keyboard

if run_pygame:
    import pygame
    import pygame.locals

# if keyboard_input:
#     run_pygame = True
keyboard_input = False


class App(BaseClass):
    """
    The main application class. This class is responsible for updating the game state each iteration. And if graphics are
    enabled, it will also display the game in a window.
    """
    pacman_status = 'pacman_dead'
    pacman_animations = []
    ghost_animations = {
        'blinky': [],
        'pinky': [],
        'inky': [],
        'clyde': []
    }
    last_ghost_direction = {
        'blinky': None,
        'pinky': None,
        'inky': None,
        'clyde': None
    }
    pacman_position = (0, 0)
    ghost_positions: Dict[str, Tuple[int, int]] = {}
    game_state: PacmanState
    frame = 0
    last_pacman_direction = None

    def __init__(self):
        logging.info(f"Starting a new game")
        logging.info(f"Using layout {args.layout}")
        with open(args.layout, 'r') as f:
            layout_content = f.read()

        logging.info(f"Using agent {args.agent}")
        self.game_state = PacmanState(
            Layout(layout_content),
            pacman_agent=args.agent,
            clipping_bug=args.clipping_bug,
            ghost_agent=args.ghost_agent
        )

        if run_pygame:
            pygame.init()
            self.layout_size = self.game_state.layout.get_dimensions()
            self.size = self.weight, self.height = self.layout_size[0] * SPRITE_SIZE[0], self.layout_size[1] * SPRITE_SIZE[1] + 32 + (len(self.game_state.ghosts)) * SPRITE_SIZE[1]
            self._display_surf = pygame.display.set_mode(self.size, pygame.locals.HWSURFACE)
            self._background = pygame.image.load('sprites/bg.png')
            self._pacman_sprites = pygame.image.load('sprites/pacman.png')
            self._font = pygame.font.SysFont('arial', 16)
            self._pacman_sprites.set_colorkey((0, 0, 0))

        self._running = True
        self.pacman_position = self.game_state.pacman.position.coordinates[0] * SPRITE_SIZE[0], self.game_state.pacman.position.coordinates[1] * SPRITE_SIZE[1]
        for index, name in enumerate(self.game_state.ghosts):
            self.ghost_positions[name] = self.game_state.ghosts[name].position.coordinates[0] * SPRITE_SIZE[0], self.game_state.ghosts[name].position.coordinates[1] * SPRITE_SIZE[1]

    def on_event(self, event):
        """
            Event handler, only used when pygame is enabled
        """
        if event is not None:
            if event.type == pygame.locals.QUIT:
                self._running = False
        if keyboard_input:
            legal_actions = self.game_state.pacman.get_legal_actions(self.game_state)
            if self.game_state.pacman.position.direction not in legal_actions:
                self.game_state.pacman.position.direction = choice(legal_actions)
            if event is not None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if (0, -1) in legal_actions:
                            self.game_state.pacman.position.direction = (0, -1)
                    if event.key == pygame.K_DOWN:
                        if (0, 1) in legal_actions:
                            self.game_state.pacman.position.direction = (0, 1)
                    if event.key == pygame.K_LEFT:
                        if (-1, 0) in legal_actions:
                            self.game_state.pacman.position.direction = (-1, 0)
                    if event.key == pygame.K_RIGHT:
                        if (1, 0) in legal_actions:
                            self.game_state.pacman.position.direction = (1, 0)

    def game_over(self):
        """
            Called when the game is over
        """
        if run_pygame:
            pygame.event.post(pygame.event.Event(pygame.locals.QUIT))
        else:
            self._running = False

    def on_loop(self):
        """
            Main loop, called every frame.
            When pygame is not enabled, this loops runs each turn to update the game state
            When pygame is enabled, this loop runs each frame to update the display, and every 16 frames to update the game state.
        """
        if self.game_state.game_over:
            self.game_over()

        if self.frame % FRAME_PER_EPOCH == 0:
            self.pacman_position = self.game_state.pacman.position.coordinates[0] * SPRITE_SIZE[0], self.game_state.pacman.position.coordinates[1] * SPRITE_SIZE[1]
            for index, name in enumerate(self.game_state.ghosts):
                self.ghost_positions[name] = self.game_state.ghosts[name].position.coordinates[0] * SPRITE_SIZE[0], self.game_state.ghosts[name].position.coordinates[1] * SPRITE_SIZE[1]
            over = self.game_state.update(with_pacman=True, keyboard_input=keyboard_input)
            if over:
                self.game_over()

        self.pacman_position = add_tuples(self.pacman_position, self.game_state.pacman.position.direction)
        for index, name in enumerate(self.game_state.ghosts):
            self.ghost_positions[name] = add_tuples(self.ghost_positions[name], self.game_state.ghosts[name].position.direction)
        self.frame += 1

    def get_sprite_coordinates(self, coordinates):
        """
        Get the pixel coordinates of a sprite in the spritesheet using its grid coordinates
        """
        return coordinates[0] * SPRITE_SIZE[0] + SPRITE_OFFSET[0], coordinates[1] * SPRITE_SIZE[1] + SPRITE_OFFSET[1], SPRITE_SIZE[0], SPRITE_SIZE[1]

    def get_pacman_sprite(self):
        """
        Get the sprite coordinates of the pacman sprite used for the current animation frame
        """
        if len(self.pacman_animations) == 0:
            try:
                self.pacman_animations = copy(ANIMATIONS[f"pacman_{self.game_state.pacman.position.get_direction()}"])
                self.last_pacman_direction = f"pacman_{self.game_state.pacman.position.get_direction()}"
            except KeyError:
                self.pacman_animations = copy(ANIMATIONS[self.last_pacman_direction])
        return self.get_sprite_coordinates(self.pacman_animations.pop(0))

    def get_ghost_sprite(self, ghost_name: str, status: str):
        """
        For a given ghost name, get the sprite coordinates of the ghost sprite used for the current animation frame
        """
        if len(self.ghost_animations[ghost_name]) == 0:
            try:
                self.ghost_animations[ghost_name] = copy(ANIMATIONS[status])
                self.last_ghost_direction[ghost_name] = status
            except KeyError:
                self.ghost_animations[ghost_name] = copy(ANIMATIONS[self.last_ghost_direction[ghost_name]])
        return self.get_sprite_coordinates(self.ghost_animations[ghost_name].pop(0))

    def on_render(self):
        """
        Called every frame when pygame is enabled, to render the game state on the screen
        """
        self._display_surf.blit(self._background, (0, 0))
        self.render_layout()
        self.render_ghosts()
        self.render_score_and_distances()
        pygame.display.flip()

    def render_layout(self):
        for wall in self.game_state.layout.walls:
            self._display_surf.blit(self._pacman_sprites, (wall[0] * SPRITE_SIZE[0], wall[1] * SPRITE_SIZE[1]), self.get_sprite_coordinates((12, 2)))
        for food in self.game_state.layout.food:
            self._display_surf.blit(self._pacman_sprites, (food[0] * SPRITE_SIZE[0], food[1] * SPRITE_SIZE[1]), self.get_sprite_coordinates((12, 3)))
        for cherry in self.game_state.layout.cherries:
            self._display_surf.blit(self._pacman_sprites, (cherry[0] * SPRITE_SIZE[0], cherry[1] * SPRITE_SIZE[1]), self.get_sprite_coordinates((2, 3)))

        self._display_surf.blit(self._pacman_sprites, self.pacman_position, self.get_pacman_sprite())

    def render_ghosts(self):
        for index, name in enumerate(self.ghost_positions):
            direction = self.game_state.ghosts[name].position.get_direction()
            status = f"{name}_{direction}"
            if self.game_state.ghosts[name].scared:
                status = "ghost_scared"
            if self.game_state.ghosts[name].dead:
                status = f"ghost_dead_{direction}"
            self.check_ghost_in_portal(name, status)
            self._display_surf.blit(self._pacman_sprites, self.ghost_positions[name], self.get_ghost_sprite(name, status))

    def render_pacman(self):
        self._display_surf.blit(self._pacman_sprites, self.pacman_position, self.get_pacman_sprite())

    def render_score_and_distances(self):
        score = self._font.render(f"Score: {self.game_state.score}", True, (255, 255, 255))
        self._display_surf.blit(score, (SPRITE_SIZE[0], self.layout_size[1] * SPRITE_SIZE[1]))
        distances = self._font.render(f"Distances:", True, (255, 255, 255))
        self._display_surf.blit(distances, (SPRITE_SIZE[0], self.layout_size[1] * SPRITE_SIZE[1] + SPRITE_SIZE[1] * 1))
        for index, ghost in enumerate(self.game_state.ghosts):
            d_ghost = self._font.render(
                f"- {ghost}: {manhattan_distance(self.game_state.ghosts[ghost].position.coordinates, self.game_state.pacman.position.coordinates)}",
                True, DISPLAY_COLORS[ghost])
            self._display_surf.blit(d_ghost,
                                    (SPRITE_SIZE[0], self.layout_size[1] * SPRITE_SIZE[1] + SPRITE_SIZE[1] * (index + 2)))

    def check_ghost_in_portal(self, ghost_name, status):
        """
        Check if a ghost is in a portal, and if so, starts to draw it at the other side of the portal
        """
        for portal in self.game_state.layout.portals:
            if self.game_state.ghosts[ghost_name].position.coordinates in self.game_state.layout.portals[portal]:
                source_portal = self.game_state.layout.portals[portal][0] if self.game_state.ghosts[ghost_name].position.coordinates == self.game_state.layout.portals[portal][1] else self.game_state.layout.portals[portal][1]
                source_portal = (source_portal[0] * SPRITE_SIZE[0], source_portal[1] * SPRITE_SIZE[1])
                source_portal = add_tuples(source_portal, (self.game_state.ghosts[ghost_name].position.direction[0] * SPRITE_SIZE[0], self.game_state.ghosts[ghost_name].position.direction[1] * SPRITE_SIZE[1]))
                ghost_position = self.game_state.ghosts[ghost_name].position.coordinates[0] * SPRITE_SIZE[0], self.game_state.ghosts[ghost_name].position.coordinates[1] * SPRITE_SIZE[1]
                ghost_offset = reverse_tuple(sub_tuples(self.ghost_positions[ghost_name], ghost_position))

                self._display_surf.blit(self._pacman_sprites, sub_tuples(source_portal, ghost_offset), self.get_ghost_sprite(ghost_name, status))

    def check_pacman_in_portal(self):
        """
        Check if pacman is in a portal, and if so, starts to draw it at the other side of the portal
        """
        for portal in self.game_state.layout.portals:
            if self.game_state.pacman.position.coordinates in self.game_state.layout.portals[portal]:
                source_portal = self.game_state.layout.portals[portal][0] if self.game_state.pacman.position.coordinates == self.game_state.layout.portals[portal][1] else self.game_state.layout.portals[portal][1]
                source_portal = (source_portal[0] * SPRITE_SIZE[0], source_portal[1] * SPRITE_SIZE[1])
                source_portal = add_tuples(source_portal, (self.game_state.pacman.position.direction[0] * SPRITE_SIZE[0], self.game_state.pacman.position.direction[1] * SPRITE_SIZE[1]))
                pacman_position = self.game_state.pacman.position.coordinates[0] * SPRITE_SIZE[0], self.game_state.pacman.position.coordinates[1] * SPRITE_SIZE[1]
                pacman_offset = reverse_tuple(sub_tuples(self.pacman_position, pacman_position))
                self._display_surf.blit(self._pacman_sprites, sub_tuples(source_portal, pacman_offset), self.get_pacman_sprite())

    def on_cleanup(self):
        pygame.quit()

    def start(self):
        """
        Main loop of the game
        """
        while self._running:
            if run_pygame:
                for event in pygame.event.get():
                    self.on_event(event)
            self.on_loop()
            if run_pygame:
                time.sleep(DELAY_BETWEEN_FRAMES)
                self.on_render()
            else:
                self.frame += FRAME_PER_EPOCH

        if run_pygame:
            self.on_cleanup()


if __name__ == "__main__":
    for i in range(args.number_of_games):
        theApp = App()
        theApp.start()
