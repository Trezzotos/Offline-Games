"""Unit test per il menu principale."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pygame
import pytest

from menu.app import OfflineGames
from menu.catalog import DEFAULT_CATALOG, GameEntry


@pytest.fixture(name="launcher")
def fixture_launcher() -> MagicMock:
    """Launcher finto: nessun sotto-processo reale."""
    return MagicMock()


@pytest.fixture(name="app")
def fixture_app(launcher: MagicMock) -> Iterator[OfflineGames]:
    """Gestisce il ciclo di vita dell'app OfflineGames."""
    pygame.init()
    instance = OfflineGames(launcher=launcher)
    yield instance
    pygame.quit()


def key_event(key: int) -> pygame.event.Event:
    """Evento di pressione tasto."""
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def run_one_frame(app: OfflineGames, events: list[pygame.event.Event]) -> None:
    """Esegue un solo giro del loop principale."""
    clock = MagicMock()
    clock.tick.side_effect = StopIteration
    with patch("pygame.time.Clock", return_value=clock):
        with patch("pygame.event.get", return_value=events):
            with pytest.raises(StopIteration):
                app.start_engine()


def test_init_state(app: OfflineGames) -> None:
    """Stato iniziale della dashboard."""
    assert app.pointer == 0
    assert app.catalog == DEFAULT_CATALOG
    assert app.catalog[0].label == "SUDOKU"


def test_custom_catalog_is_injectable(launcher: MagicMock) -> None:
    """Il catalogo è iniettabile (Open/Closed)."""
    catalog = (GameEntry("TEST", "test.py"),)
    pygame.init()
    app = OfflineGames(catalog=catalog, launcher=launcher)
    with patch.object(OfflineGames, "shutdown"):
        app.boot_selected_game()
    launcher.launch.assert_called_once_with("test.py")


@patch("sys.exit")
def test_shutdown(mock_exit: MagicMock, app: OfflineGames) -> None:
    """shutdown chiama sys.exit()."""
    app.shutdown()
    mock_exit.assert_called_once()


def test_boot_selected_game_success(app: OfflineGames, launcher: MagicMock) -> None:
    """Avvia lo script selezionato e chiude il menu."""
    app.pointer = 1
    with patch.object(OfflineGames, "shutdown") as mock_shutdown:
        app.boot_selected_game()
    launcher.launch.assert_called_once_with("battleship.py")
    mock_shutdown.assert_called_once()


@patch("builtins.print")
def test_boot_selected_game_error(
    mock_print: MagicMock, app: OfflineGames, launcher: MagicMock
) -> None:
    """Un errore di avvio viene riportato e il menu resta aperto."""
    launcher.launch.side_effect = OSError("File non trovato")
    with patch.object(OfflineGames, "shutdown") as mock_shutdown:
        app.boot_selected_game()
    mock_shutdown.assert_not_called()
    mock_print.assert_called_once()


@patch("pygame.display.flip")
def test_rendering(mock_flip: MagicMock, app: OfflineGames) -> None:
    """Il rendering mostra il frame una volta."""
    app.pointer = 1
    app.refresh_ui()
    mock_flip.assert_called_once()


def test_navigation_down_and_wrap(app: OfflineGames) -> None:
    """Freccia giù avanza e torna all'inizio."""
    run_one_frame(app, [key_event(pygame.K_DOWN)])
    assert app.pointer == 1
    app.handle_key(pygame.K_DOWN)
    assert app.pointer == 0


def test_navigation_up_wraps(app: OfflineGames) -> None:
    """Freccia su dal primo elemento va all'ultimo."""
    run_one_frame(app, [key_event(pygame.K_UP)])
    assert app.pointer == len(app.catalog) - 1


def test_return_boots_game(app: OfflineGames) -> None:
    """INVIO avvia il gioco."""
    with patch.object(OfflineGames, "boot_selected_game") as mock_boot:
        run_one_frame(app, [key_event(pygame.K_RETURN)])
    mock_boot.assert_called_once()


def test_escape_and_quit_shutdown(app: OfflineGames) -> None:
    """ESC e QUIT chiudono l'app."""
    with patch.object(OfflineGames, "shutdown") as mock_shutdown:
        run_one_frame(app, [key_event(pygame.K_ESCAPE)])
        run_one_frame(app, [pygame.event.Event(pygame.QUIT)])
    assert mock_shutdown.call_count == 2
