# Quality Development - Offline Games 🕹️
This repository was created to provide a Python template dedicated to **offline game development**, including <ins>automation pipelines and instructions</ins> for testing with pytest.

## How to start (one-time step)
To **download** the project and set up your local environment, run these commands:

```Plaintext
git clone git@github.com:USERNAME/repo-name.git
cd repo-name
git pull origin main
```
**Virtualenv setup**:
```Plaintext
python -m venv .venv
source .venv/bin/activate    # on Linux/macOS
.venv\Scripts\activate       # on Windows
pip install -r requirements.txt        # runtime dependencies only
pip install -r requirements_dev.txt    # runtime + development tools (lint, test)
```
Launch: `python src/main_menu.py` (or directly `src/sudoku.py` / `src/battleship.py`).

## Architecture
Each game is a package with separated responsibilities (SRP) and injectable dependencies (DIP):

```
src/
├── main_menu.py, sudoku.py, battleship.py   # thin entry points
├── common/launcher.py                       # GameLauncher (Protocol) + SubprocessLauncher
├── menu/        catalog.py · view.py · app.py
├── sudoku_game/ config · engine · state · renderer · app
└── battleship_game/
    ├── config.py      constants and layout
    ├── model.py       Cell, Ship, Board, Orientation (pure domain)
    ├── placement.py   FleetPlacer (Protocol) + RandomFleetPlacer
    ├── ai.py          ShootingStrategy (Protocol) + HuntTargetStrategy
    ├── game.py        BattleshipGame: rules, turns, phases (no Pygame)
    ├── board_view.py  rendering of a single board
    ├── screens.py     screens and overlays
    └── app.py         controller: events, enemy timer, loop
```
Game logic does not depend on Pygame, so it is testable without a window; there are no global variables.

## Pipeline & Repository Structure
To ensure the automations work correctly, we kept the structure of the original template. The **pipelines** take care of **verifying code quality** on every change.

**Directory Structure**: Make sure not to move the .github/ folder.

**Workflow**: The pipeline definitions are located in:

```
.github/workflows
```
## How to make a commit
When working on your game, make <ins>frequent and descriptive commits</ins>. Use **Conventional Commits** as in these examples:

```
git add src/game_logic.py
git commit -m 'feat(sudoku): add grid generation logic'
```
Other examples of approved messages:
```
fix(battleship): prevent ships from overlapping

docs(readme): update installation guide

test(logic): add unit tests for score calculation
```
## Software Testing & Coverage
Quality is essential. We use **pytest** to make sure everything works and to monitor **how much code is covered by tests**.

To run the tests and see the report:

```
pytest --cov --cov-report=term-missing
```
The CI runs the tests (`test.yml`) and fails if coverage drops below the threshold defined in `pyproject.toml` (`fail_under`, currently 90%).

Quality checks executed in CI (`lint.yml`): `pylint`, `flake8`, `mypy` (with `disallow_untyped_defs`), `black`, `isort`.

⚠️ The project maintains a minimum code coverage of 90%.

# The Project: Offline Games
## Main Menu
![Main Menu Screenshot](docs/images/MainMenu.png)

## Sudoku
![Sudoku Screenshot](docs/images/Sudoku.png)

## Battleship
![Battleship Screenshot](docs/images/Battleship.png)

The software is a collection of **classic games** developed purely in **Python**, designed to be played **without an internet connection**.

**Sudoku**: A logical challenge with dynamic grid generation.

**Battleship**: The classic strategy game reproduced in digital form.

To offer a superior user experience and an appealing graphical interface, the project uses:
```
Reference graphics library:  [pygame] 
```
