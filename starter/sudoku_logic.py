import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 35,
    "hard": 30,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def count_solutions(board):
    working_board = deep_copy(board)

    # Reject boards whose already-filled cells violate Sudoku rules.
    for row in range(SIZE):
        for col in range(SIZE):
            number = working_board[row][col]
            if number != EMPTY:
                if number not in range(1, SIZE + 1):
                    return 0
                working_board[row][col] = EMPTY
                is_valid = is_safe(working_board, row, col, number)
                working_board[row][col] = number
                if not is_valid:
                    return 0

    solutions = 0

    def search():
        nonlocal solutions

        if solutions >= 2:
            return

        best_cell = None
        best_candidates = None
        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] == EMPTY:
                    candidates = [
                        number
                        for number in range(1, SIZE + 1)
                        if is_safe(working_board, row, col, number)
                    ]
                    if not candidates:
                        return
                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_cell = (row, col)
                        best_candidates = candidates
                        if len(best_candidates) == 1:
                            break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            solutions += 1
            return

        row, col = best_cell
        for candidate in best_candidates:
            working_board[row][col] = candidate
            search()
            working_board[row][col] = EMPTY
            if solutions >= 2:
                return

    search()
    return solutions

def remove_cells(board, clues):
    if not isinstance(clues, int) or not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be an integer between 0 and 81")

    working_board = deep_copy(board)
    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if working_board[row][col] != EMPTY
    ]
    random.shuffle(positions)

    for row, col in positions:
        current_clues = sum(
            cell != EMPTY
            for board_row in working_board
            for cell in board_row
        )
        if current_clues <= clues:
            break

        original_number = working_board[row][col]
        working_board[row][col] = EMPTY
        if count_solutions(working_board) != 1:
            working_board[row][col] = original_number

    final_clues = sum(
        cell != EMPTY
        for row in working_board
        for cell in row
    )
    if final_clues != clues:
        raise ValueError(
            "could not reach the requested clue count while keeping one solution"
        )

    for row in range(SIZE):
        board[row][:] = working_board[row]

def generate_puzzle(clues=35, difficulty=None):
    if difficulty is not None:
        if not isinstance(difficulty, str):
            raise ValueError("difficulty must be Easy, Medium, or Hard")
        difficulty_name = difficulty.strip().lower()
        if difficulty_name not in DIFFICULTY_CLUES:
            raise ValueError("difficulty must be Easy, Medium, or Hard")
        clues = DIFFICULTY_CLUES[difficulty_name]

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
