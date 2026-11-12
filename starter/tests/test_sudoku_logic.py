import pytest

import sudoku_logic


def test_create_empty_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == 9
    assert all(len(row) == 9 for row in board)
    assert all(
        cell == 0
        for row in board
        for cell in row
    )


def test_is_safe_for_valid_number():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5)


def test_is_safe_rejects_duplicate_in_row():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)


def test_generate_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == 9
    assert len(solution) == 9

    assert sum(
        cell != 0
        for row in puzzle
        for cell in row
    ) == 35
    assert sudoku_logic.count_solutions(puzzle) == 1


@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [
        ("Easy", 40),
        ("Medium", 35),
        ("Hard", 30),
        (" EASY ", 40),
    ],
)
def test_generate_puzzle_for_each_difficulty(difficulty, expected_clues):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    assert sum(cell != 0 for row in puzzle for cell in row) == expected_clues
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][col] == 0 or puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


@pytest.mark.parametrize("difficulty", ["", "expert", 42])
def test_generate_puzzle_rejects_invalid_difficulty(difficulty):
    with pytest.raises(ValueError, match="difficulty must be"):
        sudoku_logic.generate_puzzle(difficulty=difficulty)


def test_count_solutions_finds_one_solution_without_changing_board():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    original = sudoku_logic.deep_copy(puzzle)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert puzzle == original


def test_count_solutions_stops_at_two_for_an_ambiguous_board():
    assert sudoku_logic.count_solutions(
        sudoku_logic.create_empty_board()
    ) == 2


def test_count_solutions_rejects_conflicting_givens():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 5

    assert sudoku_logic.count_solutions(board) == 0


def test_remove_cells_raises_if_unique_target_cannot_be_reached():
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    original = sudoku_logic.deep_copy(board)

    with pytest.raises(ValueError):
        sudoku_logic.remove_cells(board, 0)

    assert board == original
