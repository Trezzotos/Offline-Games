"""Test dei punti di ingresso degli script di gioco."""

from unittest.mock import patch

import battleship
import main_menu
import sudoku


def test_battleship_main_runs_app() -> None:
    """battleship.main avvia il ciclo di gioco."""
    with patch("battleship.BattleshipApp") as app:
        battleship.main()
    app.return_value.run.assert_called_once()


def test_sudoku_main_runs_game() -> None:
    """sudoku.main avvia il ciclo di gioco."""
    with patch("sudoku.SudokuGame") as game:
        sudoku.main()
    game.return_value.run.assert_called_once()


def test_main_menu_main_starts_engine() -> None:
    """main_menu.main avvia il menu."""
    with patch("main_menu.OfflineGames") as menu:
        main_menu.main()
    menu.return_value.start_engine.assert_called_once()
