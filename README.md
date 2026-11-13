# Sudoku Flask Game

A browser-based Sudoku game with Easy, Medium, and Hard puzzles, unique-solution
generation, hints, answer checking, a timer, a local leaderboard, and light/dark
themes.


## Features

- **Sudoku Gameplay:** Interactive 9×9 Sudoku board.
- **Difficulty Levels:** Easy, Medium, and Hard puzzles.
- **Unique Solution:** Every generated puzzle has exactly one valid solution.
- **Hint System:** Reveal one correct empty cell at a time.
- **Answer Checking:** Identify incorrect player entries.
- **Game Timer:** Track the time taken to complete a puzzle.
- **Leaderboard:** Save the top 10 fastest completed games.
- **Theme Selection:** Switch between Light and Dark modes.
- **Responsive Design:** Play on desktop, tablet, and mobile devices.
- **Input Validation:** Prevent invalid and conflicting entries.



## Requirements

- Python 3.10 or newer
- A modern web browser

## Install

Open a terminal at the repository root, then move into the application folder:

```powershell
cd starter
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

Install the application and test dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the game

From the `starter` directory, start Flask:

```powershell
python app.py
```

Open <http://127.0.0.1:5000> in a browser. The built-in Flask server is for
local development; use a production WSGI server for deployment.

## Run tests

From the `starter` directory:

```powershell
python -m pytest -v
```

## Browser storage

The leaderboard and selected theme are saved in the current browser's
`localStorage`. They are not shared between browsers or devices.

Active puzzles are stored in the Flask server process and associated with a
signed browser session. They expire after 24 hours and are cleared when the
server restarts. For deployment, set `FLASK_SECRET_KEY` to a long, random value
and use a shared server-side store if the app runs with multiple worker
processes.


## Test Results

The project test suite currently contains 30 passing tests.

Run the following command to verify:

python -m pytest -v

## Project Screenshots

Screenshots documenting the development process and GitHub Copilot interactions are available in:

`starter/screenshots/`

They include evidence of:
- Testing framework setup.
- Unique Sudoku solution validation.
- Difficulty selection.
- Hint and answer-checking functionality.
- Leaderboard implementation.
- Timer and theme functionality.
- Responsive design.
- Critical evaluation of a GitHub Copilot suggestion.