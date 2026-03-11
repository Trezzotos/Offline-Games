import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pygame

# 1. Imposta driver video/audio "dummy" PRIMA di importare il main_menu
# Questo permette ai test grafici di girare in background senza aprire finestre.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Importiamo il modulo dopo aver settato l'ambiente dummy
import main_menu
from main_menu import OfflineGames

class TestOfflineGames(unittest.TestCase):
    
    def setUp(self):
        """Prepara l'ambiente prima di ogni test."""
        # Forziamo l'init di pygame in modalità dummy
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

    @patch('sys.exit')
    def test_shutdown(self, mock_exit):
        """Verifica che la funzione shutdown chiami sys.exit()"""
        self.app.shutdown()
        mock_exit.assert_called_once()

    @patch('subprocess.Popen')
    @patch.object(OfflineGames, 'shutdown')
    def test_boot_selected_game_success(self, mock_shutdown, mock_popen):
        """Verifica il corretto avvio di un gioco."""
        self.app.pointer = 1  # Selezioniamo BATTAGLIA NAVALE
        self.app.boot_selected_game()
        
        # Verifica che subprocess.Popen sia stato chiamato
        mock_popen.assert_called_once()
        # Verifica che il path contenga il file corretto
        called_args = mock_popen.call_args[0][0]
        self.assertIn("BattagliaNavale.py", called_args[1])
        # Verifica che l'app venga chiusa dopo l'avvio
        mock_shutdown.assert_called_once()

    @patch('subprocess.Popen')
    @patch('builtins.print')
    @patch.object(OfflineGames, 'shutdown')
    def test_boot_selected_game_exception(self, mock_shutdown, mock_print, mock_popen):
        """Verifica la gestione dell'errore (OSError) in fase di avvio."""
        mock_popen.side_effect = OSError("File non trovato")
        self.app.pointer = 0
        
        self.app.boot_selected_game()
        
        # Il programma non deve chiudersi se l'avvio fallisce
        mock_shutdown.assert_not_called()
        # Deve però stampare l'errore a terminale
        mock_print.assert_called_once()

    @patch('pygame.display.flip')
    def test_rendering(self, mock_flip):
        """
        Esegue il rendering UI forzando i rami if/else 
        per massimizzare la coverage visiva.
        """
        self.app.pointer = 1  # Mettiamo il puntatore su un elemento diverso da 0
        self.app.refresh_ui()
        mock_flip.assert_called_once()

    # --- Test del loop infinito ---
    # Usiamo side_effect su clock.tick per lanciare un'eccezione
    # e rompere il 'while True' altrimenti il test si bloccherebbe per sempre.
    
    
    @patch('pygame.time.Clock')
    @patch('pygame.event.get')
    def test_start_engine_navigation_down(self, mock_event_get, mock_clock_class):
        """Verifica la navigazione verso il BASSO."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst
        
        mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)]
        
        with self.assertRaises(StopIteration):
            self.app.start_engine()
            
        self.assertEqual(self.app.pointer, 1)

    @patch('pygame.time.Clock')
    @patch('pygame.event.get')
    def test_start_engine_navigation_up(self, mock_event_get, mock_clock_class):
        """Verifica la navigazione verso l'ALTO."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        self.app.pointer = 0
        mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)]
        
        with self.assertRaises(StopIteration):
            self.app.start_engine()
            
        # Essendo 0, facendo SU, con il modulo (%) andrà all'ultimo elemento
        self.assertEqual(self.app.pointer, len(self.app.catalog) - 1)

    @patch('pygame.time.Clock')
    @patch('pygame.event.get')
    @patch.object(OfflineGames, 'boot_selected_game')
    def test_start_engine_return(self, mock_boot, mock_event_get, mock_clock_class):
        """Verifica che premendo INVIO si chiami il boot del gioco."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
        
        with self.assertRaises(StopIteration):
            self.app.start_engine()
            
        mock_boot.assert_called_once()

    @patch('pygame.time.Clock')
    @patch('pygame.event.get')
    @patch.object(OfflineGames, 'shutdown')
    def test_start_engine_quit(self, mock_shutdown, mock_event_get, mock_clock_class):
        """Verifica la chiusura tramite pulsante (X) o tasto ESC."""
        mock_clock_inst = MagicMock()
        mock_clock_inst.tick.side_effect = StopIteration
        mock_clock_class.return_value = mock_clock_inst

        # Testiamo ESC
        mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
        with self.assertRaises(StopIteration):
            self.app.start_engine()
        
        # Testiamo evento QUIT (X della finestra)
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]
        with self.assertRaises(StopIteration):
            self.app.start_engine()

        self.assertEqual(mock_shutdown.call_count, 2)