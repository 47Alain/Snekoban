"""
6.1010 Lab:
Snekoban Game
"""

import json  # optional import for loading test_levels
import typing  # optional import
import pprint  # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}
PLAYER = 0
TARGET_FLAGS = 1
WALLS = 2
COMPUTERS = 3


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    player_position = None
    target_flag = set()
    wall_position = set()
    computer_position = set()

    for r, row in enumerate(level_description):
        for c, char in enumerate(row):
            for element in char:
                if element == "player":
                    player_position = (r, c)
                elif element == "target":
                    target_flag.add((r, c))
                elif element == "wall":
                    wall_position.add((r, c))
                elif element == "computer":
                    computer_position.add((r, c))

    return (
        player_position,
        frozenset(target_flag),
        frozenset(wall_position),
        frozenset(computer_position),
    )


def find_player(game):
    """
    Finds the players location
    Args:
        game: our game description

    Returns:
        tuple: game player position
    """

    return game[PLAYER]


def move_player(game, r, c, nr, nc):
    """
    Attempts to move the player from (r, c) to (nr, nc) in the
    given game state.

    The function checks if the new position is valid:
    - If (nr, nc) is a wall, the player cannot move.
    - If (nr, nc) contains a computer, the computer is pushed in
    the same direction.
      - If the new computer position is a wall or another object,
      movement is blocked.
    - Otherwise, the player moves to (nr, nc).

    Returns the updated game state as a tuple.
    """
    _, target_flags, walls, computers = game[0], game[1], game[2], game[3]

    if (nr, nc) in walls: #You cant move if the newposition is in walls
        return game
    if (nr, nc) in computers:
        dr, dc = nr - r, nc - c
        new_computer_position = (nr + dr, nc + dc)

        #You cant move if the new_computer position is in walls
        if new_computer_position in walls or new_computer_position in game:
            return game

        new_computer_set = set(computers)
        new_computer_set.remove((nr, nc))
        new_computer_set.add(new_computer_position)

        return ((nr, nc), target_flags, walls, frozenset(new_computer_set))

    return ((nr, nc), target_flags, walls, computers)


def count_target_flags(game):
    """

    Args:
        game: our game description

    Returns: length of the counrt_flags we have
    """
    return len(game[TARGET_FLAGS])


def can_move(game, r, c, nr, nc):
    """
    Checks if the player can move from (r, c) to (nr, nc).
    """
    _, _, walls, computers = game[0], game[1], game[2], game[3]
    dr, dc = nr - r, nc - c

    return (
        (nr, nc) not in walls
        and (nr, nc) not in computers
        or (nr + dr, nc + dc) not in walls
        and (nr + dr, nc + dc) not in computers
    )


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """

    _, target_flag_set, _, computer_position_set = game

    if len(computer_position_set) == 0 or len(target_flag_set) == 0:
        return False

    elif computer_position_set == target_flag_set:
        return True

    else:
        return False


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    r, c = find_player(game)

    dr, dc = DIRECTION_VECTOR[direction]

    nr, nc = r + dr, c + dc

    if can_move(game, r, c, nr, nc):
        new_game = move_player(game, r, c, nr, nc)
        return new_game

    return game


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    player_position, target_flags, walls, computers = game[0], game[1], game[2], game[3]

    all_positions = set(
        list(target_flags) + list(walls) + list(computers) + [player_position]
    )

    if all_positions:
        max_row = max(r for r, _ in all_positions) + 1
        max_col = max(c for _, c in all_positions) + 1


    else:
        max_row, max_col = (1, 1)

    # We need to also store our empty_set for positions where we have nothing,
    our_level_description = [[[] for _ in range(max_col)] for _ in range(max_row)]


    for r, c in walls:

        our_level_description[r][c].append("wall")

    for r, c in target_flags:
        our_level_description[r][c].append("target")

    for r, c in computers:
        our_level_description[r][c].append("computer")

    pr, pc = find_player(game)

    our_level_description[pr][pc].append("player")

    return our_level_description


def find_path(neighbors_function, start, goal_test):
    """
    Return the shortest path through a graph from a given starting state to
    any state that satsifies a given goal condition

    Parameters:
      *neighbors_function(state) is a function which returns a list of legal
       neighbor states

      *start is the starting state for the search

      * goal_test(state) is a function which returns True if
      the given state is a goal state for search , and False otherwise.

    Returns: a shortest path from start to a state satisfying goal_test(state)
    as a tuple of states or None if no path exists.

    """
    if goal_test(start):
        return []  # No moves needed if already solved

    agenda = [(start, [])]  # (state, path taken)
    visited = set()
    visited.add(start)

    while agenda:

        current_state, path = agenda.pop(0)

        for neighbor, move in neighbors_function(current_state):
            if neighbor not in visited:
                new_path = path + [move]

                if goal_test(neighbor):
                    return new_path
                agenda.append((neighbor, new_path))
                visited.add(neighbor)

    return None


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    def neighbors(game):

        r, c = find_player(game)

        possible_moves = []

        for direction, (dr, dc) in DIRECTION_VECTOR.items():
            nr, nc = r + dr, c + dc

            if can_move(game, r, c, nr, nc):
                new_game = step_game(game, direction)
                possible_moves.append((new_game, direction)) #keep track both of the direction and the game

        return possible_moves

    def goal_test(game):
        return victory_check(game)

    start = game

    def get_neighbor_states(game):
        """Helper function to get a list of states from neighbors."""
        return neighbors(game)

    path = find_path(get_neighbor_states, start, goal_test)


    return path



if __name__ == "__main__":

    # game = [[["wall"], ["wall"], ["wall"], ["wall"], ["wall"]], [["wall"], [], [], [], ["wall"]], [["wall"], [], ["player"], [], ["wall"]], [["wall"], [], [], [], ["wall"]], [["wall"], ["wall"], ["wall"], ["wall"], ["wall"]]]
    # # print(dump_game(make_new_game(game)))
    # new_game = make_new_game(game)

    # new_1 = step_game(new_game,"up")
    # # print(step_game(new_1,"up"))
    # print(dump_game(new_1))

    # game = [
    #   [["wall"], ["wall"], ["wall"], ["wall"], [], [], []],
    #   [["wall"], [], [], ["wall"], ["wall"], ["wall"], ["wall"]],
    #   [["wall"], [], ["target"], [], ["target"], [], ["wall"]],
    #   [["wall"], [], ["computer"], ["computer"], ["wall"], ["player"], ["wall"]],
    #   [["wall"], ["wall"], [], [], [], [], ["wall"]],
    #   [[], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]]
    # ]
    #     new_game = make_new_game(game)

    #     game = [
    #   [[], [], [], ["wall"], ["wall"], ["wall"], ["wall"]],
    #   [[], [], [], ["wall"], [], [], ["wall"]],
    #   [[], [], [], ["wall"], ["player"], [], ["wall"]],
    #   [["wall"], ["wall"], ["wall"], ["wall"], [], ["target", "computer"], ["wall"]],
    #   [["wall"], [], [], [], [], ["target", "computer"], ["wall"]],
    #   [["wall"], [], ["wall"], [], [], ["target", "computer"], ["wall"]],
    #   [["wall"], [], [], [], [], ["wall"], ["wall"]],
    #   [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], []]
    # ]

    #     new_game = make_new_game(game)

    #     print(new_game)
    # print(dump_game(new_game))
    pass
