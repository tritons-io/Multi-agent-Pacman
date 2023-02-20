# Multi-agent Pacman

This project is widely inspired by the [Berkeley Pacman AI project](http://ai.berkeley.edu/project_overview.html).

The goal of this project is the same: provide an AI sandbox for developers to implement agents that can play Pacman.

The project is working with python3 and [pygame 2.1.3](https://github.com/pygame/pygame/releases/tag/2.1.3).

This environment aims to be simple and extensible.
- It is simple because there are not many dependencies and a straightforward way to implement your own agents.
- It is extensible because you can easily add complex agents while you progress in learning AI, and integrate complex patterns like Deep Q-Learning or Reinforcement Learning.

## Installation

- Download and install [python 3.10](https://www.python.org/downloads/) (_NB: as of 2023-20-02, the project is not working with python 3.11_) and install [pipenv](https://pypi.org/project/pipenv/).

- Clone the repository

```bash
git clone https://github.com/tritons-io/multi-agent-pacman.git
```

- Install the dependencies

```bash
pipenv install
```

It will install the dependencies in a virtual environment where you can add your own dependencies without affecting your system.


## Usage

`main.py [options]`

| Option                    | Description                                                               | Default                |
|---------------------------|---------------------------------------------------------------------------|------------------------|
| `-n`, `--number-of-games` | Number of games to play                                                   | 1                      |
| `-h`, `--help`            | Show the help message and exit                                            |                        |
| `-G`, `--no-graphics`     | Disable rendering                                                         | False                  |
| `-l`, `--layout`          | Layout file to use                                                        | `layouts/original.lay` |
| `-p`, `--pacman`          | Pacman agent to use                                                       | `RightTurnAgent`       |
| `-g`, `--ghosts`          | Ghosts agents to apply to all ghost instead of the original Pacman ghosts | None                   |
| `-C`, `--clipping-bug`    | Enable the clipping bug to check if the AI learn to exploit it            | False                  |
| `--log-level`             | Log level to use (DEBUG, INFO, WARNING, ERROR)                            | `INFO`                 |

### Clipping bug

With the option `-C`, the clipping bug is enabled. This bug is a bug made accidentally while developing this environment.
You will see that if Pacman is side by side with a ghost, and they switch positions, the ghost will go right through Pacman without killing him.

You can enable this bug to check if your AI is able to learn to exploit it.

## Layouts

The layouts are defined in the `layouts` folder.

The original Berkeley layout formats can be found in `layouts/legacy`, while there is a slightly modified version with additional characters in `layouts/original.lay`.
The layout file is a text file with the following format:

### Berkeley layout format:

| Character | Description                                                                              |
|-----------|------------------------------------------------------------------------------------------|
| ` `       | Empty space, both pacman and ghosts can walk on it                                       |
| `.`       | Dot, pacman can eat it                                                                   |
| `%`       | Wall, both pacman and ghosts can't walk on it                                            |
| `P`       | Pacman, the player                                                                       |
| `G`       | Ghost, spawn location of a Ghost                                                         |
| `o`       | Cherry, pacman can eat it to get more points and be able to eat ghosts for a short time  |

### Additional characters implemented by this project:

| Character  | Description                                                                                 |
|------------|---------------------------------------------------------------------------------------------|
| `b`        | Blinky, the ghost in this location will be red and use the agent BlinkyAgent                |
| `p`        | Pinky, the ghost in this location will be pink and use the agent PinkyAgent                 |
| `i`        | Inky, the ghost in this location will be cyan and use the agent InkyAgent                   |
| `c`        | Clyde, the ghost in this location will be orange and use the agent ClydeAgent               |
| `0-9`      | Portal, an agent entering this portal will be teleported to the portal with the same number |

## Ghosts

Like in the original Game, the Ghost have different behaviours (that's why they are now named in the layout file).

A layout defined by the Berkeley file format will attribute a behaviour to each ghost in order of parsing.

First ghost will be Blinky, second will be Pinky, then Inky and finally Clyde.

### Blinky
This is the red ghost. He will always try to go to the same location as Pacman.

### Pinky
This is the pink ghost. He will always try to go 4 tiles in front of Pacman.

### Inky
This is the cyan ghost. He exits his spawn location after a short amount of dots has been eaten by pacman. He will then target his location.

### Clyde
This is the orange ghost. He exits his spawn location after a large amount of dots has been eaten by pacman.  
He will then target his location, but if he is less than 8 tiles away from Pacman, he will flee.


## The pacman agent Class

You can define your own pacman agent by creating or importing a class in `libs/pacman_agents` that inherits from  `libs.PacmanAgent`.

The class must implement the method `get_action(self, state: PacmanState) -> Tuple[int, int]` that returns the action to perform.
The actions are:
- `(1, 0)` to go right
- `(-1, 0)` to go left
- `(0, 1)` to go up
- `(0, -1)` to go down

You can get the available actions by calling `get_legal_actions(state: PacmanState) -> List[Tuple[int, int]` on a PacmanAgent instance.
You can generate the next state for an action by calling `generate_successor(action: Tuple[int, int]) -> PacmanState` on a PacmanState instance.


### Get information from the game
Once loaded in the game, the food and cherries of the layout will be updated in real time, so you can get the following information:
- `state.layout.food` is a list of the food positions, expressed as a tuple of integers (x, y).
- So `len(state.layout.food)` is the number of food left on the map.
- `state.layout.cherries` is a list of the cherries positions, expressed as a tuple of integers (x, y).
- So `len(state.layout.cherries)` is the number of cherries left on the map.
The layout is attached to the PacmanState instance, so a generated successor will have its own layout.

The PacmanState also contains the following information:
- `state.ghosts` is a dictionary containing the ghosts agents instances, with the ghost name as key. `'blinky', 'pinky', 'inky', 'clyde'`
- The pacman agent instance can be accessed from the `state.pacman` attribute.
- The ghosts and pacman positions can be accessed from their respective instance attributes `position`.
  - `position` contains a `coordinates` attribute: the position of the agent, expressed as a tuple of integers (x, y).
  - `position` also contains a `direction` attribute: the direction the agent is facing, expressed as a tuple of integers (x, y) Expressed the same way as actions. `(1, 0)` for right, `(-1, 0)` for left, `(0, 1)` for up, `(0, -1)` for down.
- `state.score` is the current score of the game.
- `state.turn` is the number of turns that have been played since the beginning of the game, in other words the number of actions that have been performed by each agent.

## Contributing

If you want to contribute to this project, you can fork it and create a merge request, they are always welcome.
The main upgrades that are needed are:
- Record and replay system
- Change ghost behaviour:
  - Pinky should use a better way to calculate the projected position of Pacman
  - Inky should use its original game behaviour (draw a line between Blinky and Pacman, double the distance and go there)

You can also create an issue if you find a bug or want to suggest a feature: [https://github.com/tritons-io/multi-agent-pacman/issues](https://github.com/tritons-io/multi-agent-pacman/issues)
