"""Unit test per il modulo main_menu."""

# pylint: disable=no-member
# pylint: disable=line-too-long, missing-final-newline

import os
import unittest
from unittest.mock import MagicMock, patch

import pygame

from main_menu import OfflineGames

# Driver grafici dummy per pygame (test headless)
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


class TestOfflineGames(unittest.TestCase):
    """Test della dashboard OfflineGames."""

    def setUp(self):
        """Prepara l'ambiente prima di ogni test."""
        pygame.init()
        self.app = OfflineGames()

    def tearDown(self):
        """Pulisce l'ambiente dopo ogni test."""
        pygame.quit()

    def test_init_state(self):
        """Verifica lo stato iniziale della dashboard."""
        self.assertEqual(self.app.pointer, 0)
        self.assertEqual(len(self.app.catalog), 2)
        self.assertIn("SUDOKU", self.app.catalog[0]["label"])

    @patch("sys.exit")
    def test_shutdown(self, mock_exit):
        """Verifica che shutdown chiami sys.exit()."""
        self.app.shutdown()
        mock_exit.assert_called_once()

    @patch("subprocess.Popen")
    @patch.object(OfflineGames, "shutdown")
    def test_boot_selected_game_success(self, mock_shutdown, mock_popen):
        """Verifica il corretto avvio di un gioco."""
        self.app.pointer = 1
        self.app.boot_selected_game()

        mock_popen.assert_called_once()

        called_args = mock_popen.call_args[0][0]
        self.assertIn("BattagliaNavale.py", called_args[1])

        mock_shutdown.assert_called_once()

    @patch("subprocess.Popen")
    @patch("builtins.print")
    @patch.object(OfflineGames, "shutdown")
    def test_boot_selected_game_exception(self, mock_shutdown, mock_print, mock_popen):
        """Verifica la gestione errore durante l'avvio."""
        mock_popen.side_effect = OSError("File non trovato")
        self.app.pointer = 0

        self.app.boot_selected_game()

        mock_shutdown.assert_not_called()
        mock_print.assert_called_once()

    @patch("pygame.display.flip")
    def test_rendering(self, mock_flip):
        """Test del rendering UI."""
        self.app.pointer = 1
        self.app.refresh_ui()
        mock_flip.assert_called_once()

    @patch("pygame.time.Clock")
    @patch("pygame.event.get")
    def test_start_engine_navigation_down(self, mock_event_get, mock_clock_class):
        """Verifica la navigazione verso il basso."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        ]

        with self.assertRaises(StopIteration):
            self.app.start_engine()

        self.assertEqual(self.app.pointer, 1)

    @patch("pygame.time.Clock")
    @patch("pygame.event.get")
    def test_start_engine_navigation_up(self, mock_event_get, mock_clock_class):
        """Verifica la navigazione verso l'alto."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        self.app.pointer = 0

        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        ]

        with self.assertRaises(StopIteration):
            self.app.start_engine()

        self.assertEqual(self.app.pointer, len(self.app.catalog) - 1)

    @patch("pygame.time.Clock")
    @patch("pygame.event.get")
    @patch.object(OfflineGames, "boot_selected_game")
    def test_start_engine_return(self, mock_boot, mock_event_get, mock_clock_class):
        """Verifica che INVIO avvii il gioco."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        ]

        with self.assertRaises(StopIteration):
            self.app.start_engine()

        mock_boot.assert_called_once()

    @patch("pygame.time.Clock")
    @patch("pygame.event.get")
    @patch.object(OfflineGames, "shutdown")
    def test_start_engine_quit(self, mock_shutdown, mock_event_get, mock_clock_class):
        """Verifica la chiusura con ESC o QUIT."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        ]

        with self.assertRaises(StopIteration):
            self.app.start_engine()

        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        with self.assertRaises(StopIteration):
            self.app.start_engine()

        self.assertEqual(mock_shutdown.call_count, 2)
