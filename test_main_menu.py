# pylint: disable=no-member, line-too-long, missing-final-newline
"""Unit test per il modulo main_menu con pytest."""

import os
import pytest
from unittest.mock import MagicMock, patch
import pygame
from main_menu import OfflineGames

# Driver grafici dummy per pygame (test headless)
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# =========================
# FIXTURES
# =========================

@pytest.fixture
def app():
    """Fixture che gestisce il ciclo di vita dell'app OfflineGames."""
    pygame.init()
    app_instance = OfflineGames()
    yield app_instance
    pygame.quit()

# =========================
# TEST DASHBOARD
# =========================

def test_init_state(app):
    """Verifica lo stato iniziale della dashboard."""
    assert app.pointer == 0
    assert len(app.catalog) == 2
    assert "SUDOKU" in app.catalog[0]["label"]

@patch("sys.exit")
def test_shutdown(mock_exit, app):
    """Verifica che shutdown chiami sys.exit()."""
    app.shutdown()
    mock_exit.assert_called_once()

@patch("subprocess.Popen")
@patch.object(OfflineGames, "shutdown")
def test_boot_selected_game_success(mock_shutdown, mock_popen, app):
    """Verifica il corretto avvio di un gioco."""
    app.pointer = 1
    app.boot_selected_game()

    mock_popen.assert_called_once()
    called_args = mock_popen.call_args[0][0]
    assert "BattagliaNavale.py" in called_args[1]
    mock_shutdown.assert_called_once()

@patch("subprocess.Popen")
@patch("builtins.print")
@patch.object(OfflineGames, "shutdown")
def test_boot_selected_game_exception(mock_shutdown, mock_print, mock_popen, app):
    """Verifica la gestione errore durante l'avvio."""
    mock_popen.side_effect = OSError("File non trovato")
    app.pointer = 0

    app.boot_selected_game()

    mock_shutdown.assert_not_called()
    mock_print.assert_called_once()

@patch("pygame.display.flip")
def test_rendering(mock_flip, app):
    """Test del rendering UI."""
    app.pointer = 1
    app.refresh_ui()
    mock_flip.assert_called_once()

# =========================
# TEST NAVIGAZIONE
# =========================

@patch("pygame.time.Clock")
@patch("pygame.event.get")
def test_start_engine_navigation_down(mock_event_get, mock_clock_class, app):
    """Verifica la navigazione verso il basso."""
    mock_clock_inst = MagicMock()
    mock_clock_inst.tick.side_effect = StopIteration
    mock_clock_class.return_value = mock_clock_inst

    mock_event_get.return_value = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    ]

    with pytest.raises(StopIteration):
        app.start_engine()

    assert app.pointer == 1

@patch("pygame.time.Clock")
@patch("pygame.event.get")
def test_start_engine_navigation_up(mock_event_get, mock_clock_class, app):
    """Verifica la navigazione verso l'alto."""
    mock_clock_inst = MagicMock()
    mock_clock_inst.tick.side_effect = StopIteration
    mock_clock_class.return_value = mock_clock_inst

    app.pointer = 0
    mock_event_get.return_value = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    ]

    with pytest.raises(StopIteration):
        app.start_engine()

    assert app.pointer == len(app.catalog) - 1

@patch("pygame.time.Clock")
@patch("pygame.event.get")
@patch.object(OfflineGames, "boot_selected_game")
def test_start_engine_return(mock_boot, mock_event_get, mock_clock_class, app):
    """Verifica che INVIO avvii il gioco."""
    mock_clock_inst = MagicMock()
    mock_clock_inst.tick.side_effect = StopIteration
    mock_clock_class.return_value = mock_clock_inst

    mock_event_get.return_value = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    ]

    with pytest.raises(StopIteration):
        app.start_engine()

    mock_boot.assert_called_once()

@patch("pygame.time.Clock")
@patch("pygame.event.get")
@patch.object(OfflineGames, "shutdown")
def test_start_engine_quit(mock_shutdown, mock_event_get, mock_clock_class, app):
    """Verifica la chiusura con ESC o QUIT."""
    mock_clock_inst = MagicMock()
    # Usiamo una lista di effetti per gestire due chiamate separate
    mock_clock_inst.tick.side_effect = [StopIteration, StopIteration]
    mock_clock_class.return_value = mock_clock_inst

    # Test ESCAPE
    mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    with pytest.raises(StopIteration):
        app.start_engine()

    # Test QUIT
    mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]
    with pytest.raises(StopIteration):
        app.start_engine()

    assert mock_shutdown.call_count == 2