TUPLE_ELONGATION = 5  # How many times a tuple should be repeated in the animation list


def elongate_tuple_list(tuples: list, length: int) -> list:
    """
    Elongates a list of tuples by repeating each tuple a given number of times. Used to produce longer and smoother animations.
    :param tuples: list of tuples
    :param length: number of times each tuple should be repeated
    :return:
    """
    tuple_list = []
    for element in tuples:
        tuple_list += [element for _ in range(length)]
    return tuple_list


ANIMATIONS = {
    'pacman_right': elongate_tuple_list([(0, 0), (1, 0)], TUPLE_ELONGATION),
    'pacman_left': elongate_tuple_list([(0, 1), (1, 1)], TUPLE_ELONGATION),
    'pacman_down': elongate_tuple_list([(0, 2), (1, 2)], TUPLE_ELONGATION),
    'pacman_up': elongate_tuple_list([(0, 3), (1, 3)], TUPLE_ELONGATION),
    'pacman_dead': elongate_tuple_list([(3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0)], TUPLE_ELONGATION),
    'blinky_right': elongate_tuple_list([(0, 4), (1, 4)], TUPLE_ELONGATION),
    'blinky_left': elongate_tuple_list([(2, 4), (3, 4)], TUPLE_ELONGATION),
    'blinky_down': elongate_tuple_list([(4, 4), (5, 4)], TUPLE_ELONGATION),
    'blinky_up': elongate_tuple_list([(6, 4), (7, 4)], TUPLE_ELONGATION),
    'pinky_right': elongate_tuple_list([(0, 5), (1, 5)], TUPLE_ELONGATION),
    'pinky_left': elongate_tuple_list([(2, 5), (3, 5)], TUPLE_ELONGATION),
    'pinky_down': elongate_tuple_list([(4, 5), (5, 5)], TUPLE_ELONGATION),
    'pinky_up': elongate_tuple_list([(6, 5), (7, 5)], TUPLE_ELONGATION),
    'inky_right': elongate_tuple_list([(0, 6), (1, 6)], TUPLE_ELONGATION),
    'inky_left': elongate_tuple_list([(2, 6), (3, 6)], TUPLE_ELONGATION),
    'inky_down': elongate_tuple_list([(4, 6), (5, 6)], TUPLE_ELONGATION),
    'inky_up': elongate_tuple_list([(6, 6), (7, 6)], TUPLE_ELONGATION),
    'clyde_right': elongate_tuple_list([(0, 7), (1, 7)], TUPLE_ELONGATION),
    'clyde_left': elongate_tuple_list([(2, 7), (3, 7)], TUPLE_ELONGATION),
    'clyde_down': elongate_tuple_list([(4, 7), (5, 7)], TUPLE_ELONGATION),
    'clyde_up': elongate_tuple_list([(6, 7), (7, 7)], TUPLE_ELONGATION),
    'ghost_scared': elongate_tuple_list([(8, 4), (9, 4), (10, 4), (11, 4)], TUPLE_ELONGATION),
    'ghost_dead_right': [(8, 5)],
    'ghost_dead_left': [(9, 5)],
    'ghost_dead_down': [(10, 5)],
    'ghost_dead_up': [(11, 5)],
}
