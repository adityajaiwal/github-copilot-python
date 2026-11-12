import secrets
import time

import pytest

import app


@pytest.fixture
def active_game(monkeypatch):
    solution = [
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
    puzzle = [row[:] for row in solution]
    puzzle[0][0] = 0
    puzzle[0][2] = 0
    game_id = secrets.token_urlsafe(12)
    monkeypatch.setitem(
        app.GAMES,
        game_id,
        {
            "puzzle": puzzle,
            "solution": solution,
            "hinted": set(),
            "hints_used": 0,
            "last_access": time.monotonic(),
        },
    )
    client = app.app.test_client()
    with client.session_transaction() as browser_session:
        browser_session["game_id"] = game_id
    return puzzle, solution, client


def get_client_game(client):
    with client.session_transaction() as browser_session:
        return app.GAMES[browser_session["game_id"]]


def test_home_page_displays_timer():
    response = app.app.test_client().get("/")

    assert response.status_code == 200
    assert b'id="timer"' in response.data
    assert b"00:00" in response.data
    assert b"Top 10 Fastest Times" in response.data
    assert b'id="score-entry"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'id="theme-status"' in response.data
    assert b'name="viewport"' in response.data
    assert b'aria-label="Sudoku puzzle"' in response.data
    assert b'aria-live="polite"' in response.data


def test_theme_assets_include_light_dark_variables_and_persistence():
    client = app.app.test_client()

    css_response = client.get("/static/styles.css")
    js_response = client.get("/static/main.js")

    assert css_response.status_code == 200
    assert b":root" in css_response.data
    assert b':root[data-theme="dark"]' in css_response.data
    assert b"--page-bg" in css_response.data
    assert js_response.status_code == 200
    assert b"sudokuTheme" in js_response.data
    assert b"applyTheme" in js_response.data
    assert b"alternate-box" in css_response.data
    assert b"addEventListener('input', handleBoardInput)" in js_response.data
    assert b"aria-label" in js_response.data


@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [
        ("easy", 40),
        ("medium", 35),
        ("hard", 30),
    ],
)
def test_new_game_route_accepts_difficulty(difficulty, expected_clues):
    client = app.app.test_client()

    response = client.get("/new", query_string={"difficulty": difficulty})

    assert response.status_code == 200
    data = response.get_json()
    assert data["difficulty"] == difficulty.capitalize()
    assert sum(cell != 0 for row in data["puzzle"] for cell in row) == expected_clues
    game = get_client_game(client)
    assert game["hints_used"] == 0
    assert game["hinted"] == set()


def test_new_game_route_rejects_invalid_difficulty():
    client = app.app.test_client()

    response = client.get("/new", query_string={"difficulty": "expert"})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_new_game_route_preserves_clue_count_parameter():
    client = app.app.test_client()

    response = client.get("/new", query_string={"clues": 35})

    assert response.status_code == 200
    data = response.get_json()
    assert sum(cell != 0 for row in data["puzzle"] for cell in row) == 35


def test_hint_route_fills_one_empty_cell_and_tracks_hint_count(active_game):
    puzzle, solution, client = active_game

    response = client.post("/hint", json={"board": puzzle})

    assert response.status_code == 200
    data = response.get_json()
    assert data["hint"] == {"row": 0, "col": 0, "value": solution[0][0]}
    assert data["hints_used"] == 1
    assert get_client_game(client)["hinted"] == {(0, 0)}


def test_hint_route_reports_when_no_empty_cells_remain(active_game):
    _, solution, client = active_game

    response = client.post("/hint", json={"board": solution})

    assert response.status_code == 200
    data = response.get_json()
    assert data["hint"] is None
    assert "no empty cells" in data["message"].lower()


def test_check_route_reports_only_incorrect_player_entries(active_game):
    puzzle, _, client = active_game
    get_client_game(client)["hinted"].add((0, 0))
    board = [row[:] for row in puzzle]
    board[0][0] = 9  # Hinted cell
    board[0][1] = 9  # Originally prefilled cell
    board[0][2] = 9  # Incorrect player entry

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    data = response.get_json()
    assert data["incorrect"] == [[0, 2]]
    assert data["complete"] is False


@pytest.mark.parametrize("endpoint", ["/hint", "/check"])
def test_game_routes_reject_invalid_boards(endpoint, active_game):
    _, _, client = active_game

    response = client.post(endpoint, json={"board": [[1, 2]]})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_check_route_accepts_a_fully_solved_board(active_game):
    _, solution, client = active_game

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [], "complete": True}


def test_check_route_rejects_request_without_active_game():
    client = app.app.test_client()

    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_game_state_is_isolated_between_browser_sessions(monkeypatch):
    base_solution = [
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
    other_solution = [
        [number % 9 + 1 for number in row]
        for row in base_solution
    ]

    def generate_puzzle(clues=35, difficulty=None):
        solution = base_solution if difficulty == "easy" else other_solution
        puzzle = [row[:] for row in solution]
        puzzle[0][0] = 0
        puzzle[0][2] = 0
        return puzzle, [row[:] for row in solution]

    monkeypatch.setattr(app.sudoku_logic, "generate_puzzle", generate_puzzle)
    first_client = app.app.test_client()
    second_client = app.app.test_client()
    first_puzzle = first_client.get("/new?difficulty=easy").get_json()["puzzle"]
    second_puzzle = second_client.get("/new?difficulty=hard").get_json()["puzzle"]

    with first_client.session_transaction() as first_session:
        first_game_id = first_session["game_id"]
        assert "solution" not in first_session
    with second_client.session_transaction() as second_session:
        second_game_id = second_session["game_id"]
        assert "solution" not in second_session

    first_hint = first_client.post("/hint", json={"board": first_puzzle}).get_json()
    second_hint = second_client.post("/hint", json={"board": second_puzzle}).get_json()

    assert first_game_id != second_game_id
    assert first_hint["hint"]["value"] == base_solution[0][0]
    assert second_hint["hint"]["value"] == other_solution[0][0]
    assert app.GAMES[first_game_id]["hints_used"] == 1
    assert app.GAMES[second_game_id]["hints_used"] == 1
