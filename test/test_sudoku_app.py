"""Test di controller e rendering del Sudoku."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from sudoku_game.app import Mode, SudokuGame


@pytest.fixture(name="launcher")
def fixture_launcher() -> MagicMock:
    """Launcher finto."""
    return MagicMock()


@pytest.fixture(name="game")
def fixture_game(launcher: MagicMock) -> SudokuGame:
    """Gioco con launcher finto."""
    pygame.init()
    return SudokuGame(launcher=launcher)


def test_setup_game(game: SudokuGame) -> None:
    """Avviare una partita crea lo stato e passa a PLAYING."""
    game.setup_game("MEDIUM")
    assert game.mode is Mode.PLAYING
    assert game.state is not None and game.state.difficulty_label == "MEDIUM"
    assert game.state.grid.shape == (9, 9)


def test_menu_navigation_and_start(game: SudokuGame) -> None:
    """Frecce e INVIO nel menu."""
    game.handle_key(pygame.K_DOWN)
    assert game.menu_sel == 2
    game.handle_key(pygame.K_DOWN)
    assert game.menu_sel == 0
    game.handle_key(pygame.K_UP)
    assert game.menu_sel == 2
    game.handle_key(pygame.K_a)
    assert game.mode is Mode.MENU
    game.handle_key(pygame.K_RETURN)
    assert game.mode is Mode.PLAYING


def test_play_keys(game: SudokuGame) -> None:
    """Tasti di gioco: note, movimento, numeri e cancellazione."""
    game.setup_game("EASY")
    state = game.state
    assert state is not None
    game.handle_key(pygame.K_a)
    assert state.note_mode
    game.handle_key(pygame.K_UP)
    assert state.selected == [3, 4]
    state.selected = [0, 0]
    state.is_fixed[0, 0] = False
    state.grid[0, 0] = 0
    game.handle_key(pygame.K_5, "5")
    assert 5 in state.notes[0][0]
    game.handle_key(pygame.K_6)
    assert 6 in state.notes[0][0]
    state.note_mode = False
    state.grid[0, 0] = 7
    game.handle_key(pygame.K_BACKSPACE)
    assert state.grid[0, 0] == 0
    game.handle_key(pygame.K_F1)


def test_play_keys_ignored_when_game_over(game: SudokuGame) -> None:
    """A partita persa i tasti di gioco sono ignorati."""
    game.setup_game("EASY")
    assert game.state is not None
    game.state.game_over = True
    game.handle_key(pygame.K_a)
    assert not game.state.note_mode


def test_escape_returns_to_menu_then_launches_main_menu(
    game: SudokuGame, launcher: MagicMock
) -> None:
    """ESC in partita torna al menu; ESC nel menu riavvia il menu principale."""
    game.setup_game("EASY")
    game.handle_key(pygame.K_ESCAPE)
    assert game.mode is Mode.MENU
    with patch("sys.exit") as mock_exit:
        game.handle_key(pygame.K_ESCAPE)
    launcher.launch.assert_called_once_with("main_menu.py")
    mock_exit.assert_called_once()


def test_draw_all_modes(game: SudokuGame) -> None:
    """Disegno di menu, partita, note, vittoria e sconfitta."""
    game.draw()
    game.setup_game("EASY")
    state = game.state
    assert state is not None
    state.notes[0][0] = {1, 5, 9}
    state.note_mode = True
    state.grid[1, 1] = (state.solution[1, 1] % 9) + 1
    state.lives = 1
    game.draw()
    state.won = True
    game.draw()
    state.won, state.game_over = False, True
    game.draw()


def test_run_handles_events_and_quits(game: SudokuGame) -> None:
    """Il ciclo principale gestisce tasti e QUIT."""
    events = iter(
        [
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode="")],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    with patch("pygame.event.get", lambda: next(events)):
        with patch.object(SudokuGame, "quit", side_effect=StopIteration):
            with pytest.raises(StopIteration):
                game.run()
    assert game.menu_sel == 2


def test_quit_exits(game: SudokuGame) -> None:
    """quit chiude Pygame e il processo."""
    with patch("sys.exit") as mock_exit:
        game.quit()
    mock_exit.assert_called_once()
