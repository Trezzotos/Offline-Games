"""Controller del menu principale."""

from __future__ import annotations

import subprocess
import sys

import pygame

from common.launcher import GameLauncher, SubprocessLauncher
from menu.catalog import DEFAULT_CATALOG, GameEntry
from menu.view import SCREEN_SIZE, MenuView

FPS = 60


class OfflineGames:
    """Dashboard grafica per selezionare e avviare giochi offline."""

    def __init__(
        self,
        catalog: tuple[GameEntry, ...] = DEFAULT_CATALOG,
        launcher: GameLauncher | None = None,
    ) -> None:
        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("MULTIGAME DASHBOARD")
        self.view = MenuView(self.window)
        self.catalog = catalog
        self.launcher = launcher or SubprocessLauncher()
        self.pointer = 0

    def refresh_ui(self) -> None:
        """Aggiorna la UI."""
        self.view.draw(self.catalog, self.pointer)

    def boot_selected_game(self) -> None:
        """Avvia il gioco selezionato e chiude il menu."""
        script = self.catalog[self.pointer].script
        try:
            self.launcher.launch(script)
        except (OSError, subprocess.SubprocessError) as error:
            print(f"Errore nell'avvio di {script}: {error}")
            return
        self.shutdown()

    @staticmethod
    def shutdown() -> None:
        """Chiude l'applicazione."""
        pygame.quit()
        sys.exit()

    def handle_key(self, key: int) -> None:
        """Gestisce la pressione di un tasto."""
        if key == pygame.K_UP:
            self.pointer = (self.pointer - 1) % len(self.catalog)
        elif key == pygame.K_DOWN:
            self.pointer = (self.pointer + 1) % len(self.catalog)
        elif key == pygame.K_RETURN:
            self.boot_selected_game()
        elif key == pygame.K_ESCAPE:
            self.shutdown()

    def start_engine(self) -> None:
        """Loop principale."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.shutdown()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.refresh_ui()
            clock.tick(FPS)
