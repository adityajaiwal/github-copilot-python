// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const LEADERBOARD_LIMIT = 10;
const THEME_KEY = 'sudokuTheme';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let currentDifficulty = 'Medium';
let gameCompleted = false;
let scoreSubmitted = false;
let leaderboardScores = [];
let leaderboardAvailable = true;

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function isValidScore(score) {
  return score !== null
    && typeof score === 'object'
    && typeof score.name === 'string'
    && score.name.trim().length > 0
    && Number.isInteger(score.timeSeconds)
    && score.timeSeconds >= 0
    && ['Easy', 'Medium', 'Hard'].includes(score.difficulty)
    && Number.isInteger(score.hintsUsed)
    && score.hintsUsed >= 0;
}

function setLeaderboardStatus(message, isError = false) {
  const status = document.getElementById('leaderboard-status');
  status.innerText = message;
  status.classList.toggle('error', isError);
}

function setThemeStatus(message, isError = false) {
  const status = document.getElementById('theme-status');
  status.innerText = message;
  status.classList.toggle('error', isError);
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const isDark = theme === 'dark';
  const toggle = document.getElementById('theme-toggle');
  toggle.innerText = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  toggle.setAttribute('aria-pressed', String(isDark));
}

function restoreTheme() {
  let theme = 'light';
  try {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'light' || savedTheme === 'dark') {
      theme = savedTheme;
    } else if (savedTheme !== null) {
      setThemeStatus('Saved theme was invalid; Light Mode is active.', true);
    }
  } catch (error) {
    setThemeStatus('Theme preference could not be loaded; using Light Mode.', true);
  }
  applyTheme(theme);
}

function toggleTheme() {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(theme);
  try {
    localStorage.setItem(THEME_KEY, theme);
    setThemeStatus('');
  } catch (error) {
    setThemeStatus('Theme changed, but the preference could not be saved.', true);
  }
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  body.innerHTML = '';

  if (leaderboardScores.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.innerText = 'No completed games yet.';
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }

  leaderboardScores.forEach((score, index) => {
    const row = document.createElement('tr');
    const values = [
      index + 1,
      score.name,
      formatTime(score.timeSeconds),
      score.difficulty,
      score.hintsUsed
    ];
    values.forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = String(value);
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
}

function loadLeaderboard() {
  try {
    const savedScores = localStorage.getItem(LEADERBOARD_KEY);
    if (savedScores === null) {
      leaderboardScores = [];
      return true;
    }

    const parsedScores = JSON.parse(savedScores);
    if (!Array.isArray(parsedScores) || !parsedScores.every(isValidScore)) {
      throw new Error('Saved leaderboard data has an invalid format.');
    }
    const sortedScores = parsedScores
      .sort((first, second) => first.timeSeconds - second.timeSeconds);
    leaderboardScores = sortedScores.slice(0, LEADERBOARD_LIMIT);
    if (leaderboardScores.length < sortedScores.length) {
      localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(leaderboardScores));
    }
    return true;
  } catch (error) {
    leaderboardScores = [];
    setLeaderboardStatus('Saved scores could not be loaded from browser storage.', true);
    return false;
  }
}

function saveScore() {
  if (!gameCompleted || scoreSubmitted) {
    return;
  }

  const nameInput = document.getElementById('player-name');
  const name = nameInput.value.trim();
  const message = document.getElementById('score-entry-message');
  if (!name) {
    message.innerText = 'Please enter your name before saving.';
    nameInput.focus();
    return;
  }
  if (!leaderboardAvailable) {
    message.innerText = 'Scores cannot be saved because browser storage is unavailable.';
    return;
  }

  const score = {
    name: name,
    timeSeconds: elapsedSeconds,
    difficulty: currentDifficulty,
    hintsUsed: hintsUsed
  };
  const updatedScores = [...leaderboardScores, score]
    .sort((first, second) => first.timeSeconds - second.timeSeconds)
    .slice(0, LEADERBOARD_LIMIT);

  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(updatedScores));
  } catch (error) {
    message.innerText = 'Your score could not be saved to browser storage.';
    return;
  }

  leaderboardScores = updatedScores;
  renderLeaderboard();
  setLeaderboardStatus('Score saved.');
  scoreSubmitted = true;
  document.getElementById('score-entry').hidden = true;
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  resetTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      inp.setAttribute('aria-describedby', 'board-help');
      inp.inputMode = 'numeric';
      if ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 1) {
        inp.classList.add('alternate-box');
      }
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function updateConflicts() {
  const cells = Array.from(
    document.getElementById('sudoku-board').getElementsByTagName('input')
  );
  cells.forEach((cell) => cell.classList.remove('conflict'));

  for (let first = 0; first < cells.length; first += 1) {
    const firstValue = cells[first].value;
    if (!firstValue) continue;

    const firstRow = Math.floor(first / SIZE);
    const firstCol = first % SIZE;
    for (let second = first + 1; second < cells.length; second += 1) {
      if (cells[second].value !== firstValue) continue;

      const secondRow = Math.floor(second / SIZE);
      const secondCol = second % SIZE;
      const sharesRow = firstRow === secondRow;
      const sharesColumn = firstCol === secondCol;
      const sharesBox = Math.floor(firstRow / 3) === Math.floor(secondRow / 3)
        && Math.floor(firstCol / 3) === Math.floor(secondCol / 3);
      if (sharesRow || sharesColumn || sharesBox) {
        if (!cells[first].disabled) cells[first].classList.add('conflict');
        if (!cells[second].disabled) cells[second].classList.add('conflict');
      }
    }
  }
}

function handleBoardInput(event) {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !input.classList.contains('sudoku-cell') || input.disabled) {
    return;
  }

  input.value = input.value.replace(/[^1-9]/g, '');
  input.classList.remove('incorrect');
  updateConflicts();
}

async function newGame() {
  resetTimer();
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error || 'Could not start a new game.';
    return;
  }
  renderPuzzle(data.puzzle);
  currentDifficulty = data.difficulty || difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  gameCompleted = false;
  scoreSubmitted = false;
  document.getElementById('score-entry').hidden = true;
  document.getElementById('player-name').value = '';
  document.getElementById('score-entry-message').innerText = '';
  startTimer();
  hintsUsed = 0;
  document.getElementById('hints-used').innerText = `Hints used: ${hintsUsed}`;
  document.getElementById('message').innerText = '';
}

function readBoard() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function useHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok) {
    msg.style.color = 'var(--error-text)';
    msg.innerText = data.error || 'Could not get a hint.';
    return;
  }

  hintsUsed = data.hints_used;
  document.getElementById('hints-used').innerText = `Hints used: ${hintsUsed}`;
  if (data.hint === null) {
    msg.style.color = 'var(--error-text)';
    msg.innerText = data.message;
    return;
  }

  const index = data.hint.row * SIZE + data.hint.col;
  const input = document.getElementById('sudoku-board').getElementsByTagName('input')[index];
  input.value = data.hint.value;
  input.disabled = true;
  input.classList.add('hinted');
  updateConflicts();
  msg.style.color = 'var(--success-text)';
  msg.innerText = 'A correct cell was filled in and locked.';
}

async function checkSolution() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--error-text)';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    } else {
      inp.classList.remove('incorrect');
    }
  }
  if (data.complete) {
    stopTimer();
    if (!gameCompleted) {
      gameCompleted = true;
      if (!scoreSubmitted) {
        document.getElementById('score-entry').hidden = false;
        document.getElementById('player-name').focus();
      }
    }
    msg.style.color = 'var(--success-text)';
    msg.innerText = 'Congratulations! You solved it!';
  } else if (incorrect.size === 0) {
    msg.style.color = 'var(--success-text)';
    msg.innerText = 'No incorrect entries found yet.';
  } else {
    msg.style.color = 'var(--error-text)';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
restoreTheme();
window.addEventListener('load', () => {
  leaderboardAvailable = loadLeaderboard();
  renderLeaderboard();
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', useHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('sudoku-board').addEventListener('input', handleBoardInput);
  document.getElementById('score-entry').addEventListener('submit', (event) => {
    event.preventDefault();
    saveScore();
  });
  // initialize
  newGame();
});