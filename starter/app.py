import os
import secrets
import time
from threading import RLock

from flask import Flask, render_template, jsonify, request
from flask import session
import sudoku_logic

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

GAMES = {}
GAME_TTL_SECONDS = 24 * 60 * 60
GAME_LOCK = RLock()


def _remove_expired_games(now):
    expired_games = [
        game_id
        for game_id, game in GAMES.items()
        if now - game["last_access"] > GAME_TTL_SECONDS
    ]
    for game_id in expired_games:
        del GAMES[game_id]


def get_current_game():
    with GAME_LOCK:
        now = time.monotonic()
        _remove_expired_games(now)
        game_id = session.get("game_id")
        game = GAMES.get(game_id)
        if game is not None:
            game["last_access"] = now
        return game


def store_current_game(puzzle, solution):
    with GAME_LOCK:
        now = time.monotonic()
        _remove_expired_games(now)
        game_id = session.get("game_id")
        if game_id is None:
            game_id = secrets.token_urlsafe(32)
            session["game_id"] = game_id
        GAMES[game_id] = {
            "puzzle": puzzle,
            "solution": solution,
            "hinted": set(),
            "hints_used": 0,
            "last_access": now,
        }

def is_valid_board(board):
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(
            isinstance(row, list)
            and len(row) == sudoku_logic.SIZE
            and all(type(cell) is int and 0 <= cell <= sudoku_logic.SIZE for cell in row)
            for row in board
        )
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    try:
        if difficulty is None:
            clues = int(request.args.get('clues', 35))
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
        else:
            puzzle, solution = sudoku_logic.generate_puzzle(
                difficulty=difficulty
            )
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    store_current_game(puzzle, solution)
    response = {'puzzle': puzzle}
    if difficulty is not None:
        response['difficulty'] = difficulty.strip().capitalize()
    return jsonify(response)

@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if not is_valid_board(board):
        return jsonify({'error': 'A valid 9x9 board is required'}), 400

    with GAME_LOCK:
        game = get_current_game()
        if game is None:
            return jsonify({'error': 'No game in progress'}), 400

        for row in range(sudoku_logic.SIZE):
            for col in range(sudoku_logic.SIZE):
                position = (row, col)
                if (
                    game["puzzle"][row][col] == sudoku_logic.EMPTY
                    and board[row][col] == sudoku_logic.EMPTY
                    and position not in game["hinted"]
                ):
                    game["hinted"].add(position)
                    game["hints_used"] += 1
                    return jsonify({
                        'hint': {
                            'row': row,
                            'col': col,
                            'value': game["solution"][row][col]
                        },
                        'hints_used': game["hints_used"]
                    })

        return jsonify({
            'hint': None,
            'message': 'There are no empty cells left to hint.',
            'hints_used': game["hints_used"]
        })

@app.route('/check', methods=['POST'])
def check_solution():
    game = get_current_game()
    if game is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if not is_valid_board(board):
        return jsonify({'error': 'A valid 9x9 board is required'}), 400

    solution = game["solution"]
    puzzle = game["puzzle"]
    hinted = game["hinted"]
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if (
                puzzle[i][j] == sudoku_logic.EMPTY
                and (i, j) not in hinted
                and board[i][j] != sudoku_logic.EMPTY
                and board[i][j] != solution[i][j]
            ):
                incorrect.append([i, j])

    complete = all(
        board[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    return jsonify({'incorrect': incorrect, 'complete': complete})

if __name__ == '__main__':
    app.run(debug=True)