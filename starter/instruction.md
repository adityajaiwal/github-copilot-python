# GitHub Copilot Instructions – Sudoku Game

## Project Overview
Build a complete, user-friendly Sudoku game using Python Flask, HTML, CSS, and JavaScript.

The project starts with a legacy Sudoku application. Refactor and improve the existing code instead of unnecessarily replacing the entire application.

## Technology Requirements
- Python for backend logic.
- Flask for web application routes.
- HTML for page structure.
- CSS for responsive styling.
- JavaScript for interactive game features.
- pytest for automated testing.
- Browser localStorage for leaderboard persistence.

## Coding Standards
- Write clean, readable, maintainable code.
- Use meaningful variable and function names.
- Organize code into reusable functions and modules.
- Avoid unnecessary duplication.
- Add comments where logic is not obvious.
- Handle errors gracefully.
- Preserve existing working functionality when refactoring.

## Sudoku Game Requirements
1. Display a 9×9 Sudoku grid.
2. Support Easy, Medium, and Hard difficulty levels.
3. Generate puzzles with exactly one valid solution.
4. Lock prefilled cells so players cannot edit them.
5. Validate rows, columns, and 3×3 boxes.
6. Highlight conflicting or incorrect entries.
7. Provide a Hint button that fills one valid empty cell and locks it.
8. Provide a Check button that identifies incorrect entries.
9. Display a congratulatory message when the puzzle is solved correctly.
10. Include a timer to track playing time.
11. Maintain a Top 10 leaderboard with player name, time, difficulty, and hints used.
12. Save leaderboard information in browser localStorage.
13. Include a Dark/Light mode toggle.

## User Interface Requirements
- Use responsive CSS for desktop and mobile devices.
- Alternate background colors between the 3×3 Sudoku boxes.
- Keep numbers, buttons, and instructions readable.
- Support both light and dark modes.
- Ensure the interface is consistent and accessible.

## Testing Requirements
- Use pytest for automated tests.
- Test Sudoku puzzle generation and validation.
- Test that generated puzzles have exactly one solution.
- Test difficulty levels.
- Test Flask routes and responses.
- Test invalid moves, hints, and completed puzzles.
- Run tests after every major change.
- Fix failing tests before continuing.

## GitHub Copilot Usage
- Explain proposed changes before implementing major modifications.
- Work in small, understandable steps.
- Do not modify unrelated files.
- Do not remove existing functionality without explaining why.
- Ask for clarification when requirements are unclear.
- Review generated code before accepting suggestions.
- Explain unfamiliar Python, Flask, HTML, CSS, and JavaScript concepts in beginner-friendly language.

## Project Quality
The final application should be functional, responsive, maintainable, tested, and ready for public GitHub submission.

Update README.md with project setup, installation, running, and testing instructions.


## Critical Evaluation of GitHub Copilot Suggestions

- Do not automatically accept every Copilot-generated suggestion.
- Review proposed code for correctness, compatibility, and maintainability.
- Compare suggestions with the existing project architecture.
- Reject suggestions that introduce unnecessary changes or break existing functionality.
- Modify suggestions when improvements are needed.
- Explain the reason for accepting, modifying, or rejecting important suggestions.
- Keep screenshots or code comments as evidence of critical evaluation.
- Run relevant tests after implementing accepted changes.

The developer is responsible for reviewing and validating all AI-generated code.